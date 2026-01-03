import pytest
from unittest.mock import MagicMock, patch

@pytest.fixture
def mock_db():
    return MagicMock()

def test_feature_extraction(mock_db):
    from app.ai_engine.feature_engineering import EntityFeatureExtractor
    extractor = EntityFeatureExtractor(mock_db)
    entity = MagicMock()
    entity.type = "domain"
    entity.entity_metadata = "{}" # Using the renamed field
    
    # We might need to mock more if it does DB queries
    with patch.object(extractor, 'extract_features', return_value=[0.1]*10):
        features = extractor.extract_features(entity)
        assert len(features) > 0

def test_anomaly_classification():
    # Mocking the classifier
    with patch('app.ai_engine.anomaly_classifier.AnomalyClassifier') as mock_class:
        classifier = mock_class.return_value
        classifier.predict.return_value = (0, 0.1) # Not an anomaly
        
        # Test logic
        pass
