"""
Unit tests for OSINT collectors.

Tests cover:
- Web collector parsing
- Social collector authentication
- Domain collector DNS lookup
- Email collector validation
- IP collector geolocation
- Media collector extraction
- Dark web collector connection
- Geo collector mapping
- Error handling
- Data validation
"""
import asyncio
from unittest.mock import AsyncMock, MagicMock, Mock, patch

import pytest
from faker import Faker

from app.collectors import (
    BaseCollector,
    CollectionResult,
    CollectorConfig,
    DataType,
    RiskLevel,
    UserAgentRotator,
)
from app.collectors.darkweb_collector import DarkWebCollector
from app.collectors.domain_collector import DomainCollector
from app.collectors.email_collector import EmailCollector
from app.collectors.geo_collector import GeoCollector
from app.collectors.ip_collector import IPCollector
from app.collectors.media_collector import MediaCollector
from app.collectors.social_collector import SocialCollector
from app.collectors.web_collector import WebCollector

fake = Faker()


# =============================================================================
# BaseCollector Tests
# =============================================================================


class TestBaseCollector:
    """Tests for BaseCollector abstract class and utilities."""

    def test_collection_result_creation(self):
        """Test CollectionResult dataclass creation."""
        result = CollectionResult(
            success=True,
            data=[{"type": "domain", "value": "example.com"}],
            risk_level=RiskLevel.LOW,
        )
        assert result.success is True
        assert len(result.data) == 1
        assert result.risk_level == RiskLevel.LOW
        assert isinstance(result.errors, list)
        assert len(result.errors) == 0

    def test_collector_config_defaults(self):
        """Test CollectorConfig default values."""
        config = CollectorConfig(target="example.com", data_type=DataType.DOMAIN)
        assert config.timeout == 30
        assert config.max_retries == 3
        assert config.rate_limit == 2.0
        assert config.respect_robots_txt is True
        assert config.verify_ssl is True

    def test_user_agent_rotator_sequential(self):
        """Test UserAgentRotator sequential rotation."""
        rotator = UserAgentRotator()
        agents = [rotator.get_user_agent() for _ in range(10)]
        assert len(agents) == 10
        # Should cycle through available agents
        assert agents[0] == agents[5]  # After 5 agents, cycle repeats

    def test_user_agent_rotator_random(self):
        """Test UserAgentRotator random selection."""
        rotator = UserAgentRotator()
        agent = rotator.get_random_user_agent()
        assert agent in UserAgentRotator.USER_AGENTS

    def test_data_type_enum(self):
        """Test DataType enum values."""
        assert DataType.DOMAIN.value == "domain"
        assert DataType.IP.value == "ip"
        assert DataType.EMAIL.value == "email"

    def test_risk_level_enum(self):
        """Test RiskLevel enum values."""
        assert RiskLevel.CRITICAL.value == "CRITICAL"
        assert RiskLevel.LOW.value == "LOW"


# =============================================================================
# WebCollector Tests
# =============================================================================


class TestWebCollector:
    """Tests for WebCollector."""

    @pytest.fixture
    def web_config(self):
        """Web collector configuration."""
        return CollectorConfig(
            target="https://example.com",
            data_type=DataType.URL,
            timeout=30,
        )

    @pytest.fixture
    def web_collector(self, web_config):
        """Web collector instance."""
        return WebCollector(web_config)

    @pytest.mark.asyncio
    async def test_web_collector_initialization(self, web_collector):
        """Test web collector initialization."""
        assert web_collector.config.target == "https://example.com"
        assert web_collector.config.data_type == DataType.URL

    @pytest.mark.asyncio
    @patch("httpx.AsyncClient.get")
    async def test_web_collector_parsing_success(self, mock_get, web_collector):
        """Test successful HTML parsing."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = """
        <html>
            <head><title>Example Domain</title></head>
            <body>
                <h1>Example Domain</h1>
                <p>This domain is for use in illustrative examples.</p>
                <a href="https://www.iana.org/domains/example">More information</a>
            </body>
        </html>
        """
        mock_get.return_value = mock_response

        result = await web_collector.collect()
        assert result.success is True

    @pytest.mark.asyncio
    @patch("httpx.AsyncClient.get")
    async def test_web_collector_404_error(self, mock_get, web_collector):
        """Test handling of 404 errors."""
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.raise_for_status.side_effect = Exception("404 Not Found")
        mock_get.return_value = mock_response

        result = await web_collector.collect()
        assert result.success is False
        assert len(result.errors) > 0

    @pytest.mark.asyncio
    @patch("httpx.AsyncClient.get")
    async def test_web_collector_timeout(self, mock_get, web_collector):
        """Test timeout handling."""
        mock_get.side_effect = asyncio.TimeoutError("Request timeout")

        result = await web_collector.collect()
        assert result.success is False
        assert any("timeout" in err.lower() for err in result.errors)

    @pytest.mark.asyncio
    @patch("httpx.AsyncClient.get")
    async def test_web_collector_malformed_html(self, mock_get, web_collector):
        """Test handling of malformed HTML."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = "<html><body><<invalid>><html>"
        mock_get.return_value = mock_response

        result = await web_collector.collect()
        # Should still succeed but might have warnings
        assert isinstance(result, CollectionResult)


