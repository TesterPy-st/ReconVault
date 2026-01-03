"""
Reverse OSINT Detector Service

Detects tracking, surveillance, and data collection capabilities.
"""

import asyncio
import re
from typing import Any, Dict, List, Optional

from bs4 import BeautifulSoup
from loguru import logger

from app.collectors.base_collector import RiskLevel


class ReverseOSINTService:
    """
    Service for detecting reverse OSINT and tracking.

    Handles:
    - Browser fingerprinting detection
    - Tracking pixel detection
    - Analytics service detection
    - Tracking network detection
    - CDN provider detection
    """

    # Known tracking domains
    TRACKING_DOMAINS = {
        "google-analytics.com": "Google Analytics",
        "googletagmanager.com": "Google Tag Manager",
        "googleadservices.com": "Google Ads",
        "doubleclick.net": "Google DoubleClick",
        "facebook.com/tr": "Facebook Pixel",
        "connect.facebook.net": "Facebook Connect",
        "stats.wp.com": "WordPress Stats",
        "pixel.wp.com": "WordPress Pixel",
        "analytics.twitter.com": "Twitter Analytics",
        "t.co": "Twitter Tracking",
        "hotjar.com": "Hotjar",
        "mixpanel.com": "Mixpanel",
        "segment.com": "Segment",
        "amplitude.com": "Amplitude",
        "fullstory.com": "FullStory",
        "mouseflow.com": "Mouseflow",
        "inspectlet.com": "Inspectlet",
        "crazyegg.com": "Crazy Egg",
        "optimizely.com": "Optimizely",
        "chartbeat.com": "Chartbeat",
        "pingdom.net": "Pingdom",
        "newrelic.com": "New Relic",
        "datadoghq.com": "DataDog",
        "bugsnag.com": "Bugsnag",
        "sentry.io": "Sentry",
        "logrocket.com": "LogRocket",
    }

    # Ad networks and data brokers
    AD_NETWORKS = {
        "ad.doubleclick.net": "Google Ad Network",
        "googleads.g.doubleclick.net": "Google Ads",
        "pagead2.googlesyndication.com": "Google AdSense",
        "amazon-adsystem.com": "Amazon Ads",
        "ads-twitter.com": "Twitter Ads",
        "criteo.com": "Criteo",
        "taboola.com": "Taboola",
        "outbrain.com": "Outbrain",
        "adnxs.com": "AppNexus",
        "rubiconproject.com": "Rubicon Project",
        "pubmatic.com": "PubMatic",
        "indexww.com": "Index Exchange",
        "triplelift.com": "TripleLift",
        "openx.net": "OpenX",
    }

    # CDN providers
    CDN_PROVIDERS = {
        "cloudflare.net": "Cloudflare",
        "cloudflare.com": "Cloudflare",
        "akamai.net": "Akamai",
        "akamai.com": "Akamai",
        "akamaized.net": "Akamai",
        "fastly.net": "Fastly",
        "fastly.com": "Fastly",
        "cdn.jsdelivr.net": "jsDelivr",
        "cdnjs.cloudflare.com": "Cloudflare CDN",
        "unpkg.com": "unpkg",
        "cdnjs.com": "cdnjs",
        "bootstrapcdn.com": "Bootstrap CDN",
    }

    # Common tracking scripts/patterns
    TRACKING_PATTERNS = {
        "google_analytics": r"gtag\(['\"]",
        "facebook_pixel": r"fbq\(['\"]",
        "hotjar": r"hj\.",
        "mixpanel": r"mixpanel\.",
        "segment": r"analytics\.track\(",
        "amplitude": r"amplitude\.getInstance\(\)",
        "fullstory": r"FS\.",
        "chartbeat": r"CB",
    }

    def __init__(self):
        self.tracking_domains = set(self.TRACKING_DOMAINS.keys())
        self.ad_networks = set(self.AD_NETWORKS.keys())
        self.cdn_providers = set(self.CDN_PROVIDERS.keys())

    async def fingerprint_browser(self, url: str, html: str) -> Dict[str, Any]:
        """
        Detect browser fingerprinting capabilities.

        Args:
            url: Target URL
            html: HTML content

        Returns:
            Fingerprinting detection results
        """
        logger.info(f"Detecting browser fingerprinting for {url}")

        result = {
            "url": url,
            "fingerprinting_detected": False,
            "fingerprinting_techniques": [],
            "risk_score": 0,
        }

        try:
            soup = BeautifulSoup(html, "html.parser")

            # Check for canvas fingerprinting
            canvas_scripts = soup.find_all(
                "script", string=re.compile(r"canvas|getContext|toDataURL", re.I)
            )
            if canvas_scripts:
                result["fingerprinting_detected"] = True
                result["fingerprinting_techniques"].append("canvas_fingerprinting")
                result["risk_score"] += 30
                logger.warning("Canvas fingerprinting detected")

            # Check for WebGL fingerprinting
            webgl_scripts = soup.find_all(
                "script", string=re.compile(r"WebGL|createWebGL|getShader", re.I)
            )
            if webgl_scripts:
                result["fingerprinting_detected"] = True
                result["fingerprinting_techniques"].append("webgl_fingerprinting")
                result["risk_score"] += 30
                logger.warning("WebGL fingerprinting detected")

            # Check for audio fingerprinting
            audio_scripts = soup.find_all(
                "script", string=re.compile(r"AudioContext|createOscillator", re.I)
            )
            if audio_scripts:
                result["fingerprinting_detected"] = True
                result["fingerprinting_techniques"].append("audio_fingerprinting")
                result["risk_score"] += 25
                logger.warning("Audio fingerprinting detected")

            # Check for font fingerprinting
            font_scripts = soup.find_all(
                "script", string=re.compile(r"document\.fonts|FontFace", re.I)
            )
            if font_scripts:
                result["fingerprinting_detected"] = True
                result["fingerprinting_techniques"].append("font_fingerprinting")
                result["risk_score"] += 20
                logger.warning("Font fingerprinting detected")

            # Check for battery/RTC APIs (can be used for fingerprinting)
            api_scripts = soup.find_all(
                "script", string=re.compile(r"getBattery|RTCDataChannel", re.I)
            )
            if api_scripts:
                result["fingerprinting_detected"] = True
                result["fingerprinting_techniques"].append("api_fingerprinting")
                result["risk_score"] += 15
                logger.warning("API fingerprinting detected")

            result["risk_score"] = min(result["risk_score"], 100)

        except Exception as e:
            logger.error(f"Error detecting browser fingerprinting: {e}")

        return result

    async def detect_tracking_pixels(self, url: str, html: str) -> List[Dict[str, Any]]:
        """
        Identify tracking pixels in page.

        Args:
            url: Target URL
            html: HTML content

        Returns:
            List of detected tracking pixels
        """
        logger.info(f"Detecting tracking pixels for {url}")

        tracking_pixels = []

        try:
            soup = BeautifulSoup(html, "html.parser")

            # Find all images
            for img in soup.find_all("img"):
                src = img.get("src", "")
                width = img.get("width", "")
                height = img.get("height", "")

                # Check for 1x1 pixel images (common for tracking)
                if (width == "1" and height == "1") or src.endswith(".gif"):
                    # Check if it's from known tracking domain
                    tracking_service = None
                    for domain, service in self.TRACKING_DOMAINS.items():
                        if domain in src:
                            tracking_service = service
                            break

                    if tracking_service:
                        tracking_pixels.append(
                            {
                                "type": "tracking_pixel",
                                "src": src,
                                "service": tracking_service,
                                "risk_level": RiskLevel.MEDIUM.value,
                            }
                        )
                        logger.warning(f"Found tracking pixel from {tracking_service}")

        except Exception as e:
            logger.error(f"Error detecting tracking pixels: {e}")

        return tracking_pixels

    async def detect_analytics(self, url: str, html: str) -> List[Dict[str, Any]]:
        """
        Detect analytics services.

        Args:
            url: Target URL
            html: HTML content

        Returns:
            List of detected analytics services
        """
        logger.info(f"Detecting analytics for {url}")

        analytics_services = []

        try:
            # Check script sources
            soup = BeautifulSoup(html, "html.parser")

            for script in soup.find_all("script", src=True):
                src = script["src"]

                # Check against known tracking domains
                for domain, service in self.TRACKING_DOMAINS.items():
                    if domain in src:
                        analytics_services.append(
                            {
                                "type": "analytics",
                                "service": service,
                                "domain": domain,
                                "src": src,
                                "risk_level": RiskLevel.LOW.value,
                            }
                        )
                        logger.info(f"Found analytics: {service}")
                        break

            # Also check script content for tracking patterns
            for script in soup.find_all("script"):
                if script.string:
                    for pattern_name, pattern in self.TRACKING_PATTERNS.items():
                        if re.search(pattern, script.string):
                            analytics_services.append(
                                {
                                    "type": "analytics",
                                    "service": pattern_name,
                                    "method": "inline_script",
                                    "risk_level": RiskLevel.LOW.value,
                                }
                            )
                            logger.info(f"Found {pattern_name} via inline script")

        except Exception as e:
            logger.error(f"Error detecting analytics: {e}")

        return analytics_services

    async def find_tracking_networks(self, url: str, html: str) -> List[Dict[str, Any]]:
        """
        Find ad networks and data brokers.

        Args:
            url: Target URL
            html: HTML content

        Returns:
            List of detected tracking networks
        """
        logger.info(f"Finding tracking networks for {url}")

        tracking_networks = []

        try:
            soup = BeautifulSoup(html, "html.parser")

            for script in soup.find_all("script", src=True):
                src = script["src"]

                # Check against ad networks
                for domain, network in self.AD_NETWORKS.items():
                    if domain in src:
                        tracking_networks.append(
                            {
                                "type": "ad_network",
                                "network": network,
                                "domain": domain,
                                "src": src,
                                "risk_level": RiskLevel.MEDIUM.value,
                            }
                        )
                        logger.warning(f"Found ad network: {network}")

            # Also check iframes
            for iframe in soup.find_all("iframe", src=True):
                src = iframe["src"]

                for domain, network in self.AD_NETWORKS.items():
                    if domain in src:
                        tracking_networks.append(
                            {
                                "type": "ad_network",
                                "network": network,
                                "domain": domain,
                                "src": src,
                                "method": "iframe",
                                "risk_level": RiskLevel.MEDIUM.value,
                            }
                        )

        except Exception as e:
            logger.error(f"Error finding tracking networks: {e}")

        return tracking_networks

    async def identify_cdn(self, url: str, html: str) -> Dict[str, Any]:
        """
        Identify CDN provider.

        Args:
            url: Target URL
            html: HTML content

        Returns:
            CDN information
        """
        logger.info(f"Identifying CDN for {url}")

        result = {"url": url, "cdn_provider": None, "cdn_domains": []}

        try:
            soup = BeautifulSoup(html, "html.parser")

            # Check script sources
            for script in soup.find_all("script", src=True):
                src = script["src"]

                for domain, provider in self.CDN_PROVIDERS.items():
                    if domain in src:
                        if result["cdn_provider"] is None:
                            result["cdn_provider"] = provider
                        result["cdn_domains"].append(
                            {
                                "domain": domain,
                                "provider": provider,
                                "src": src,
                            }
                        )
                        break

            # Check link tags for CSS
            for link in soup.find_all("link", href=True):
                href = link["href"]

                for domain, provider in self.CDN_PROVIDERS.items():
                    if domain in href:
                        if result["cdn_provider"] is None:
                            result["cdn_provider"] = provider
                        result["cdn_domains"].append(
                            {
                                "domain": domain,
                                "provider": provider,
                                "href": href,
                            }
                        )
                        break

            if result["cdn_provider"]:
                logger.info(f"Detected CDN: {result['cdn_provider']}")

        except Exception as e:
            logger.error(f"Error identifying CDN: {e}")

        return result

    async def analyze_reverse_osint(
        self,
        url: str,
        html: Optional[str] = None,
        session=None,
    ) -> Dict[str, Any]:
        """
        Perform comprehensive reverse OSINT analysis.

        Args:
            url: Target URL
            html: HTML content (if already fetched)
            session: HTTP session (if not provided, will fetch)

        Returns:
            Complete reverse OSINT analysis
        """
        logger.info(f"Performing reverse OSINT analysis for {url}")

        # Fetch HTML if not provided
        if html is None and session:
            try:
                response = await session.get(url)
                html = response.text
            except Exception as e:
                logger.error(f"Failed to fetch {url}: {e}")
                return {"error": str(e)}

        if not html:
            return {"error": "No HTML content provided"}

        # Run all detections
        results = await asyncio.gather(
            self.fingerprint_browser(url, html),
            self.detect_tracking_pixels(url, html),
            self.detect_analytics(url, html),
            self.find_tracking_networks(url, html),
            self.identify_cdn(url, html),
            return_exceptions=True,
        )

        fingerprinting = results[0] if not isinstance(results[0], Exception) else {}
        tracking_pixels = results[1] if not isinstance(results[1], Exception) else []
        analytics = results[2] if not isinstance(results[2], Exception) else []
        tracking_networks = results[3] if not isinstance(results[3], Exception) else []
        cdn = results[4] if not isinstance(results[4], Exception) else {}

        # Calculate overall risk
        risk_score = 0
        if fingerprinting.get("risk_score", 0) > 0:
            risk_score += fingerprinting["risk_score"]
        risk_score += len(tracking_pixels) * 10
        risk_score += len(analytics) * 5
        risk_score += len(tracking_networks) * 15

        risk_score = min(risk_score, 100)

        # Determine risk level
        if risk_score >= 60:
            risk_level = RiskLevel.HIGH
        elif risk_score >= 30:
            risk_level = RiskLevel.MEDIUM
        else:
            risk_level = RiskLevel.LOW

        return {
            "url": url,
            "overall_risk_score": risk_score,
            "risk_level": risk_level.value,
            "fingerprinting": fingerprinting,
            "tracking_pixels": tracking_pixels,
            "analytics": analytics,
            "tracking_networks": tracking_networks,
            "cdn": cdn,
            "summary": {
                "total_trackers": (
                    len(tracking_pixels) + len(analytics) + len(tracking_networks)
                ),
                "fingerprinting_detected": fingerprinting.get(
                    "fingerprinting_detected", False
                ),
                "recommendation": self._get_recommendation(risk_score),
            },
        }

    def _get_recommendation(self, risk_score: int) -> str:
        """Get risk recommendation based on score"""
        if risk_score >= 60:
            return "High tracking/surveillance detected - consider using privacy tools"
        elif risk_score >= 30:
            return "Moderate tracking detected - use ad blockers and privacy extensions"
        else:
            return (
                "Low tracking detected - standard privacy measures should be sufficient"
            )
