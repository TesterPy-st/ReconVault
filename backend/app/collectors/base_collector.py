"""
Base Collector Module

Provides abstract base class and common functionality for all OSINT collectors.
"""

import asyncio
import time
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Set
from urllib.robotparser import RobotFileParser

import httpx
from loguru import logger


class DataType(Enum):
    """Enumeration of data types collectors can collect"""

    DOMAIN = "domain"
    IP = "ip"
    EMAIL = "email"
    USERNAME = "username"
    URL = "url"
    SOCIAL_PROFILE = "social_profile"
    IMAGE = "image"
    AUDIO = "audio"
    VIDEO = "video"
    TEXT = "text"
    METADATA = "metadata"


class RiskLevel(Enum):
    """Risk levels for collected entities"""

    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    INFO = "INFO"


@dataclass
class CollectorConfig:
    """Configuration for collectors"""

    target: str
    data_type: DataType
    timeout: int = 30
    max_retries: int = 3
    rate_limit: float = 2.0  # seconds between requests
    respect_robots_txt: bool = True
    user_agent: Optional[str] = None
    proxy: Optional[str] = None
    verify_ssl: bool = True


@dataclass
class CollectionResult:
    """Result from a collector"""

    success: bool
    data: List[Dict[str, Any]] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    risk_level: RiskLevel = RiskLevel.INFO
    metadata: Dict[str, Any] = field(default_factory=dict)
    collector_name: str = ""
    correlation_id: str = ""
    collection_time: float = 0.0


class UserAgentRotator:
    """Rotates user agents to avoid detection"""

    USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    ]

    def __init__(self):
        self.current_index = 0

    def get_user_agent(self) -> str:
        """Get next user agent in rotation"""
        ua = self.USER_AGENTS[self.current_index]
        self.current_index = (self.current_index + 1) % len(self.USER_AGENTS)
        return ua

    def get_random_user_agent(self) -> str:
        """Get a random user agent"""
        import random

        return random.choice(self.USER_AGENTS)


