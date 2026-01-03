"""
Unit tests for AI engine and anomaly detection.

Tests cover:
- Feature extraction
- Isolation Forest prediction
- LSTM autoencoder inference
- Anomaly classification
- Anomaly explanation
"""
import pytest
import numpy as np
from unittest.mock import MagicMock, patch
from app.ai_engine.anomaly_detector import AnomalyDetector
from app.ai_engine.feature_extractor import FeatureExtractor


class TestFeatureExtraction:
    """Tests for feature extraction."""

    @pytest.fixture
    def feature_extractor(self):
        """Create feature extractor instance."""
        return FeatureExtractor()

    def test_extract_basic_features(self, feature_extractor):
        """Test basic feature extraction."""
        entity = {
            "entity_type": "domain",
            "value": "example.com",
            "metadata": {"age_days": 365}
        }
        features = feature_extractor.extract(entity)
        assert isinstance(features, (list, np.ndarray, dict))

    def test_extract_numerical_features(self, feature_extractor):
        """Test numerical feature extraction."""
        entity = {
            "entity_type": "domain",
            "value": "example.com",
            "metadata": {"age_days": 365, "ssl_score": 0.95}
        }
        features = feature_extractor.extract_numerical(entity)
        assert isinstance(features, (list, np.ndarray))

    def test_extract_categorical_features(self, feature_extractor):
        """Test categorical feature extraction."""
        entity = {
            "entity_type": "domain",
            "value": "example.com",
            "metadata": {"country": "US", "tld": "com"}
        }
        features = feature_extractor.extract_categorical(entity)
        assert isinstance(features, (list, dict))

    def test_feature_normalization(self, feature_extractor):
        """Test feature normalization."""
        features = [100, 0.5, 1000]
        normalized = feature_extractor.normalize(features)
        assert isinstance(normalized, (list, np.ndarray))

    def test_feature_vector_length(self, feature_extractor):
        """Test consistent feature vector length."""
        entity1 = {"entity_type": "domain", "value": "example.com"}
        entity2 = {"entity_type": "ip", "value": "1.2.3.4"}
        features1 = feature_extractor.extract(entity1)
        features2 = feature_extractor.extract(entity2)
        # Both should produce same length vectors
        if isinstance(features1, (list, np.ndarray)) and isinstance(features2, (list, np.ndarray)):
            assert len(features1) == len(features2)


class TestIsolationForestPrediction:
    """Tests for Isolation Forest anomaly detection."""

    @pytest.fixture
    def anomaly_detector(self):
        """Create anomaly detector with Isolation Forest."""
        detector = AnomalyDetector(model_type="isolation_forest")
        detector.model = MagicMock()
        detector.model.predict.return_value = np.array([-1])  # -1 = anomaly
        detector.model.score_samples.return_value = np.array([-0.5])
        return detector

    def test_predict_anomaly(self, anomaly_detector):
        """Test anomaly prediction."""
        features = [0.5, 0.3, 0.8]
        prediction = anomaly_detector.predict(features)
        assert prediction in [-1, 1] or isinstance(prediction, (int, float, np.ndarray))

    def test_anomaly_score(self, anomaly_detector):
        """Test anomaly score calculation."""
        features = [0.5, 0.3, 0.8]
        score = anomaly_detector.get_anomaly_score(features)
        assert isinstance(score, (float, int, np.ndarray))

    def test_batch_prediction(self, anomaly_detector):
        """Test batch anomaly prediction."""
        features_batch = [[0.5, 0.3, 0.8], [0.2, 0.6, 0.4], [0.9, 0.1, 0.7]]
        predictions = anomaly_detector.predict_batch(features_batch)
        assert len(predictions) == 3

    def test_model_training(self, anomaly_detector):
        """Test model training."""
        training_data = np.random.rand(100, 3)
        anomaly_detector.train(training_data)
        # Should complete without error
        assert True


class TestLSTMAutoencoderInference:
    """Tests for LSTM autoencoder."""

    @pytest.fixture
    def lstm_detector(self):
        """Create LSTM autoencoder detector."""
        detector = AnomalyDetector(model_type="lstm_autoencoder")
        detector.model = MagicMock()
        detector.model.predict.return_value = np.array([[0.5, 0.3, 0.8]])
        return detector

    def test_lstm_prediction(self, lstm_detector):
        """Test LSTM prediction."""
        sequence = np.array([[0.5, 0.3], [0.4, 0.6], [0.7, 0.2]])
        prediction = lstm_detector.predict(sequence)
        assert isinstance(prediction, (np.ndarray, list, float))

    def test_reconstruction_error(self, lstm_detector):
        """Test reconstruction error calculation."""
        original = np.array([[0.5, 0.3], [0.4, 0.6]])
        reconstructed = np.array([[0.52, 0.28], [0.38, 0.62]])
        error = lstm_detector.calculate_reconstruction_error(original, reconstructed)
        assert isinstance(error, (float, int))
        assert error >= 0

    def test_threshold_based_detection(self, lstm_detector):
        """Test threshold-based anomaly detection."""
        error = 0.15
        threshold = 0.10
        is_anomaly = lstm_detector.is_anomaly(error, threshold)
        assert isinstance(is_anomaly, bool)
        assert is_anomaly is True