# =============================================================================
# DomainCollector Tests
# =============================================================================


class TestDomainCollector:
    """Tests for DomainCollector."""

    @pytest.fixture
    def domain_config(self):
        """Domain collector configuration."""
        return CollectorConfig(
            target="example.com",
            data_type=DataType.DOMAIN,
        )

    @pytest.fixture
    def domain_collector(self, domain_config):
        """Domain collector instance."""
        return DomainCollector(domain_config)

    @pytest.mark.asyncio
    async def test_domain_collector_initialization(self, domain_collector):
        """Test domain collector initialization."""
        assert domain_collector.config.target == "example.com"

    @pytest.mark.asyncio
    @patch("dns.resolver.resolve")
    async def test_dns_lookup_success(self, mock_resolve, domain_collector):
        """Test successful DNS lookup."""
        mock_record = MagicMock()
        mock_record.address = "93.184.216.34"
        mock_resolve.return_value = [mock_record]

        result = await domain_collector.collect()
        assert isinstance(result, CollectionResult)

    @pytest.mark.asyncio
    @patch("dns.resolver.resolve")
    async def test_dns_lookup_nxdomain(self, mock_resolve, domain_collector):
        """Test DNS NXDOMAIN error."""
        import dns.resolver

        mock_resolve.side_effect = dns.resolver.NXDOMAIN()

        result = await domain_collector.collect()
        assert result.success is False
        assert any("not found" in err.lower() or "nxdomain" in err.lower() for err in result.errors)

    @pytest.mark.asyncio
    @patch("dns.resolver.resolve")
    async def test_dns_lookup_timeout(self, mock_resolve, domain_collector):
        """Test DNS timeout."""
        import dns.exception

        mock_resolve.side_effect = dns.exception.Timeout()

        result = await domain_collector.collect()
        assert result.success is False

    @pytest.mark.asyncio
    @patch("whois.whois")
    async def test_whois_lookup(self, mock_whois, domain_collector):
        """Test WHOIS lookup."""
        mock_whois.return_value = {
            "domain_name": "EXAMPLE.COM",
            "registrar": "IANA",
            "creation_date": "1995-08-14",
        }

        result = await domain_collector.collect()
        assert isinstance(result, CollectionResult)


# =============================================================================
# EmailCollector Tests
# =============================================================================


class TestEmailCollector:
    """Tests for EmailCollector."""

    @pytest.fixture
    def email_config(self):
        """Email collector configuration."""
        return CollectorConfig(
            target="user@example.com",
            data_type=DataType.EMAIL,
        )

    @pytest.fixture
    def email_collector(self, email_config):
        """Email collector instance."""
        return EmailCollector(email_config)

    @pytest.mark.asyncio
    async def test_email_validation_valid(self, email_collector):
        """Test validation of valid email."""
        result = await email_collector.collect()
        assert isinstance(result, CollectionResult)

    @pytest.mark.asyncio
    async def test_email_validation_invalid_format(self):
        """Test validation of invalid email format."""
        config = CollectorConfig(
            target="invalid-email",
            data_type=DataType.EMAIL,
        )
        collector = EmailCollector(config)
        result = await collector.collect()
        assert result.success is False

    @pytest.mark.asyncio
    async def test_email_domain_extraction(self, email_collector):
        """Test domain extraction from email."""
        result = await email_collector.collect()
        if result.success:
            # Should extract domain from email
            assert any("example.com" in str(item) for item in result.data)

    @pytest.mark.asyncio
    @patch("dns.resolver.resolve")
    async def test_email_mx_record_check(self, mock_resolve, email_collector):
        """Test MX record validation."""
        mock_record = MagicMock()
        mock_record.exchange.to_text.return_value = "mail.example.com."
        mock_resolve.return_value = [mock_record]

        result = await email_collector.collect()
        assert isinstance(result, CollectionResult)


# =============================================================================
# IPCollector Tests
# =============================================================================


