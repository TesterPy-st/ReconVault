"""
ReconVault Real-Time Anomaly Detection Inference Engine

This module provides real-time anomaly detection using pre-trained models,
with caching, batch processing, and fallback mechanisms.
"""

import json
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

import numpy as np
from loguru import logger
from sqlalchemy.orm import Session

try:
    import redis

    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    logger.warning("Redis not available for caching")

try:
    import shap

    SHAP_AVAILABLE = True
except ImportError:
    SHAP_AVAILABLE = False

from app.ai_engine.feature_engineering import (EntityFeatureExtractor,
                                               RelationshipFeatureExtractor,
                                               SequenceFeatureExtractor,
                                               get_feature_names)
from app.ai_engine.models import (BehavioralAnomalyDetector,
                                  EntityAnomalyDetector, ModelPersistence,
                                  RelationshipAnomalyDetector,
                                  StatisticalAnomalyDetector)
from app.models.entity import Entity
from app.models.relationship import Relationship


class InferenceConfig:
    """Configuration for inference engine."""

    def __init__(
        self,
        models_dir: Path = Path("backend/app/ai_engine/models/v1.0"),
        cache_ttl: int = 3600,
        enable_caching: bool = True,
        fallback_to_rules: bool = True,
        batch_size: int = 100,
    ):
        """Initialize inference configuration."""
        self.models_dir = Path(models_dir)
        self.cache_ttl = cache_ttl
        self.enable_caching = enable_caching and REDIS_AVAILABLE
        self.fallback_to_rules = fallback_to_rules
        self.batch_size = batch_size