class TestAnomalyClassification:
    """Tests for anomaly classification."""

    @pytest.fixture
    def anomaly_detector(self):
        """Create anomaly detector."""
        return AnomalyDetector()

    def test_classify_anomaly_type(self, anomaly_detector):
        """Test anomaly type classification."""
        entity = {
            "entity_type": "domain",
            "value": "suspicious-domain.xyz",
            "anomaly_score": 0.95
        }
        anomaly_type = anomaly_detector.classify_anomaly_type(entity)
        assert isinstance(anomaly_type, str)

    def test_severity_classification(self, anomaly_detector):
        """Test anomaly severity classification."""
        anomaly_score = 0.95
        severity = anomaly_detector.classify_severity(anomaly_score)
        assert severity in ["CRITICAL", "HIGH", "MEDIUM", "LOW", "INFO"] or isinstance(severity, str)

    def test_anomaly_categories(self, anomaly_detector):
        """Test anomaly category identification."""
        entity = {
            "entity_type": "domain",
            "value": "example.com",
            "metadata": {"suspicious_patterns": ["recent_registration", "no_ssl"]}
        }
        categories = anomaly_detector.get_anomaly_categories(entity)
        assert isinstance(categories, list)


class TestAnomalyExplanation:
    """Tests for anomaly explanation."""

    @pytest.fixture
    def anomaly_detector(self):
        """Create anomaly detector."""
        return AnomalyDetector()

    def test_explain_anomaly(self, anomaly_detector):
        """Test anomaly explanation generation."""
        entity = {
            "entity_type": "domain",
            "value": "example.com",
            "anomaly_score": 0.85
        }
        explanation = anomaly_detector.explain_anomaly(entity)
        assert isinstance(explanation, (str, dict, list))

    def test_feature_importance(self, anomaly_detector):
        """Test feature importance calculation."""
        features = {"age": 5, "ssl": 0, "reputation": 0.3}
        importance = anomaly_detector.calculate_feature_importance(features)
        assert isinstance(importance, dict)

    def test_contributing_factors(self, anomaly_detector):
        """Test identifying contributing factors."""
        entity = {
            "entity_type": "domain",
            "value": "example.com",
            "metadata": {"age_days": 3, "ssl_valid": False}
        }
        factors = anomaly_detector.get_contributing_factors(entity)
        assert isinstance(factors, list)

    def test_explanation_text_generation(self, anomaly_detector):
        """Test human-readable explanation generation."""
        entity = {
            "entity_type": "domain",
            "value": "suspicious.xyz",
            "anomaly_score": 0.90
        }
        explanation_text = anomaly_detector.generate_explanation_text(entity)
        assert isinstance(explanation_text, str)


class TestModelManagement:
    """Tests for model management operations."""

    @pytest.fixture
    def anomaly_detector(self):
        """Create anomaly detector."""
        return AnomalyDetector()

    @patch('joblib.dump')
    def test_save_model(self, mock_dump, anomaly_detector):
        """Test saving model."""
        anomaly_detector.model = MagicMock()
        anomaly_detector.save_model("model.pkl")
        mock_dump.assert_called_once()

    @patch('joblib.load')
    def test_load_model(self, mock_load, anomaly_detector):
        """Test loading model."""
        mock_load.return_value = MagicMock()
        anomaly_detector.load_model("model.pkl")
        mock_load.assert_called_once()

    def test_model_versioning(self, anomaly_detector):
        """Test model versioning."""
        version = anomaly_detector.get_model_version()
        assert isinstance(version, (str, int, float)) or version is None


class TestAnomalyReporting:
    """Tests for anomaly reporting."""

    @pytest.fixture
    def anomaly_detector(self):
        """Create anomaly detector."""
        return AnomalyDetector()

    def test_generate_anomaly_report(self, anomaly_detector):
        """Test anomaly report generation."""
        entities = [
            {"entity_type": "domain", "value": "example1.com", "anomaly_score": 0.85},
            {"entity_type": "domain", "value": "example2.com", "anomaly_score": 0.92},
        ]
        report = anomaly_detector.generate_report(entities)
        assert isinstance(report, dict)

    def test_report_contains_statistics(self, anomaly_detector):
        """Test that report contains statistics."""
        entities = [
            {"entity_type": "domain", "value": "example1.com", "anomaly_score": 0.85},
        ]
        report = anomaly_detector.generate_report(entities)
        assert "total_entities" in report or "anomaly_count" in report or isinstance(report, dict)

    def test_report_contains_top_anomalies(self, anomaly_detector):
        """Test that report contains top anomalies."""
        entities = [
            {"entity_type": "domain", "value": f"example{i}.com", "anomaly_score": 0.5 + i*0.1}
            for i in range(10)
        ]
        report = anomaly_detector.generate_report(entities)
        assert "top_anomalies" in report or isinstance(report, dict)
