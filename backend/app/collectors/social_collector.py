"""
Social OSINT Collector

Collects OSINT data from social media platforms including:
- Username search across platforms
- Twitter/X profile analysis
- GitHub profile analysis
- Email-associated account discovery
- Social connection mapping
- Posting pattern analysis
"""

import asyncio
import json
import re
from datetime import datetime
from typing import Any, Dict, List, Optional
from urllib.parse import urljoin

from bs4 import BeautifulSoup
from loguru import logger

from app.collectors.base_collector import (BaseCollector, CollectionResult,
                                           CollectorConfig, DataType,
                                           RiskLevel)


class SocialCollector(BaseCollector):
    """
    Social OSINT Collector

    Collects OSINT data from social media platforms and profiles.
    """

    def __init__(self, config: CollectorConfig):
        super().__init__(config, name="SocialCollector")

        # Platform detection patterns
        self.platform_patterns = {
            "twitter": [r"twitter\.com/", r"x\.com/"],
            "github": [r"github\.com/"],
            "facebook": [r"facebook\.com/", r"fb\.com/"],
            "instagram": [r"instagram\.com/"],
            "linkedin": [r"linkedin\.com/"],
            "reddit": [r"reddit\.com/u/", r"reddit\.com/user/"],
            "youtube": [r"youtube\.com/@"],
            "tiktok": [r"tiktok\.com/@"],
        }

    async def collect(self) -> CollectionResult:
        """
        Collect OSINT data from social media.

        Returns:
            CollectionResult with discovered entities
        """
        result = CollectionResult(
            success=False, collector_name=self.name, correlation_id=self.correlation_id
        )

        try:
            target = self.config.target

            # Determine target type and route to appropriate methods
            if self._is_email(target):
                logger.info(f"Collecting social OSINT for email: {target}")
                tasks = [
                    self._search_email(target),
                    self._find_associated_accounts(target),
                ]
            elif self._is_social_url(target):
                logger.info(f"Collecting social OSINT for URL: {target}")
                tasks = [self._extract_social_profile(target)]
            else:
                # Assume it's a username
                logger.info(f"Collecting social OSINT for username: {target}")
                tasks = [
                    self._search_username(target),
                    self._extract_social_connections(target),
                    self._analyze_posting_patterns(target),
                ]

            results = await asyncio.gather(*tasks, return_exceptions=True)

            for task_result in results:
                if isinstance(task_result, Exception):
                    logger.error(f"Social collection task failed: {task_result}")
                    result.errors.append(str(task_result))
                elif task_result:
                    result.data.extend(task_result)

            result.success = len(result.errors) == 0
            result.metadata = {
                "target": target,
                "target_type": "email" if self._is_email(target) else "username",
            }

        except Exception as e:
            logger.exception(f"Error in social collection: {e}")
            result.errors.append(str(e))

        return result

    def _is_email(self, target: str) -> bool:
        """Check if target is an email address"""
        email_pattern = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
        return bool(email_pattern.match(target))

    def _is_social_url(self, target: str) -> bool:
        """Check if target is a social media URL"""
        for platform_patterns in self.platform_patterns.values():
            for pattern in platform_patterns:
                if re.search(pattern, target.lower()):
                    return True
        return False

    async def _search_username(self, username: str) -> List[Dict[str, Any]]:
        """Search for username across platforms"""
        entities = []

        # Base URLs for username checks
        platform_urls = {
            "twitter": f"https://twitter.com/{username}",
            "github": f"https://github.com/{username}",
            "reddit": f"https://reddit.com/user/{username}",
            "instagram": f"https://instagram.com/{username}",
        }

        for platform, url in platform_urls.items():
            try:
                await self._apply_rate_limit()

                response = await self.session.get(url, timeout=10)

                if response.status_code == 200:
                    # Check if it's a real profile (not a generic error page)
                    text = response.text.lower()
                    is_valid = (
                        f"@{username}".lower() in text or username.lower() in text
                    )

                    if is_valid or platform == "github":
                        entities.append(
                            self._create_entity(
                                entity_type="SOCIAL_PROFILE",
                                value=url,
                                risk_level=RiskLevel.INFO,
                                metadata={
                                    "platform": platform,
                                    "username": username,
                                    "status_code": response.status_code,
                                },
                            )
                        )

                        logger.info(f"Found {platform} profile for {username}")

                await asyncio.sleep(1)

            except Exception as e:
                logger.debug(f"Failed to check {platform} for {username}: {e}")

        # Create USERNAME entity
        if entities:
            entities.append(
                self._create_entity(
                    entity_type="USERNAME",
                    value=username,
                    risk_level=RiskLevel.INFO,
                    metadata={
                        "platforms_found": [e["metadata"]["platform"] for e in entities]
                    },
                )
            )

        return entities

    async def _extract_twitter_profile(self, username: str) -> List[Dict[str, Any]]:
        """Extract Twitter/X profile information"""
        entities = []

        try:
            # Note: Twitter API requires authentication
            # This uses basic scraping for public profiles
            url = f"https://twitter.com/{username}"

            response = await self.session.get(url, timeout=10)

            if response.status_code == 200:
                # Parse profile data from page
                soup = BeautifulSoup(response.text, "html.parser")

                # Note: Twitter uses dynamic content, so this is limited
                # Real implementation would use Tweepy with API keys
                entities.append(
                    self._create_entity(
                        entity_type="SOCIAL_PROFILE",
                        value=url,
                        risk_level=RiskLevel.INFO,
                        metadata={
                            "platform": "twitter",
                            "username": username,
                            "note": "Full profile data requires API access",
                        },
                    )
                )

        except Exception as e:
            logger.error(f"Error extracting Twitter profile: {e}")

        return entities

    async def _extract_github_profile(self, username: str) -> List[Dict[str, Any]]:
        """Extract GitHub profile information"""
        entities = []

        try:
            url = f"https://api.github.com/users/{username}"

            # Add GitHub token if available in environment
            headers = {"Accept": "application/vnd.github.v3+json"}

            import os

            github_token = os.getenv("GITHUB_TOKEN")
            if github_token:
                headers["Authorization"] = f"token {github_token}"

            response = await self.session.get(url, headers=headers, timeout=10)

            if response.status_code == 200:
                data = response.json()

                entities.append(
                    self._create_entity(
                        entity_type="SOCIAL_PROFILE",
                        value=data.get("html_url", ""),
                        risk_level=RiskLevel.INFO,
                        metadata={
                            "platform": "github",
                            "username": username,
                            "name": data.get("name", ""),
                            "bio": data.get("bio", ""),
                            "location": data.get("location", ""),
                            "public_repos": data.get("public_repos", 0),
                            "followers": data.get("followers", 0),
                            "following": data.get("following", 0),
                            "created_at": data.get("created_at", ""),
                            "company": data.get("company", ""),
                            "email": data.get("email", ""),
                            "blog": data.get("blog", ""),
                        },
                    )
                )

                # Create ORG entity if company is specified
                if data.get("company"):
                    entities.append(
                        self._create_entity(
                            entity_type="ORG",
                            value=data["company"].strip("@"),
                            risk_level=RiskLevel.INFO,
                            metadata={"source": "github_profile", "username": username},
                        )
                    )

                logger.info(f"Extracted GitHub profile for {username}")

        except Exception as e:
            logger.error(f"Error extracting GitHub profile: {e}")

        return entities

    async def _search_email(self, email: str) -> List[Dict[str, Any]]:
        """Search for email-associated accounts"""
        entities = []

        # Extract username from email
        username_part = email.split("@")[0]

        # Create EMAIL entity
        entities.append(
            self._create_entity(
                entity_type="EMAIL",
                value=email,
                risk_level=RiskLevel.INFO,
                metadata={
                    "source": "social_collector",
                    "extraction_method": "direct_input",
                },
            )
        )

        # Create USERNAME entity from email
        entities.append(
            self._create_entity(
                entity_type="USERNAME",
                value=username_part,
                risk_level=RiskLevel.INFO,
                metadata={"source": "email_derived", "email": email},
            )
        )

        # Try to find accounts with similar username
        try:
            import dns.resolver

            # Check MX records to get email provider
            domain = email.split("@")[1]
            try:
                mx_records = dns.resolver.resolve(domain, "MX")
                providers = [str(rdata.exchange).rstrip(".") for rdata in mx_records]

                entities[0]["metadata"]["email_provider"] = (
                    providers[0] if providers else None
                )

            except Exception:
                pass

        except ImportError:
            pass

        return entities

    async def _find_associated_accounts(self, email: str) -> List[Dict[str, Any]]:
        """Find accounts associated with email"""
        entities = []

        # Note: This would typically use username enumeration
        # Real implementation would check HaveIBeenPwned, social APIs, etc.

        username_part = email.split("@")[0]

        # Check common platforms
        platforms_to_check = [
            ("github", f"https://github.com/{username_part}"),
            ("reddit", f"https://reddit.com/user/{username_part}"),
        ]

        for platform, url in platforms_to_check:
            try:
                await self._apply_rate_limit()
                response = await self.session.get(url, timeout=10)

                if response.status_code == 200:
                    entities.append(
                        self._create_entity(
                            entity_type="USERNAME",
                            value=username_part,
                            risk_level=RiskLevel.INFO,
                            metadata={
                                "platform": platform,
                                "associated_email": email,
                                "profile_url": url,
                            },
                        )
                    )

                await asyncio.sleep(1)

            except Exception as e:
                logger.debug(f"Failed to check {platform}: {e}")

        return entities

    async def _extract_social_profile(self, url: str) -> List[Dict[str, Any]]:
        """Extract profile data from social URL"""
        entities = []

        try:
            response = await self.session.get(url, timeout=10)

            if response.status_code == 200:
                # Detect platform
                platform = "unknown"
                for plat, patterns in self.platform_patterns.items():
                    for pattern in patterns:
                        if re.search(pattern, url.lower()):
                            platform = plat
                            break

                # Extract username from URL
                if platform == "github":
                    username = url.rstrip("/").split("/")[-1]
                    entities.extend(await self._extract_github_profile(username))
                else:
                    entities.append(
                        self._create_entity(
                            entity_type="SOCIAL_PROFILE",
                            value=url,
                            risk_level=RiskLevel.INFO,
                            metadata={
                                "platform": platform,
                                "note": "Full profile data requires platform-specific API",
                            },
                        )
                    )

                logger.info(f"Extracted {platform} profile from {url}")

        except Exception as e:
            logger.error(f"Error extracting social profile: {e}")

        return entities

    async def _extract_social_connections(self, username: str) -> List[Dict[str, Any]]:
        """Extract social connections and relationships"""
        entities = []

        # Note: This would require authenticated API access
        # Placeholder for future implementation

        # GitHub - check organizations
        try:
            url = f"https://api.github.com/users/{username}/orgs"

            import os

            headers = {"Accept": "application/vnd.github.v3+json"}
            github_token = os.getenv("GITHUB_TOKEN")
            if github_token:
                headers["Authorization"] = f"token {github_token}"

            response = await self.session.get(url, headers=headers, timeout=10)

            if response.status_code == 200:
                orgs = response.json()

                for org in orgs:
                    entities.append(
                        self._create_entity(
                            entity_type="ORG",
                            value=org.get("login", ""),
                            risk_level=RiskLevel.INFO,
                            metadata={
                                "platform": "github",
                                "org_id": org.get("id"),
                                "description": org.get("description", ""),
                                "associated_username": username,
                            },
                        )
                    )

                    # Create relationship
                    entities.append(
                        {
                            "relationship_type": "MEMBER_OF",
                            "source": username,
                            "target": org.get("login", ""),
                            "metadata": {"platform": "github"},
                        }
                    )

                logger.info(f"Found {len(orgs)} GitHub orgs for {username}")

        except Exception as e:
            logger.debug(f"Error extracting GitHub orgs: {e}")

        return entities

    async def _analyze_posting_patterns(self, username: str) -> List[Dict[str, Any]]:
        """Analyze posting patterns and activity"""
        entities = []

        # Note: This would require access to posting history via APIs
        # Placeholder for future implementation

        # For now, create a basic activity profile
        entities.append(
            {
                "entity_type": "USERNAME",
                "value": username,
                "metadata": {
                    "activity_analysis": "Requires API access",
                    "note": "Post timing and frequency analysis requires authenticated API access",
                },
            }
        )

        return entities

    def normalize(self, raw_data: Any) -> List[Dict[str, Any]]:
        """Normalize raw social data"""
        return raw_data if isinstance(raw_data, list) else []

    def validate(self, data: Dict[str, Any]) -> bool:
        """Validate normalized data"""
        if isinstance(data, dict) and "relationship_type" in data:
            return True
        required_fields = ["entity_type", "value"]
        return all(field in data for field in required_fields)
