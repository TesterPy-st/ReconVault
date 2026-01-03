"""
ReconVault Collectors Module - Phase 1: Complete OSINT Intelligence Pipeline

This module contains comprehensive OSINT collectors for various data sources
including web scraping, social media, DNS/WHOIS, dark web, geolocation,
and media analysis capabilities.

Implemented Collectors:
- BaseCollector: Abstract base class with rate limiting and ethics compliance
- WebCollector: Web scraping with Scrapy/Selenium integration
- SocialCollector: Social media intelligence (Twitter, GitHub, etc.)
- DomainCollector: WHOIS, DNS enumeration, and domain reputation
- IPCollector: IP geolocation, port scanning, and threat intel
- EmailCollector: Email verification, breach checking, and OSINT
- MediaCollector: Image/audio analysis with ML-based extraction
- DarkWebCollector: Tor-based dark web intelligence gathering
- GeoCollector: Geospatial intelligence and location analysis
"""

from .base_collector import BaseCollector, CollectorConfig
from .web_collector import WebCollector
from .social_collector import SocialCollector
from .domain_collector import DomainCollector
from .ip_collector import IPCollector
from .email_collector import EmailCollector
from .media_collector import MediaCollector
from .darkweb_collector import DarkWebCollector
from .geo_collector import GeoCollector

__all__ = [
    'BaseCollector',
    'CollectorConfig', 
    'WebCollector',
    'SocialCollector',
    'DomainCollector',
    'IPCollector',
    'EmailCollector',
    'MediaCollector',
    'DarkWebCollector',
    'GeoCollector'
]
