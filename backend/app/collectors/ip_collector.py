"""
IP OSINT Collector for ReconVault intelligence system.

This module provides IP address intelligence gathering using geolocation,
port scanning, and threat intelligence services.
"""

import asyncio
import re
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging
import socket
from ipaddress import ip_address, IPv4Address, IPv6Address

# Conditional imports for optional dependencies
try:
    import nmap
    NMAP_AVAILABLE = True
except ImportError:
    NMAP_AVAILABLE = False
    nmap = None

try:
    from geopy.geocoders import Nominatim
    GEO_AVAILABLE = True
except ImportError:
    GEO_AVAILABLE = False
    Nominatim = None

from .base_collector import BaseCollector, CollectorConfig


class IPCollector(BaseCollector):
    """IP OSINT collector for IP address intelligence"""
    
    def __init__(self, config: CollectorConfig):
        super().__init__(config)
        self.logger = logging.getLogger(__name__)
        self.nm = nmap.PortScanner() if NMAP_AVAILABLE and nmap else None
        self.geolocator = Nominatim(user_agent="ReconVault-OSINT") if GEO_AVAILABLE and Nominatim else None
    
    async def collect(self) -> Dict[str, Any]:
        """Collect IP intelligence data"""
        self.logger.info(f"Starting IP collection for target: {self.config.target}")
        
        ip = self._extract_ip(self.config.target)
        if not ip:
            raise ValueError(f"Invalid IP address format: {self.config.target}")
        
        results = {
            "target": ip,
            "entities": [],
            "relationships": [],
            "metadata": {}
        }
        
        try:
            # Geolocate IP
            geo_data = await self.geolocate_ip(ip)
            if geo_data:
                results["entities"].extend(geo_data.get("entities", []))
                results["relationships"].extend(geo_data.get("relationships", []))
                results["metadata"]["geolocation"] = geo_data.get("metadata", {})
            
            # Scan ports if configured
            if self.nm:
                port_data = await self.scan_ports(ip)
                results["entities"].extend(port_data.get("entities", []))
                results["metadata"]["open_ports"] = port_data.get("open_ports", [])
            
            # Reverse DNS lookup
            reverse_dns_data = await self.reverse_dns(ip)
            if reverse_dns_data:
                results["entities"].extend(reverse_dns_data.get("entities", []))
                results["relationships"].extend(reverse_dns_data.get("relationships", []))
            
            # Check IP reputation
            reputation_data = await self.check_ip_reputation(ip)
            if reputation_data:
                results["metadata"]["reputation"] = reputation_data
            
            # Get WHOIS IP information
            whois_ip_data = await self.get_whois_ip(ip)
            if whois_ip_data:
                results["entities"].extend(whois_ip_data.get("entities", []))
                results["relationships"].extend(whois_ip_data.get("relationships", []))
                results["metadata"]["ip_whois"] = whois_ip_data.get("metadata", {})
            
            # Detect VPN/proxy
            vpn_proxy_data = await self.detect_vpn_proxy(ip)
            results["metadata"]["vpn_proxy"] = vpn_proxy_data
            
            return results
            
        except Exception as e:
            self.logger.error(f"IP collection failed: {e}")
            raise
    
    def _extract_ip(self, target: str) -> Optional[str]:
        """Extract and validate IP address"""
        if not target:
            return None
        
        # Clean up target
        target = target.strip()
        
        try:
            # Validate as IP address
            ip = ip_address(target)
            return str(ip)
        except ValueError:
            # Try to resolve hostname to IP
            try:
                resolved_ip = socket.gethostbyname(target)
                return str(ip_address(resolved_ip))
            except:
                pass
        
        return None
    
    async def geolocate_ip(self, ip: str) -> Optional[Dict[str, Any]]:
        """Geolocate IP address"""
        if not self.geolocator:
            self.logger.warning("Geolocation service not available")
            return None
        
        try:
            self.logger.debug(f"Geolocating IP: {ip}")
            
            # Use ip-api.com for free geolocation
            api_url = f"http://ip-api.com/json/{ip}"
            response = self._make_request(api_url, timeout=15)
            
            if response.status_code == 200:
                geo_data = response.json()
                
                if geo_data.get("status") == "success":
                    entities = [{
                        "value": ip,
                        "type": "IP_ADDRESS",
                        "metadata": {
                            "latitude": geo_data.get("lat"),
                            "longitude": geo_data.get("lon"),
                            "country": geo_data.get("country"),
                            "country_code": geo_data.get("countryCode"),
                            "region": geo_data.get("regionName"),
                            "region_code": geo_data.get("region"),
                            "city": geo_data.get("city"),
                            "zip_code": geo_data.get("zip"),
                            "timezone": geo_data.get("timezone"),
                            "isp": geo_data.get("isp"),
                            "org": geo_data.get("org"),
                            "as": geo_data.get("as"),
                            "asname": geo_data.get("asname"),
                            "reverse_dns": geo_data.get("reverse"),
                            "mobile": geo_data.get("mobile", False),
                            "proxy": geo_data.get("proxy", False),
                            "hosting": geo_data.get("hosting", False),
                            "collected_at": datetime.utcnow().isoformat()
                        },
                        "source": "ip_geolocation"
                    }]
                    
                    # Create location entity
                    location_parts = []
                    if geo_data.get("city"):
                        location_parts.append(geo_data.get("city"))
                    if geo_data.get("regionName"):
                        location_parts.append(geo_data.get("regionName"))
                    if geo_data.get("country"):
                        location_parts.append(geo_data.get("country"))
                    
                    location_str = ", ".join(location_parts) if location_parts else "Unknown"
                    
                    location_entity = {
                        "value": location_str,
                        "type": "LOCATION",
                        "metadata": {
                            "latitude": geo_data.get("lat"),
                            "longitude": geo_data.get("lon"),
                            "country": geo_data.get("country"),
                            "country_code": geo_data.get("countryCode"),
                            "region": geo_data.get("regionName"),
                            "city": geo_data.get("city"),
                            "collected_at": datetime.utcnow().isoformat()
                        },
                        "source": "ip_geolocation"
                    }
                    
                    entities.append(location_entity)
                    
                    # Create relationships
                    relationships = [
                        {
                            "type": "LOCATED_AT",
                            "source_value": ip,
                            "source_type": "IP_ADDRESS",
                            "target_value": location_str,
                            "target_type": "LOCATION",
                            "metadata": {
                                "confidence": geo_data.get("accuracy", 0),
                                "strength": 0.9,
                                "collected_at": datetime.utcnow().isoformat()
                            }
                        }
                    ]
                    
                    # Add ISP/Organization relationship
                    if geo_data.get("org") or geo_data.get("isp"):
                        org_name = geo_data.get("org") or geo_data.get("isp")
                        relationships.append({
                            "type": "OWNS",
                            "source_value": org_name,
                            "source_type": "ORG",
                            "target_value": ip,
                            "target_type": "IP_ADDRESS",
                            "metadata": {
                                "relationship": "ip_allocation",
                                "asn": geo_data.get("as"),
                                "strength": 0.8,
                                "collected_at": datetime.utcnow().isoformat()
                            }
                        })
                    
                    return {
                        "entities": entities,
                        "relationships": relationships,
                        "metadata": {
                            "geolocation_service": "ip-api.com",
                            "confidence": geo_data.get("accuracy")
                        }
                    }
            
        except Exception as e:
            self.logger.error(f"Error geolocating IP {ip}: {e}")
        
        return None
    
    async def scan_ports(self, ip: str) -> Dict[str, Any]:
        """Scan common ports on IP address"""
        entities = []
        open_ports = []
        
        if not self.nm:
            self.logger.warning("Nmap not available for port scanning")
            return {"entities": entities, "open_ports": open_ports}
        
        try:
            self.logger.debug(f"Scanning ports for IP: {ip}")
            
            # Common ports to scan
            common_ports = "21,22,23,25,53,80,110,135,139,143,443,993,995,1723,3306,3389,5900,8080,8443"
            
            # Run nmap scan
            self.nm.scan(ip, common_ports, arguments='-sV --open -T4')
            
            if ip in self.nm.all_hosts():
                host = self.nm[ip]
                
                if host.state() == "up":
                    # Extract scan results
                    for proto in host.all_protocols():
                        lport = host[proto].keys()
                        for port in sorted(lport):
                            port_info = host[proto][port]
                            
                            if port_info['state'] == 'open':
                                port_data = {
                                    "port": port,
                                    "protocol": proto,
                                    "service": port_info.get('name', 'unknown'),
                                    "state": port_info['state'],
                                    "product": port_info.get('product', 'unknown'),
                                    "version": port_info.get('version', 'unknown'),
                                    "cpe": port_info.get('cpe', [])
                                }
                                
                                open_ports.append(port_data)
                                
                                # Create service entity
                                service_entity = {
                                    "value": f"{ip}:{port}",
                                    "type": "NETWORK_SERVICE",
                                    "metadata": {
                                        "ip": ip,
                                        "port": port,
                                        "protocol": proto,
                                        "service": port_info.get('name', 'unknown'),
                                        "product": port_info.get('product'),
                                        "version": port_info.get('version'),
                                        "cpe": port_info.get('cpe', []),
                                        "extrainfo": port_info.get('extrainfo'),
                                        "conf": port_info.get('conf', 0),
                                        "collected_at": datetime.utcnow().isoformat()
                                    },
                                    "source": "port_scanner"
                                }
                                
                                entities.append(service_entity)
                                
                                # Create relationship between IP and service
                                relationship = {
                                    "type": "RUNS",
                                    "source_value": ip,
                                    "source_type": "IP_ADDRESS",
                                    "target_value": f"{ip}:{port}",
                                    "target_type": "NETWORK_SERVICE",
                                    "metadata": {
                                        "port": port,
                                        "service": port_info.get('name', 'unknown'),
                                        "strength": 1.0
                                    }
                                }
                                
                                entities.append(relationship)
                    
                    self.logger.info(f"Found {len(open_ports)} open ports on {ip}")
            
        except Exception as e:
            self.logger.error(f"Error scanning ports for {ip}: {e}")
        
        return {"entities": entities, "open_ports": open_ports}
    
    async def reverse_dns(self, ip: str) -> Optional[Dict[str, Any]]:
        """Perform reverse DNS lookup for IP"""
        entities = []
        relationships = []
        
        try:
            self.logger.debug(f"Performing reverse DNS for IP: {ip}")
            
            # Try reverse DNS lookup
            try:
                hostname, aliaslist, ipaddrlist = socket.gethostbyaddr(ip)
                
                # Create hostname entity
                hostname_entity = {
                    "value": hostname,
                    "type": "HOSTNAME",
                    "metadata": {
                        "ip": ip,
                        "aliases": aliaslist,
                        "ip_addresses": ipaddrlist,
                        "collected_at": datetime.utcnow().isoformat()
                    },
                    "source": "reverse_dns"
                }
                
                entities.append(hostname_entity)
                
                # Create relationship
                relationship = {
                    "type": "RESOLVES_TO",
                    "source_value": hostname,
                    "source_type": "HOSTNAME",
                    "target_value": ip,
                    "target_type": "IP_ADDRESS",
                    "metadata": {
                        "strength": 1.0,
                        "verified": True
                    }
                }
                
                relationships.append(relationship)
                
                # Create alias entities
                for alias in aliaslist:
                    alias_entity = {
                        "value": alias,
                        "type": "HOSTNAME",
                        "metadata": {
                            "primary_hostname": hostname,
                            "ip": ip,
                            "collected_at": datetime.utcnow().isoformat()
                        },
                        "source": "reverse_dns"
                    }
                    
                    entities.append(alias_entity)
                    
                    # Create alias relationship
                    alias_relationship = {
                        "type": "ALIAS_OF",
                        "source_value": alias,
                        "source_type": "HOSTNAME",
                        "target_value": hostname,
                        "target_type": "HOSTNAME",
                        "metadata": {
                            "strength": 1.0
                        }
                    }
                    
                    entities.append(alias_relationship)
            
            except:
                self.logger.debug(f"No reverse DNS entry found for {ip}")
        
        except Exception as e:
            self.logger.error(f"Error in reverse DNS for {ip}: {e}")
        
        return {
            "entities": entities,
            "relationships": relationships
        } if entities else None
    
    async def check_ip_reputation(self, ip: str) -> Optional[Dict[str, Any]]:
        """Check IP address reputation and threat intelligence"""
        reputation = {
            "blacklist_status": [],
            "threat_intel": [],
            "abuse_reports": 0,
            "risk_score": 0
        }
        
        try:
            self.logger.debug(f"Checking IP reputation for: {ip}")
            
            # Check multiple reputation services
            
            # AbuseIPDB check (requires API key)
            try:
                from app.config import settings
                if hasattr(settings, 'ABUSEIPDB_API_KEY') and settings.ABUSEIPDB_API_KEY:
                    abuse_url = "https://api.abuseipdb.com/api/v2/check"
                    headers = {
                        'Key': settings.ABUSEIPDB_API_KEY,
                        'Accept': 'application/json'
                    }
                    params = {
                        'ipAddress': ip,
                        'maxAgeInDays': '90',
                        'verbose': ''
                    }
                    
                    response = self._make_request(abuse_url, headers=headers, params=params, timeout=20)
                    if response.status_code == 200:
                        abuse_data = response.json().get("data", {})
                        reputation["abuse_reports"] = abuse_data.get("totalReports", 0)
                        reputation["abuse_confidence"] = abuse_data.get("abuseConfidenceScore", 0)
                        reputation["country_code"] = abuse_data.get("countryCode")
                        reputation["usage_type"] = abuse_data.get("usageType")
                        reputation["isp"] = abuse_data.get("isp")
            except:
                self.logger.debug("AbuseIPDB not configured")
            
            # Check against blocklists using MultiRBL
            try:
                multirbl_url = f"http://multirbl.valli.org/lookup/{ip}.html"
                # Would parse MultiRBL results here
                self.logger.debug("MultiRBL check would require HTML parsing")
            except:
                pass
            
            # Check Project Honeypot
            try:
                # Would implement Project Honeypot API check here
                self.logger.debug("Project Honeypot check placeholder")
            except:
                pass
            
            # Calculate risk score
            risk_factors = 0
            
            if reputation.get("abuse_reports", 0) > 10:
                risk_factors += 3
            elif reputation.get("abuse_reports", 0) > 3:
                risk_factors += 2
            elif reputation.get("abuse_reports", 0) > 0:
                risk_factors += 1
            
            if reputation.get("abuse_confidence", 0) > 80:
                risk_factors += 3
            elif reputation.get("abuse_confidence", 0) > 50:
                risk_factors += 2
            elif reputation.get("abuse_confidence", 0) > 20:
                risk_factors += 1
            
            # Convert risk factors to risk score (0-100)
            reputation["risk_score"] = min(risk_factors * 20, 100)
            
        except Exception as e:
            self.logger.error(f"Error checking IP reputation for {ip}: {e}")
        
        return reputation
    
    async def get_whois_ip(self, ip: str) -> Optional[Dict[str, Any]]:
        """Get WHOIS information for IP address"""
        try:
            self.logger.debug(f"Getting IP WHOIS for: {ip}")
            
            # Use ip-api.com for WHOIS-like information
            api_url = f"http://ip-api.com/json/{ip}?fields=status,message,country,countryCode,region,regionName,city,zip,lat,lon,timezone,isp,org,as,asname,reverse,mobile,proxy,hosting,query"
            
            response = self._make_request(api_url, timeout=15)
            
            if response.status_code == 200:
                whois_data = response.json()
                
                if whois_data.get("status") == "success":
                    entities = []
                    relationships = []
                    
                    # IP entity
                    ip_entity = {
                        "value": ip,
                        "type": "IP_ADDRESS",
                        "metadata": {
                            "isp": whois_data.get("isp"),
                            "organization": whois_data.get("org"),
                            "asn": whois_data.get("as"),
                            "as_name": whois_data.get("asname"),
                            "reverse_dns": whois_data.get("reverse"),
                            "collected_at": datetime.utcnow().isoformat()
                        },
                        "source": "ip_whois"
                    }
                    
                    entities.append(ip_entity)
                    
                    # Organization entity if available
                    if whois_data.get("org"):
                        org_entity = {
                            "value": whois_data.get("org"),
                            "type": "ORG",
                            "metadata": {
                                "asn": whois_data.get("as"),
                                "as_name": whois_data.get("asname"),
                                "collected_at": datetime.utcnow().isoformat()
                            },
                            "source": "ip_whois"
                        }
                        
                        entities.append(org_entity)
                        
                        # Link organization to IP
                        relationships.append({
                            "type": "OWNS",
                            "source_value": whois_data.get("org"),
                            "source_type": "ORG",
                            "target_value": ip,
                            "target_type": "IP_ADDRESS",
                            "metadata": {
                                "allocation_type": "ip_assignment",
                                "strength": 0.9
                            }
                        })
                    
                    # ISP entity
                    if whois_data.get("isp") and whois_data.get("isp") != whois_data.get("org"):
                        isp_entity = {
                            "value": whois_data.get("isp"),
                            "type": "ORG",
                            "sub_type": "ISP",
                            "metadata": {
                                "asn": whois_data.get("as"),
                                "collected_at": datetime.utcnow().isoformat()
                            },
                            "source": "ip_whois"
                        }
                        
                        entities.append(isp_entity)
                    
                    return {
                        "entities": entities,
                        "relationships": relationships,
                        "metadata": whois_data
                    }
            
        except Exception as e:
            self.logger.error(f"Error getting IP WHOIS for {ip}: {e}")
        
        return None
    
    async def detect_vpn_proxy(self, ip: str) -> Dict[str, Any]:
        """Detect if IP is a VPN or proxy"""
        detection = {
            "is_vpn": False,
            "is_proxy": False,
            "is_datacenter": False,
            "is_hosting": False,
            "confidence": 0,
            "evidence": []
        }
        
        try:
            self.logger.debug(f"Detecting VPN/Proxy for IP: {ip}")
            
            # Check using ip-api.com data
            geo_check = await self.geolocate_ip(ip)
            if geo_check:
                geo_metadata = geo_check.get("metadata", {})
                
                if geo_metadata.get("proxy"):
                    detection["is_proxy"] = True
                    detection["confidence"] += 30
                    detection["evidence"].append("ip_api_proxy_flag")
                
                if geo_metadata.get("hosting"):
                    detection["is_hosting"] = True
                    detection["confidence"] += 20
                    detection["evidence"].append("ip_api_hosting_flag")
                
                if geo_metadata.get("mobile"):
                    detection["evidence"].append("mobile_network")
            
            # Check if IP is in known hosting/datacenter ranges
            # This would use a database of known datacenter IPs
            
            # Check against known VPN/proxy lists
            # This would use threat intelligence feeds
            
            # Check for unusual geolocation discrepancies
            if detection["confidence"] > 50:
                detection["is_vpn"] = True
            
        except Exception as e:
            self.logger.error(f"Error detecting VPN/Proxy for {ip}: {e}")
        
        return detection
    
    def normalize(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Normalize IP collection results"""
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
                    "type": "IP_ADDRESS",
                    "metadata": data.get("metadata", {}),
                    "source": data.get("source", "ip_collector")
                })
        
        return entities