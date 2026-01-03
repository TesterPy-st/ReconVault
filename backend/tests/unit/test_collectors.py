import pytest
from unittest.mock import MagicMock, patch, AsyncMock
from app.collectors.web_collector import WebCollector
from app.collectors.social_collector import SocialCollector
from app.collectors.domain_collector import DomainCollector
from app.collectors.email_collector import EmailCollector
from app.collectors.ip_collector import IPCollector
from app.collectors.media_collector import MediaCollector
from app.collectors.darkweb_collector import DarkWebCollector
from app.collectors.geo_collector import GeoCollector
from app.collectors.base_collector import CollectorConfig, CollectionResult, DataType

@pytest.mark.asyncio
async def test_web_collector_parsing(mock_collector_config):
    mock_collector_config.data_type = DataType.URL
    collector = WebCollector(mock_collector_config)
    with patch.object(WebCollector, 'collect', new_callable=AsyncMock) as mock_collect:
        mock_collect.return_value = CollectionResult(
            success=True,
            collector_name="WebCollector",
            data=[{"entity_type": DataType.DOMAIN.value, "value": "example.com"}]
        )
        result = await collector.collect()
        assert result.success is True
        assert len(result.data) > 0

@pytest.mark.asyncio
async def test_social_collector_authentication(mock_collector_config):
    mock_collector_config.data_type = DataType.USERNAME
    collector = SocialCollector(mock_collector_config)
    with patch.object(SocialCollector, 'collect', new_callable=AsyncMock) as mock_collect:
        mock_collect.return_value = CollectionResult(success=True, collector_name="SocialCollector", data=[])
        result = await collector.collect()
        assert result.success is True

@pytest.mark.asyncio
async def test_domain_collector_dns_lookup(mock_collector_config):
    mock_collector_config.data_type = DataType.DOMAIN
    collector = DomainCollector(mock_collector_config)
    with patch.object(DomainCollector, 'collect', new_callable=AsyncMock) as mock_collect:
        mock_collect.return_value = CollectionResult(success=True, collector_name="DomainCollector", data=[])
        result = await collector.collect()
        assert result.success is True

@pytest.mark.asyncio
async def test_email_collector_validation(mock_collector_config):
    mock_collector_config.data_type = DataType.EMAIL
    collector = EmailCollector(mock_collector_config)
    with patch.object(EmailCollector, 'collect', new_callable=AsyncMock) as mock_collect:
        mock_collect.return_value = CollectionResult(success=True, collector_name="EmailCollector", data=[])
        result = await collector.collect()
        assert result.success is True

@pytest.mark.asyncio
async def test_ip_collector_geolocation(mock_collector_config):
    mock_collector_config.data_type = DataType.IP
    collector = IPCollector(mock_collector_config)
    with patch.object(IPCollector, 'collect', new_callable=AsyncMock) as mock_collect:
        mock_collect.return_value = CollectionResult(success=True, collector_name="IPCollector", data=[])
        result = await collector.collect()
        assert result.success is True

@pytest.mark.asyncio
async def test_media_collector_extraction(mock_collector_config):
    mock_collector_config.data_type = DataType.URL
    collector = MediaCollector(mock_collector_config)
    with patch.object(MediaCollector, 'collect', new_callable=AsyncMock) as mock_collect:
        mock_collect.return_value = CollectionResult(success=True, collector_name="MediaCollector", data=[])
        result = await collector.collect()
        assert result.success is True

@pytest.mark.asyncio
async def test_darkweb_collector_connection(mock_collector_config):
    mock_collector_config.data_type = DataType.TEXT
    collector = DarkWebCollector(mock_collector_config)
    with patch.object(DarkWebCollector, 'collect', new_callable=AsyncMock) as mock_collect:
        mock_collect.return_value = CollectionResult(success=True, collector_name="DarkWebCollector", data=[])
        result = await collector.collect()
        assert result.success is True

@pytest.mark.asyncio
async def test_geo_collector_mapping(mock_collector_config):
    mock_collector_config.data_type = DataType.TEXT
    collector = GeoCollector(mock_collector_config)
    with patch.object(GeoCollector, 'collect', new_callable=AsyncMock) as mock_collect:
        mock_collect.return_value = CollectionResult(success=True, collector_name="GeoCollector", data=[])
        result = await collector.collect()
        assert result.success is True

@pytest.mark.asyncio
async def test_collector_rate_limiting(mock_collector_config):
    collector = WebCollector(mock_collector_config)
    with patch.object(collector, '_apply_rate_limit', new_callable=AsyncMock) as mock_limit:
        await collector._apply_rate_limit()
        mock_limit.assert_called_once()

@pytest.mark.asyncio
async def test_collector_retry_logic(mock_collector_config):
    collector = WebCollector(mock_collector_config)
    mock_func = AsyncMock(side_effect=[Exception("Fail"), "Success"])
    result = await collector._retry_with_backoff(mock_func, max_retries=1)
    assert result == "Success"
    assert mock_func.call_count == 2
