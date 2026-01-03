"""
Social OSINT Collector for ReconVault intelligence system.

This module provides social media intelligence gathering capabilities using
Tweepy, GitHub API, and web scraping for social platforms.
"""

import asyncio
import re
import json
from typing import Dict, List, Any, Optional
from urllib.parse import urlparse, urljoin
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import logging

# Optional imports - will handle if not available
try:
    import tweepy
    TWITTER_AVAILABLE = True
except ImportError:
    TWITTER_AVAILABLE = False
    tweepy = None

try:
    from github import Github
    GITHUB_AVAILABLE = True
except ImportError:
    GITHUB_AVAILABLE = False
    Github = None

from .base_collector import BaseCollector, CollectorConfig


class SocialCollector(BaseCollector):
    """Social OSINT collector for social media intelligence"""
    
    def __init__(self, config: CollectorConfig):
        super().__init__(config)
        self.logger = logging.getLogger(__name__)
        
        # Initialize API clients if credentials available
        self.twitter_client = None
        self.github_client = None
        
        try:
            from app.config import settings
            
            # Twitter API setup
            if TWITTER_AVAILABLE and hasattr(settings, 'TWITTER_API_KEY') and settings.TWITTER_API_KEY:
                auth = tweepy.OAuth1UserHandler(
                    settings.TWITTER_API_KEY,
                    settings.TWITTER_API_SECRET,
                    settings.TWITTER_ACCESS_TOKEN,
                    settings.TWITTER_ACCESS_TOKEN_SECRET
                )
                self.twitter_client = tweepy.API(auth, wait_on_rate_limit=True)
            
            # GitHub API setup
            if GITHUB_AVAILABLE and hasattr(settings, 'GITHUB_TOKEN') and settings.GITHUB_TOKEN:
                self.github_client = Github(settings.GITHUB_TOKEN)
                
        except Exception as e:
            self.logger.info(f"Social API clients not configured: {e}")
    
    async def collect(self) -> Dict[str, Any]:
        """Collect social media intelligence data"""
        self.logger.info(f"Starting social collection for target: {self.config.target}")
        
        results = {
            "target": self.config.target,
            "entities": [],
            "relationships": [],
            "metadata": {}
        }
        
        try:
            # Determine target type
            if self._is_email(self.config.target):
                # Email-based social search
                social_accounts = await self.search_email(self.config.target)
                results["entities"].extend(social_accounts)
                
            elif self._is_username(self.config.target):
                # Username-based search across platforms
                self.logger.info(f"Searching for username: {self.config.target}")
                
                # Search across different platforms
                platforms = ["twitter", "github", "facebook", "instagram", "linkedin"]
                
                for platform in platforms:
                    try:
                        platform_data = await self.search_username(self.config.target, platform)
                        results["entities"].extend(platform_data.get("entities", []))
                        results["relationships"].extend(platform_data.get("relationships", []))
                        results["metadata"][platform] = platform_data.get("metadata", {})
                    except Exception as e:
                        self.logger.warning(f"Error collecting from {platform}: {e}")
                        continue
                
                # Extract social connections
                connections = await self.extract_social_connections(self.config.target)
                results["relationships"].extend(connections)
                
                # Analyze posting patterns
                patterns = await self.analyze_posting_patterns(self.config.target)
                results["metadata"]["posting_patterns"] = patterns
                
            else:
                raise ValueError(f"Target {self.config.target} is not a valid email or username")
            
            return results
            
        except Exception as e:
            self.logger.error(f"Social collection failed: {e}")
            raise
    
    def _is_email(self, target: str) -> bool:
        """Check if target is an email address"""
        import re
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[A-Z|a-z]{2,}$'
        return bool(re.match(email_pattern, target))
    
    def _is_username(self, target: str) -> bool:
        """Check if target is a username"""
        # Username pattern: alphanumeric, underscores, hyphens, 3-30 chars
        import re
        username_pattern = r'^[a-zA-Z0-9_\-]{3,30}$'
        return bool(re.match(username_pattern, target))
    
    async def search_username(self, username: str, platform: str = "all") -> Dict[str, Any]:
        """Search for username across social platforms"""
        results = {
            "entities": [],
            "relationships": [],
            "metadata": {"platform": platform, "username": username}
        }
        
        if platform in ["all", "twitter"]:
            twitter_data = await self.extract_twitter_profile(username)
            if twitter_data:
                results["entities"].extend(twitter_data.get("entities", []))
                results["relationships"].extend(twitter_data.get("relationships", []))
                results["metadata"]["twitter"] = twitter_data.get("metadata", {})
        
        if platform in ["all", "github"] and self.github_client:
            github_data = await self.extract_github_profile(username)
            if github_data:
                results["entities"].extend(github_data.get("entities", []))
                results["relationships"].extend(github_data.get("relationships", []))
                results["metadata"]["github"] = github_data.get("metadata", {})
        
        if platform in ["all", "facebook"]:
            facebook_data = await self._extract_facebook_profile(username)
            if facebook_data:
                results["entities"].extend(facebook_data.get("entities", []))
                results["metadata"]["facebook"] = facebook_data.get("metadata", {})
        
        if platform in ["all", "instagram"]:
            instagram_data = await self._extract_instagram_profile(username)
            if instagram_data:
                results["entities"].extend(instagram_data.get("entities", []))
                results["metadata"]["instagram"] = instagram_data.get("metadata", {})
        
        return results
    
    async def extract_twitter_profile(self, username: str) -> Optional[Dict[str, Any]]:
        """Extract Twitter/X profile information"""
        if not self.twitter_client:
            self.logger.warning("Twitter client not configured")
            return None
        
        try:
            self.logger.debug(f"Extracting Twitter profile for: {username}")
            
            # Search for user
            users = self.twitter_client.search_users(q=username, count=1)
            
            if not users:
                self.logger.info(f"No Twitter user found for username: {username}")
                return None
            
            user = users[0]
            screen_name = user.screen_name.lower()
            
            # Get user timeline for analysis
            tweets = self.twitter_client.user_timeline(screen_name=screen_name, count=100)
            
            # Analyze tweets
            tweet_data = {
                "total_tweets": user.statuses_count,
                "followers_count": user.followers_count,
                "following_count": user.friends_count,
                "listed_count": user.listed_count,
                "favorites_count": user.favourites_count,
                "account_age_days": (datetime.now() - user.created_at).days,
                "verified": user.verified,
                "protected": user.protected,
                "location": user.location,
                "default_profile": user.default_profile,
                "default_profile_image": user.default_profile_image,
                "description_length": len(user.description) if user.description else 0,
                "has_url": bool(user.url),
                "has_location": bool(user.location)
            }
            
            # Analyze tweet patterns
            if tweets:
                # Time zone analysis
                tweet_hours = [tweet.created_at.hour for tweet in tweets]
                tweet_days = [tweet.created_at.weekday() for tweet in tweets]
                
                tweet_data.update({
                    "avg_tweets_per_day": len(tweets) / max(1, user.account_age_days),
                    "common_posting_hours": self._get_common_hours(tweet_hours),
                    "common_posting_days": self._get_common_days(tweet_days),
                    "retweet_ratio": sum(1 for t in tweets if hasattr(t, 'retweeted_status')) / len(tweets),
                    "reply_ratio": sum(1 for t in tweets if t.in_reply_to_status_id) / len(tweets),
                    "media_ratio": sum(1 for t in tweets if 'media' in t.entities) / len(tweets)
                })
            
            entities = [
                {
                    "value": f"@{screen_name}",
                    "type": "SOCIAL_PROFILE",
                    "platform": "twitter",
                    "metadata": {
                        "username": screen_name,
                        "name": user.name,
                        **tweet_data,
                        "profile_image": user.profile_image_url_https,
                        "banner_image": getattr(user, 'profile_banner_url', None),
                        "collected_at": datetime.utcnow().isoformat()
                    },
                    "source": "twitter_api"
                }
            ]
            
            # Add email entity if available
            if hasattr(user, 'email') and user.email:
                entities.append({
                    "value": user.email,
                    "type": "EMAIL",
                    "platform": "twitter",
                    "metadata": {
                        "twitter_username": screen_name,
                        "verified": user.verified
                    },
                    "source": "twitter_api"
                })
                
                # Add relationship between Twitter profile and email
                relationships = [
                    {
                        "type": "ASSOCIATES_WITH",
                        "source_value": f"@{screen_name}",
                        "source_type": "SOCIAL_PROFILE",
                        "target_value": user.email,
                        "target_type": "EMAIL",
                        "metadata": {
                            "platform": "twitter",
                            "strength": 0.9,
                            "verified": user.verified
                        }
                    }
                ]
            else:
                relationships = []
            
            return {
                "entities": entities,
                "relationships": relationships,
                "metadata": {
                    "platform": "twitter",
                    "username": screen_name,
                    "api_used": True
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error extracting Twitter profile for {username}: {e}")
            return None
    
    async def extract_github_profile(self, username: str) -> Optional[Dict[str, Any]]:
        """Extract GitHub profile information"""
        if not self.github_client:
            self.logger.warning("GitHub client not configured")
            return None
        
        try:
            self.logger.debug(f"Extracting GitHub profile for: {username}")
            
            # Get user
            user = self.github_client.get_user(username)
            
            # Get repositories
            repos = list(user.get_repos())[:100]  # Limit to 100 repos
            
            # Analyze repositories
            languages = {}
            total_stars = 0
            total_forks = 0
            
            for repo in repos:
                if not repo.fork:  # Skip forks
                    # Count languages
                    if repo.language:
                        languages[repo.language] = languages.get(repo.language, 0) + 1
                    
                    total_stars += repo.stargazers_count
                    total_forks += repo.forks_count
            
            # Get organizations
            orgs = list(user.get_orgs())
            
            profile_data = {
                "username": user.login,
                "name": user.name,
                "email": user.email,
                "company": user.company,
                "location": user.location,
                "bio": user.bio,
                "blog": user.blog,
                "followers": user.followers,
                "following": user.following,
                "public_repos": user.public_repos,
                "created_at": user.created_at.isoformat() if user.created_at else None,
                "updated_at": user.updated_at.isoformat() if user.updated_at else None,
                "hireable": user.hireable,
                "site_admin": user.site_admin,
                "account_age_days": (datetime.now() - user.created_at).days if user.created_at else 0,
                "languages": dict(sorted(languages.items(), key=lambda x: x[1], reverse=True)),
                "top_languages": list(languages.keys())[:5],
                "total_stars": total_stars,
                "total_forks": total_forks,
                "organization_count": len(orgs)
            }
            
            entities = [
                {
                    "value": f"@{user.login}",
                    "type": "SOCIAL_PROFILE",
                    "platform": "github",
                    "metadata": profile_data,
                    "source": "github_api"
                }
            ]
            
            # Add email entity if available
            relationships = []
            if user.email:
                entities.append({
                    "value": user.email,
                    "type": "EMAIL",
                    "platform": "github",
                    "metadata": {
                        "github_username": user.login,
                        "public": True
                    },
                    "source": "github_api"
                })
                
                relationships.append({
                    "type": "ASSOCIATES_WITH",
                    "source_value": f"@{user.login}",
                    "source_type": "SOCIAL_PROFILE",
                    "target_value": user.email,
                    "target_type": "EMAIL",
                    "metadata": {
                        "platform": "github",
                        "strength": 1.0,
                        "public": True
                    }
                })
            
            # Add organization entities and relationships
            for org in orgs:
                entities.append({
                    "value": org.login,
                    "type": "ORG",
                    "platform": "github",
                    "metadata": {
                        "name": org.name,
                        "description": org.description,
                        "github_url": org.html_url
                    },
                    "source": "github_api"
                })
                
                relationships.append({
                    "type": "MEMBER_OF",
                    "source_value": f"@{user.login}",
                    "source_type": "SOCIAL_PROFILE",
                    "target_value": org.login,
                    "target_type": "ORG",
                    "metadata": {
                        "platform": "github",
                        "role": "member"
                    }
                })
            
            return {
                "entities": entities,
                "relationships": relationships,
                "metadata": {
                    "platform": "github",
                    "username": user.login,
                    "api_used": True
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error extracting GitHub profile for {username}: {e}")
            return None
    
    async def _extract_facebook_profile(self, username: str) -> Optional[Dict[str, Any]]:
        """Extract Facebook profile information (web scraping)"""
        try:
            # Note: Facebook requires authentication for most data
            # This is a simplified implementation
            profile_url = f"https://www.facebook.com/{username}"
            
            # Try to access public profile
            response = self._make_request(profile_url, timeout=15)
            
            if response.status_code == 200:
                # Parse basic information from public profile
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Extract title (often contains name)
                title = soup.title.string if soup.title else ""
                
                entities = [{
                    "value": f"fb:{username}",
                    "type": "SOCIAL_PROFILE",
                    "platform": "facebook",
                    "metadata": {
                        "username": username,
                        "profile_url": profile_url,
                        "page_title": title,
                        "visibility": "public",
                        "collected_at": datetime.utcnow().isoformat()
                    },
                    "source": "facebook_scraper"
                }]
                
                return {
                    "entities": entities,
                    "metadata": {
                        "platform": "facebook",
                        "method": "web_scraping"
                    }
                }
            
        except Exception as e:
            self.logger.error(f"Error extracting Facebook profile for {username}: {e}")
        
        return None
    
    async def _extract_instagram_profile(self, username: str) -> Optional[Dict[str, Any]]:
        """Extract Instagram profile information (web scraping)"""
        try:
            profile_url = f"https://www.instagram.com/{username}/"
            
            response = self._make_request(profile_url, timeout=15)
            
            if response.status_code == 200:
                # Parse JSON data from page
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Look for JSON data in script tags
                scripts = soup.find_all('script', type='application/ld+json')
                
                profile_data = {}
                for script in scripts:
                    try:
                        data = json.loads(script.string)
                        if '@type' in data and data['@type'] == 'Person':
                            profile_data.update(data)
                            break
                    except:
                        continue
                
                entities = [{
                    "value": f"ig:{username}",
                    "type": "SOCIAL_PROFILE",
                    "platform": "instagram",
                    "metadata": {
                        "username": username,
                        "profile_url": profile_url,
                        "name": profile_data.get('name', ''),
                        "description": profile_data.get('description', ''),
                        "visibility": "public" if soup.find('h2') else "private",
                        "collected_at": datetime.utcnow().isoformat()
                    },
                    "source": "instagram_scraper"
                }]
                
                return {
                    "entities": entities,
                    "metadata": {
                        "platform": "instagram",
                        "method": "web_scraping"
                    }
                }
            
        except Exception as e:
            self.logger.error(f"Error extracting Instagram profile for {username}: {e}")
        
        return None
    
    async def search_email(self, email: str) -> List[Dict[str, Any]]:
        """Search for social accounts using email address"""
        entities = []
        
        try:
            # Extract username from email
            username = email.split('@')[0]
            
            # Search for this username across platforms
            if self._is_username(username):
                social_results = await self.search_username(username, "all")
                entities.extend(social_results.get("entities", []))
        
        except Exception as e:
            self.logger.error(f"Error searching email {email}: {e}")
        
        return entities
    
    async def extract_social_connections(self, username: str) -> List[Dict[str, Any]]:
        """Extract social connections and relationships"""
        relationships = []
        
        try:
            # This would analyze social graphs from various platforms
            # For now, return placeholder relationships
            
            # Check if we collected related entities
            # In a full implementation, this would analyze:
            # - GitHub followers/following
            # - Twitter followers/following
            # - LinkedIn connections (if accessible)
            
            self.logger.debug(f"Extracting social connections for: {username}")
            
        except Exception as e:
            self.logger.error(f"Error extracting social connections for {username}: {e}")
        
        return relationships
    
    async def analyze_posting_patterns(self, username: str) -> Dict[str, Any]:
        """Analyze posting patterns and activity"""
        patterns = {
            "username": username,
            "timezone_hints": [],
            "active_hours": [],
            "activity_frequency": "unknown",
            "platforms": []
        }
        
        try:
            # This would analyze posting times across platforms
            # to infer timezone and activity patterns
            
            self.logger.debug(f"Analyzing posting patterns for: {username}")
            
        except Exception as e:
            self.logger.error(f"Error analyzing posting patterns for {username}: {e}")
        
        return patterns
    
    def _get_common_hours(self, hours: list) -> list:
        """Get most common posting hours"""
        from collections import Counter
        hour_counts = Counter(hours)
        return [hour for hour, count in hour_counts.most_common(3)]
    
    def _get_common_days(self, days: list) -> list:
        """Get most common posting days"""
        from collections import Counter
        day_counts = Counter(days)
        day_names = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        return [day_names[day] for day, count in day_counts.most_common(3)]
    
    def normalize(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Normalize social collection results"""
        entities = []
        
        if isinstance(data, dict):
            if "entities" in data:
                # Already normalized format
                return data["entities"]
            
            # Handle direct entity data
            target = data.get("target", self.config.target)
            platform = data.get("platform", "unknown")
            
            if target:
                entities.append({
                    "value": target,
                    "type": "SOCIAL_PROFILE",
                    "platform": platform,
                    "metadata": data.get("metadata", {}),
                    "source": data.get("source", "social_collector")
                })
        
        return entities