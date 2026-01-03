import pytest
import uuid
import sys
from unittest.mock import MagicMock

# Mock torch before any app code imports it
mock_torch = MagicMock()
sys.modules["torch"] = mock_torch
sys.modules["torch.nn"] = MagicMock()
sys.modules["torch.utils"] = MagicMock()
sys.modules["torch.utils.data"] = MagicMock()
sys.modules["torchvision"] = MagicMock()
sys.modules["torchvision.models"] = MagicMock()

from datetime import datetime
from app.collectors.base_collector import CollectorConfig, RiskLevel

@pytest.fixture
def mock_collector_config():
    return CollectorConfig(
        target="example.com",
        data_type=None, # Will be set in tests
        timeout=30,
        max_retries=3
    )

@pytest.fixture
def sample_entity_data():
    return {
        "id": str(uuid.uuid4()),
        "name": "Test Entity",
        "type": "DOMAIN",
        "risk_score": 0.5,
        "metadata": {"test": True},
        "discovered_at": datetime.now().isoformat()
    }
