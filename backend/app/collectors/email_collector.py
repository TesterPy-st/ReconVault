"""
Email OSINT Collector for ReconVault intelligence system.

This module provides email intelligence gathering capabilities including
email verification, breach checking, and pattern analysis.
"""

import asyncio
import re
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging
import smtplib
import dns.resolver

from .base_collector import BaseCollector, CollectorConfig


class EmailCollector(BaseCollector):
    """Email OSINT collector for email intelligence"""
    
    def __init__(self, config: CollectorConfig):
        super().__init__(config)
        self.logger = logging.getLogger(__name__)
    
    async def collect(self) -> Dict[str, Any]:
        """Collect email intelligence data"""
        self.logger.info(f"Starting email collection for target: {self.config.target}")
        
        email = self._normalize_email(self.config.target)
        if not email:
            raise ValueError(f"Invalid email format: {self.config.target}")
        
        results = {
            "target": email,
            "entities": [],
            "relationships": [],
            "metadata": {}
        }
        
        try:
            # Verify email format and existence
            verification = await self.verify_email(email)
            results["metadata"]["verification"] = verification
            
            # Check for breaches
            breach_data = await self.check_breaches(email)
            if breach_data:
                results["entities"].extend(breach_data.get("entities", []))
                results["metadata"]["breaches"] = breach_data.get("breaches", [])
            
            # Extract domain from email
            domain_data = await self.extract_domain(email)
            if domain_data:
                results["entities"].extend(domain_data.get("entities", []))
                results["relationships"].extend(domain_data.get("relationships", []))
            
            # Find associated accounts
            accounts = await self.find_associated_accounts(email)
            results["entities"].extend(accounts)
            
            # Get email provider info
            provider_info = await self.get_email_provider_info(email)
            results["metadata"]["provider"] = provider_info
            
            # Check common variants
            variants = await self.check_common_variants(email)
            results["entities"].extend(variants)
            
            return results
            
        except Exception as e:
            self.logger.error(f"Email collection failed: {e}")
            raise
    
    def _normalize_email(self, target: str) -> Optional[str]:
        """Normalize and validate email address"""
        if not target:
            return None
        
        # Basic email validation
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[A-Z|a-z]{2,}$'
        if not re.match(email_pattern, target.strip()):
            return None
        
        return target.strip().lower()
    
    async def verify_email(self, email: str) -> Dict[str, Any]:
        """Verify email format and MX record existence"""
        verification = {
            "email": email,
            "format_valid": False,
            "domain_exists": False,
            "mx_records": [],
            "smtp_check": False,
            "disposable": False,
            "role_account": False,
            "overall_score": 0
        }
        
        try:
            self.logger.debug(f"Verifying email: {email}")
            
            # Check format
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[A-Z|a-z]{2,}$'
            verification["format_valid"] = bool(re.match(email_pattern, email))
            
            if not verification["format_valid"]:
                return verification
            
            # Extract domain
            domain = email.split('@')[1]
            
            # Check if disposable email
            disposable_domains = [
                'mailinator.com', 'tempmail.com', '10minutemail.com', 'guerrillamail.com',
                'yopmail.com', 'temp-mail.org', 'getnada.com', 'burnermail.io'
            ]
            verification["disposable"] = domain.lower() in disposable_domains
            
            # Check if role account
            local_part = email.split('@')[0].lower()
            role_prefixes = [
                'admin', 'administrator', 'webmaster', 'hostmaster', 'postmaster',
                'root', 'support', 'info', 'sales', 'contact', 'help', 'billing',
                'abuse', 'security', 'legal', 'press', 'media', 'careers', 'jobs'
            ]
            verification["role_account"] = local_part in role_prefixes
            
            # Check MX records
            try:
                mx_records = []
                answers = dns.resolver.resolve(domain, 'MX')
                
                for rdata in answers:
                    mx_record = {
                        "priority": rdata.preference,
                        "exchange": str(rdata.exchange).rstrip('.')
                    }
                    mx_records.append(mx_record)
                
                verification["mx_records"] = mx_records
                verification["domain_exists"] = len(mx_records) > 0
                
            except:
                verification["domain_exists"] = False
                verification["mx_records"] = []
            
            # Calculate overall verification score
            score = 0
            if verification["format_valid"]:
                score += 25
            if verification["domain_exists"]:
                score += 35
            if len(verification["mx_records"]) > 0:
                score += 20
            if not verification["disposable"]:
                score += 10
            if not verification["role_account"]:
                score += 10
            
            verification["overall_score"] = min(score, 100)
            
        except Exception as e:
            self.logger.error(f"Error verifying email {email}: {e}")
        
        return verification
    
    async def check_breaches(self, email: str) -> Optional[Dict[str, Any]]:
        """Check if email has been in data breaches using HaveIBeenPwned API"""
        breach_info = {
            "email": email,
            "breached": False,
            "breach_count": 0,
            "breaches": [],
            "paste_count": 0,
            "pastes": []
        }
        
        try:
            self.logger.debug(f"Checking breaches for email: {email}")
            
            # HaveIBeenPwned API requires User-Agent header
            headers = {
                'User-Agent': 'ReconVault-OSINT-Collector',
                'hibp-api-key': ''  # Would use API key here if available
            }
            
            # Check breaches
            breach_url = f"https://haveibeenpwned.com/api/v3/breachedaccount/{email}"
            
            try:
                response = self._make_request(breach_url, headers=headers, timeout=15)
                
                if response.status_code == 200:
                    breach_data = response.json()
                    
                    breach_info["breached"] = True
                    breach_info["breach_count"] = len(breach_data)
                    
                    for breach in breach_data:
                        breach_details = {
                            "name": breach.get("Name"),
                            "title": breach.get("Title"),
                            "domain": breach.get("Domain"),
                            "breach_date": breach.get("BreachDate"),
                            "added_date": breach.get("AddedDate"),
                            "modified_date": breach.get("ModifiedDate"),
                            "pwn_count": breach.get("PwnCount"),
                            "description": breach.get("Description"),
                            "data_classes": breach.get("DataClasses", []),
                            "is_verified": breach.get("IsVerified", False),
                            "is_fabricated": breach.get("IsFabricated", False),
                            "is_sensitive": breach.get("IsSensitive", False),
                            "is_retired": breach.get("IsRetired", False),
                            "is_spam_list": breach.get("IsSpamList", False)
                        }
                        
                        breach_info["breaches"].append(breach_details)
                
                elif response.status_code == 404:
                    # Not breached
                    breach_info["breached"] = False
                
                elif response.status_code == 429:
                    # Rate limited
                    self.logger.warning("HaveIBeenPwned rate limit exceeded")
                    breach_info["error"] = "Rate limit exceeded"
                
                else:
                    self.logger.warning(f"HaveIBeenPwned API error: {response.status_code}")
            except:
                # Fallback: check using breach directory API
                try:
                    breach_directory_url = f"https://breachdirectory.org/api?query={email}"
                    response = self._make_request(breach_directory_url, timeout=15)
                    if response.status_code == 200:
                        breach_data = response.json()
                        # Process breach directory response
                        pass
                except:
                    pass
            
            # Check pastes
            paste_url = f"https://haveibeenpwned.com/api/v3/pasteaccount/{email}"
            try:
                paste_response = self._make_request(paste_url, headers=headers, timeout=15)
                
                if paste_response.status_code == 200:
                    paste_data = paste_response.json()
                    
                    breach_info["paste_count"] = len(paste_data)
                    
                    for paste in paste_data:
                        paste_details = {
                            "source": paste.get("Source"),
                            "id": paste.get("Id"),
                            "title": paste.get("Title"),
                            "date": paste.get("Date"),
                            "email_count": paste.get("EmailCount")
                        }
                        
                        breach_info["pastes"].append(paste_details)
                
            except:
                pass  # Paste check failed, continue
            
        except Exception as e:
            self.logger.error(f"Error checking breaches for {email}: {e}")
        
        # Convert to entities if breached
        entities = []
        if breach_info["breached"]:
            for breach in breach_info["breaches"]:
                breach_entity = {
                    "value": breach["name"],
                    "type": "DATA_BREACH",
                    "metadata": {
                        "email": email,
                        "title": breach["title"],
                        "domain": breach["domain"],
                        "breach_date": breach["breach_date"],
                        "pwn_count": breach["pwn_count"],
                        "data_classes": breach["data_classes"],
                        "is_verified": breach["is_verified"],
                        "collected_at": datetime.utcnow().isoformat()
                    },
                    "source": "haveibeenpwned"
                }
                
                entities.append(breach_entity)
        
        return {
            "breaches": breach_info,
            "entities": entities
        }
    
    async def extract_domain(self, email: str) -> Optional[Dict[str, Any]]:
        """Extract domain from email and create relationship"""
        try:
            domain = email.split('@')[1]
            
            entities = [
                {
                    "value": domain,
                    "type": "DOMAIN",
                    "metadata": {
                        "email": email,
                        "source": "email_extractor",
                        "collected_at": datetime.utcnow().isoformat()
                    },
                    "source": "email_extractor"
                },
                {
                    "value": email,
                    "type": "EMAIL",
                    "metadata": {
                        "domain": domain,
                        "source": "email_extractor",
                        "collected_at": datetime.utcnow().isoformat()
                    },
                    "source": "email_extractor"
                }
            ]
            
            relationships = [
                {
                    "type": "USES",
                    "source_value": email,
                    "source_type": "EMAIL",
                    "target_value": domain,
                    "target_type": "DOMAIN",
                    "metadata": {
                        "strength": 1.0,
                        "collected_at": datetime.utcnow().isoformat()
                    }
                }
            ]
            
            return {
                "entities": entities,
                "relationships": relationships
            }
            
        except Exception as e:
            self.logger.error(f"Error extracting domain from {email}: {e}")
            return None
    
    async def find_associated_accounts(self, email: str) -> List[Dict[str, Any]]:
        """Find social accounts associated with email"""
        entities = []
        
        try:
            self.logger.debug(f"Finding associated accounts for: {email}")
            
            # Extract username from email
            username = email.split('@')[0]
            
            # Check if username follows patterns indicating real name
            name_patterns = [
                r'^[a-z]+\.[a-z]+$',  # first.last
                r'^[a-z]+_[a-z]+$',   # first_last
                r'^[a-z]+[a-z]$',     # firstlast
                r'^[a-z]\.[a-z]+$',   # f.last
            ]
            
            has_name_pattern = any(re.match(pattern, username) for pattern in name_patterns)
            
            if len(username) >= 3 and (has_name_pattern or len(username) <= 20):
                # Create username entities for common platforms
                platforms = [
                    ("twitter", f"@{username}"),
                    ("github", f"@{username}"),
                    ("instagram", f"@{username}"),
                    ("facebook", username)
                ]
                
                for platform, platform_username in platforms:
                    entity = {
                        "value": platform_username,
                        "type": "USERNAME",
                        "platform": platform,
                        "metadata": {
                            "email": email,
                            "pattern_match": has_name_pattern,
                            "confidence": 0.6 if has_name_pattern else 0.3,
                            "source": "pattern_analysis",
                            "collected_at": datetime.utcnow().isoformat()
                        },
                        "source": "email_associator"
                    }
                    
                    entities.append(entity)
            
            # Search for email on public platforms (simplified)
            # In a real implementation, would search various APIs and databases
            
        except Exception as e:
            self.logger.error(f"Error finding associated accounts for {email}: {e}")
        
        return entities
    
    async def get_email_provider_info(self, email: str) -> Dict[str, Any]:
        """Get information about email provider"""
        provider_info = {
            "domain": "",
            "provider": "unknown",
            "provider_type": "unknown",
            "free_provider": False,
            "popular_provider": False,
            "security_features": []
        }
        
        try:
            self.logger.debug(f"Getting provider info for: {email}")
            
            domain = email.split('@')[1].lower()
            provider_info["domain"] = domain
            
            # Common free providers
            free_providers = {
                'gmail.com': {'provider': 'Google', 'type': 'free', 'features': ['2fa', 'spf', 'dkim', 'dmarc']},
                'yahoo.com': {'provider': 'Yahoo', 'type': 'free', 'features': ['2fa', 'spf', 'dkim', 'dmarc']},
                'outlook.com': {'provider': 'Microsoft', 'type': 'free', 'features': ['2fa', 'spf', 'dkim', 'dmarc']},
                'hotmail.com': {'provider': 'Microsoft', 'type': 'free', 'features': ['2fa', 'spf', 'dkim', 'dmarc']},
                'aol.com': {'provider': 'AOL', 'type': 'free', 'features': ['spf', 'dkim']},
                'protonmail.com': {'provider': 'ProtonMail', 'type': 'secure', 'features': ['2fa', 'encrypt', 'spf', 'dkim', 'dmarc']},
                'icloud.com': {'provider': 'Apple', 'type': 'free', 'features': ['2fa', 'spf', 'dkim', 'dmarc']},
                'mail.com': {'provider': 'Mail.com', 'type': 'free', 'features': ['spf', 'dkim']}
            }
            
            # Popular business providers
            business_providers = {
                'office365.com': {'provider': 'Microsoft 365', 'type': 'enterprise', 'features': ['2fa', 'spf', 'dkim', 'dmarc', 'encrypt']},
                'googlemail.com': {'provider': 'Google Workspace', 'type': 'enterprise', 'features': ['2fa', 'spf', 'dkim', 'dmarc']},
                'outlook.office365.com': {'provider': 'Microsoft 365', 'type': 'enterprise', 'features': ['2fa', 'spf', 'dkim', 'dmarc', 'encrypt']}
            }
            
            all_providers = {**free_providers, **business_providers}
            
            if domain in all_providers:
                provider_data = all_providers[domain]
                provider_info["provider"] = provider_data['provider']
                provider_info["provider_type"] = provider_data['type']
                provider_info["free_provider"] = provider_data['type'] == 'free'
                provider_info["popular_provider"] = True
                provider_info["security_features"] = provider_data['features']
            else:
                # Check if domain has typical enterprise/business features
                try:
                    # Check for SPF record
                    spf_records = []
                    txt_answers = dns.resolver.resolve(domain, 'TXT')
                    for rdata in txt_answers:
                        txt_str = str(rdata)
                        if txt_str.startswith('v=spf1'):
                            provider_info["security_features"].append('spf')
                            break
                    
                    # Check for MX records (indicates configured email)
                    mx_answers = dns.resolver.resolve(domain, 'MX')
                    if len(mx_answers) > 0:
                        provider_info["provider_type"] = "custom" if not provider_info["popular_provider"] else provider_info["provider_type"]
                        
                except:
                    pass
                
                # Determine if likely free/custom
                provider_info["free_provider"] = provider_info["provider_type"] == 'free' or domain in ['protonmail.com', 'tutanota.com']
            
        except Exception as e:
            self.logger.error(f"Error getting provider info for {email}: {e}")
        
        return provider_info
    
    async def check_common_variants(self, email: str) -> List[Dict[str, Any]]:
        """Check for common email variants based on patterns"""
        entities = []
        
        try:
            self.logger.debug(f"Checking common variants for: {email}")
            
            local_part, domain = email.split('@')
            
            # Generate common variants
            variants = set()
            
            # Common separator variations
            separators = ['.', '_', '-', '']
            
            # For patterns like first.last, first_last, etc.
            for sep in separators:
                if sep in local_part:
                    parts = local_part.split(sep)
                    if len(parts) == 2:
                        first, last = parts
                        # Generate variants
                        variants.add(f"{first}{sep}{last}")
                        variants.add(f"{last}{sep}{first}")
                        variants.add(f"{first[0]}{sep}{last}")
                        variants.add(f"{first}{last}")
                        variants.add(f"{first[0]}{last}")
                        
                        # Add common domains for variant checking
                        common_domains = ['gmail.com', 'yahoo.com', 'outlook.com', 'hotmail.com']
                        for variant in variants.copy():
                            for common_domain in common_domains:
                                if domain != common_domain:
                                    variants.add(f"{variant}@{common_domain}")
            
            # Remove original email and add variants as entities
            variants.discard(local_part)
            
            for variant in variants:
                if '@' in variant:
                    variant_email = variant
                else:
                    variant_email = f"{variant}@{domain}"
                
                if variant_email != email:
                    entity = {
                        "value": variant_email,
                        "type": "EMAIL",
                        "metadata": {
                            "original_email": email,
                            "variant_type": "pattern",
                            "confidence": 0.4,
                            "source": "variant_generator",
                            "collected_at": datetime.utcnow().isoformat()
                        },
                        "source": "email_variant"
                    }
                    
                    entities.append(entity)
            
        except Exception as e:
            self.logger.error(f"Error checking common variants for {email}: {e}")
        
        return entities
    
    def normalize(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Normalize email collection results"""
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
                    "type": "EMAIL",
                    "metadata": data.get("metadata", {}),
                    "source": data.get("source", "email_collector")
                })
        
        return entities