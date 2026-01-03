"""
ReconVault Collectors Module

Provides OSINT collectors for various data sources.
"""

from app.collectors.base_collector import (BaseCollector, CollectionResult,
                                           CollectorConfig, DataType,
                                           RiskLevel, UserAgentRotator)
from app.collectors.darkweb_collector import DarkWebCollector
from app.collectors.domain_collector import DomainCollector
from app.collectors.email_collector import EmailCollector
from app.collectors.geo_collector import GeoCollector
from app.collectors.ip_collector import IPCollector
from app.collectors.media_collector import MediaCollector
from app.collectors.social_collector import SocialCollector
from app.collectors.web_collector import WebCollector

__all__ = [
    # Base classes
    "BaseCollector",
    "CollectorConfig",
    "CollectionResult",
    "DataType",
    "RiskLevel",
    "UserAgentRotator",
    # Collectors
    "WebCollector",
    "SocialCollector",
    "DomainCollector",
    "IPCollector",
    "EmailCollector",
    "MediaCollector",
    "DarkWebCollector",
    "GeoCollector",
]


class CollectorFactory:
    """Factory for creating collectors based on data type"""

    @staticmethod
    def create_collector(data_type: DataType, config: CollectorConfig) -> BaseCollector:
        """
        Create appropriate collector for data type.

        Args:
            data_type: Type of data to collect
            config: Collector configuration

        Returns:
            Instance of appropriate collector

        Raises:
            ValueError: If data type not supported
        """
        collectors = {
            DataType.URL: WebCollector,
            DataType.DOMAIN: DomainCollector,
            DataType.IP: IPCollector,
            DataType.EMAIL: EmailCollector,
            DataType.USERNAME: SocialCollector,
            DataType.SOCIAL_PROFILE: SocialCollector,
            DataType.IMAGE: MediaCollector,
            DataType.AUDIO: MediaCollector,
            DataType.VIDEO: MediaCollector,
            DataType.TEXT: WebCollector,
        }

        collector_class = collectors.get(data_type)

        if not collector_class:
            raise ValueError(f"No collector available for data type: {data_type}")

        return collector_class(config)


def infer_data_type(target: str) -> DataType:
    """
    Infer data type from target string.

    Args:
        target: Target string (domain, email, IP, etc.)

    Returns:
        Inferred DataType
    """
    import re

    # Email
    email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    if re.match(email_pattern, target):
        return DataType.EMAIL

    # IP address
    ip_pattern = r"^(\d{1,3}\.){3}\d{1,3}$"
    if re.match(ip_pattern, target):
        return DataType.IP

    # URL
    if target.startswith(("http://", "https://")):
        return DataType.URL

    # Domain (has a dot, not IP, not email)
    if "." in target and not target.startswith(".") and "@" not in target:
        # Check if it might be a social URL
        if any(
            platform in target.lower()
            for platform in [
                "twitter.com",
                "github.com",
                "facebook.com",
                "instagram.com",
                "linkedin.com",
                "reddit.com",
            ]
        ):
            return DataType.SOCIAL_PROFILE
        return DataType.DOMAIN

    # Coordinates (lat,lon)
    coord_pattern = r"^-?\d+\.?\d*,-?\d+\.?\d*$"
    if re.match(coord_pattern, target):
        return DataType.TEXT  # Will be handled by geo collector

    # Default to username/text
    return DataType.USERNAME
