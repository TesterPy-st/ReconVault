"""
Domain OSINT Collector for ReconVault intelligence system.

This module provides domain intelligence gathering using WHOIS lookups,
DNS enumeration, and historical data retrieval.
"""

import asyncio
import re
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging
from whois import whois as python_whois
import requests
from bs4 import BeautifulSoup

from .base_collector import BaseCollector, CollectorConfig


class DomainCollector(BaseCollector):
    """Domain OSINT collector for domain intelligence"""
    
    def __init__(self, config: CollectorConfig):
        super().__init__(config)
        self.logger = logging.getLogger(__name__)
    
    async def collect(self) -> Dict[str, Any]:
        """Collect domain intelligence data"""
        self.logger.info(f"Starting domain collection for target: {self.config.target}")
        
        domain = self._extract_domain(self.config.target)
        if not domain:
            raise ValueError(f"Invalid domain format: {self.config.target}")
        
        results = {
            "target": domain,
            "entities": [],
            "relationships": [],
            "metadata": {}
        }
        
        try:
            # Perform WHOIS lookup
            whois_data = await self.whois_lookup(domain)
            if whois_data:
                results["entities"].extend(whois_data.get("entities", []))
                results["relationships"].extend(whois_data.get("relationships", []))
                results["metadata"]["whois"] = whois_data.get("metadata", {})
            
            # Perform DNS enumeration
            dns_data = await self.dns_enumeration(domain)
            results["entities"].extend(dns_data)
            
            # Get historical data
            historical_data = await self.get_historical_data(domain)
            if historical_data:
                results["metadata"]["historical"] = historical_data
            
            # Check reputation
            reputation_data = await self.check_reputation(domain)
            if reputation_data:
                results["metadata"]["reputation"] = reputation_data
            
            # Get nameservers
            nameservers = await self.get_nameservers(domain)
            results["entities"].extend(nameservers)
            
            # Detect mail servers
            mail_servers = await self.detect_mail_servers(domain)
            results["entities"].extend(mail_servers)
            
            return results
            
        except Exception as e:
            self.logger.error(f"Domain collection failed: {e}")
            raise
    
    def _extract_domain(self, target: str) -> Optional[str]:
        """Extract clean domain from target"""
        if not target:
            return None
        
        # Remove protocols
        domain = target.lower()
        if "://" in domain:
            domain = domain.split("://")[1]
        
        # Remove paths and queries
        domain = domain.split('/')[0].split('?')[0]
        
        # Remove port numbers
        domain = domain.split(':')[0]
        
        return domain
    
    async def whois_lookup(self, domain: str) -> Optional[Dict[str, Any]]:
        """Perform WHOIS lookup for domain"""
        try:
            self.logger.debug(f"Performing WHOIS lookup for: {domain}")
            
            whois_result = python_whois(domain)
            
            if not whois_result:
                self.logger.warning(f"No WHOIS data found for {domain}")
                return None
            
            entities = []
            relationships = []
            
            # Extract domain entity
            domain_entity = {
                "value": domain,
                "type": "DOMAIN",
                "metadata": {
                    "whois_available": True,
                    "registrar": whois_result.get("registrar", "unknown"),
                    "whois_server": whois_result.get("whois_server", "unknown"),
                    "referral_url": whois_result.get("referral_url"),
                    "status": whois_result.get("status", []),
                    "name_servers": whois_result.get("name_servers", []),
                    "collected_at": datetime.utcnow().isoformat()
                },
                "source": "whois_lookup"
            }
            
            # Parse dates
            def parse_date(date_value):
                if isinstance(date_value, list) and date_value:
                    date_value = date_value[0]
                
                if isinstance(date_value, datetime):
                    return date_value
                
                if date_value:
                    try:
                        return datetime.strptime(str(date_value), "%Y-%m-%d %H:%M:%S")
                    except:
                        try:
                            return datetime.fromisoformat(str(date_value))
                        except:
                            return None
                
                return None
            
            creation_date = parse_date(whois_result.get("creation_date"))
            if creation_date:
                domain_entity["metadata"]["creation_date"] = creation_date.isoformat()
                domain_entity["metadata"]["domain_age_days"] = (datetime.now() - creation_date).days
            
            expiration_date = parse_date(whois_result.get("expiration_date"))
            if expiration_date:
                domain_entity["metadata"]["expiration_date"] = expiration_date.isoformat()
                domain_entity["metadata"]["days_until_expiration"] = (expiration_date - datetime.now()).days
            
            updated_date = parse_date(whois_result.get("updated_date"))
            if updated_date:
                domain_entity["metadata"]["updated_date"] = updated_date.isoformat()
            
            entities.append(domain_entity)
            
            # Extract registrant information
            registrant_data = {
                "name": whois_result.get("name"),
                "org": whois_result.get("org"),
                "email": whois_result.get("email"),
                "address": whois_result.get("address"),
                "city": whois_result.get("city"),
                "state": whois_result.get("state"),
                "zipcode": whois_result.get("zipcode"),
                "country": whois_result.get("country")
            }
            
            # Create registrant entity if available
            registrant_name = registrant_data.get("name") or registrant_data.get("email")
            if registrant_name:
                registrant_entity = {
                    "value": registrant_name,
                    "type": "ORG" if registrant_data.get("org") else "PERSON",
                    "metadata": {
                        **{k: v for k, v in registrant_data.items() if v},
                        "role": "registrant",
                        "collected_at": datetime.utcnow().isoformat()
                    },
                    "source": "whois_lookup"
                }
                
                entities.append(registrant_entity)
                
                # Create relationship between registrant and domain
                relationships.append({
                    "type": "OWNS",
                    "source_value": registrant_name,
                    "source_type": "ORG" if registrant_data.get("org") else "PERSON",
                    "target_value": domain,
                    "target_type": "DOMAIN",
                    "metadata": {
                        "relationship": "domain_registration",
                        "strength": 0.9
                    }
                })
            
            # Extract nameservers
            name_servers = whois_result.get("name_servers", [])
            for ns in name_servers:
                ns_str = str(ns).lower().rstrip('.')
                ns_entity = {
                    "value": ns_str,
                    "type": "NAMESERVER",
                    "metadata": {
                        "domain": domain,
                        "source": "whois",
                        "collected_at": datetime.utcnow().isoformat()
                    },
                    "source": "whois_lookup"
                }
                
                entities.append(ns_entity)
                
                # Link nameserver to domain
                relationships.append({
                    "type": "RELATED_TO",
                    "source_value": domain,
                    "source_type": "DOMAIN",
                    "target_value": ns_str,
                    "target_type": "NAMESERVER",
                    "metadata": {
                        "relationship": "dns_configuration",
                        "strength": 0.8
                    }
                })
            
            return {
                "entities": entities,
                "relationships": relationships,
                "metadata": {
                    "registrar": whois_result.get("registrar"),
                    "lookup_success": True
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error in WHOIS lookup for {domain}: {e}")
            return None
    
    async def dns_enumeration(self, domain: str) -> List[Dict[str, Any]]:
        """Enumerate all DNS records for domain"""
        entities = []
        
        try:
            import dns.resolver
            import dns.rdatatype
            
            self.logger.debug(f"Performing DNS enumeration for: {domain}")
            
            # Common DNS record types to check
            record_types = [
                'A', 'AAAA', 'CNAME', 'MX', 'TXT', 'NS', 'SOA', 'SRV',
                'PTR', 'CAA', 'DNSKEY', 'DS'
            ]
            
            for record_type in record_types:
                try:
                    self.logger.debug(f"Querying {record_type} records for {domain}")
                    
                    answers = dns.resolver.resolve(domain, record_type)
                    
                    for rdata in answers:
                        entity = {
                            "value": str(rdata),
                            "type": record_type,
                            "metadata": {
                                "domain": domain,
                                "record_type": record_type,
                                "ttl": getattr(answers, 'ttl', None),
                                "collected_at": datetime.utcnow().isoformat()
                            },
                            "source": "dns_enumeration"
                        }
                        
                        # Add record-type specific metadata
                        if record_type == 'A':
                            entity["metadata"]["ip_version"] = "IPv4"
                            
                        elif record_type == 'AAAA':
                            entity["metadata"]["ip_version"] = "IPv6"
                            
                        elif record_type == 'CNAME':
                            entity["metadata"]["canonical_name"] = str(rdata)
                            
                        elif record_type == 'MX':
                            entity["metadata"].update({
                                "priority": getattr(rdata, 'preference', None),
                                "exchange": str(rdata.exchange).rstrip('.')
                            })
                            
                        elif record_type == 'TXT':
                            txt_data = str(rdata)
                            entity["metadata"]["text"] = txt_data
                            
                            # Parse common TXT record types
                            if txt_data.startswith('v=spf1'):
                                entity["metadata"]["spf_record"] = True
                            elif 'DKIM' in txt_data:
                                entity["metadata"]["dkim_record"] = True
                            elif 'DMARC' in txt_data:
                                entity["metadata"]["dmarc_record"] = True
                            
                        elif record_type == 'NS':
                            entity["metadata"]["nameserver"] = str(rdata).rstrip('.')
                            
                        elif record_type == 'SOA':
                            entity["metadata"].update({
                                "primary_ns": str(rdata.mname).rstrip('.'),
                                "responsible_email": str(rdata.rname).rstrip('.'),
                                "serial": rdata.serial,
                                "refresh": rdata.refresh,
                                "retry": rdata.retry,
                                "expire": rdata.expire,
                                "minimum_ttl": rdata.minimum
                            })
                        
                        entities.append(entity)
                        
                except dns.resolver.NXDOMAIN:
                    self.logger.warning(f"Domain {domain} does not exist")
                    break
                except dns.resolver.NoAnswer:
                    self.logger.debug(f"No {record_type} record for {domain}")
                except Exception as e:
                    self.logger.debug(f"Error resolving {record_type} for {domain}: {e}")
            
        except ImportError:
            self.logger.warning("dnspython not available for DNS enumeration")
        except Exception as e:
            self.logger.error(f"Error in DNS enumeration for {domain}: {e}")
        
        self.logger.info(f"Found {len(entities)} DNS records for {domain}")
        return entities
    
    async def get_historical_data(self, domain: str) -> Optional[Dict[str, Any]]:
        """Get historical data for domain from Wayback Machine and other sources"""
        historical_data = {
            "wayback_snapshots": [],
            "dns_history": [],
            "registrar_history": []
        }
        
        try:
            self.logger.debug(f"Getting historical data for: {domain}")
            
            # Wayback Machine snapshots
            wayback_url = f"http://archive.org/wayback/available?url={domain}"
            response = self._make_request(wayback_url, timeout=20)
            
            if response.status_code == 200:
                wayback_data = response.json()
                if wayback_data.get("archived_snapshots"):
                    snapshots = wayback_data["archived_snapshots"]
                    for key, snapshot in snapshots.items():
                        if snapshot.get("available"):
                            historical_data["wayback_snapshots"].append({
                                "timestamp": snapshot.get("timestamp"),
                                "url": snapshot.get("url"),
                                "status": "available"
                            })
            
            # Try DNS history from SecurityTrails (free tier limited)
            try:
                securitytrails_url = f"https://api.securitytrails.com/v1/history/{domain}/dns/a"
                # Note: This requires API key for full functionality
                self.logger.debug("SecurityTrails DNS history would require API key")
            except:
                pass
            
            # Historical WHOIS data
            # Note: This would typically require paid services for historical data
            self.logger.debug("Historical WHOIS data requires paid services for full functionality")
            
        except Exception as e:
            self.logger.error(f"Error getting historical data for {domain}: {e}")
        
        return historical_data
    
    async def check_reputation(self, domain: str) -> Optional[Dict[str, Any]]:
        """Check domain reputation and blacklist status"""
        reputation = {
            "blacklist_status": [],
            "phishing_score": 0,
            "malware_score": 0,
            "suspicious_indicators": []
        }
        
        try:
            self.logger.debug(f"Checking reputation for: {domain}")
            
            # Check multiple blacklist services
            blacklist_checks = [
                ("Google Safe Browsing", f"https://www.google.com/transparencyreport/safebrowsing/diagnostic/#domain:{domain}"),
                ("PhishTank", f"http://checkurl.phishtank.com/checkurl/"),
                ("VirusTotal", f"https://www.virustotal.com/gui/domain/{domain}")
            ]
            
            # VirusTotal API check (if API key available)
            try:
                from app.config import settings
                if hasattr(settings, 'VIRUSTOTAL_API_KEY') and settings.VIRUSTOTAL_API_KEY:
                    vt_url = f"https://www.virustotal.com/vtapi/v2/domain/report"
                    params = {
                        'apikey': settings.VIRUSTOTAL_API_KEY,
                        'domain': domain
                    }
                    
                    response = self._make_request(vt_url, params=params, timeout=20)
                    if response.status_code == 200:
                        vt_data = response.json()
                        reputation["virustotal_data"] = {
                            "positives": vt_data.get("positives", 0),
                            "total": vt_data.get("total", 0),
                            "scan_date": vt_data.get("scan_date", "")
                        }
            except:
                self.logger.debug("VirusTotal API not configured")
            
            # Check URLVoid (blacklist aggregator)
            try:
                urlvoid_url = f"http://api.urlvoid.com/api1000/{settings.URLVOID_API_KEY}/host/{domain}/"
                # Would process URLVoid response here
            except:
                self.logger.debug("URLVoid check not configured")
            
            # Analyze domain characteristics for suspicious indicators
            domain_lower = domain.lower()
            
            # Check for suspicious TLDs
            suspicious_tlds = ['.tk', '.ml', '.ga', '.cf', '.gq', '.xyz', '.pw', '.cc', '.ws']
            if any(domain_lower.endswith(tld) for tld in suspicious_tlds):
                reputation["suspicious_indicators"].append("suspicious_tld")
            
            # Check for brand impersonation
            brand_keywords = ['paypal', 'amazon', 'facebook', 'google', 'microsoft', 'apple']
            if any(brand in domain_lower for brand in brand_keywords):
                reputation["suspicious_indicators"].append("potential_brand_impersonation")
            
            # Check domain age (young domains are riskier)
            if "domain_age_days" in results.get("metadata", {}).get("whois", {}):
                age_days = results["metadata"]["whois"].get("domain_age_days", 0)
                if age_days < 30:
                    reputation["suspicious_indicators"].append("very_new_domain")
                elif age_days < 90:
                    reputation["suspicious_indicators"].append("new_domain")
            
            # Calculate risk scores
            reputation["phishing_score"] = min(len(reputation["suspicious_indicators"]) * 20, 100)
            reputation["malware_score"] = reputation["phishing_score"]  # Simplified
            
        except Exception as e:
            self.logger.error(f"Error checking reputation for {domain}: {e}")
        
        return reputation
    
    async def get_nameservers(self, domain: str) -> List[Dict[str, Any]]:
        """Get nameserver information for domain"""
        entities = []
        
        try:
            import dns.resolver
            
            self.logger.debug(f"Getting nameservers for: {domain}")
            
            # Query NS records
            answers = dns.resolver.resolve(domain, 'NS')
            
            for rdata in answers:
                nameserver = str(rdata).rstrip('.')
                
                # Try to get nameserver IP
                ns_ips = []
                try:
                    ns_answers = dns.resolver.resolve(nameserver, 'A')
                    ns_ips = [str(ip) for ip in ns_answers]
                except:
                    pass
                
                entity = {
                    "value": nameserver,
                    "type": "NAMESERVER",
                    "metadata": {
                        "domain": domain,
                        "ips": ns_ips,
                        "ttl": getattr(answers, 'ttl', None),
                        "priority": 0,  # NS records don't have priority
                        "collected_at": datetime.utcnow().isoformat()
                    },
                    "source": "nameserver_lookup"
                }
                
                entities.append(entity)
                
                # Add IP entities if found
                for ip in ns_ips:
                    entities.append({
                        "value": ip,
                        "type": "IP_ADDRESS",
                        "metadata": {
                            "associated_nameserver": nameserver,
                            "domain": domain,
                            "source": "dns_resolution"
                        },
                        "source": "nameserver_lookup"
                    })
            
        except Exception as e:
            self.logger.error(f"Error getting nameservers for {domain}: {e}")
        
        return entities
    
    async def detect_mail_servers(self, domain: str) -> List[Dict[str, Any]]:
        """Detect and analyze mail servers for domain"""
        entities = []
        
        try:
            import dns.resolver
            
            self.logger.debug(f"Detecting mail servers for: {domain}")
            
            # Query MX records
            try:
                answers = dns.resolver.resolve(domain, 'MX')
                
                for rdata in answers:
                    mail_server = str(rdata.exchange).rstrip('.')
                    priority = rdata.preference
                    
                    entity = {
                        "value": mail_server,
                        "type": "MAIL_SERVER",
                        "metadata": {
                            "domain": domain,
                            "priority": priority,
                            "ttl": getattr(answers, 'ttl', None),
                            "collected_at": datetime.utcnow().isoformat()
                        },
                        "source": "mail_server_detection"
                    }
                    
                    entities.append(entity)
                    
                    # Try to resolve mail server IP
                    try:
                        mail_ip_answers = dns.resolver.resolve(mail_server, 'A')
                        for mail_ip_rdata in mail_ip_answers:
                            mail_ip = str(mail_ip_rdata)
                            
                            entities.append({
                                "value": mail_ip,
                                "type": "IP_ADDRESS",
                                "metadata": {
                                    "mail_server": mail_server,
                                    "domain": domain,
                                    "source": "mail_server_resolution"
                                },
                                "source": "mail_server_detection"
                            })
                            
                            # Link mail server to IP
                            entities.append({
                                "value": f"{mail_server}->{mail_ip}",
                                "type": "RELATIONSHIP",
                                "metadata": {
                                    "source_type": "MAIL_SERVER",
                                    "target_type": "IP_ADDRESS",
                                    "relationship": "resolves_to"
                                },
                                "source": "mail_server_detection"
                            })
                            
                    except Exception as e:
                        self.logger.debug(f"Could not resolve mail server IP: {e}")
            
            except dns.resolver.NoAnswer:
                # No MX records, try A record for direct mail
                self.logger.debug(f"No MX records found for {domain}, checking A record")
                
            except Exception as e:
                self.logger.error(f"Error detecting mail servers for {domain}: {e}")
            
            # Check for SPF records
            try:
                txt_answers = dns.resolver.resolve(domain, 'TXT')
                for rdata in txt_answers:
                    txt_str = str(rdata)
                    if txt_str.startswith('v=spf1'):
                        entities.append({
                            "value": f"SPF_{domain}",
                            "type": "DNS_RECORD",
                            "record_type": "TXT",
                            "metadata": {
                                "domain": domain,
                                "record": "SPF",
                                "data": txt_str,
                                "ttl": getattr(txt_answers, 'ttl', None),
                                "collected_at": datetime.utcnow().isoformat()
                            },
                            "source": "mail_server_detection"
                        })
                        break
            except:
                pass
                
        except ImportError:
            self.logger.warning("dnspython not available for mail server detection")
        except Exception as e:
            self.logger.error(f"Error in mail server detection for {domain}: {e}")
        
        self.logger.info(f"Found {len(entities)} mail server entities for {domain}")
        return entities
    
    def normalize(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Normalize domain collection results"""
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
                    "source": data.get("source", "domain_collector")
                })
        
        return entities