"""
Risk Engine Test Suite

Comprehensive tests for risk assessment engine components.
"""

import pytest
from typing import Dict, Any, List

from app.risk_engine.exposure_models import (
    DataExposureModel,
    NetworkExposureModel,
    IdentityExposureModel,
    InfrastructureExposureModel,
    ExposureAnalyzer
)
from app.risk_engine.ml_models import RiskMLModel, generate_synthetic_training_data
from app.risk_engine.risk_analyzer import RiskAnalyzer


# Test data fixtures
@pytest.fixture
def sample_entity() -> Dict[str, Any]:
    """Sample entity for testing."""
    return {
        "id": 1,
        "type": "domain",
        "value": "example.com",
        "risk_score": 0.0,
        "confidence": 0.85,
        "relationship_count": 5,
        "is_verified": True,
        "metadata": {
            "sources": ["whois", "dns", "ssl"],
            "collection_count": 3,
            "is_anomaly": False,
            "anomaly_score": 0.0,
            "breaches_found": 0,
            "dark_web_mentions": False,
            "malware_detected": False,
            "phishing_indicator": False,
            "country": "US",
            "domain_age_days": 365,
            "days_until_expiry": 90,
            "has_ssl": True,
            "open_ports": [{"port": 80}, {"port": 443}],
            "data_quality": 0.8
        }
    }


@pytest.fixture
def high_risk_entity() -> Dict[str, Any]:
    """High-risk entity for testing."""
    return {
        "id": 2,
        "type": "ip_address",
        "value": "192.168.1.1",
        "risk_score": 75.0,
        "confidence": 0.9,
        "relationship_count": 15,
        "is_verified": False,
        "metadata": {
            "sources": ["shodan", "virustotal", "abuseipdb"],
            "collection_count": 10,
            "is_anomaly": True,
            "anomaly_score": 0.8,
            "breaches_found": 3,
            "dark_web_mentions": True,
            "malware_detected": True,
            "phishing_indicator": False,
            "country": "RU",
            "domain_age_days": 30,
            "days_until_expiry": 5,
            "has_ssl": False,
            "open_ports": [
                {"port": 22}, {"port": 3389}, {"port": 445}, 
                {"port": 135}, {"port": 139}
            ],
            "data_quality": 0.7
        }
    }


@pytest.fixture
def sample_relationship() -> Dict[str, Any]:
    """Sample relationship for testing."""
    return {
        "id": 1,
        "source_entity_id": 1,
        "target_entity_id": 2,
        "type": "resolves_to",
        "confidence": 0.9,
        "weight": 1.0,
        "verified": True,
        "metadata": {
            "dark_web_related": False,
            "malware_related": False
        }
    }


# Data Exposure Model Tests
class TestDataExposureModel:
    """Test data exposure calculations."""
    
    def test_calculate_exposure_no_breaches(self, sample_entity):
        """Test exposure calculation with no breaches."""
        model = DataExposureModel()
        score = model.calculate_exposure(sample_entity)
        assert 0 <= score <= 100
        assert score < 30  # Should be low without breaches
    
    def test_calculate_exposure_with_breaches(self, high_risk_entity):
        """Test exposure calculation with breaches."""
        model = DataExposureModel()
        score = model.calculate_exposure(high_risk_entity)
        assert score > 50  # Should be high with breaches and dark web
    
    def test_get_exposure_details(self, sample_entity):
        """Test detailed exposure information."""
        model = DataExposureModel()
        details = model.get_exposure_details(sample_entity)
        assert "exposure_score" in details
        assert "exposure_level" in details
        assert "breaches_found" in details
        assert details["exposure_level"] in ["low", "medium", "high", "critical"]


# Network Exposure Model Tests
class TestNetworkExposureModel:
    """Test network exposure calculations."""
    
    def test_calculate_exposure_low(self, sample_entity):
        """Test network exposure with minimal ports."""
        model = NetworkExposureModel()
        score = model.calculate_exposure(sample_entity)
        assert 0 <= score <= 100
        assert score < 40  # Should be low with just HTTP/HTTPS
    
    def test_calculate_exposure_high(self, high_risk_entity):
        """Test network exposure with high-risk ports."""
        model = NetworkExposureModel()
        score = model.calculate_exposure(high_risk_entity)
        assert score > 40  # Should be higher with risky ports
    
    def test_get_exposure_details(self, sample_entity):
        """Test detailed network exposure."""
        model = NetworkExposureModel()
        details = model.get_exposure_details(sample_entity)
        assert "open_ports_count" in details
        assert "open_ports" in details
        assert details["open_ports_count"] == 2


