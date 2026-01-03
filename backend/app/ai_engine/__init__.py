"""
ReconVault AI Engine Module

This module handles AI-powered anomaly detection and analysis.

Components:
- models: ML model definitions (Isolation Forest, LSTM Autoencoder)
- feature_engineering: Feature extraction from entities and relationships
- training: Model training pipeline with evaluation
- inference: Real-time anomaly detection inference engine
- anomaly_classifier: Anomaly type classification and severity assessment
"""

from app.ai_engine.anomaly_classifier import AnomalyClassifier, AnomalySeverity, AnomalyType, get_anomaly_classifier
from app.ai_engine.feature_engineering import (
    EntityFeatureExtractor,
    RelationshipFeatureExtractor,
    SequenceFeatureExtractor,
    get_feature_names,
)
from app.ai_engine.inference import AnomalyInferenceEngine, InferenceConfig, get_inference_engine
from app.ai_engine.models import (
    BehavioralAnomalyDetector,
    EntityAnomalyDetector,
    LSTMAutoencoder,
    ModelPersistence,
    RelationshipAnomalyDetector,
    StatisticalAnomalyDetector,
)
from app.ai_engine.training import ModelTrainer, TrainingConfig, train_models_cli

__all__ = [
    # Models
    "EntityAnomalyDetector",
    "RelationshipAnomalyDetector",
    "BehavioralAnomalyDetector",
    "StatisticalAnomalyDetector",
    "LSTMAutoencoder",
    "ModelPersistence",
    # Feature Engineering
    "EntityFeatureExtractor",
    "RelationshipFeatureExtractor",
    "SequenceFeatureExtractor",
    "get_feature_names",
    # Training
    "ModelTrainer",
    "TrainingConfig",
    "train_models_cli",
    # Inference
    "AnomalyInferenceEngine",
    "InferenceConfig",
    "get_inference_engine",
    # Classification
    "AnomalyClassifier",
    "AnomalyType",
    "AnomalySeverity",
    "get_anomaly_classifier",
]


class AIEngine:
    """Legacy base class for AI engine operations - kept for backward compatibility"""

    def __init__(self):
        self.models = {}

    def analyze(self, data: dict) -> dict:
        """Analyze data using AI models"""
        raise NotImplementedError("Use AnomalyInferenceEngine.detect_entity_anomaly() instead")

    def predict(self, input_data: dict) -> dict:
        """Make predictions using trained models"""
        raise NotImplementedError("Use AnomalyInferenceEngine for predictions")
