import pytest
from unittest.mock import MagicMock, patch, AsyncMock
from app.ethics.osint_compliance import OSINTCompliance

@pytest.fixture
def compliance():
    return OSINTCompliance()

@pytest.mark.asyncio
async def test_robots_txt_checking(compliance):
    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = MagicMock(status_code=200, text="User-agent: *\nDisallow: /private")
        assert await compliance.check_robots_txt("example.com", path="/") is True
        assert await compliance.check_robots_txt("example.com", path="/private") is False

def test_blocked_domains(compliance):
    assert compliance.is_domain_blocked("test.gov") is True
    assert compliance.is_domain_blocked("example.com") is False