class AnomalyInferenceEngine:
    """Main inference engine for anomaly detection."""

    def __init__(
        self,
        db: Session,
        config: Optional[InferenceConfig] = None,
        redis_client: Optional[Any] = None,
    ):
        """
        Initialize inference engine.

        Args:
            db: Database session
            config: Inference configuration
            redis_client: Redis client for caching
        """
        self.db = db
        self.config = config or InferenceConfig()
        self.redis_client = redis_client

        # Model instances
        self.entity_detector: Optional[EntityAnomalyDetector] = None
        self.relationship_detector: Optional[RelationshipAnomalyDetector] = None
        self.behavioral_detector: Optional[BehavioralAnomalyDetector] = None

        # Feature extractors
        self.entity_extractor = EntityFeatureExtractor(db)
        self.relationship_extractor = RelationshipFeatureExtractor(db)
        self.sequence_extractor = SequenceFeatureExtractor(db)

        # Statistics
        self.inference_count = 0
        self.cache_hits = 0
        self.cache_misses = 0

        # Load models
        self.load_models()

    def load_models(self) -> None:
        """Load pre-trained models from disk."""
        logger.info("Loading anomaly detection models...")

        try:
            # Load entity detector
            entity_model_path = self.config.models_dir / "isolation_forest_entity.pkl"
            if entity_model_path.exists():
                model, scaler, metadata = ModelPersistence.load_sklearn_model(
                    entity_model_path
                )
                self.entity_detector = EntityAnomalyDetector()
                self.entity_detector.model = model
                self.entity_detector.scaler = scaler
                self.entity_detector.is_fitted = True
                self.entity_detector.feature_names = metadata.get("features", [])
                logger.info("Entity detector loaded successfully")
            else:
                logger.warning(f"Entity detector not found at {entity_model_path}")
        except Exception as e:
            logger.error(f"Failed to load entity detector: {e}")

        try:
            # Load relationship detector
            rel_model_path = (
                self.config.models_dir / "isolation_forest_relationship.pkl"
            )
            if rel_model_path.exists():
                model, scaler, metadata = ModelPersistence.load_sklearn_model(
                    rel_model_path
                )
                self.relationship_detector = RelationshipAnomalyDetector()
                self.relationship_detector.model = model
                self.relationship_detector.scaler = scaler
                self.relationship_detector.is_fitted = True
                self.relationship_detector.feature_names = metadata.get("features", [])
                logger.info("Relationship detector loaded successfully")
            else:
                logger.warning(f"Relationship detector not found at {rel_model_path}")
        except Exception as e:
            logger.error(f"Failed to load relationship detector: {e}")

        try:
            # Load behavioral detector
            behavioral_model_path = self.config.models_dir / "lstm_autoencoder.pt"
            threshold_path = self.config.models_dir / "lstm_threshold.json"

            if behavioral_model_path.exists():
                model, scaler, metadata = ModelPersistence.load_pytorch_model(
                    behavioral_model_path
                )
                self.behavioral_detector = BehavioralAnomalyDetector()
                self.behavioral_detector.model = model
                self.behavioral_detector.scaler = scaler
                self.behavioral_detector.is_fitted = True

                # Load threshold
                if threshold_path.exists():
                    with open(threshold_path, "r") as f:
                        threshold_data = json.load(f)
                        self.behavioral_detector.threshold = threshold_data.get(
                            "threshold", 0.1
                        )

                logger.info("Behavioral detector loaded successfully")
            else:
                logger.warning(
                    f"Behavioral detector not found at {behavioral_model_path}"
                )
        except Exception as e:
            logger.error(f"Failed to load behavioral detector: {e}")

        logger.info("Model loading complete")

    def detect_entity_anomaly(
        self, entity: Entity, use_cache: bool = True
    ) -> Dict[str, Any]:
        """
        Detect if an entity is anomalous.

        Args:
            entity: Entity to analyze
            use_cache: Whether to use cache

        Returns:
            Dictionary with detection results
        """
        start_time = time.time()
        self.inference_count += 1

        # Check cache
        if use_cache and self.config.enable_caching and self.redis_client:
            cache_key = f"anomaly:entity:{entity.id}"
            cached_result = self._get_from_cache(cache_key)
            if cached_result:
                self.cache_hits += 1
                return cached_result
            self.cache_misses += 1

        # Extract features
        features = self.entity_extractor.extract(entity)

        # Detect using ML model
        if self.entity_detector and self.entity_detector.is_fitted:
            is_anomaly, anomaly_score = self.entity_detector.predict_single(features)
            confidence = 0.9  # High confidence for ML-based detection
            detection_method = "isolation_forest"
        elif self.config.fallback_to_rules:
            # Fallback to rule-based detection
            is_anomaly, anomaly_score = self._rule_based_entity_detection(
                entity, features
            )
            confidence = 0.6  # Lower confidence for rule-based
            detection_method = "rule_based"
        else:
            # No detection available
            is_anomaly = False
            anomaly_score = 0.0
            confidence = 0.0
            detection_method = "none"

        # Feature importance (SHAP)
        explanation = (
            self._explain_entity_anomaly(features, entity) if is_anomaly else {}
        )

        result = {
            "entity_id": entity.id,
            "is_anomalous": is_anomaly,
            "anomaly_score": float(anomaly_score),
            "confidence": confidence,
            "detection_method": detection_method,
            "explanation": explanation,
            "inference_time_ms": (time.time() - start_time) * 1000,
            "detected_at": datetime.utcnow().isoformat(),
        }

        # Cache result
        if use_cache and self.config.enable_caching and self.redis_client:
            self._set_cache(cache_key, result, self.config.cache_ttl)

        return result

    def detect_relationship_anomaly(
        self, relationship: Relationship, use_cache: bool = True
    ) -> Dict[str, Any]:
        """
        Detect if a relationship is anomalous.

        Args:
            relationship: Relationship to analyze
            use_cache: Whether to use cache

        Returns:
            Dictionary with detection results
        """
        start_time = time.time()
        self.inference_count += 1

        # Check cache
        if use_cache and self.config.enable_caching and self.redis_client:
            cache_key = f"anomaly:relationship:{relationship.id}"
            cached_result = self._get_from_cache(cache_key)
            if cached_result:
                self.cache_hits += 1
                return cached_result
            self.cache_misses += 1

        # Extract features
        features = self.relationship_extractor.extract(relationship)

        # Detect using ML model
        if self.relationship_detector and self.relationship_detector.is_fitted:
            is_anomaly, anomaly_score = self.relationship_detector.predict_single(
                features
            )
            confidence = 0.85
            detection_method = "isolation_forest"
        elif self.config.fallback_to_rules:
            is_anomaly, anomaly_score = self._rule_based_relationship_detection(
                relationship
            )
            confidence = 0.6
            detection_method = "rule_based"
        else:
            is_anomaly = False
            anomaly_score = 0.0
            confidence = 0.0
            detection_method = "none"

        result = {
            "relationship_id": relationship.id,
            "is_anomalous": is_anomaly,
            "anomaly_score": float(anomaly_score),
            "confidence": confidence,
            "detection_method": detection_method,
            "inference_time_ms": (time.time() - start_time) * 1000,
            "detected_at": datetime.utcnow().isoformat(),
        }

        # Cache result
        if use_cache and self.config.enable_caching and self.redis_client:
            self._set_cache(cache_key, result, self.config.cache_ttl)

        return result

    def detect_behavioral_anomaly(
        self, entity: Entity, use_cache: bool = True
    ) -> Dict[str, Any]:
        """
        Detect behavioral anomalies using LSTM autoencoder.

        Args:
            entity: Entity to analyze
            use_cache: Whether to use cache

        Returns:
            Dictionary with detection results
        """
        start_time = time.time()

        # Extract sequence
        sequence = self.sequence_extractor.extract(entity)

        # Detect using LSTM
        if self.behavioral_detector and self.behavioral_detector.is_fitted:
            is_anomaly, anomaly_score = self.behavioral_detector.predict_single(
                sequence
            )
            confidence = 0.80
            detection_method = "lstm_autoencoder"
        else:
            is_anomaly = False
            anomaly_score = 0.0
            confidence = 0.0
            detection_method = "none"

        result = {
            "entity_id": entity.id,
            "is_anomalous": is_anomaly,
            "anomaly_score": float(anomaly_score),
            "confidence": confidence,
            "detection_method": detection_method,
            "inference_time_ms": (time.time() - start_time) * 1000,
            "detected_at": datetime.utcnow().isoformat(),
        }

        return result

    def detect_batch(self, entities: List[Entity]) -> List[Dict[str, Any]]:
        """
        Batch anomaly detection for multiple entities.

        Args:
            entities: List of entities

        Returns:
            List of detection results
        """
        logger.info(f"Running batch detection on {len(entities)} entities")
        start_time = time.time()

        results = []
        for entity in entities:
            result = self.detect_entity_anomaly(entity, use_cache=True)
            results.append(result)

        total_time = time.time() - start_time
        logger.info(
            f"Batch detection complete: {len(entities)} entities in {total_time:.2f}s "
            f"({total_time/len(entities)*1000:.2f}ms per entity)"
        )

        return results

    def _rule_based_entity_detection(
        self, entity: Entity, features: np.ndarray
    ) -> Tuple[bool, float]:
        """
        Fallback rule-based anomaly detection for entities.

        Args:
            entity: Entity to analyze
            features: Extracted features

        Returns:
            Tuple of (is_anomaly, anomaly_score)
        """
        anomaly_score = 0.0

        # Rule 1: High risk + low confidence
        if entity.risk_score > 0.7 and entity.confidence < 0.4:
            anomaly_score += 0.4

        # Rule 2: Unusually high degree
        relationship_count = entity.relationship_count
        if relationship_count > 50:
            anomaly_score += 0.3

        # Rule 3: Low metadata richness + high risk
        if not entity.metadata and entity.risk_score > 0.5:
            anomaly_score += 0.2

        # Rule 4: Multiple suspicious tags
        tags = entity.get_tags()
        suspicious_tags = ["suspicious", "anomaly", "threat", "malicious"]
        if any(tag.lower() in suspicious_tags for tag in tags):
            anomaly_score += 0.3

        anomaly_score = min(1.0, anomaly_score)
        is_anomaly = anomaly_score > 0.5

        return is_anomaly, anomaly_score

    def _rule_based_relationship_detection(
        self, relationship: Relationship
    ) -> Tuple[bool, float]:
        """
        Fallback rule-based anomaly detection for relationships.

        Args:
            relationship: Relationship to analyze

        Returns:
            Tuple of (is_anomaly, anomaly_score)
        """
        anomaly_score = 0.0

        # Rule 1: Very low confidence
        if relationship.confidence < 0.2:
            anomaly_score += 0.5

        # Rule 2: Mismatched entity risk scores
        if relationship.source_entity and relationship.target_entity:
            risk_diff = abs(
                relationship.source_entity.risk_score
                - relationship.target_entity.risk_score
            )
            if risk_diff > 0.6:
                anomaly_score += 0.3

        # Rule 3: Unusual relationship type
        unusual_types = ["targets", "exploits", "compromises"]
        if relationship.type in unusual_types:
            anomaly_score += 0.2

        anomaly_score = min(1.0, anomaly_score)
        is_anomaly = anomaly_score > 0.5

        return is_anomaly, anomaly_score

    def _explain_entity_anomaly(
        self, features: np.ndarray, entity: Entity
    ) -> Dict[str, Any]:
        """
        Generate explanation for entity anomaly using SHAP or simple feature importance.

        Args:
            features: Feature vector
            entity: Entity object

        Returns:
            Dictionary with explanation
        """
        if not self.entity_detector or not self.entity_detector.is_fitted:
            return {}

        feature_names = get_feature_names("entity")

        # Simple feature importance (top contributing features)
        # In production, use SHAP for better explanations
        feature_values = dict(zip(feature_names, features))

        # Find top anomalous features (heuristic: extreme values)
        mean_features = np.abs(features)
        top_indices = np.argsort(mean_features)[-5:][::-1]

        top_features = {
            feature_names[i]: {
                "value": float(features[i]),
                "contribution": float(mean_features[i]),
            }
            for i in top_indices
        }

        return {
            "method": "feature_importance",
            "top_features": top_features,
            "all_features": {k: float(v) for k, v in feature_values.items()},
        }

    def _get_from_cache(self, key: str) -> Optional[Dict[str, Any]]:
        """Get result from cache."""
        if not self.redis_client:
            return None

        try:
            cached = self.redis_client.get(key)
            if cached:
                return json.loads(cached)
        except Exception as e:
            logger.warning(f"Cache retrieval failed: {e}")

        return None

    def _set_cache(self, key: str, value: Dict[str, Any], ttl: int) -> None:
        """Set result in cache."""
        if not self.redis_client:
            return

        try:
            self.redis_client.setex(key, ttl, json.dumps(value))
        except Exception as e:
            logger.warning(f"Cache write failed: {e}")

    def get_statistics(self) -> Dict[str, Any]:
        """Get inference engine statistics."""
        cache_hit_rate = (
            self.cache_hits / (self.cache_hits + self.cache_misses)
            if (self.cache_hits + self.cache_misses) > 0
            else 0.0
        )

        return {
            "inference_count": self.inference_count,
            "cache_hits": self.cache_hits,
            "cache_misses": self.cache_misses,
            "cache_hit_rate": cache_hit_rate,
            "models_loaded": {
                "entity_detector": self.entity_detector is not None
                and self.entity_detector.is_fitted,
                "relationship_detector": self.relationship_detector is not None
                and self.relationship_detector.is_fitted,
                "behavioral_detector": self.behavioral_detector is not None
                and self.behavioral_detector.is_fitted,
            },
        }


# Global inference engine instance (lazy loading)
_inference_engine: Optional[AnomalyInferenceEngine] = None


def get_inference_engine(
    db: Session, redis_client: Optional[Any] = None
) -> AnomalyInferenceEngine:
    """
    Get or create global inference engine instance.

    Args:
        db: Database session
        redis_client: Redis client

    Returns:
        Inference engine instance
    """
    global _inference_engine

    if _inference_engine is None:
        _inference_engine = AnomalyInferenceEngine(db, redis_client=redis_client)

    return _inference_engine
