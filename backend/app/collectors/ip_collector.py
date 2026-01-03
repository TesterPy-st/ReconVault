"""
IP OSINT Collector

Collects OSINT data for IP addresses including:
- Geolocation
- Port scanning
- Reverse DNS
- Reputation checking
- WHOIS data
- VPN/proxy detection
"""

import asyncio
import socket
from datetime import datetime
from typing import Any, Dict, List, Optional

import dns.resolver
import nmap
from geopy.geocoders import Nominatim
from loguru import logger

from app.collectors.base_collector import (BaseCollector, CollectionResult,
                                           CollectorConfig, DataType,
                                           RiskLevel)


class IPCollector(BaseCollector):
    """
    IP OSINT Collector

    Collects comprehensive OSINT data for IP addresses.
    """

    def __init__(self, config: CollectorConfig):
        super().__init__(config, name="IPCollector")

    async def collect(self) -> CollectionResult:
        """
        Collect OSINT data for the target IP.

        Returns:
            CollectionResult with discovered entities
        """
        result = CollectionResult(
            success=False, collector_name=self.name, correlation_id=self.correlation_id
        )

        try:
            ip = self.config.target

            # Validate IP address
            import ipaddress

            try:
                ipaddress.ip_address(ip)
            except ValueError:
                result.errors.append(f"Invalid IP address: {ip}")
                return result

            logger.info(f"Collecting IP OSINT for {ip}")

            # Collect various types of data
            tasks = [
                self._geolocate_ip(ip),
                self._reverse_dns(ip),
                self._check_ip_reputation(ip),
                self._get_whois_ip(ip),
                self._detect_vpn_proxy(ip),
            ]

            # Port scanning can be intrusive, make optional
            tasks.append(self._scan_ports(ip))

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
                "ip": ip,
                "tasks_completed": len(
                    [r for r in results if not isinstance(r, Exception)]
                ),
            }

        except Exception as e:
            logger.exception(f"Error in IP collection: {e}")
            result.errors.append(str(e))

        return result

    async def _geolocate_ip(self, ip: str) -> List[Dict[str, Any]]:
        """Geolocate IP address"""
        entities = []

        try:
            # Use free geolocation APIs
            # Try ip-api.com
            geo_url = f"http://ip-api.com/json/{ip}"

            response = await self.session.get(geo_url, timeout=10)

            if response.status_code == 200:
                geo_data = response.json()

                if geo_data.get("status") == "success":
                    entity = self._create_entity(
                        entity_type="IP_ADDRESS",
                        value=ip,
                        risk_level=RiskLevel.INFO,
                        metadata={
                            "country": geo_data.get("country"),
                            "country_code": geo_data.get("countryCode"),
                            "region": geo_data.get("regionName"),
                            "city": geo_data.get("city"),
                            "zip": geo_data.get("zip"),
                            "lat": geo_data.get("lat"),
                            "lon": geo_data.get("lon"),
                            "timezone": geo_data.get("timezone"),
                            "isp": geo_data.get("isp"),
                            "org": geo_data.get("org"),
                            "as": geo_data.get("as"),
                            "query": geo_data.get("query"),
                        },
                    )

                    entities.append(entity)

                    # Create ORG entity for ISP
                    if geo_data.get("org"):
                        entities.append(
                            self._create_entity(
                                entity_type="ORG",
                                value=geo_data["org"],
                                risk_level=RiskLevel.INFO,
                                metadata={
                                    "type": "isp",
                                    "country": geo_data.get("country"),
                                    "asn": geo_data.get("as"),
                                },
                            )
                        )

                        # Create relationship
                        entities.append(
                            {
                                "relationship_type": "OWNS",
                                "source": geo_data["org"],
                                "target": ip,
                                "metadata": {"relationship": "ip_assignment"},
                            }
                        )

                    logger.info(
                        f"Geolocated {ip}: {geo_data.get('city')}, {geo_data.get('country')}"
                    )

        except Exception as e:
            logger.error(f"Error geolocating {ip}: {e}")

        return entities

    async def _scan_ports(self, ip: str) -> List[Dict[str, Any]]:
        """Scan common ports"""
        entities = []

        try:
            # Use nmap for port scanning
            # Note: This can be slow and may be detected

            loop = asyncio.get_event_loop()

            async def run_nmap():
                nm = nmap.PortScanner()
                nm.scan(ip, arguments="-F")  # Fast scan of common ports

                results = []

                if ip in nm.all_hosts():
                    host = nm[ip]

                    # Get open ports
                    for proto in nm[ip].all_protocols():
                        ports = nm[ip][proto].keys()

                        for port in ports:
                            port_info = nm[ip][proto][port]

                            results.append(
                                {
                                    "port": port,
                                    "protocol": proto,
                                    "state": port_info["state"],
                                    "service": port_info.get("name", ""),
                                    "product": port_info.get("product", ""),
                                    "version": port_info.get("version", ""),
                                    "extrainfo": port_info.get("extrainfo", ""),
                                }
                            )

                return results

            port_results = await loop.run_in_executor(None, asyncio.run, run_nmap())

            if port_results:
                # Check for high-risk ports
                high_risk_ports = [21, 22, 23, 135, 139, 445, 3389, 5432, 3306]
                open_ports = [p["port"] for p in port_results]

                risk_level = RiskLevel.INFO
                if any(p in high_risk_ports for p in open_ports):
                    risk_level = RiskLevel.HIGH

                entities.append(
                    self._create_entity(
                        entity_type="IP_ADDRESS",
                        value=ip,
                        risk_level=risk_level,
                        metadata={
                            "open_ports": port_results,
                            "open_ports_count": len(port_results),
                            "high_risk_ports": [
                                p for p in open_ports if p in high_risk_ports
                            ],
                        },
                    )
                )

                logger.info(f"Found {len(port_results)} open ports on {ip}")

        except ImportError:
            logger.warning("python-nmap not installed, skipping port scan")
        except Exception as e:
            logger.error(f"Error scanning ports on {ip}: {e}")

        return entities

    async def _reverse_dns(self, ip: str) -> List[Dict[str, Any]]:
        """Perform reverse DNS lookup"""
        entities = []

        try:
            # Run in thread pool as it's blocking
            loop = asyncio.get_event_loop()

            try:
                hostname, _, _ = await loop.run_in_executor(
                    None, socket.gethostbyaddr, ip
                )

                entities.append(
                    self._create_entity(
                        entity_type="IP_ADDRESS",
                        value=ip,
                        risk_level=RiskLevel.INFO,
                        metadata={"reverse_dns": hostname, "hostname": hostname},
                    )
                )

                # Create DOMAIN entity
                entities.append(
                    self._create_entity(
                        entity_type="DOMAIN",
                        value=hostname,
                        risk_level=RiskLevel.INFO,
                        metadata={"source": "reverse_dns", "ip_address": ip},
                    )
                )

                logger.info(f"Reverse DNS for {ip}: {hostname}")

            except socket.herror:
                logger.debug(f"No reverse DNS found for {ip}")

        except Exception as e:
            logger.error(f"Error performing reverse DNS for {ip}: {e}")

        return entities

    async def _check_ip_reputation(self, ip: str) -> List[Dict[str, Any]]:
        """Check IP reputation"""
        entities = []

        try:
            # Check against known bad IPs (placeholder)
            # Real implementation would check:
            # - Spamhaus
            # - AbuseIPDB
            # - VirusTotal
            # - Project Honey Pot

            # For now, do basic checks
            reputation_indicators = []

            # Check if it's a private IP
            import ipaddress

            try:
                ip_obj = ipaddress.ip_address(ip)
                if ip_obj.is_private:
                    reputation_indicators.append("private_ip")
                elif ip_obj.is_loopback:
                    reputation_indicators.append("loopback")
                elif ip_obj.is_link_local:
                    reputation_indicators.append("link_local")
                elif ip_obj.is_reserved:
                    reputation_indicators.append("reserved")
            except Exception:
                pass

            risk_level = RiskLevel.INFO
            if reputation_indicators:
                risk_level = RiskLevel.LOW

            entities.append(
                self._create_entity(
                    entity_type="IP_ADDRESS",
                    value=ip,
                    risk_level=risk_level,
                    metadata={
                        "reputation_indicators": reputation_indicators,
                        "note": "Full reputation check requires API access to blacklist services",
                    },
                )
            )

            logger.info(f"Reputation check completed for {ip}")

        except Exception as e:
            logger.error(f"Error checking IP reputation for {ip}: {e}")

        return entities

    async def _get_whois_ip(self, ip: str) -> List[Dict[str, Any]]:
        """Get WHOIS data for IP"""
        entities = []

        try:
            # Use whois command or library
            import whois

            loop = asyncio.get_event_loop()
            whois_data = await loop.run_in_executor(None, whois.whois, ip)

            if whois_data:
                # Parse organization and netrange
                org = whois_data.org or whois_data.organization

                if org:
                    entities.append(
                        self._create_entity(
                            entity_type="ORG",
                            value=org,
                            risk_level=RiskLevel.INFO,
                            metadata={
                                "source": "whois",
                                "ip_address": ip,
                                "nets": whois_data.nets
                                if hasattr(whois_data, "nets")
                                else None,
                            },
                        )
                    )

                    # Create relationship
                    entities.append(
                        {
                            "relationship_type": "OWNS",
                            "source": org,
                            "target": ip,
                            "metadata": {
                                "source": "whois",
                                "relationship": "ip_allocation",
                            },
                        }
                    )

                logger.info(f"WHOIS lookup completed for {ip}")

        except ImportError:
            logger.warning("python-whois not installed, skipping WHOIS lookup")
        except Exception as e:
            logger.error(f"Error getting WHOIS for {ip}: {e}")

        return entities

    async def _detect_vpn_proxy(self, ip: str) -> List[Dict[str, Any]]:
        """Detect VPN or proxy"""
        entities = []

        try:
            # Check against known VPN/proxy lists (placeholder)
            # Real implementation would check services like:
            # - ipqualityscore.com
            # - proxycheck.io
            # - getipintel.net

            # For now, basic detection based on port patterns and geolocation
            detection_indicators = []

            # Check common VPN ports if we have port scan results
            # This would require correlating with previous scan results

            # Check hostname patterns (if reverse DNS exists)
            try:
                hostname = socket.gethostbyaddr(ip)[0]
                if any(
                    keyword in hostname.lower()
                    for keyword in ["vpn", "proxy", "tunnel", "tor", "relay", "gateway"]
                ):
                    detection_indicators.append("suspicious_hostname")
            except Exception:
                pass

            risk_level = RiskLevel.INFO
            if detection_indicators:
                risk_level = RiskLevel.MEDIUM

            entities.append(
                self._create_entity(
                    entity_type="IP_ADDRESS",
                    value=ip,
                    risk_level=risk_level,
                    metadata={
                        "vpn_proxy_indicators": detection_indicators,
                        "note": "Full VPN/proxy detection requires API access",
                    },
                )
            )

            logger.info(f"VPN/proxy detection completed for {ip}")

        except Exception as e:
            logger.error(f"Error detecting VPN/proxy for {ip}: {e}")

        return entities

    def normalize(self, raw_data: Any) -> List[Dict[str, Any]]:
        """Normalize raw IP data"""
        return raw_data if isinstance(raw_data, list) else []

    def validate(self, data: Dict[str, Any]) -> bool:
        """Validate normalized data"""
        if isinstance(data, dict) and "relationship_type" in data:
            return True
        required_fields = ["entity_type", "value"]
        return all(field in data for field in required_fields)
