"""
Base OSINT Collector class for ReconVault intelligence system.

This module provides an abstract base class for all OSINT collectors with
common functionality for data collection, validation, rate limiting, and
ethics compliance.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Tuple
import logging
import time
import random
from urllib.robotparser import RobotFileParser
import requests
from urllib.parse import urlparse
import fake_useragent
import uuid

@dataclass
class CollectorConfig:
    """Configuration for OSINT collectors"""
    target: str
    data_type: str
    timeout: int = 30
    max_retries: int = 3
    rate_limit: float = 2.0  # Requests per second
    respect_robots_txt: bool = True
    use_proxy: bool = False
    proxy_url: Optional[str] = None

class BaseCollector(ABC):
    """Abstract base class for all OSINT collectors"""
    
    def __init__(self, config: CollectorConfig):
        self.config = config
        self.logger = logging.getLogger(f"{self.__class__.__name__}")
        self.session = self._create_session()
        self.robots_parser = RobotFileParser()
        self.last_request_time = 0
        self.user_agent_rotator = fake_useragent.UserAgent()
        self.correlation_id = self._generate_correlation_id()
        
    def _create_session(self) -> requests.Session:
        """Create requests session with proper configuration"""
        session = requests.Session()
        session.timeout = self.config.timeout
        session.headers.update({
            'User-Agent': self._rotate_user_agent(),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        })
        
        if self.config.use_proxy and self.config.proxy_url:
            session.proxies.update({
                'http': self.config.proxy_url,
                'https': self.config.proxy_url
            })
            
        return session
    
    def _rotate_user_agent(self) -> str:
        """Rotate user agent for stealth collection"""
        return self.user_agent_rotator.random
    
    def _generate_correlation_id(self) -> str:
        """Generate unique correlation ID for logging"""
        return str(uuid.uuid4())
    
    def _rate_limit_wait(self) -> None:
        """Implement rate limiting with random jitter"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        required_delay = 1.0 / self.config.rate_limit
        
        if time_since_last < required_delay:
            sleep_time = required_delay - time_since_last + random.uniform(0, 0.5)
            self.logger.debug(f"[{self.correlation_id}] Rate limiting: sleeping for {sleep_time:.2f}s")
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()
    
    def _check_robots_txt(self, url: str) -> bool:
        """Check robots.txt compliance"""
        if not self.config.respect_robots_txt:
            return True
            
        try:
            parsed_url = urlparse(url)
            robots_url = f"{parsed_url.scheme}://{parsed_url.netloc}/robots.txt"
            
            self._rate_limit_wait()
            self.robots_parser.set_url(robots_url)
            self.robots_parser.read()
            
            can_fetch = self.robots_parser.can_fetch(self._rotate_user_agent(), url)
            if not can_fetch:
                self.logger.warning(f"[{self.correlation_id}] Robots.txt disallows crawling: {url}")
                return False
                
            return True
        except Exception as e:
            self.logger.error(f"[{self.correlation_id}] Error checking robots.txt for {url}: {e}")
            return True  # Allow crawling if robots.txt is unavailable
    
    def _make_request(self, url: str, method: str = "GET", **kwargs) -> requests.Response:
        """Make HTTP request with retry logic and rate limiting"""
        if not self._check_robots_txt(url):
            raise Exception(f"Robots.txt disallows crawling: {url}")
        
        retry_count = 0
        last_exception = None
        
        while retry_count < self.config.max_retries:
            try:
                self._rate_limit_wait()
                self.logger.debug(f"[{self.correlation_id}] {method} request to {url} (attempt {retry_count + 1})")
                
                response = self.session.request(method, url, **kwargs)
                response.raise_for_status()
                
                # Handle rate limiting
                if response.status_code == 429:
                    retry_after = int(response.headers.get('Retry-After', 60))
                    self.logger.warning(f"[{self.correlation_id}] Rate limit hit, waiting {retry_after}s")
                    time.sleep(retry_after)
                    continue
                
                return response
                
            except requests.exceptions.RequestException as e:
                last_exception = e
                retry_count += 1
                
                if retry_count < self.config.max_retries:
                    backoff_time = (2 ** retry_count) + random.uniform(0, 1)
                    self.logger.warning(f"[{self.correlation_id}] Request failed: {e}. Retrying in {backoff_time}s")
                    time.sleep(backoff_time)
                else:
                    self.logger.error(f"[{self.correlation_id}] Max retries exceeded for {url}")
        
        raise last_exception
    
    @abstractmethod
    async def collect(self) -> Dict[str, Any]:
        """Main collection method to be implemented by subclasses"""
        pass
    
    @abstractmethod
    def normalize(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Normalize collected data to Entity/Relationship format"""
        pass
    
    def validate(self, data: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], List[str]]:
        """Validate normalized data and return (valid_data, errors)"""
        valid_data = []
        errors = []
        
        for item in data:
            if not item.get("value") or not item.get("type"):
                errors.append(f"Invalid entity: missing required fields in {item}")
                continue
            
            valid_data.append(item)
        
        return valid_data, errors
    
    async def execute(self) -> Tuple[List[Dict[str, Any]], List[str]]:
        """Execute the full collection pipeline"""
        try:
            self.logger.info(f"[{self.correlation_id}] Starting collection for target: {self.config.target}")
            
            # Collect data
            raw_data = await self.collect()
            
            # Normalize data
            normalized_data = self.normalize(raw_data)
            self.logger.info(f"[{self.correlation_id}] Normalized {len(normalized_data)} entities")
            
            # Validate data
            valid_data, validation_errors = self.validate(normalized_data)
            self.logger.info(f"[{self.correlation_id}] Validated {len(valid_data)} entities, {len(validation_errors)} errors")
            
            if validation_errors:
                self.logger.warning(f"[{self.correlation_id}] Validation errors: {validation_errors}")
            
            self.logger.info(f"[{self.correlation_id}] Collection completed successfully")
            return valid_data, validation_errors
            
        except Exception as e:
            self.logger.error(f"[{self.correlation_id}] Collection failed: {e}")
            raise
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.session.close()