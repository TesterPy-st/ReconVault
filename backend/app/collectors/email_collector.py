"""
Email OSINT Collector

Collects OSINT data for email addresses including:
- Email verification
- Breach checking (HaveIBeenPwned)
- Domain extraction
- Associated account discovery
- Email provider detection
- Common variant checking
"""

import asyncio
import re
from typing import Any, Dict, List, Optional

import dns.resolver
from loguru import logger
from validators import email as validate_email

from app.collectors.base_collector import (BaseCollector, CollectionResult,
                                           CollectorConfig, DataType,
                                           RiskLevel)


class EmailCollector(BaseCollector):
    """
    Email OSINT Collector

    Collects comprehensive OSINT data for email addresses.
    """

    def __init__(self, config: CollectorConfig):
        super().__init__(config, name="EmailCollector")

    async def collect(self) -> CollectionResult:
        """
        Collect OSINT data for the target email.

        Returns:
            CollectionResult with discovered entities
        """
        result = CollectionResult(
            success=False, collector_name=self.name, correlation_id=self.correlation_id
        )

        try:
            email_address = self.config.target

            # Validate email format
            if not validate_email(email_address):
                result.errors.append(f"Invalid email format: {email_address}")
                return result

            logger.info(f"Collecting email OSINT for {email_address}")

            # Collect various types of data
            tasks = [
                self._verify_email(email_address),
                self._check_breaches(email_address),
                self._extract_domain(email_address),
                self._get_email_provider_info(email_address),
                self._check_common_variants(email_address),
            ]

            results = await asyncio.gather(*tasks, return_exceptions=True)

            # Aggregate results
            for i, task_result in enumerate(results):
                if isinstance(task_result, Exception):
                    logger.error(f"Task {i} failed: {task_result}")
                    result.errors.append(str(task_result))
                elif task_result:
                    result.data.extend(task_result)

            # Find associated accounts (if email verified)
            if any(
                e.get("entity_type") == "EMAIL" and e.get("metadata", {}).get("valid")
                for e in result.data
            ):
                associated = await self._find_associated_accounts(email_address)
                result.data.extend(associated)

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
                "email": email_address,
                "tasks_completed": len(
                    [r for r in results if not isinstance(r, Exception)]
                ),
            }

        except Exception as e:
            logger.exception(f"Error in email collection: {e}")
            result.errors.append(str(e))

        return result

    async def _verify_email(self, email_address: str) -> List[Dict[str, Any]]:
        """Verify email format and check if domain can receive email"""
        entities = []

        try:
            # Extract domain
            domain = email_address.split("@")[1]

            # Check MX records
            resolver = dns.resolver.Resolver()
            resolver.timeout = 10
            resolver.lifetime = 10

            try:
                mx_records = resolver.resolve(domain, "MX")
                mx_exists = len(mx_records) > 0
            except Exception:
                mx_exists = False

            # Create EMAIL entity
            entity = self._create_entity(
                entity_type="EMAIL",
                value=email_address,
                risk_level=RiskLevel.INFO,
                metadata={
                    "valid_format": True,
                    "mx_records_exist": mx_exists,
                    "domain": domain,
                    "local_part": email_address.split("@")[0],
                },
            )

            entities.append(entity)

            logger.info(f"Email verification completed for {email_address}")

        except Exception as e:
            logger.error(f"Error verifying email {email_address}: {e}")

        return entities

    async def _check_breaches(self, email_address: str) -> List[Dict[str, Any]]:
        """Check if email has been in data breaches"""
        entities = []

        try:
            # Use HaveIBeenPwned API (free tier, requires API key)
            import os

            hibp_api_key = os.getenv("HIBP_API_KEY")

            if not hibp_api_key:
                logger.warning("HIBP_API_KEY not set, skipping breach check")
                return entities

            # HaveIBeenPwned API
            hibp_url = (
                f"https://haveibeenpwned.com/api/v3/breachedaccount/{email_address}"
            )
            headers = {"hibp-api-key": hibp_api_key, "User-Agent": "ReconVault-OSINT"}

            response = await self.session.get(hibp_url, headers=headers, timeout=10)

            if response.status_code == 200:
                breaches = response.json()

                risk_level = RiskLevel.CRITICAL if breaches else RiskLevel.INFO

                breach_summaries = []
                for breach in breaches:
                    breach_summaries.append(
                        {
                            "name": breach.get("Name", ""),
                            "title": breach.get("Title", ""),
                            "domain": breach.get("Domain", ""),
                            "breach_date": breach.get("BreachDate", ""),
                            "added_date": breach.get("AddedDate", ""),
                            "pwn_count": breach.get("PwnCount", 0),
                            "description": breach.get("Description", ""),
                            "data_classes": breach.get("DataClasses", []),
                        }
                    )

                entity = self._create_entity(
                    entity_type="EMAIL",
                    value=email_address,
                    risk_level=risk_level,
                    metadata={
                        "breaches_found": len(breach_summaries),
                        "breaches": breach_summaries,
                        "total_records_exposed": sum(
                            b["pwn_count"] for b in breach_summaries
                        ),
                    },
                )

                entities.append(entity)

                # Create COMPROMISED_BY relationships
                for breach in breach_summaries:
                    entities.append(
                        {
                            "relationship_type": "COMPROMISED_BY",
                            "source": email_address,
                            "target": breach["name"],
                            "metadata": {
                                "breach_date": breach["breach_date"],
                                "records_exposed": breach["pwn_count"],
                                "data_classes": breach["data_classes"],
                            },
                        }
                    )

                logger.warning(
                    f"Found {len(breach_summaries)} breaches for {email_address}"
                )

            elif response.status_code == 404:
                # No breaches found
                logger.info(f"No breaches found for {email_address}")
            elif response.status_code == 401:
                logger.error("HIBP API key unauthorized")

        except Exception as e:
            logger.error(f"Error checking breaches for {email_address}: {e}")

        return entities

    async def _extract_domain(self, email_address: str) -> List[Dict[str, Any]]:
        """Extract domain from email"""
        entities = []

        try:
            domain = email_address.split("@")[1]

            # Create DOMAIN entity
            entities.append(
                self._create_entity(
                    entity_type="DOMAIN",
                    value=domain,
                    risk_level=RiskLevel.INFO,
                    metadata={"source": "email_extraction", "email": email_address},
                )
            )

            # Create relationship
            entities.append(
                {
                    "relationship_type": "RELATED_TO",
                    "source": email_address,
                    "target": domain,
                    "metadata": {"relationship": "email_domain"},
                }
            )

        except Exception as e:
            logger.error(f"Error extracting domain from {email_address}: {e}")

        return entities

    async def _find_associated_accounts(
        self, email_address: str
    ) -> List[Dict[str, Any]]:
        """Find accounts associated with email"""
        entities = []

        try:
            # Note: This would typically require username enumeration
            # Real implementation would check:
            # - Username databases
            # - Social APIs (if available)
            # - HaveIBeenPwned paste leaks

            username_part = email_address.split("@")[0]

            # Check for common account patterns
            platforms = [
                ("github", f"https://github.com/{username_part}"),
                ("reddit", f"https://reddit.com/user/{username_part}"),
            ]

            for platform, url in platforms:
                try:
                    await self._apply_rate_limit()
                    response = await self.session.get(url, timeout=10)

                    if response.status_code == 200:
                        entities.append(
                            {
                                "relationship_type": "ASSOCIATES_WITH",
                                "source": email_address,
                                "target": url,
                                "metadata": {
                                    "platform": platform,
                                    "inferred_username": username_part,
                                },
                            }
                        )

                        logger.info(
                            f"Found potential {platform} account for {email_address}"
                        )

                    await asyncio.sleep(1)

                except Exception as e:
                    logger.debug(f"Failed to check {platform}: {e}")

        except Exception as e:
            logger.error(f"Error finding associated accounts for {email_address}: {e}")

        return entities

    async def _get_email_provider_info(
        self, email_address: str
    ) -> List[Dict[str, Any]]:
        """Get email provider information"""
        entities = []

        try:
            domain = email_address.split("@")[1]

            # Identify provider type
            common_providers = {
                "gmail.com": {"type": "free", "provider": "Google"},
                "yahoo.com": {"type": "free", "provider": "Yahoo"},
                "outlook.com": {"type": "free", "provider": "Microsoft"},
                "hotmail.com": {"type": "free", "provider": "Microsoft"},
                "icloud.com": {"type": "free", "provider": "Apple"},
                "protonmail.com": {"type": "secure", "provider": "Proton Technologies"},
                "tutanota.com": {"type": "secure", "provider": "Tutanota"},
            }

            provider_info = common_providers.get(
                domain.lower(), {"type": "custom", "provider": domain}
            )

            # Update metadata
            # Find the EMAIL entity and add provider info
            for entity in entities:
                if (
                    entity.get("entity_type") == "EMAIL"
                    and entity.get("value") == email_address
                ):
                    entity["metadata"].update(
                        {
                            "provider_type": provider_info["type"],
                            "provider": provider_info["provider"],
                        }
                    )

            logger.info(
                f"Email provider for {email_address}: {provider_info['provider']}"
            )

        except Exception as e:
            logger.error(f"Error getting email provider info: {e}")

        return entities

    async def _check_common_variants(self, email_address: str) -> List[Dict[str, Any]]:
        """Check common email variants"""
        entities = []

        try:
            local_part, domain = email_address.split("@")

            # Common patterns
            variants = []

            # Split by common delimiters
            if "." in local_part:
                # firstname.lastname variants
                parts = local_part.split(".")
                if len(parts) >= 2:
                    variants.append(f"{parts[0]}{parts[1]}@{domain}")  # firstlast
                    variants.append(f"{parts[1]}.{parts[0]}@{domain}")  # last.first

            # Check which variants exist (have MX records)
            resolver = dns.resolver.Resolver()
            resolver.timeout = 5
            resolver.lifetime = 5

            valid_variants = []
            for variant in variants:
                try:
                    variant_domain = variant.split("@")[1]
                    resolver.resolve(variant_domain, "MX")
                    valid_variants.append(variant)
                except Exception:
                    continue

            if valid_variants:
                entity = self._create_entity(
                    entity_type="EMAIL",
                    value=email_address,
                    risk_level=RiskLevel.INFO,
                    metadata={
                        "valid_variants": valid_variants,
                        "variant_count": len(valid_variants),
                    },
                )

                entities.append(entity)

                # Create ASSOCIATES_WITH relationships
                for variant in valid_variants:
                    entities.append(
                        {
                            "relationship_type": "ASSOCIATES_WITH",
                            "source": email_address,
                            "target": variant,
                            "metadata": {"relationship": "email_variant"},
                        }
                    )

                logger.info(f"Found {len(valid_variants)} valid email variants")

        except Exception as e:
            logger.error(f"Error checking email variants: {e}")

        return entities

    def normalize(self, raw_data: Any) -> List[Dict[str, Any]]:
        """Normalize raw email data"""
        return raw_data if isinstance(raw_data, list) else []

    def validate(self, data: Dict[str, Any]) -> bool:
        """Validate normalized data"""
        if isinstance(data, dict) and "relationship_type" in data:
            return True
        required_fields = ["entity_type", "value"]
        return all(field in data for field in required_fields)
