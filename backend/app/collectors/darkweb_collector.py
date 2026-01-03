"""
Dark Web Collector

Collects OSINT data from the dark web including:
- Tor session initialization
- Onion site searching
- Onion data extraction
- Dark web mention checking
"""

import asyncio
import re
from typing import Any, Dict, List, Optional

import httpx
from bs4 import BeautifulSoup
from loguru import logger

from app.collectors.base_collector import (BaseCollector, CollectionResult,
                                           CollectorConfig, DataType,
                                           RiskLevel)

try:
    from stem import Signal
    from stem.control import Controller

    STEM_AVAILABLE = True
except ImportError:
    STEM_AVAILABLE = False
    logger.warning("stem library not available, dark web collector will be limited")


class DarkWebCollector(BaseCollector):
    """
    Dark Web OSINT Collector

    Collects OSINT data from .onion sites and dark web sources.
    """

    def __init__(self, config: CollectorConfig):
        super().__init__(config, name="DarkWebCollector")

        self.tor_session = None
        self.tor_available = STEM_AVAILABLE

    async def collect(self) -> CollectionResult:
        """
        Collect OSINT data from dark web.

        Returns:
            CollectionResult with discovered entities
        """
        result = CollectionResult(
            success=False,
            collector_name=self.name,
            correlation_id=self.correlation_id,
            risk_level=RiskLevel.HIGH,
        )

        try:
            query = self.config.target

            logger.info(f"Collecting dark web OSINT for: {query}")

            # Check if Tor is available
            if not self.tor_available:
                result.errors.append(
                    "Tor/stem not available - dark web collection disabled"
                )
                result.success = False
                return result

            # Initialize Tor session
            tor_initialized = await self._initialize_tor_session()

            if not tor_initialized:
                result.errors.append("Failed to initialize Tor session")
                result.success = False
                return result

            # Collect dark web data
            tasks = [
                self._check_dark_web_mentions(query),
            ]

            results = await asyncio.gather(*tasks, return_exceptions=True)

            # Aggregate results
            for i, task_result in enumerate(results):
                if isinstance(task_result, Exception):
                    logger.error(f"Task {i} failed: {task_result}")
                    result.errors.append(str(task_result))
                elif task_result:
                    result.data.extend(task_result)

            # Determine overall risk level
            if result.data:
                result.risk_level = RiskLevel.CRITICAL

            result.success = len(result.errors) == 0
            result.metadata = {
                "query": query,
                "tor_available": self.tor_available,
                "tasks_completed": len(
                    [r for r in results if not isinstance(r, Exception)]
                ),
            }

        except Exception as e:
            logger.exception(f"Error in dark web collection: {e}")
            result.errors.append(str(e))

        finally:
            # Close Tor session if open
            if self.tor_session:
                await self._close_tor_session()

        return result

    async def _initialize_tor_session(self) -> bool:
        """Initialize Tor connection"""
        try:
            if not STEM_AVAILABLE:
                return False

            # Check if Tor is running (default port 9050)
            import socket

            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(5)
                result = sock.connect_ex(("127.0.0.1", 9050))
                sock.close()

                if result != 0:
                    logger.error("Tor is not running on localhost:9050")
                    return False
            except Exception as e:
                logger.error(f"Failed to connect to Tor: {e}")
                return False

            # Configure session to use Tor proxy
            self.session = httpx.AsyncClient(
                proxy="socks5://127.0.0.1:9050",
                timeout=self.config.timeout,
                verify=False,
            )

            self.tor_available = True
            logger.info("Tor session initialized successfully")

            return True

        except Exception as e:
            logger.error(f"Error initializing Tor session: {e}")
            return False

    async def _close_tor_session(self):
        """Close Tor session"""
        try:
            if self.session:
                await self.session.aclose()
                self.tor_session = None
                logger.info("Tor session closed")
        except Exception as e:
            logger.error(f"Error closing Tor session: {e}")

    async def _search_darkweb(self, query: str) -> List[Dict[str, Any]]:
        """Search dark web for query"""
        entities = []

        try:
            if not self.tor_available:
                return entities

            # Note: Dark web search requires specific search engines
            # Common ones (may change frequently):
            # - ahmia.fi
            # - onionsearchengine.com
            # - notevil

            # Example using Ahmia (clearweb gateway)
            search_url = f"https://ahmia.fi/search/?q={query}"

            response = await self.session.get(search_url, timeout=30)

            if response.status_code == 200:
                soup = BeautifulSoup(response.text, "html.parser")

                # Extract onion links
                onion_links = []
                for link in soup.find_all("a", href=True):
                    href = link["href"]
                    if ".onion" in href:
                        onion_links.append(href)

                if onion_links:
                    entities.append(
                        self._create_entity(
                            entity_type="URL",
                            value=search_url,
                            risk_level=RiskLevel.HIGH,
                            metadata={
                                "type": "darkweb_search",
                                "query": query,
                                "onion_links_found": onion_links[
                                    :10
                                ],  # Limit to first 10
                            },
                        )
                    )

                    logger.warning(
                        f"Found {len(onion_links)} onion links for query: {query}"
                    )

        except Exception as e:
            logger.error(f"Error searching dark web: {e}")

        return entities

    async def _extract_onion_data(self, url: str) -> List[Dict[str, Any]]:
        """Extract data from onion site"""
        entities = []

        try:
            if not self.tor_available:
                return entities

            # Ensure URL is onion site
            if ".onion" not in url:
                logger.warning(f"Not an onion URL: {url}")
                return entities

            response = await self.session.get(url, timeout=30)

            if response.status_code == 200:
                soup = BeautifulSoup(response.text, "html.parser")

                # Extract text content
                text_content = soup.get_text(separator=" ", strip=True)

                # Extract links
                links = [a["href"] for a in soup.find_all("a", href=True)]

                entities.append(
                    self._create_entity(
                        entity_type="URL",
                        value=url,
                        risk_level=RiskLevel.HIGH,
                        metadata={
                            "type": "onion_site",
                            "title": soup.title.get_text() if soup.title else "",
                            "content_length": len(text_content),
                            "links_count": len(links),
                            "sample_text": text_content[:500] if text_content else "",
                        },
                    )
                )

                logger.info(f"Extracted data from onion site: {url}")

        except Exception as e:
            logger.error(f"Error extracting onion data from {url}: {e}")

        return entities

    async def _check_dark_web_mentions(self, query: str) -> List[Dict[str, Any]]:
        """Check for dark web mentions of username/email"""
        entities = []

        try:
            if not self.tor_available:
                return entities

            # Determine query type
            is_email = "@" in query

            # This would typically search dark web marketplaces, paste sites, forums
            # For this implementation, we'll do a basic search

            search_results = await self._search_darkweb(query)

            if search_results:
                # Create COMPROMISED_BY relationships if mentions found
                for result in search_results:
                    if result.get("metadata", {}).get("onion_links_found"):
                        entities.append(
                            {
                                "relationship_type": "COMPROMISED_BY",
                                "source": query,
                                "target": "dark_web_mention",
                                "metadata": {
                                    "query": query,
                                    "query_type": "email" if is_email else "username",
                                    "onion_links": result["metadata"][
                                        "onion_links_found"
                                    ],
                                },
                            }
                        )

                        logger.warning(f"Dark web mentions found for: {query}")

            # Also add search results
            entities.extend(search_results)

        except Exception as e:
            logger.error(f"Error checking dark web mentions: {e}")

        return entities

    def normalize(self, raw_data: Any) -> List[Dict[str, Any]]:
        """Normalize raw dark web data"""
        return raw_data if isinstance(raw_data, list) else []

    def validate(self, data: Dict[str, Any]) -> bool:
        """Validate normalized data"""
        if isinstance(data, dict) and "relationship_type" in data:
            return True
        required_fields = ["entity_type", "value"]
        return all(field in data for field in required_fields)