# Identity Exposure Model Tests
class TestIdentityExposureModel:
    """Test identity exposure calculations."""
    
    def test_calculate_exposure_email(self):
        """Test identity exposure for email."""
        model = IdentityExposureModel()
        entity = {
            "id": 3,
            "type": "email",
            "value": "test@example.com",
            "metadata": {"breaches_found": 2}
        }
        score = model.calculate_exposure(entity)
        assert score > 30  # Should be elevated for email with breaches
    
    def test_get_exposure_details(self):
        """Test identity exposure details."""
        model = IdentityExposureModel()
        entity = {
            "id": 3,
            "type": "person",
            "value": "John Doe",
            "metadata": {
                "email_exposed": True,
                "phone_exposed": True,
                "breaches_found": 1
            }
        }
        details = model.get_exposure_details(entity)
        assert "exposed_pii_fields" in details
        assert len(details["exposed_pii_fields"]) == 2


# Infrastructure Exposure Model Tests
class TestInfrastructureExposureModel:
    """Test infrastructure exposure calculations."""
    
    def test_calculate_exposure_secure(self, sample_entity):
        """Test infrastructure exposure for secure system."""
        model = InfrastructureExposureModel()
        score = model.calculate_exposure(sample_entity)
        assert score < 30  # Should be low with valid SSL
    
    def test_calculate_exposure_vulnerable(self, high_risk_entity):
        """Test infrastructure exposure for vulnerable system."""
        model = InfrastructureExposureModel()
        score = model.calculate_exposure(high_risk_entity)
        assert score > 40  # Should be high without SSL and expiring soon
    
    def test_get_exposure_details(self, sample_entity):
        """Test infrastructure exposure details."""
        model = InfrastructureExposureModel()
        details = model.get_exposure_details(sample_entity)
        assert "ssl_days_until_expiry" in details
        assert "has_ssl" in details
        assert details["has_ssl"] is True


# Exposure Analyzer Tests
class TestExposureAnalyzer:
    """Test comprehensive exposure analyzer."""
    
    def test_calculate_total_exposure(self, sample_entity):
        """Test total exposure calculation."""
        analyzer = ExposureAnalyzer()
        total = analyzer.calculate_total_exposure(sample_entity)
        assert 0 <= total <= 100
    
    def test_comprehensive_exposure(self, sample_entity):
        """Test comprehensive exposure analysis."""
        analyzer = ExposureAnalyzer()
        comprehensive = analyzer.get_comprehensive_exposure(sample_entity)
        assert "total_exposure" in comprehensive
        assert "data_exposure" in comprehensive
        assert "network_exposure" in comprehensive
        assert "identity_exposure" in comprehensive
        assert "infrastructure_exposure" in comprehensive


# ML Model Tests
class TestRiskMLModel:
    """Test ML model functionality."""
    
    def test_feature_extraction(self, sample_entity):
        """Test feature extraction from entity."""
        model = RiskMLModel()
        features = model.extract_features(sample_entity)
        assert isinstance(features, list)
        assert len(features) == 19  # Should have 19 features
    
    def test_generate_synthetic_data(self):
        """Test synthetic data generation."""
        entities, labels = generate_synthetic_training_data(100)
        assert len(entities) == 100
        assert len(labels) == 100
        assert all(0 <= label <= 3 for label in labels)
    
    def test_model_training(self):
        """Test model training."""
        model = RiskMLModel()
        entities, labels = generate_synthetic_training_data(200)
        results = model.train_model(entities, labels)
        
        assert results["success"] is True
        assert "accuracy" in results
        assert "f1_score" in results
        assert 0 <= results["accuracy"] <= 1
        assert model.model_trained is True
    
    def test_prediction_untrained(self, sample_entity):
        """Test prediction with untrained model."""
        model = RiskMLModel()
        prediction = model.predict_risk(sample_entity)
        assert "risk_level" in prediction
        assert prediction["risk_level"] in ["low", "medium", "high", "critical"]
    
    def test_prediction_trained(self, sample_entity):
        """Test prediction with trained model."""
        model = RiskMLModel()
        entities, labels = generate_synthetic_training_data(200)
        model.train_model(entities, labels)
        
        prediction = model.predict_risk(sample_entity)
        assert "risk_level" in prediction
        assert "confidence" in prediction
        assert "probabilities" in prediction
        assert len(prediction["probabilities"]) == 4
    
    def test_batch_prediction(self):
        """Test batch prediction."""
        model = RiskMLModel()
        entities, labels = generate_synthetic_training_data(200)
        model.train_model(entities, labels)
        
        test_entities = entities[:10]
        predictions = model.batch_predict(test_entities)
        
        assert len(predictions) == 10
        assert all("risk_level" in p for p in predictions)
    
    def test_feature_importance(self):
        """Test feature importance extraction."""
        model = RiskMLModel()
        entities, labels = generate_synthetic_training_data(200)
        model.train_model(entities, labels)
        
        importance = model.get_feature_importance()
        assert isinstance(importance, dict)
        assert len(importance) > 0


