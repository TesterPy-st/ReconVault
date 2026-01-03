import pytest
from app.risk_engine.risk_analyzer import RiskAnalyzer

@pytest.fixture
def risk_analyzer():
    return RiskAnalyzer()

def test_entity_risk_calculation(risk_analyzer):
    entity = {
        "id": 1,
        "type": "domain",
        "value": "example.com",
        "metadata": {"breaches_found": 0}
    }
    score = risk_analyzer.calculate_entity_risk_score(entity)
    assert 0 <= score <= 100

def test_risk_scoring_formula(risk_analyzer):
    # Test high risk entity
    entity = {
        "id": 2,
        "type": "ip_address",
        "value": "1.2.3.4",
        "metadata": {"malware_detected": True, "breaches_found": 5}
    }
    score = risk_analyzer.calculate_entity_risk_score(entity)
    assert score > 50
