"""
Pytest configuration and shared fixtures for ReconVault tests.
"""
import asyncio
import os
from typing import AsyncGenerator, Generator
from unittest.mock import AsyncMock, MagicMock

import pytest
from faker import Faker
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.config import Settings
from app.database import Base, get_db
from app.main import app

# Initialize Faker
fake = Faker()


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def test_settings() -> Settings:
    """Test settings with overrides."""
    return Settings(
        DATABASE_URL="sqlite:///:memory:",
        NEO4J_URI="bolt://localhost:7687",
        NEO4J_USER="neo4j",
        NEO4J_PASSWORD="test",
        REDIS_URL="redis://localhost:6379/1",
        SECRET_KEY="test-secret-key",
        ENVIRONMENT="test",
    )


@pytest.fixture(scope="function")
def db_engine():
    """Create test database engine."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest.fixture(scope="function")
def db_session(db_engine) -> Generator[Session, None, None]:
    """Create test database session."""
    TestingSessionLocal = sessionmaker(
        autocommit=False, autoflush=False, bind=db_engine
    )
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture(scope="function")
def client(db_session) -> Generator[TestClient, None, None]:
    """Create test client with database session."""

    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def mock_neo4j_driver():
    """Mock Neo4j driver."""
    driver = MagicMock()
    session = MagicMock()
    driver.session.return_value.__enter__.return_value = session
    driver.session.return_value.__exit__.return_value = None
    return driver


@pytest.fixture
def mock_redis_client():
    """Mock Redis client."""
    redis_client = MagicMock()
    redis_client.get.return_value = None
    redis_client.set.return_value = True
    redis_client.delete.return_value = 1
    return redis_client


@pytest.fixture
def sample_target_data():
    """Sample target data for testing."""
    return {
        "name": "Test Target",
        "type": "domain",
        "value": "example.com",
        "description": "Test target for unit tests",
        "priority": "high",
        "tags": ["test", "osint"],
    }


@pytest.fixture
def sample_entity_data():
    """Sample entity data for testing."""
    return {
        "type": "domain",
        "value": "example.com",
        "confidence": 0.95,
        "source": "web_collector",
        "metadata": {
            "ip_address": "93.184.216.34",
            "country": "US",
            "registrar": "IANA",
        },
    }


@pytest.fixture
def sample_relationship_data():
    """Sample relationship data for testing."""
    return {
        "source_id": 1,
        "target_id": 2,
        "relationship_type": "resolves_to",
        "confidence": 0.90,
        "metadata": {"discovered_at": "2024-01-01T00:00:00Z"},
    }


@pytest.fixture
def sample_collection_result():
    """Sample collection result for testing."""
    from app.collectors import CollectionResult

    return CollectionResult(
        entities=[
            {
                "type": "domain",
                "value": "example.com",
                "confidence": 0.95,
                "metadata": {"ip": "93.184.216.34"},
            }
        ],
        relationships=[
            {
                "source": "example.com",
                "target": "93.184.216.34",
                "type": "resolves_to",
                "confidence": 0.90,
            }
        ],
        metadata={"collector": "domain_collector", "timestamp": "2024-01-01T00:00:00Z"},
    )


@pytest.fixture
def mock_http_response():
    """Mock HTTP response."""
    response = MagicMock()
    response.status_code = 200
    response.text = "<html><body>Test content</body></html>"
    response.json.return_value = {"status": "success"}
    response.headers = {"Content-Type": "text/html"}
    return response


@pytest.fixture
def mock_dns_resolver():
    """Mock DNS resolver."""
    resolver = MagicMock()
    resolver.resolve.return_value = [MagicMock(address="93.184.216.34")]
    return resolver


@pytest.fixture
def mock_whois_response():
    """Mock WHOIS response."""
    return {
        "domain_name": "EXAMPLE.COM",
        "registrar": "IANA",
        "creation_date": "1995-08-14",
        "expiration_date": "2025-08-13",
        "name_servers": ["A.IANA-SERVERS.NET", "B.IANA-SERVERS.NET"],
    }


@pytest.fixture
def sample_graph_data():
    """Sample graph data for testing."""
    return {
        "nodes": [
            {"id": "1", "type": "domain", "value": "example.com"},
            {"id": "2", "type": "ip", "value": "93.184.216.34"},
        ],
        "edges": [
            {
                "source": "1",
                "target": "2",
                "type": "resolves_to",
                "confidence": 0.90,
            }
        ],
    }


@pytest.fixture
def mock_ml_model():
    """Mock ML model for testing."""
    model = MagicMock()
    model.predict.return_value = [[0.1]]  # Anomaly score
    model.predict_proba.return_value = [[0.9, 0.1]]  # Classification probabilities
    return model


@pytest.fixture
def sample_risk_data():
    """Sample risk data for testing."""
    return {
        "entity_id": 1,
        "risk_score": 75.5,
        "risk_level": "high",
        "factors": [
            {"name": "suspicious_tld", "weight": 0.3, "score": 80},
            {"name": "recent_registration", "weight": 0.2, "score": 70},
        ],
        "recommendations": ["Monitor closely", "Verify legitimacy"],
    }


@pytest.fixture
def mock_collector_config():
    """Mock collector configuration."""
    from app.collectors import CollectorConfig

    return CollectorConfig(
        max_depth=2,
        timeout=30,
        rate_limit=10,
        respect_robots_txt=True,
        user_agent="ReconVault-Test/1.0",
    )


# Environment setup
@pytest.fixture(autouse=True)
def set_test_env():
    """Set test environment variables."""
    os.environ["ENVIRONMENT"] = "test"
    os.environ["DATABASE_URL"] = "sqlite:///:memory:"
    yield
    # Cleanup
    if "ENVIRONMENT" in os.environ:
        del os.environ["ENVIRONMENT"]