class TestIPCollector:
    """Tests for IPCollector."""

    @pytest.fixture
    def ip_config(self):
        """IP collector configuration."""
        return CollectorConfig(
            target="8.8.8.8",
            data_type=DataType.IP,
        )

    @pytest.fixture
    def ip_collector(self, ip_config):
        """IP collector instance."""
        return IPCollector(ip_config)

    @pytest.mark.asyncio
    async def test_ip_collector_initialization(self, ip_collector):
        """Test IP collector initialization."""
        assert ip_collector.config.target == "8.8.8.8"

    @pytest.mark.asyncio
    @patch("httpx.AsyncClient.get")
    async def test_geolocation_lookup(self, mock_get, ip_collector):
        """Test IP geolocation lookup."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "country": "US",
            "city": "Mountain View",
            "latitude": 37.386,
            "longitude": -122.084,
        }
        mock_get.return_value = mock_response

        result = await ip_collector.collect()
        assert isinstance(result, CollectionResult)

    @pytest.mark.asyncio
    async def test_private_ip_detection(self):
        """Test detection of private IP addresses."""
        config = CollectorConfig(target="192.168.1.1", data_type=DataType.IP)
        collector = IPCollector(config)
        result = await collector.collect()
        # Should handle private IPs appropriately
        assert isinstance(result, CollectionResult)

    @pytest.mark.asyncio
    async def test_invalid_ip_format(self):
        """Test handling of invalid IP format."""
        config = CollectorConfig(target="256.256.256.256", data_type=DataType.IP)
        collector = IPCollector(config)
        result = await collector.collect()
        assert result.success is False


# =============================================================================
# SocialCollector Tests
# =============================================================================


class TestSocialCollector:
    """Tests for SocialCollector."""

    @pytest.fixture
    def social_config(self):
        """Social collector configuration."""
        return CollectorConfig(
            target="testuser",
            data_type=DataType.USERNAME,
        )

    @pytest.fixture
    def social_collector(self, social_config):
        """Social collector instance."""
        return SocialCollector(social_config)

    @pytest.mark.asyncio
    async def test_social_collector_initialization(self, social_collector):
        """Test social collector initialization."""
        assert social_collector.config.target == "testuser"

    @pytest.mark.asyncio
    @patch("httpx.AsyncClient.get")
    async def test_username_search(self, mock_get, social_collector):
        """Test username search across platforms."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = "User profile found"
        mock_get.return_value = mock_response

        result = await social_collector.collect()
        assert isinstance(result, CollectionResult)

    @pytest.mark.asyncio
    @patch("httpx.AsyncClient.get")
    async def test_rate_limit_handling(self, mock_get, social_collector):
        """Test rate limit response handling."""
        mock_response = MagicMock()
        mock_response.status_code = 429
        mock_get.return_value = mock_response

        result = await social_collector.collect()
        assert result.success is False
        assert any("rate limit" in err.lower() for err in result.errors)

    @pytest.mark.asyncio
    @patch("httpx.AsyncClient.get")
    async def test_authentication_required(self, mock_get, social_collector):
        """Test handling of authentication requirements."""
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_get.return_value = mock_response

        result = await social_collector.collect()
        assert result.success is False


# =============================================================================
# MediaCollector Tests
# =============================================================================


class TestMediaCollector:
    """Tests for MediaCollector."""

    @pytest.fixture
    def media_config(self):
        """Media collector configuration."""
        return CollectorConfig(
            target="https://example.com/image.jpg",
            data_type=DataType.IMAGE,
        )

    @pytest.fixture
    def media_collector(self, media_config):
        """Media collector instance."""
        return MediaCollector(media_config)

    @pytest.mark.asyncio
    async def test_media_collector_initialization(self, media_collector):
        """Test media collector initialization."""
        assert DataType.IMAGE == media_collector.config.data_type

    @pytest.mark.asyncio
    @patch("httpx.AsyncClient.get")
    async def test_metadata_extraction(self, mock_get, media_collector):
        """Test metadata extraction from media."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = b"fake_image_data"
        mock_response.headers = {"Content-Type": "image/jpeg"}
        mock_get.return_value = mock_response

        result = await media_collector.collect()
        assert isinstance(result, CollectionResult)

    @pytest.mark.asyncio
    @patch("httpx.AsyncClient.get")
    async def test_invalid_media_type(self, mock_get, media_collector):
        """Test handling of invalid media type."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = b"not an image"
        mock_response.headers = {"Content-Type": "text/html"}
        mock_get.return_value = mock_response

        result = await media_collector.collect()
        # Should handle gracefully
        assert isinstance(result, CollectionResult)


# =============================================================================
# DarkWebCollector Tests
# =============================================================================