# Risk Analyzer Tests
class TestRiskAnalyzer:
    """Test risk analyzer functionality."""
    
    def test_calculate_entity_risk(self, sample_entity):
        """Test entity risk calculation."""
        analyzer = RiskAnalyzer()
        result = analyzer.calculate_entity_risk(sample_entity)
        
        assert "risk_score" in result
        assert "risk_level" in result
        assert "confidence" in result
        assert "components" in result
        assert 0 <= result["risk_score"] <= 100
        assert result["risk_level"] in ["low", "medium", "high", "critical"]
    
    def test_calculate_relationship_risk(self, sample_relationship):
        """Test relationship risk calculation."""
        analyzer = RiskAnalyzer()
        result = analyzer.calculate_relationship_risk(sample_relationship)
        
        assert "risk_score" in result
        assert "risk_level" in result
        assert "risk_factors" in result
        assert 0 <= result["risk_score"] <= 100
    
    def test_calculate_exposure_level(self, sample_entity):
        """Test exposure level calculation."""
        analyzer = RiskAnalyzer()
        exposure = analyzer.calculate_exposure_level(sample_entity)
        assert 0 <= exposure <= 100
    
    def test_detect_risk_patterns_empty(self):
        """Test pattern detection with no entities."""
        analyzer = RiskAnalyzer()
        patterns = analyzer.detect_risk_patterns([], [])
        assert isinstance(patterns, list)
        assert len(patterns) == 0
    
    def test_detect_risk_patterns_breach_cluster(self):
        """Test breach cluster pattern detection."""
        analyzer = RiskAnalyzer()
        
        # Create entities with breaches
        entities = [
            {"id": i, "type": "email", "metadata": {"breaches_found": 2}}
            for i in range(5)
        ]
        
        patterns = analyzer.detect_risk_patterns(entities, [])
        breach_patterns = [p for p in patterns if p["pattern_type"] == "breach_cluster"]
        assert len(breach_patterns) > 0
    
    def test_detect_risk_patterns_dark_web(self):
        """Test dark web exposure pattern detection."""
        analyzer = RiskAnalyzer()
        
        # Create entities with dark web mentions
        entities = [
            {"id": i, "type": "domain", "metadata": {"dark_web_mentions": True}}
            for i in range(3)
        ]
        
        patterns = analyzer.detect_risk_patterns(entities, [])
        darkweb_patterns = [p for p in patterns if p["pattern_type"] == "dark_web_exposure"]
        assert len(darkweb_patterns) > 0


# Integration Tests
class TestIntegration:
    """Integration tests for complete workflows."""
    
    def test_end_to_end_risk_assessment(self, sample_entity):
        """Test complete risk assessment workflow."""
        # Train model
        model = RiskMLModel()
        entities, labels = generate_synthetic_training_data(200)
        model.train_model(entities, labels)
        
        # Create analyzer with trained model
        analyzer = RiskAnalyzer()
        analyzer.ml_model = model
        
        # Calculate risk
        result = analyzer.calculate_entity_risk(sample_entity)
        
        # Verify complete result
        assert "risk_score" in result
        assert "risk_level" in result
        assert "components" in result
        assert "ml_prediction" in result
        assert result["ml_prediction"] is not None
    
    def test_batch_risk_analysis(self):
        """Test batch risk analysis."""
        # Generate test data
        entities, labels = generate_synthetic_training_data(50)
        
        # Train model
        model = RiskMLModel()
        model.train_model(entities, labels)
        
        # Analyze batch
        analyzer = RiskAnalyzer()
        analyzer.ml_model = model
        
        results = []
        for entity in entities[:10]:
            result = analyzer.calculate_entity_risk(entity)
            results.append(result)
        
        assert len(results) == 10
        assert all("risk_score" in r for r in results)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
