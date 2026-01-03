"""
Web OSINT Collector

Collects OSINT data from websites including:
- Website content scraping
- Subdomain discovery
- SSL certificate information
- Site structure mapping
- Email extraction
- Technology detection
- DNS records
"""

import asyncio
import re
import socket
import ssl
import subprocess
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional
from urllib.parse import urljoin, urlparse

import aiofiles
from bs4 import BeautifulSoup
from loguru import logger

from app.collectors.base_collector import (BaseCollector, CollectionResult,
                                           CollectorConfig, DataType,
                                           RiskLevel)


class WebCollector(BaseCollector):
    """
    Web OSINT Collector

    Collects comprehensive OSINT data from websites.
    """

    def __init__(self, config: CollectorConfig):
        super().__init__(config, name="WebCollector")

        # Common subdomains to check
        self.common_subdomains = [
            "www",
            "mail",
            "ftp",
            "admin",
            "api",
            "dev",
            "staging",
            "test",
            "app",
            "blog",
            "shop",
            "store",
            "cdn",
            "static",
            "m",
            "mobile",
            "secure",
            "portal",
            "vpn",
            "remote",
        ]

        # Technology signatures
        self.tech_signatures = {
            "WordPress": ["wp-content", "wp-includes", "xmlrpc.php"],
            "Drupal": ["sites/default/files", "misc/drupal.js"],
            "Joomla": ["/administrator/", "components/com_"],
            "React": ["react-dom", "__reactInternalInstance"],
            "Vue": ["vue.js", "__vue__"],
            "Angular": ["ng-app", "angular.min.js"],
            "Laravel": ["laravel_session", "/storage/"],
            "Django": ["csrftoken", "/static/"],
            "Flask": ["Flask", "/static/"],
            "Next.js": ["__next", "_next/static"],
            "Nginx": ["Server: nginx"],
            "Apache": ["Server: Apache"],
            "Cloudflare": ["cf-ray", "cloudflare"],
        }

    async def collect(self) -> CollectionResult:
        """
        Collect OSINT data from the target website.

        Returns:
            CollectionResult with discovered entities
        """
        result = CollectionResult(
            success=False, collector_name=self.name, correlation_id=self.correlation_id
        )

        try:
            target = self.config.target

            # Determine if target is URL or domain
            if not target.startswith(("http://", "https://")):
                target = f"https://{target}"

            parsed_url = urlparse(target)
            domain = parsed_url.netloc

            logger.info(f"Collecting web OSINT for {domain}")

            # Check robots.txt first
            robots_allowed = await self._check_robots_txt(target, "/")
            if not robots_allowed:
                result.errors.append("robots.txt disallows crawling")
                result.success = False
                return result

            # Collect various types of data
            tasks = [
                self._scrape_website(target),
                self._extract_subdomains(domain),
                self._scan_ssl_certificate(domain),
                self._crawl_site_structure(target),
                self._extract_emails(target),
                self._detect_technologies(target),
                self._check_dns_records(domain),
            ]

            results = await asyncio.gather(*tasks, return_exceptions=True)

            # Aggregate results
            for i, task_result in enumerate(results):
                if isinstance(task_result, Exception):
                    logger.error(f"Task {i} failed: {task_result}")
                    result.errors.append(str(task_result))
                elif task_result:
                    result.data.extend(task_result)

            result.success = len(result.errors) == 0
            result.metadata = {
                "domain": domain,
                "tasks_completed": len(
                    [r for r in results if not isinstance(r, Exception)]
                ),
            }

        except Exception as e:
            logger.exception(f"Error in web collection: {e}")
            result.errors.append(str(e))

        return result

    async def _scrape_website(self, url: str) -> List[Dict[str, Any]]:
        """Scrape website for content, links, and metadata"""
        entities = []

        try:
            response = await self.session.get(url)
            response.raise_for_status()

            html = response.text
            soup = BeautifulSoup(html, "html.parser")

            # Extract page title
            title = soup.find("title")
            title_text = title.get_text().strip() if title else ""

            # Extract meta description
            meta_desc = soup.find("meta", attrs={"name": "description"})
            description = meta_desc.get("content", "") if meta_desc else ""

            # Extract all links
            links = []
            for link in soup.find_all("a", href=True):
                href = urljoin(url, link["href"])
                links.append(href)

            # Extract headers
            headers = {}
            for h in soup.find_all(["h1", "h2", "h3"]):
                headers[h.name] = headers.get(h.name, 0) + 1

            # Create DOMAIN entity with metadata
            parsed_url = urlparse(url)
            domain = parsed_url.netloc

            entities.append(
                self._create_entity(
                    entity_type="DOMAIN",
                    value=domain,
                    risk_level=RiskLevel.INFO,
                    metadata={
                        "title": title_text,
                        "description": description,
                        "url": url,
                        "links_count": len(links),
                        "headers": headers,
                        "status_code": response.status_code,
                        "content_length": len(html),
                    },
                )
            )

            logger.info(f"Scraped {url}: {len(links)} links found")

        except Exception as e:
            logger.error(f"Error scraping website {url}: {e}")

        return entities

    async def _extract_subdomains(self, domain: str) -> List[Dict[str, Any]]:
        """Extract subdomains using DNS queries"""
        entities = []

        try:
            import dns.resolver

            discovered_subdomains = []

            # Check common subdomains
            for subdomain in self.common_subdomains:
                try:
                    full_domain = f"{subdomain}.{domain}"

                    resolver = dns.resolver.Resolver()
                    resolver.timeout = 5
                    resolver.lifetime = 5

                    # Try A record
                    resolver.resolve(full_domain, "A")
                    discovered_subdomains.append(full_domain)

                    await asyncio.sleep(0.5)  # Rate limiting

                except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer, Exception):
                    continue

            # Create entities for discovered subdomains
            for subdomain in discovered_subdomains:
                entities.append(
                    self._create_entity(
                        entity_type="DOMAIN",
                        value=subdomain,
                        risk_level=RiskLevel.INFO,
                        metadata={
                            "parent_domain": domain,
                            "discovery_method": "dns_brute_force",
                        },
                    )
                )

            logger.info(
                f"Discovered {len(discovered_subdomains)} subdomains for {domain}"
            )

        except ImportError:
            logger.warning("dnspython not installed, skipping subdomain enumeration")
        except Exception as e:
            logger.error(f"Error extracting subdomains: {e}")

        return entities

    async def _scan_ssl_certificate(self, domain: str) -> List[Dict[str, Any]]:
        """Scan SSL/TLS certificate information"""
        entities = []

        try:
            context = ssl.create_default_context()

            with socket.create_connection((domain, 443), timeout=10) as sock:
                with context.wrap_socket(sock, server_hostname=domain) as ssock:
                    cert = ssock.getpeercert()

                    # Extract certificate info
                    subject = dict(x[0] for x in cert["subject"])
                    issuer = dict(x[0] for x in cert["issuer"])

                    not_before = datetime.strptime(
                        cert["notBefore"], "%b %d %H:%M:%S %Y %Z"
                    )
                    not_after = datetime.strptime(
                        cert["notAfter"], "%b %d %H:%M:%S %Y %Z"
                    )
                    days_left = (not_after - datetime.utcnow()).days

                    # Check if expiring soon
                    risk_level = RiskLevel.INFO
                    if days_left < 7:
                        risk_level = RiskLevel.CRITICAL
                    elif days_left < 30:
                        risk_level = RiskLevel.HIGH
                    elif days_left < 90:
                        risk_level = RiskLevel.MEDIUM

                    entities.append(
                        self._create_entity(
                            entity_type="DOMAIN",
                            value=domain,
                            risk_level=risk_level,
                            metadata={
                                "subject": subject.get("commonName", ""),
                                "issuer": issuer.get("organizationName", ""),
                                "not_before": cert["notBefore"],
                                "not_after": cert["notAfter"],
                                "days_until_expiry": days_left,
                                "version": cert["version"],
                                "serial_number": cert["serialNumber"],
                                "signature_algorithm": cert["signatureAlgorithm"],
                            },
                        )
                    )

                    logger.info(f"SSL cert for {domain}: expires in {days_left} days")

        except Exception as e:
            logger.error(f"Error scanning SSL certificate for {domain}: {e}")

        return entities

    async def _crawl_site_structure(self, url: str) -> List[Dict[str, Any]]:
        """Crawl website structure, robots.txt, sitemap"""
        entities = []

        try:
            parsed_url = urlparse(url)
            base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"

            # Check robots.txt
            robots_url = urljoin(base_url, "/robots.txt")
            try:
                response = await self.session.get(robots_url, timeout=5)
                if response.status_code == 200:
                    entities.append(
                        self._create_entity(
                            entity_type="URL",
                            value=robots_url,
                            risk_level=RiskLevel.INFO,
                            metadata={
                                "type": "robots_txt",
                                "content": response.text[:500],  # First 500 chars
                            },
                        )
                    )
            except Exception:
                pass

            # Check sitemap.xml
            sitemap_url = urljoin(base_url, "/sitemap.xml")
            try:
                response = await self.session.get(sitemap_url, timeout=5)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, "xml")
                    urls = [loc.text for loc in soup.find_all("loc")]

                    entities.append(
                        self._create_entity(
                            entity_type="URL",
                            value=sitemap_url,
                            risk_level=RiskLevel.INFO,
                            metadata={
                                "type": "sitemap",
                                "urls_count": len(urls),
                                "sample_urls": urls[:5],
                            },
                        )
                    )

                    logger.info(f"Found sitemap with {len(urls)} URLs")
            except Exception:
                pass

        except Exception as e:
            logger.error(f"Error crawling site structure: {e}")

        return entities

    async def _extract_emails(self, url: str) -> List[Dict[str, Any]]:
        """Extract email addresses from pages"""
        entities = []

        try:
            response = await self.session.get(url)
            response.raise_for_status()

            html = response.text
            soup = BeautifulSoup(html, "html.parser")

            # Email regex pattern
            email_pattern = re.compile(
                r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
            )

            # Extract from text
            emails = set(email_pattern.findall(soup.get_text()))

            # Extract from mailto links
            for link in soup.find_all("a", href=re.compile(r"^mailto:")):
                mailto = link["href"]
                email = mailto.replace("mailto:", "").split("?")[0]
                emails.add(email)

            # Create EMAIL entities
            for email in emails:
                entities.append(
                    self._create_entity(
                        entity_type="EMAIL",
                        value=email,
                        risk_level=RiskLevel.INFO,
                        metadata={"source_url": url, "extraction_method": "scraping"},
                    )
                )

            logger.info(f"Extracted {len(emails)} emails from {url}")

        except Exception as e:
            logger.error(f"Error extracting emails: {e}")

        return entities

    async def _detect_technologies(self, url: str) -> List[Dict[str, Any]]:
        """Detect CMS, frameworks, and server technologies"""
        entities = []

        try:
            response = await self.session.get(url)
            headers = dict(response.headers)
            html = response.text

            detected_techs = []

            # Check server headers
            server = headers.get("Server", "").lower()
            for tech, signatures in self.tech_signatures.items():
                for sig in signatures:
                    if sig.lower() in server:
                        detected_techs.append(tech)
                        break

            # Check HTML content
            soup = BeautifulSoup(html, "html.parser")
            page_text = soup.get_text().lower() + " " + html.lower()

            for tech, signatures in self.tech_signatures.items():
                if tech in detected_techs:
                    continue
                for sig in signatures:
                    if sig.lower() in page_text:
                        detected_techs.append(tech)
                        break

            # Get domain from URL
            parsed_url = urlparse(url)
            domain = parsed_url.netloc

            if detected_techs:
                entities.append(
                    self._create_entity(
                        entity_type="DOMAIN",
                        value=domain,
                        risk_level=RiskLevel.INFO,
                        metadata={
                            "technologies": detected_techs,
                            "server": headers.get("Server", ""),
                            "x_powered_by": headers.get("X-Powered-By", ""),
                        },
                    )
                )

                logger.info(f"Detected technologies for {domain}: {detected_techs}")

        except Exception as e:
            logger.error(f"Error detecting technologies: {e}")

        return entities

    async def _check_dns_records(self, domain: str) -> List[Dict[str, Any]]:
        """Check various DNS records"""
        entities = []

        try:
            import dns.resolver

            resolver = dns.resolver.Resolver()
            resolver.timeout = 5
            resolver.lifetime = 5

            record_types = ["A", "AAAA", "MX", "TXT", "NS", "CNAME", "SOA"]
            dns_records = {}

            for record_type in record_types:
                try:
                    answers = resolver.resolve(domain, record_type)
                    dns_records[record_type] = [str(rdata) for rdata in answers]
                    await asyncio.sleep(0.3)
                except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN, Exception):
                    continue

            if dns_records:
                entities.append(
                    self._create_entity(
                        entity_type="DOMAIN",
                        value=domain,
                        risk_level=RiskLevel.INFO,
                        metadata={"dns_records": dns_records},
                    )
                )

                logger.info(
                    f"Found DNS records for {domain}: {list(dns_records.keys())}"
                )

        except ImportError:
            logger.warning("dnspython not installed, skipping DNS records")
        except Exception as e:
            logger.error(f"Error checking DNS records: {e}")

        return entities

    def normalize(self, raw_data: Any) -> List[Dict[str, Any]]:
        """Normalize raw web data"""
        # This is handled in collect() method
        return raw_data if isinstance(raw_data, list) else []

    def validate(self, data: Dict[str, Any]) -> bool:
        """Validate normalized data"""
        required_fields = ["entity_type", "value"]
        return all(field in data for field in required_fields)