class BaseCollector(ABC):
    """
    Abstract base class for all OSINT collectors.

    Provides common functionality:
    - Error handling with retry logic
    - Rate limiting with exponential backoff
    - Logging with correlation IDs
    - Ethics compliance checks (robots.txt, user-agent)
    - Session management
    """

    def __init__(self, config: CollectorConfig, name: str):
        self.config = config
        self.name = name
        self.correlation_id = str(uuid.uuid4())
        self.user_agent_rotator = UserAgentRotator()
        self.session: Optional[httpx.AsyncClient] = None
        self.last_request_time = 0.0
        self.robots_cache: Dict[str, RobotFileParser] = {}

        logger.info(
            f"Initialized collector {self.name}",
            extra={"correlation_id": self.correlation_id, "target": config.target},
        )

    async def __aenter__(self):
        """Async context manager entry"""
        await self._init_session()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self._close_session()

    async def _init_session(self):
        """Initialize HTTP session"""
        user_agent = (
            self.config.user_agent or self.user_agent_rotator.get_random_user_agent()
        )
        headers = {"User-Agent": user_agent}

        self.session = httpx.AsyncClient(
            timeout=self.config.timeout,
            headers=headers,
            verify=self.config.verify_ssl,
            proxy=self.config.proxy,
            follow_redirects=True,
        )

        logger.debug(f"HTTP session initialized for {self.name}")

    async def _close_session(self):
        """Close HTTP session"""
        if self.session:
            await self.session.aclose()
            logger.debug(f"HTTP session closed for {self.name}")

    async def _apply_rate_limit(self):
        """Apply rate limiting between requests"""
        now = time.time()
        time_since_last = now - self.last_request_time

        if time_since_last < self.config.rate_limit:
            delay = self.config.rate_limit - time_since_last
            logger.debug(
                f"Rate limiting: waiting {delay:.2f}s",
                extra={"correlation_id": self.correlation_id},
            )
            await asyncio.sleep(delay)

        self.last_request_time = time.time()

    async def _check_robots_txt(self, url: str, path: str = "/") -> bool:
        """
        Check if robots.txt allows access to the given URL/path.

        Returns:
            True if allowed or robots.txt unavailable, False if disallowed
        """
        if not self.config.respect_robots_txt:
            return True

        try:
            from urllib.parse import urlparse

            parsed = urlparse(url)
            base_url = f"{parsed.scheme}://{parsed.netloc}"

            if base_url not in self.robots_cache:
                robots_url = f"{base_url}/robots.txt"
                try:
                    response = await self.session.get(robots_url, timeout=10)
                    if response.status_code == 200:
                        rp = RobotFileParser()
                        rp.parse(response.text.splitlines())
                        self.robots_cache[base_url] = rp
                        logger.debug(f"Loaded robots.txt for {base_url}")
                    else:
                        logger.debug(f"No robots.txt at {base_url}, allowing access")
                        return True
                except Exception as e:
                    logger.warning(f"Failed to fetch robots.txt: {e}")
                    return True

            robot_parser = self.robots_cache[base_url]
            user_agent = self.config.user_agent or "*"
            allowed = robot_parser.can_fetch(user_agent, path)

            if not allowed:
                logger.warning(
                    f"robots.txt disallows access to {path} for {user_agent}",
                    extra={"correlation_id": self.correlation_id},
                )

            return allowed

        except Exception as e:
            logger.error(f"Error checking robots.txt: {e}")
            return True

    async def _retry_with_backoff(
        self, func, max_retries: Optional[int] = None, base_delay: float = 1.0
    ):
        """
        Retry function with exponential backoff.

        Args:
            func: Async function to retry
            max_retries: Override default max retries
            base_delay: Initial delay in seconds

        Returns:
            Function result

        Raises:
            Last exception if all retries exhausted
        """
        retries = max_retries or self.config.max_retries
        last_exception = None

        for attempt in range(retries + 1):
            try:
                return await func()
            except Exception as e:
                last_exception = e
                if attempt == retries:
                    logger.error(
                        f"All {retries} retries exhausted for {self.name}",
                        extra={"correlation_id": self.correlation_id},
                    )
                    raise

                delay = base_delay * (2**attempt)
                logger.warning(
                    f"Attempt {attempt + 1}/{retries} failed for {self.name}: {e}, "
                    f"retrying in {delay:.2f}s",
                    extra={"correlation_id": self.correlation_id},
                )
                await asyncio.sleep(delay)

        raise last_exception

    @abstractmethod
    async def collect(self) -> CollectionResult:
        """
        Collect data from the target source.

        Must be implemented by all collectors.

        Returns:
            CollectionResult with collected data
        """
        pass

    @abstractmethod
    def normalize(self, raw_data: Any) -> List[Dict[str, Any]]:
        """
        Normalize raw collected data into standard format.

        Must be implemented by all collectors.

        Args:
            raw_data: Raw data from collection

        Returns:
            List of normalized entity dictionaries
        """
        pass

    @abstractmethod
    def validate(self, data: Dict[str, Any]) -> bool:
        """
        Validate normalized data.

        Must be implemented by all collectors.

        Args:
            data: Normalized data dictionary

        Returns:
            True if valid, False otherwise
        """
        pass

    async def execute(self) -> CollectionResult:
        """
        Execute the full collection pipeline with error handling.

        Returns:
            CollectionResult with success/failure status
        """
        start_time = time.time()

        result = CollectionResult(
            success=False, collector_name=self.name, correlation_id=self.correlation_id
        )

        try:
            logger.info(
                f"Starting collection with {self.name}",
                extra={
                    "correlation_id": self.correlation_id,
                    "target": self.config.target,
                    "data_type": self.config.data_type.value,
                },
            )

            await self._apply_rate_limit()

            raw_result = await self._retry_with_backoff(self.collect)

            result.success = raw_result.success
            result.data = raw_result.data
            result.errors = raw_result.errors
            result.risk_level = raw_result.risk_level
            result.metadata = raw_result.metadata

            collection_time = time.time() - start_time
            result.collection_time = collection_time

            if result.success:
                logger.info(
                    f"Collection completed by {self.name}",
                    extra={
                        "correlation_id": self.correlation_id,
                        "entities_collected": len(result.data),
                        "collection_time": f"{collection_time:.2f}s",
                        "risk_level": result.risk_level.value,
                    },
                )
            else:
                logger.error(
                    f"Collection failed for {self.name}",
                    extra={
                        "correlation_id": self.correlation_id,
                        "errors": result.errors,
                    },
                )

        except Exception as e:
            result.errors.append(str(e))
            result.collection_time = time.time() - start_time

            logger.exception(
                f"Exception in {self.name}",
                extra={"correlation_id": self.correlation_id},
            )

        return result

    def _create_entity(
        self,
        entity_type: str,
        value: str,
        risk_level: RiskLevel = RiskLevel.INFO,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Create a normalized entity dictionary.

        Args:
            entity_type: Type of entity (DOMAIN, EMAIL, etc.)
            value: Primary value of the entity
            risk_level: Risk level for the entity
            metadata: Additional metadata

        Returns:
            Entity dictionary
        """
        return {
            "entity_type": entity_type,
            "value": value,
            "risk_level": risk_level.value,
            "metadata": metadata or {},
            "source": self.name,
            "correlation_id": self.correlation_id,
        }
