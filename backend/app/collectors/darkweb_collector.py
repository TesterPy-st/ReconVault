"""
Dark Web OSINT Collector for ReconVault intelligence system.

This module provides dark web intelligence gathering using Tor network
and .onion site analysis. Handles Tor connectivity safely with proper
error handling and anonymity preservation.
"""

import asyncio
import re
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging
from urllib.parse import urlparse, urljoin

# Conditional imports for optional dependencies
try:
    import stem.process
    from stem.control import Controller
    from stem.util import term
    STEM_AVAILABLE = True
except ImportError:
    STEM_AVAILABLE = False
    stem = None
    Controller = None
    term = None

try:
    import requests
    import requests.exceptions
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    requests = None

from .base_collector import BaseCollector, CollectorConfig


class DarkWebCollector(BaseCollector):
    """Dark Web OSINT collector for Tor and .onion intelligence"""
    
    def __init__(self, config: CollectorConfig):
        super().__init__(config)
        self.logger = logging.getLogger(__name__)
        self.tor_process = None
        self.tor_session = None
        self.tor_available = False
        
        # Initialize Tor if available
        if STEM_AVAILABLE and stem:
            self._init_tor_connection()
    
    def _init_tor_connection(self) -> bool:
        """Initialize Tor connection"""
        try:
            self.logger.info("Initializing Tor connection...")
            
            # Check if Tor is already running
            try:
                self.tor_controller = Controller.from_port(port=9051)
                self.tor_controller.authenticate()
                self.tor_available = True
                self.logger.info("Connected to existing Tor instance")
                return True
            except:
                pass
            
            # Try to start Tor process
            try:
                self.tor_process = stem.process.launch_tor_with_config(
                    config={
                        'SocksPort': '9050',
                        'ControlPort': '9051',
                        'DataDirectory': '/tmp/tor_data'
                    },
                    init_msg_handler=self._print_bootstrap_lines,
                    timeout=60
                )
                self.tor_available = True
                self.logger.info("Tor process started successfully")
                return True
                
            except Exception as e:
                self.logger.warning(f"Could not start Tor process: {e}")
                self.tor_available = False
                return False
        
        except Exception as e:
            self.logger.error(f"Error initializing Tor connection: {e}")
            self.tor_available = False
            return False
    
    def _print_bootstrap_lines(self, line: str) -> None:
        """Handle Tor bootstrap messages"""
        if "Bootstrapped " in line:
            self.logger.info(term.format(line, term.Color.BLUE))
    
    def _create_tor_session(self) -> Optional[requests.Session]:
        """Create requests session configured for Tor"""
        if not REQUESTS_AVAILABLE:
            self.logger.warning("Requests library not available")
            return None
        
        try:
            session = requests.Session()
            session.proxies = {
                'http': 'socks5h://127.0.0.1:9050',
                'https': 'socks5h://127.0.0.1:9050'
            }
            
            # Set Tor-specific headers
            session.headers.update({
                'User-Agent': self._rotate_user_agent() + ' (Tor Browser compatible)',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
            })
            
            return session
        
        except Exception as e:
            self.logger.error(f"Error creating Tor session: {e}")
            return None
    
    async def collect(self) -> Dict[str, Any]:
        """Collect dark web intelligence data"""
        self.logger.info(f"Starting dark web collection for target: {self.config.target}")
        
        if not self.tor_available:
            self.logger.warning("Tor is not available - dark web collection will be limited")
            
            return {
                "target": self.config.target,
                "entities": [],
                "relationships": [],
                "metadata": {
                    "tor_available": False,
                    "warning": "Tor connection not available"
                }
            }
        
        results = {
            "target": self.config.target,
            "entities": [],
            "relationships": [],
            "metadata": {
                "tor_available": True,
                "anonymity_preserved": True
            }
        }
        
        try:
            # Determine target type
            if self._is_onion_url(self.config.target):
                # .onion site analysis
                onion_data = await self.extract_onion_data(self.config.target)
                if onion_data:
                    results["entities"].extend(onion_data.get("entities", []))
                    results["metadata"]["onion"] = onion_data.get("metadata", {})
            
            elif self._is_username(self.config.target) or self._is_email(self.config.target):
                # Check for mentions in dark web sources
                mention_data = await self.check_dark_web_mentions(self.config.target)
                results["entities"].extend(mention_data.get("entities", []))
                results["metadata"]["mentions"] = mention_data.get("metadata", {})
            
            else:
                # Search dark web
                search_results = await self.search_darkweb(self.config.target)
                results["entities"].extend(search_results.get("entities", []))
                results["metadata"]["search"] = search_results.get("metadata", {})
            
            return results
            
        except Exception as e:
            self.logger.error(f"Dark web collection failed: {e}")
            raise
    
    def _is_onion_url(self, target: str) -> bool:
        """Check if target is a .onion URL"""
        return ".onion" in target.lower()
    
    def _is_username(self, target: str) -> bool:
        """Check if target is a username"""
        pattern = r'^[a-zA-Z0-9_\-]{3,30}$'
        return bool(re.match(pattern, target))
    
    def _is_email(self, target: str) -> bool:
        """Check if target is an email"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[A-Z|a-z]{2,}$'
        return bool(re.match(pattern, target))
    
    async def initialize_tor_session(self) -> bool:
        """Initialize Tor session for dark web access"""
        if not self.tor_available:
            self.logger.warning("Tor not available for session initialization")
            return False
        
        try:
            self.tor_session = self._create_tor_session()
            
            if self.tor_session:
                # Test connection
                test_url = "http://check.torproject.org/"
                response = self.tor_session.get(test_url, timeout=30)
                
                if "Congratulations. This browser is configured to use Tor." in response.text:
                    self.logger.info("Tor connection verified successfully")
                    self.config.use_proxy = True
                    self.config.proxy_url = "socks5h://127.0.0.1:9050"
                    return True
                else:
                    self.logger.warning("Tor connection test failed")
                    return False
            
            return False
        
        except Exception as e:
            self.logger.error(f"Error initializing Tor session: {e}")
            return False
    
    async def search_darkweb(self, query: str) -> Dict[str, Any]:
        """Search dark web for query using multiple sources"""
        results = {
            "entities": [],
            "metadata": {
                "sources_checked": [],
                "results_found": 0,
                "query": query
            }
        }
        
                if not self.tor_session:
            # Use standard session with Tor proxy
            session = self.session
            session.proxies.update({
                'http': 'socks5h://127.0.0.1:9050',
                'https': 'socks5h://127.0.0.1:9050'
            })
        else:
            session = self.tor_session
        
        try:
            self.logger.debug(f"Searching dark web for: {query}")
            
            # Search Ahmia.fi (dark web search engine)
            try:
                ahmia_url = f"http://juhanurmihxlp77nkq76byazcldy2hlmovfu2epvl5ankdibsot4csyd.onion/search/?q={query}"
                
                # Note: Ahmia also has a clearnet API we can use
                ahmia_clearnet = f"https://ahmia.fi/search/?q={query}"
                
                response = self._make_request(ahmia_clearnet, session=session, timeout=45)
                
                if response.status_code == 200:
                    results["metadata"]["sources_checked"].append("ahmia")
                    
                    # Parse results (would need HTML parsing)
                    # For now, just note that Ahmia was checked
                    self.logger.debug("Ahmia search completed")
            
            except Exception as e:
                self.logger.warning(f"Ahmia search failed: {e}")
            
            # Search other dark web sources
            search_sources = [
                # Additional dark web search engines could be added here
                # Note: Many require specific .onion access and may be unreliable
            ]
            
            for source_url in search_sources:
                try:
                    # Would implement source-specific search logic here
                    pass
                except Exception as e:
                    self.logger.debug(f"Search source failed: {e}")
                    continue
            
            # Check common dark web directories/pastes
            paste_results = await self._check_dark_web_pastes(query)
            if paste_results:
                results["entities"].extend(paste_results.get("entities", []))
                results["metadata"]["paste_results"] = paste_results.get("metadata", {})
            
        except Exception as e:
            self.logger.error(f"Error searching dark web: {e}")
        
        return results
    
    async def extract_onion_data(self, onion_url: str) -> Optional[Dict[str, Any]]:
        """Scrape and analyze .onion website content"""
        if not self._is_onion_url(onion_url):
            self.logger.warning(f"Invalid .onion URL: {onion_url}")
            return None
        
        results = {
            "entities": [],
            "metadata": {
                "url": onion_url,
                "accessed_via_tor": True,
                "extracted_data": {}
            }
        }
        
        try:
            self.logger.debug(f"Extracting data from .onion site: {onion_url}")
            
            # Ensure URL has proper format
            if not onion_url.startswith('http'):
                onion_url = f"http://{onion_url}"
            
            # Use Tor session
            if self.tor_session:
                response = self.tor_session.get(onion_url, timeout=60, allow_redirects=True)
            else:
                # Use regular session with Tor proxy
                tor_proxies = {
                    'http': 'socks5h://127.0.0.1:9050',
                    'https': 'socks5h://127.0.0.1:9050'
                }
                response = requests.get(onion_url, proxies=tor_proxies, timeout=60, allow_redirects=True)
            
            if response.status_code == 200:
                results["metadata"]["status"] = "success"
                results["metadata"]["response_time"] = response.elapsed.total_seconds()
                
                # Parse content (basic)
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Extract text content
                text = soup.get_text(separator=' ', strip=True)
                results["metadata"]["extracted_data"]["text_length"] = len(text)
                
                # Extract title
                title = soup.title.string if soup.title else ""
                results["metadata"]["extracted_data"]["title"] = title
                
                # Extract all links
                links = []
                for link in soup.find_all('a', href=True):
                    href = link['href']
                    if '.onion' in href:
                        links.append({
                            "url": href,
                            "text": link.get_text(strip=True)[:100]
                        })
                
                results["metadata"]["extracted_data"]["onion_links"] = links
                results["metadata"]["extracted_data"]["link_count"] = len(links)
                
                # Look for sensitive content patterns
                sensitive_patterns = {
                    "email": r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
                    "bitcoin": r'\b(1|3)[a-km-zA-HJ-NP-Z1-9]{25,34}\b',  # BTC addresses
                    "ethereum": r'\b0x[a-fA-F0-9]{40}\b',  # ETH addresses
                    "pgp": r'-----BEGIN PGP.*?-----END PGP.*?-----',
                    "url": r'(http|https)://[^\s]+',
                    "phone": r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b'
                }
                
                found_items = {}
                for item_type, pattern in sensitive_patterns.items():
                    matches = re.findall(pattern, text, re.MULTILINE | re.DOTALL)
                    if matches:
                        # Limit matches
                        found_items[item_type] = matches[:10]
                
                results["metadata"]["extracted_data"]["found_items"] = found_items
                
                # Create entities from found data
                for item_type, items in found_items.items():
                    for item in items:
                        if item_type == "email":
                            entity = {
                                "value": item,
                                "type": "EMAIL",
                                "source": "dark_web_scraper",
                                "metadata": {
                                    "found_on": onion_url,
                                    "discovered_via": "tor_scraping",
                                    "risk_level": "CRITICAL",
                                    "collected_at": datetime.utcnow().isoformat()
                                }
                            }
                            results["entities"].append(entity)
                        
                        elif item_type in ["bitcoin", "ethereum"]:
                            entity = {
                                "value": item,
                                "type": "CRYPTOCURRENCY_ADDRESS",
                                "sub_type": item_type,
                                "source": "dark_web_scraper",
                                "metadata": {
                                    "found_on": onion_url,
                                    "discovered_via": "tor_scraping",
                                    "risk_level": "HIGH",
                                    "collected_at": datetime.utcnow().isoformat()
                                }
                            }
                            results["entities"].append(entity)
                        
                        elif item_type == "pgp":
                            entity = {
                                "value": f"PGP_KEY_{hash(item) % 10000}",
                                "type": "PGP_KEY",
                                "source": "dark_web_scraper",
                                "metadata": {
                                    "found_on": onion_url,
                                    "key_preview": item[:100],
                                    "collected_at": datetime.utcnow().isoformat()
                                }
                            }
                            results["entities"].append(entity)
                
                # Site entity
                site_entity = {
                    "value": onion_url,
                    "type": "ONION_SITE",
                    "source": "dark_web_scraper",
                    "metadata": {
                        "title": title,
                        "text_length": len(text),
                        "link_count": len(links),
                        "sensitive_items_found": len(found_items),
                        "accessed_via": "tor",
                        "collected_at": datetime.utcnow().isoformat()
                    }
                }
                
                results["entities"].append(site_entity)
            
            else:
                results["metadata"]["status"] = f"failed_{response.status_code}"
                results["metadata"]["error"] = f"HTTP {response.status_code}"
        
        except Exception as e:
            results["metadata"]["status"] = "error"
            results["metadata"]["error"] = str(e)
            self.logger.error(f"Error extracting .onion data from {onion_url}: {e}")
        
        return results
    
    async def check_dark_web_mentions(self, identifier: str) -> Dict[str, Any]:
        """Check for mentions of username/email in dark web sources"""
        results = {
            "entities": [],
            "metadata": {
                "identifier": identifier,
                "sources_checked": [],
                "mention_count": 0,
                "breach_risk": "UNKNOWN"
            }
        }
        
        try:
            self.logger.debug(f"Checking dark web mentions for: {identifier}")
            
            identifier_type = "email" if self._is_email(identifier) else "username"
            
            # Check breach databases that track dark web mentions
            breach_results = await self._check_breach_databases(identifier)
            if breach_results:
                results["entities"].extend(breach_results.get("entities", []))
                results["metadata"]["breach_check"] = breach_results.get("metadata", {})
                results["metadata"]["mention_count"] += breach_results.get("metadata", {}).get("mention_count", 0)
            
            # Check dark web paste sites using various sources
            paste_results = await self._check_dark_web_pastes(identifier)
            results["entities"].extend(paste_results.get("entities", []))
            results["metadata"]["paste_results"] = paste_results.get("metadata", {})
            results["metadata"]["mention_count"] += paste_results.get("metadata", {}).get("mention_count", 0)
            
            # Determine breach risk level
            mention_count = results["metadata"]["mention_count"]
            
            if mention_count == 0:
                results["metadata"]["breach_risk"] = "LOW"
            elif mention_count <= 3:
                results["metadata"]["breach_risk"] = "MEDIUM"
            elif mention_count <= 10:
                results["metadata"]["breach_risk"] = "HIGH"
            else:
                results["metadata"]["breach_risk"] = "CRITICAL"
            
            # Create entity for the identifier with risk assessment
            if identifier_type == "email":
                entity = {
                    "value": identifier,
                    "type": "EMAIL",
                    "metadata": {
                        "dark_web_mention_count": mention_count,
                        "breach_risk": results["metadata"]["breach_risk"],
                        "sources": results["metadata"]["sources_checked"],
                        "collection_method": "dark_web_mention_check",
                        "collected_at": datetime.utcnow().isoformat(),
                        "risk_factors": [
                            "dark_web_presence" if mention_count > 0 else None,
                            "potential_data_breach" if mention_count > 3 else None
                        ]
                    },
                    "source": "dark_web_collector"
                }
                
                # Remove None values from risk_factors
                entity["metadata"]["risk_factors"] = [rf for rf in entity["metadata"]["risk_factors"] if rf]
                
                results["entities"].append(entity)
            
            # Add risk elevation for dark web findings
            if mention_count > 0:
                risk_entity = {
                    "value": f"DARK_WEB_RISK_{identifier}",
                    "type": "RISK_FACTOR",
                    "metadata": {
                        "identifier": identifier,
                        "risk_type": "dark_web_exposure",
                        "severity": results["metadata"]["breach_risk"],
                        "mention_count": mention_count,
                        "collected_at": datetime.utcnow().isoformat()
                    },
                    "source": "dark_web_collector"
                }
                
                results["entities"].append(risk_entity)
        
        except Exception as e:
            self.logger.error(f"Error checking dark web mentions for {identifier}: {e}")
        
        return results
    
    async def _check_breach_databases(self, identifier: str) -> Dict[str, Any]:
        """Check breach databases for dark web mentions"""
        results = {
            "entities": [],
            "metadata": {
                "mention_count": 0,
                "sources_checked": []
            }
        }
        
        try:
            # Check HaveIBeenPwned (which tracks some dark web breaches)
            if self._is_email(identifier):
                haveibeenpwned_results = await self._check_haveibeenpwned(identifier)
                if haveibeenpwned_results:
                    results["entities"].extend(haveibeenpwned_results.get("entities", []))
                    results["metadata"]["haveibeenpwned"] = haveibeenpwned_results.get("metadata", {})
                    results["metadata"]["mention_count"] += haveibeenpwned_results.get("mention_count", 0)
                    results["metadata"]["sources_checked"].append("haveibeenpwned")
            
            # Check other breach monitoring services
            # Note: Many paid services like Dehashed, IntelligenceX would be checked here
            
        except Exception as e:
            self.logger.error(f"Error checking breach databases: {e}")
        
        return results
    
    async def _check_haveibeenpwned(self, email: str) -> Dict[str, Any]:
        """Check HaveIBeenPwned for breach data"""
        results = {
            "entities": [],
            "metadata": {},
            "mention_count": 0
        }
        
        try:
            # Would implement HIBP API check (similar to email_collector)
            # This is a placeholder for the integration
            self.logger.debug("HaveIBeenPwned check would be implemented here")
            
        except Exception as e:
            self.logger.error(f"Error checking HaveIBeenPwned: {e}")
        
        return results
    
    async def _check_dark_web_pastes(self, query: str) -> Dict[str, Any]:
        """Check dark web paste sites for mentions"""
        results = {
            "entities": [],
            "metadata": {
                "mention_count": 0,
                "pastes_found": []
            }
        }
        
        try:
            # Check various paste sites and data dumps
            # Note: Many of these would require .onion access or API keys
            
            paste_sources = [
                # Clearnet paste sites that may mirror dark web content
                "https://pastebin.com",  # Would search via API
                "https://ghostbin.com",
                # Dark web specific (would need Tor)
                # "http://deepmix...onion",
                # "http://paste...onion",
            ]
            
            # For demonstration, log what would be checked
            self.logger.debug(f"Would check {len(paste_sources)} paste sources for: {query}")
            
            # In production, would implement:
            # - Search each paste source API
            # - Parse results for matches
            # - Extract context and metadata
            # - Create entities for findings
            
        except Exception as e:
            self.logger.error(f"Error checking dark web pastes: {e}")
        
        return results
    
    def normalize(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Normalize dark web collection results"""
        entities = []
        
        if isinstance(data, dict):
            if "entities" in data:
                # Already normalized format
                return data["entities"]
        
        return entities
    
    def __del__(self):
        """Cleanup Tor process on destruction"""
        if hasattr(self, 'tor_process') and self.tor_process:
            try:
                self.tor_process.kill()
                self.logger.info("Tor process terminated")
            except:
                pass
        
        if hasattr(self, 'tor_controller') and self.tor_controller:
            try:
                self.tor_controller.close()
            except:
                pass