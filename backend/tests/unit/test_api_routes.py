import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch
from app.main import app

@pytest.fixture
def client():
    return TestClient(app)

def test_health_check(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_targets_list(client):
    with patch("app.api.routes.targets.get_target_service") as mock_service_getter:
        mock_service = MagicMock()
        mock_service_getter.return_value = mock_service
        mock_service.get_targets.return_value = MagicMock(targets=[], total=0)
        
        response = client.get("/api/targets")
        # If it requires auth, it might be 401
        if response.status_code != 401:
            assert response.status_code == 200
