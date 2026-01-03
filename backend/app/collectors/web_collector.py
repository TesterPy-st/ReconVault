"""
Web OSINT Collector for ReconVault intelligence system.

This module provides web scraping capabilities using Scrapy, Selenium, and
requests for collecting OSINT data from websites.
"""

import asyncio
import re
import json
from typing import Dict, List, Any, Optional
from urllib.parse import urlparse, urljoin
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import nmap
import OpenSSL
from OpenSSL import crypto
import socket
from .base_collector import BaseCollector, CollectorConfig
import logging


class WebCollector(BaseCollector):
    """Web OSINT collector for scraping website intelligence"""
    
    def __init__(self, config: CollectorConfig):
        super().__init__(config)
        self.logger = logging.getLogger(__name__)
        self.nm = nmap.PortScanner()
    
    async def collect(self) -> Dict[str, Any]:
        """Collect web intelligence data"""
        self.logger.info(f"Starting web collection for target: {self.config.target}")
        
        results = {
            "target": self.config.target,
            "entities": [],
            "relationships": [],
            "metadata": {}
        }
        
        try:
            # Extract domain if URL provided
            target_domain = self._extract_domain(self.config.target)
            if not target_domain:
                raise ValueError(f"Invalid target format: {self.config.target}")
            
            # Perform web collection tasks
            self.logger.info(f"Collecting web intelligence for domain: {target_domain}")
            
            # Scrape website content
            website_data = await self.scrape_website(f"https://{target_domain}")
            if website_data:
                results["entities"].extend(website_data.get("entities", []))
                results["relationships"].extend(website_data.get("relationships", []))
                results["metadata"].update(website_data.get("metadata", {}))
            
            # Extract subdomains
            subdomains = await self.extract_subdomains(target_domain)
            results["entities"].extend(subdomains)
            
            # Scan SSL certificate
            ssl_info = await self.scan_ssl_certificate(target_domain)
            if ssl_info:
                results["entities"].append(ssl_info)
            
            # Crawl site structure
            structure = await self.crawl_site_structure(target_domain)
            results["metadata"]["site_structure"] = structure
            
            # Extract emails
            emails = await self.extract_emails(target_domain)
            results["entities"].extend(emails)
            
            # Detect technologies
            tech_info = await self.detect_technologies(f"https://{target_domain}")
            results["metadata"]["technologies"] = tech_info
            
            # Check DNS records
            dns_records = await self.check_dns_records(target_domain)
            results["entities"].extend(dns_records)
            
            return results
            
        except Exception as e:
            self.logger.error(f"Web collection failed: {e}")
            raise
    
    def _extract_domain(self, target: str) -> Optional[str]:
        """Extract domain from URL or return if already domain"""
        if not target:
            return None
        
        if target.startswith(("http://", "https://")):
            parsed = urlparse(target)
            return parsed.netloc.lower()
        
        # Remove protocols that might be included
        domain = target.lower()
        if "://" in domain:
            domain = domain.split("://")[1]
        
        # Remove paths
        if "/" in domain:
            domain = domain.split("/")[0]
        
        return domain
    
    async def scrape_website(self, url: str) -> Optional[Dict[str, Any]]:
        """Scrape website to extract text, links, and metadata"""
        try:
            self.logger.debug(f"Scraping website: {url}")
            
            response = self._make_request(url, timeout=min(self.config.timeout, 30))
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            
            # Extract text
            text = soup.get_text()
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = '\n'.join(chunk for chunk in chunks if chunk)
            
            # Extract metadata
            metadata = {
                "title": soup.title.string if soup.title else "",
                "description": "",
                "keywords": "",
                "charset": soup.find("meta", charset=True)
            }
            
            # Extract description and keywords
            for meta in soup.find_all("meta"):
                if meta.get("name") == "description":
                    metadata["description"] = meta.get("content", "")
                elif meta.get("name") == "keywords":
                    metadata["keywords"] = meta.get("content", "")
            
            # Extract all links
            links = []
            for link in soup.find_all('a', href=True):
                href = link['href']
                full_url = urljoin(url, href)
                links.append({
                    "url": full_url,
                    "text": link.get_text().strip()
                })
            
            # Extract images
            images = []
            for img in soup.find_all('img', src=True):
                src = img['src']
                full_src = urljoin(url, src)
                images.append({
                    "url": full_src,
                    "alt": img.get("alt", "")
                })
            
            entities = [
                {
                    "value": url,
                    "type": "DOMAIN",
                    "metadata": {
                        "title": metadata["title"],
                        "description": metadata["description"],
                        "keywords": metadata["keywords"],
                        "content_length": len(text),
                        "language": self._detect_language(text),
                        "collected_at": datetime.utcnow().isoformat()
                    },
                    "source": "web_scraper"
                }
            ]
            
            # Create LINKS_TO relationships for each link
            relationships = []
            for link in links:
                relationships.append({
                    "type": "LINKS_TO",
                    "source_value": url,
                    "source_type": "DOMAIN",
                    "target_value": link["url"],
                    "target_type": "DOMAIN",
                    "metadata": {
                        "link_text": link["text"],
                        "strength": 0.3
                    }
                })
            
            return {
                "entities": entities,
                "relationships": relationships,
                "metadata": {
                    "text_length": len(text),
                    "link_count": len(links),
                    "image_count": len(images)
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error scraping website {url}: {e}")
            return None
    
    def _detect_language(self, text: str) -> str:
        """Detect language of text (basic implementation)"""
        if not text:
            return "unknown"
        
        # This is a basic placeholder for language detection
        # In a real implementation, you'd use a library like langdetect
        return "unknown"
    
    async def extract_subdomains(self, domain: str) -> List[Dict[str, Any]]:
        """Extract subdomains from various sources"""
        self.logger.debug(f"Extracting subdomains for: {domain}")
        
        entities = []
        discovered_subdomains = set()
        
        try:
            # Method 1: DNS enumeration
            dns_subdomains = await self._dns_based_subdomain_enum(domain)
            discovered_subdomains.update(dns_subdomains)
            
            # Method 2: Certificate Transparency logs
            ct_subdomains = await self._certificate_transparency_subdomains(domain)
            discovered_subdomains.update(ct_subdomains)
            
            # Method 3: Common subdomains list
            common_subdomains = await self._common_subdomain_brute(domain)
            discovered_subdomains.update(common_subdomains)
            
            # Method 4: Search engine queries (using site:)
            se_subdomains = await self._search_engine_subdomains(domain)
            discovered_subdomains.update(se_subdomains)
            
        except Exception as e:
            self.logger.error(f"Error extracting subdomains for {domain}: {e}")
        
        # Convert discovered subdomains to entities
        for subdomain in discovered_subdomains:
            if subdomain and subdomain.endswith(domain):
                entities.append({
                    "value": subdomain,
                    "type": "DOMAIN",
                    "metadata": {
                        "parent_domain": domain,
                        "discovered_via": "subdomain_enum",
                        "priority": "medium"
                    },
                    "source": "subdomain_enum"
                })
        
        self.logger.info(f"Found {len(entities)} subdomains for {domain}")
        return entities
    
    async def _dns_based_subdomain_enum(self, domain: str) -> set:
        """Enumerate subdomains using DNS"""
        subdomains = set()
        
        try:
            import dns.resolver
            
            # Query common records for subdomains
            record_types = ['A', 'AAAA', 'CNAME', 'MX', 'TXT']
            for record_type in record_types:
                try:
                    answers = dns.resolver.resolve(domain, record_type)
                    for rdata in answers:
                        # Extract potential subdomains from records
                        if hasattr(rdata, 'target'):
                            subdomains.add(str(rdata.target).rstrip('.'))
                except:
                    continue
                    
        except ImportError:
            self.logger.warning("dnspython not available for DNS enumeration")
        
        return subdomains
    
    async def _certificate_transparency_subdomains(self, domain: str) -> set:
        """Extract subdomains from Certificate Transparency logs"""
        subdomains = set()
        
        try:
            # Use crt.sh API
            ct_url = f"https://crt.sh/?q=%.{domain}&output=json"
            response = self._make_request(ct_url, timeout=20)
            
            if response.status_code == 200:
                data = response.json()
                for cert in data:
                    name_value = cert.get('name_value', '')
                    if name_value:
                        # Split multiple domains in certificate
                        for name in name_value.split('\\n'):
                            name = name.strip()
                            if name and name.endswith(domain) and name != domain:
                                subdomains.add(name)
                                
        except Exception as e:
            self.logger.error(f"Error fetching certificate transparency data: {e}")
        
        return subdomains
    
    async def _common_subdomain_brute(self, domain: str) -> set:
        """Brute force common subdomains"""
        subdomains = set()
        
        # Common subdomain list
        common_names = [
            'www', 'mail', 'ftp', 'localhost', 'webmail', 'smtp', 'pop', 'ns1', 'webdisk',
            'ns2', 'cpanel', 'whm', 'autodiscover', 'autoconfig', 'm', 'imap', 'test',
            'ns', 'blog', 'pop3', 'dev', 'www2', 'admin', 'forum', 'news', 'vpn', 'ns3',
            'mail2', 'new', 'mysql', 'old', 'lists', 'support', 'mobile', 'mx', 'static',
            'docs', 'beta', 'shop', 'sql', 'secure', 'demo', 'cp', 'calendar', 'wiki',
            'web', 'media', 'email', 'images', 'img', 'www1', 'intranet', 'portal', 'video',
            'sip', 'dns2', 'api', 'cdn', 'stats', 'dns1', 'www3', 'dns', 'search', 'staging',
            'server', 'mx1', 'chat', 'wap', 'my', 'svn', 'mail1', 'sites', 'proxy', 'ads',
            'host', 'crm', 'cms', 'backup', 'mx2', 'lyncdiscover', 'info', 'apps', 'download',
            'remote', 'db', 'forums', 'store', 'relay', 'files', 'newsletter', 'app', 'live',
            'owa', 'en', 'start', 'sms', 'office', 'exchange', 'ipv4', 'lync', 'sip'
        ]
        
        # Test each subdomain
        for subdomain in common_names:
            full_domain = f"{subdomain}.{domain}"
            try:
                # Quick DNS check
                socket.gethostbyname(full_domain)
                subdomains.add(full_domain)
                self.logger.debug(f"Found subdomain: {full_domain}")
            except:
                continue
        
        return subdomains
    
    async def _search_engine_subdomains(self, domain: str) -> set:
        """Find subdomains using search engines"""
        subdomains = set()
        
        try:
            # Using Bing API or simple search (placeholder)
            # This would require API keys for proper implementation
            search_query = f"site:{domain}"
            search_url = f"https://duckduckgo.com/html/?q={search_query}"
            
            response = self._make_request(search_url, timeout=15)
            if response.status_code == 200:
                # Parse results for subdomain patterns
                # This is simplified - real implementation would parse results
                self.logger.debug("Search engine subdomain extraction would require API keys")
                
        except Exception as e:
            self.logger.error(f"Error in search engine subdomain enumeration: {e}")
        
        return subdomains
    
    async def scan_ssl_certificate(self, domain: str) -> Optional[Dict[str, Any]]:
        """Scan SSL/TLS certificate for domain"""
        try:
            self.logger.debug(f"Scanning SSL certificate for: {domain}")
            
            # Connect to domain and get certificate
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(10)
            sock.connect((domain, 443))
            
            ctx = OpenSSL.SSL.Context(OpenSSL.SSL.SSLv23_METHOD)
            ctx.check_hostname = False
            ctx.verify_mode = OpenSSL.SSL.VERIFY_NONE
            
            ssl_sock = OpenSSL.SSL.Connection(ctx, sock)
            ssl_sock.set_connect_state()
            ssl_sock.set_tlsext_host_name(domain.encode())
            
            ssl_sock.sendall(b"HEAD / HTTP/1.0\r\nHost: " + domain.encode() + b"\r\n\r\n")
            ssl_sock.do_handshake()
            
            # Get certificate
            cert = ssl_sock.get_peer_certificate()
            
            # Extract certificate information
            subject = dict(cert.get_subject().get_components())
            issuer = dict(cert.get_issuer().get_components())
            
            not_before = datetime.strptime(cert.get_notBefore().decode(), '%Y%m%d%H%M%SZ')
            not_after = datetime.strptime(cert.get_notAfter().decode(), '%Y%m%d%H%M%SZ')
            
            cert_info = {
                "value": f"{domain}:{cert.get_serial_number()}",
                "type": "SSL_CERTIFICATE",
                "metadata": {
                    "domain": domain,
                    "subject": {k.decode(): v.decode() for k, v in subject.items()},
                    "issuer": {k.decode(): v.decode() for k, v in issuer.items()},
                    "serial_number": cert.get_serial_number(),
                    "version": cert.get_version(),
                    "not_before": not_before.isoformat(),
                    "not_after": not_after.isoformat(),
                    "expired": cert.has_expired(),
                    "signature_algorithm": cert.get_signature_algorithm().decode(),
                    "public_key_bits": cert.get_pubkey().bits(),
                    "san_entries": []
                },
                "source": "ssl_scanner"
            }
            
            # Extract SAN entries if available
            for i in range(cert.get_extension_count()):
                ext = cert.get_extension(i)
                if ext.get_short_name().decode() == 'subjectAltName':
                    san_data = ext.__str__()
                    san_entries = []
                    for san in san_data.split(','):
                        san = san.strip()
                        if san.startswith('DNS:'):
                            san_entries.append(san[4:])
                    cert_info["metadata"]["san_entries"] = san_entries
            
            ssl_sock.close()
            sock.close()
            
            return cert_info
            
        except Exception as e:
            self.logger.error(f"Error scanning SSL certificate for {domain}: {e}")
            return None
    
    async def crawl_site_structure(self, domain: str) -> Dict[str, Any]:
        """Crawl site structure and map hierarchy"""
        structure = {
            "domain": domain,
            "pages_scanned": [],
            "robots_txt": None,
            "sitemap_xml": None,
            "redirects": [],
            "broken_links": []
        }
        
        try:
            # Check robots.txt
            robots_url = f"https://{domain}/robots.txt"
            try:
                robots_response = self._make_request(robots_url, timeout=10)
                if robots_response.status_code == 200:
                    structure["robots_txt"] = robots_response.text
            except:
                pass
            
            # Check sitemap.xml
            sitemap_url = f"https://{domain}/sitemap.xml"
            try:
                sitemap_response = self._make_request(sitemap_url, timeout=10)
                if sitemap_response.status_code == 200:
                    structure["sitemap_xml"] = sitemap_response.text
            except:
                pass
            
            # Basic crawling of main pages
            pages_to_check = [f"https://{domain}/", f"https://{domain}/robots.txt"]
            if structure["sitemap_xml"]:
                # Parse sitemap for additional URLs
                self.logger.debug("Would parse sitemap XML for additional URLs")
            
            for page_url in pages_to_check:
                try:
                    page_response = self._make_request(page_url, timeout=10)
                    structure["pages_scanned"].append({
                        "url": page_url,
                        "status_code": page_response.status_code,
                        "headers": dict(page_response.headers),
                        "content_type": page_response.headers.get('content-type', 'unknown')
                    })
                except Exception as e:
                    structure["broken_links"].append({
                        "url": page_url,
                        "error": str(e)
                    })
            
        except Exception as e:
            self.logger.error(f"Error crawling site structure for {domain}: {e}")
        
        return structure
    
    async def extract_emails(self, domain: str) -> List[Dict[str, Any]]:
        """Extract email addresses from domain"""
        entities = []
        
        try:
            # Search for common email patterns on the website
            urls = [
                f"https://{domain}",
                f"http://{domain}",
                f"https://www.{domain}",
                f"http://www.{domain}"
            ]
            
            email_pattern = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
            found_emails = set()
            
            for url in urls:
                try:
                    response = self._make_request(url, timeout=15)
                    if response.status_code == 200:
                        emails = email_pattern.findall(response.text)
                        found_emails.update(emails)
                except:
                    continue
            
            # Convert found emails to entities
            for email in found_emails:
                if email.lower().endswith(f"@{domain}"):
                    entities.append({
                        "value": email.lower(),
                        "type": "EMAIL",
                        "metadata": {
                            "domain": domain,
                            "verified": False,
                            "found_on": domain,
                            "confidence": 0.8
                        },
                        "source": "email_extractor"
                    })
            
        except Exception as e:
            self.logger.error(f"Error extracting emails for {domain}: {e}")
        
        return entities
    
    async def detect_technologies(self, url: str) -> Dict[str, Any]:
        """Detect technologies used on website"""
        technologies = {
            "server": "unknown",
            "framework": "unknown",
            "cms": "unknown",
            "analytics": [],
            "javascript_frameworks": []
        }
        
        try:
            response = self._make_request(url, timeout=15)
            
            # Extract server information
            technologies["server"] = response.headers.get('server', 'unknown')
            
            # Detect CMS
            content = response.text.lower()
            
            if 'wp-content' in content or 'wp-includes' in content:
                technologies["cms"] = "WordPress"
            elif 'drupal' in content:
                technologies["cms"] = "Drupal"
            elif 'joomla' in content:
                technologies["cms"] = "Joomla"
            elif 'magento' in content:
                technologies["cms"] = "Magento"
            elif 'shopify' in content.lower():
                technologies["cms"] = "Shopify"
            
            # Detect JavaScript frameworks
            if 'react' in content:
                technologies["javascript_frameworks"].append("React")
            if 'angular' in content:
                technologies["javascript_frameworks"].append("Angular")
            if 'vue' in content:
                technologies["javascript_frameworks"].append("Vue")
            if 'jquery' in content:
                technologies["javascript_frameworks"].append("jQuery")
            
            # Detect analytics
            if 'google-analytics' in content or 'ga.js' in content:
                technologies["analytics"].append("Google Analytics")
            if 'googletagmanager' in content:
                technologies["analytics"].append("Google Tag Manager")
            if 'mixpanel' in content:
                technologies["analytics"].append("Mixpanel")
            
        except Exception as e:
            self.logger.error(f"Error detecting technologies for {url}: {e}")
        
        return technologies
    
    async def check_dns_records(self, domain: str) -> List[Dict[str, Any]]:
        """Check DNS records for domain"""
        entities = []
        
        try:
            import dns.resolver
            
            record_types = ['A', 'AAAA', 'MX', 'TXT', 'CNAME', 'NS', 'SOA']
            
            for record_type in record_types:
                try:
                    answers = dns.resolver.resolve(domain, record_type)
                    
                    for rdata in answers:
                        entity = {
                            "value": str(rdata),
                            "type": record_type,
                            "metadata": {
                                "domain": domain,
                                "record_type": record_type,
                                "ttl": answers.ttl if hasattr(answers, 'ttl') else None
                            },
                            "source": "dns_lookup"
                        }
                        
                        # Add specific metadata based on record type
                        if record_type == 'MX':
                            entity["metadata"]["priority"] = rdata.preference
                            entity["metadata"]["exchange"] = str(rdata.exchange)
                        
                        entities.append(entity)
                        
                except dns.resolver.NXDOMAIN:
                    self.logger.warning(f"Domain {domain} does not exist")
                except dns.resolver.NoAnswer:
                    pass  # No records for this type
                except Exception as e:
                    self.logger.debug(f"Error resolving {record_type} for {domain}: {e}")
            
        except ImportError:
            self.logger.warning("dnspython not available for DNS record checks")
        except Exception as e:
            self.logger.error(f"Error checking DNS records for {domain}: {e}")
        
        return entities
    
    def normalize(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Normalize web collection results"""
        entities = []
        
        if isinstance(data, dict):
            if "entities" in data:
                # Already normalized format
                return data["entities"]
            
            # Handle direct entity data
            target = data.get("target", self.config.target)
            if target:
                entities.append({
                    "value": target,
                    "type": "DOMAIN",
                    "metadata": data.get("metadata", {}),
                    "source": data.get("source", "web_collector")
                })
        
        return entities