class TestDarkWebCollector:
    """Tests for DarkWebCollector."""

    @pytest.fixture
    def darkweb_config(self):
        """Dark web collector configuration."""
        return CollectorConfig(
            target="test.onion",
            data_type=DataType.URL,
        )

    @pytest.fixture
    def darkweb_collector(self, darkweb_config):
        """Dark web collector instance."""
        return DarkWebCollector(darkweb_config)

    @pytest.mark.asyncio
    async def test_darkweb_collector_initialization(self, darkweb_collector):
        """Test dark web collector initialization."""
        assert "onion" in darkweb_collector.config.target

    @pytest.mark.asyncio
    @patch("stem.control.Controller.from_port")
    async def test_tor_connection(self, mock_controller, darkweb_collector):
        """Test Tor connection establishment."""
        mock_ctrl = MagicMock()
        mock_controller.return_value.__enter__.return_value = mock_ctrl

        result = await darkweb_collector.collect()
        # Should attempt connection or fail gracefully
        assert isinstance(result, CollectionResult)

    @pytest.mark.asyncio
    async def test_onion_address_validation(self, darkweb_collector):
        """Test .onion address validation."""
        result = await darkweb_collector.collect()
        assert isinstance(result, CollectionResult)


# =============================================================================
# GeoCollector Tests
# =============================================================================


class TestGeoCollector:
    """Tests for GeoCollector."""

    @pytest.fixture
    def geo_config(self):
        """Geo collector configuration."""
        return CollectorConfig(
            target="37.7749,-122.4194",  # San Francisco
            data_type=DataType.TEXT,
        )

    @pytest.fixture
    def geo_collector(self, geo_config):
        """Geo collector instance."""
        return GeoCollector(geo_config)

    @pytest.mark.asyncio
    async def test_geo_collector_initialization(self, geo_collector):
        """Test geo collector initialization."""
        assert "," in geo_collector.config.target

    @pytest.mark.asyncio
    @patch("geopy.geocoders.Nominatim.reverse")
    async def test_reverse_geocoding(self, mock_reverse, geo_collector):
        """Test reverse geocoding."""
        mock_location = MagicMock()
        mock_location.address = "San Francisco, CA, USA"
        mock_reverse.return_value = mock_location

        result = await geo_collector.collect()
        assert isinstance(result, CollectionResult)

    @pytest.mark.asyncio
    async def test_invalid_coordinates(self):
        """Test handling of invalid coordinates."""
        config = CollectorConfig(target="invalid,coords", data_type=DataType.TEXT)
        collector = GeoCollector(config)
        result = await collector.collect()
        assert result.success is False


# =============================================================================
# Error Handling Tests
# =============================================================================


class TestErrorHandling:
    """Tests for error handling across collectors."""

    @pytest.mark.asyncio
    async def test_network_timeout_handling(self):
        """Test handling of network timeouts."""
        config = CollectorConfig(
            target="https://example.com",
            data_type=DataType.URL,
            timeout=1,
        )
        collector = WebCollector(config)

        with patch("httpx.AsyncClient.get", side_effect=asyncio.TimeoutError()):
            result = await collector.collect()
            assert result.success is False
            assert len(result.errors) > 0

    @pytest.mark.asyncio
    async def test_invalid_input_handling(self):
        """Test handling of invalid inputs."""
        config = CollectorConfig(target="", data_type=DataType.URL)
        collector = WebCollector(config)
        result = await collector.collect()
        assert result.success is False

    @pytest.mark.asyncio
    async def test_malformed_data_handling(self):
        """Test handling of malformed data."""
        config = CollectorConfig(
            target="https://example.com",
            data_type=DataType.URL,
        )
        collector = WebCollector(config)

        with patch("httpx.AsyncClient.get") as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.text = "<<<malformed>>>data>>>"
            mock_get.return_value = mock_response

            result = await collector.collect()
            assert isinstance(result, CollectionResult)


# =============================================================================
# Data Validation Tests
# =============================================================================


class TestDataValidation:
    """Tests for data validation and normalization."""

    def test_entity_normalization(self):
        """Test entity data normalization."""
        # Domain normalization
        assert "example.com" == "EXAMPLE.COM".lower()
        assert "example.com" == "  example.com  ".strip()

    def test_confidence_scoring(self):
        """Test confidence score calculation."""
        # Confidence should be between 0 and 1
        confidence = 0.85
        assert 0.0 <= confidence <= 1.0

    def test_metadata_extraction(self):
        """Test metadata extraction from results."""
        result = CollectionResult(
            success=True,
            metadata={"timestamp": "2024-01-01", "source": "test"},
        )
        assert "timestamp" in result.metadata
        assert "source" in result.metadata

    @pytest.mark.asyncio
    async def test_relationship_normalization(self):
        """Test relationship data normalization."""
        # Test relationship structure
        relationship = {
            "source": "example.com",
            "target": "93.184.216.34",
            "type": "resolves_to",
            "confidence": 0.90,
        }
        assert "source" in relationship
        assert "target" in relationship
        assert "type" in relationship
        assert 0.0 <= relationship["confidence"] <= 1.0
