"""
Domain OSINT Collector

Collects OSINT data for domains including:
- WHOIS lookup
- DNS enumeration
- Historical data (Wayback Machine)
- Reputation checking
- Nameserver information
- Mail server detection
"""

import asyncio
import re
from datetime import datetime
from typing import Any, Dict, List, Optional

import dns.resolver
import whois
from bs4 import BeautifulSoup
from loguru import logger

from app.collectors.base_collector import (BaseCollector, CollectionResult,
                                           CollectorConfig, DataType,
                                           RiskLevel)


class DomainCollector(BaseCollector):
    """
    Domain OSINT Collector

    Collects comprehensive OSINT data for domains.
    """

    def __init__(self, config: CollectorConfig):
        super().__init__(config, name="DomainCollector")

    async def collect(self) -> CollectionResult:
        """
        Collect OSINT data for the target domain.

        Returns:
            CollectionResult with discovered entities
        """
        result = CollectionResult(
            success=False, collector_name=self.name, correlation_id=self.correlation_id
        )

        try:
            domain = self.config.target

            # Remove protocol if present
            domain = domain.replace("http://", "").replace("https://", "")
            domain = domain.split("/")[0]

            logger.info(f"Collecting domain OSINT for {domain}")

            # Collect various types of data
            tasks = [
                self._whois_lookup(domain),
                self._dns_enumeration(domain),
                self._get_historical_data(domain),
                self._check_reputation(domain),
                self._get_nameservers(domain),
                self._detect_mail_servers(domain),
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
            risk_factors = [
                e.get("risk_level", RiskLevel.INFO.value) for e in result.data
            ]
            if RiskLevel.CRITICAL.value in risk_factors:
                result.risk_level = RiskLevel.CRITICAL
            elif RiskLevel.HIGH.value in risk_factors:
                result.risk_level = RiskLevel.HIGH
            elif RiskLevel.MEDIUM.value in risk_factors:
                result.risk_level = RiskLevel.MEDIUM

            result.success = len(result.errors) == 0
            result.metadata = {
                "domain": domain,
                "tasks_completed": len(
                    [r for r in results if not isinstance(r, Exception)]
                ),
            }

        except Exception as e:
            logger.exception(f"Error in domain collection: {e}")
            result.errors.append(str(e))

        return result

    async def _whois_lookup(self, domain: str) -> List[Dict[str, Any]]:
        """Perform WHOIS lookup"""
        entities = []

        try:
            # WHOIS can be slow, run in thread pool
            loop = asyncio.get_event_loop()
            whois_data = await loop.run_in_executor(None, whois.whois, domain)

            if whois_data:
                # Parse registration dates
                created_date = whois_data.creation_date
                if isinstance(created_date, list):
                    created_date = created_date[0]

                expiry_date = whois_data.expiration_date
                if isinstance(expiry_date, list):
                    expiry_date = expiry_date[0]

                # Check if expiring soon
                risk_level = RiskLevel.INFO
                if expiry_date and isinstance(expiry_date, datetime):
                    days_left = (expiry_date - datetime.utcnow()).days
                    if days_left < 7:
                        risk_level = RiskLevel.CRITICAL
                    elif days_left < 30:
                        risk_level = RiskLevel.HIGH
                    elif days_left < 90:
                        risk_level = RiskLevel.MEDIUM

                entity = self._create_entity(
                    entity_type="DOMAIN",
                    value=domain,
                    risk_level=risk_level,
                    metadata={
                        "registrar": whois_data.registrar,
                        "creation_date": str(created_date) if created_date else None,
                        "expiration_date": str(expiry_date) if expiry_date else None,
                        "updated_date": str(whois_data.updated_date)
                        if whois_data.updated_date
                        else None,
                        "registrant_name": whois_data.name,
                        "registrant_email": whois_data.emails,
                        "registrant_org": whois_data.org,
                        "registrant_country": whois_data.country,
                        "domain_status": whois_data.status,
                        "name_servers": whois_data.name_servers,
                        "dnssec": whois_data.dnssec,
                    },
                )

                entities.append(entity)

                # Create ORG entity if registrant organization exists
                if whois_data.org:
                    entities.append(
                        self._create_entity(
                            entity_type="ORG",
                            value=whois_data.org,
                            risk_level=RiskLevel.INFO,
                            metadata={
                                "source": "whois",
                                "domain": domain,
                                "registrant_name": whois_data.name,
                                "registrant_email": whois_data.emails,
                            },
                        )
                    )

                    # Create relationship
                    entities.append(
                        {
                            "relationship_type": "REGISTERED_BY",
                            "source": domain,
                            "target": whois_data.org,
                            "metadata": {"source": "whois"},
                        }
                    )

                logger.info(f"WHOIS lookup completed for {domain}")

        except Exception as e:
            logger.error(f"Error performing WHOIS lookup for {domain}: {e}")

        return entities

    async def _dns_enumeration(self, domain: str) -> List[Dict[str, Any]]:
        """Enumerate all DNS records"""
        entities = []

        try:
            resolver = dns.resolver.Resolver()
            resolver.timeout = 10
            resolver.lifetime = 10

            record_types = [
                "A",
                "AAAA",
                "MX",
                "TXT",
                "NS",
                "CNAME",
                "SOA",
                "SRV",
                "PTR",
            ]
            dns_records = {}

            for record_type in record_types:
                try:
                    answers = resolver.resolve(domain, record_type)
                    dns_records[record_type] = [str(rdata) for rdata in answers]
                    await asyncio.sleep(0.3)
                except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN, Exception) as e:
                    logger.debug(f"No {record_type} record for {domain}")
                    continue

            if dns_records:
                entities.append(
                    self._create_entity(
                        entity_type="DOMAIN",
                        value=domain,
                        risk_level=RiskLevel.INFO,
                        metadata={
                            "dns_records": dns_records,
                            "total_record_types": len(dns_records),
                        },
                    )
                )

                logger.info(
                    f"DNS enumeration completed for {domain}: {list(dns_records.keys())}"
                )

        except Exception as e:
            logger.error(f"Error enumerating DNS for {domain}: {e}")

        return entities

    async def _get_historical_data(self, domain: str) -> List[Dict[str, Any]]:
        """Get historical data from Wayback Machine"""
        entities = []

        try:
            # Check Wayback Machine CDX API
            cdx_url = "http://web.archive.org/cdx/search/cdx"
            params = {"url": domain, "output": "json", "limit": 10}

            response = await self.session.get(cdx_url, params=params, timeout=15)

            if response.status_code == 200:
                data = response.json()

                if len(data) > 1:  # First row is headers
                    snapshots = data[1:]

                    # Extract years from snapshots
                    years = set()
                    for snapshot in snapshots:
                        if len(snapshot) > 1:
                            year = snapshot[1][:4]
                            years.add(year)

                    entities.append(
                        self._create_entity(
                            entity_type="DOMAIN",
                            value=domain,
                            risk_level=RiskLevel.INFO,
                            metadata={
                                "wayback_snapshots": len(snapshots),
                                "years_with_data": sorted(list(years)),
                                "oldest_snapshot": snapshots[-1][1]
                                if snapshots
                                else None,
                                "newest_snapshot": snapshots[0][1]
                                if snapshots
                                else None,
                            },
                        )
                    )

                    logger.info(
                        f"Found {len(snapshots)} Wayback snapshots for {domain}"
                    )

        except Exception as e:
            logger.error(f"Error getting historical data for {domain}: {e}")

        return entities

    async def _check_reputation(self, domain: str) -> List[Dict[str, Any]]:
        """Check domain reputation"""
        entities = []

        try:
            # Check against known blacklists (placeholder)
            # Real implementation would check:
            # - Spamhaus
            # - Google Safe Browsing
            # - PhishTank
            # - VirusTotal

            # For now, do basic checks
            reputation_indicators = []

            # Check for suspicious TLDs
            suspicious_tlds = [".xyz", ".top", ".zip", ".mov", ".tk", ".ml"]
            if any(domain.lower().endswith(tld) for tld in suspicious_tlds):
                reputation_indicators.append("suspicious_tld")

            # Check for random-looking domains
            if len(domain.replace("-", "").replace(".", "")) > 20:
                if re.match(r"^[a-z0-9-]+$", domain.lower()):
                    reputation_indicators.append("random_pattern")

            risk_level = RiskLevel.INFO
            if reputation_indicators:
                risk_level = RiskLevel.MEDIUM

            entities.append(
                self._create_entity(
                    entity_type="DOMAIN",
                    value=domain,
                    risk_level=risk_level,
                    metadata={
                        "reputation_indicators": reputation_indicators,
                        "note": "Full reputation check requires API access to blacklist services",
                    },
                )
            )

            logger.info(f"Reputation check completed for {domain}")

        except Exception as e:
            logger.error(f"Error checking reputation for {domain}: {e}")

        return entities

    async def _get_nameservers(self, domain: str) -> List[Dict[str, Any]]:
        """Get nameserver information"""
        entities = []

        try:
            resolver = dns.resolver.Resolver()
            resolver.timeout = 10
            resolver.lifetime = 10

            answers = resolver.resolve(domain, "NS")
            nameservers = [str(rdata).rstrip(".") for rdata in answers]

            for ns in nameservers:
                entities.append(
                    self._create_entity(
                        entity_type="ORG",
                        value=ns,
                        risk_level=RiskLevel.INFO,
                        metadata={"type": "nameserver", "serves_domain": domain},
                    )
                )

                # Create relationship
                entities.append(
                    {
                        "relationship_type": "RELATED_TO",
                        "source": domain,
                        "target": ns,
                        "metadata": {"relationship": "dns_hosting"},
                    }
                )

            logger.info(f"Found {len(nameservers)} nameservers for {domain}")

        except Exception as e:
            logger.error(f"Error getting nameservers for {domain}: {e}")

        return entities

    async def _detect_mail_servers(self, domain: str) -> List[Dict[str, Any]]:
        """Detect mail servers from MX records"""
        entities = []

        try:
            resolver = dns.resolver.Resolver()
            resolver.timeout = 10
            resolver.lifetime = 10

            answers = resolver.resolve(domain, "MX")

            mail_servers = []
            for rdata in answers:
                priority = rdata.preference
                server = str(rdata.exchange).rstrip(".")
                mail_servers.append({"priority": priority, "server": server})

            for ms in mail_servers:
                entities.append(
                    self._create_entity(
                        entity_type="ORG",
                        value=ms["server"],
                        risk_level=RiskLevel.INFO,
                        metadata={
                            "type": "mail_server",
                            "mx_priority": ms["priority"],
                            "serves_domain": domain,
                        },
                    )
                )

                # Create relationship
                entities.append(
                    {
                        "relationship_type": "RELATED_TO",
                        "source": domain,
                        "target": ms["server"],
                        "metadata": {"relationship": "mail_exchange"},
                    }
                )

            logger.info(f"Found {len(mail_servers)} mail servers for {domain}")

        except Exception as e:
            logger.error(f"Error detecting mail servers for {domain}: {e}")

        return entities

    def normalize(self, raw_data: Any) -> List[Dict[str, Any]]:
        """Normalize raw domain data"""
        return raw_data if isinstance(raw_data, list) else []

    def validate(self, data: Dict[str, Any]) -> bool:
        """Validate normalized data"""
        if isinstance(data, dict) and "relationship_type" in data:
            return True
        required_fields = ["entity_type", "value"]
        return all(field in data for field in required_fields)
