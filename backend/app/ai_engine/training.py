"""
ReconVault Model Training Pipeline

This module handles training of anomaly detection models with data preparation,
hyperparameter tuning, cross-validation, and model evaluation.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
from loguru import logger
from sklearn.metrics import (classification_report, f1_score, precision_score,
                             recall_score, roc_auc_score)
from sklearn.model_selection import cross_val_score, train_test_split
from sqlalchemy.orm import Session

try:
    import optuna

    OPTUNA_AVAILABLE = True
except ImportError:
    OPTUNA_AVAILABLE = False
    logger.warning("Optuna not available for hyperparameter tuning")

try:
    import shap

    SHAP_AVAILABLE = True
except ImportError:
    SHAP_AVAILABLE = False
    logger.warning("SHAP not available for feature importance")

from app.ai_engine.feature_engineering import (EntityFeatureExtractor,
                                               RelationshipFeatureExtractor,
                                               SequenceFeatureExtractor,
                                               get_feature_names)
from app.ai_engine.models import (BehavioralAnomalyDetector,
                                  EntityAnomalyDetector, ModelPersistence,
                                  RelationshipAnomalyDetector)
from app.models.entity import Entity
from app.models.relationship import Relationship


class TrainingConfig:
    """Configuration for model training."""

    def __init__(
        self,
        model_version: str = "v1.0",
        models_dir: Path = Path("backend/app/ai_engine/models"),
        min_training_samples: int = 100,
        test_size: float = 0.2,
        validation_size: float = 0.1,
        random_state: int = 42,
        cv_folds: int = 5,
        enable_optuna: bool = False,
        optuna_trials: int = 20,
    ):
        """Initialize training configuration."""
        self.model_version = model_version
        self.models_dir = Path(models_dir) / model_version
        self.min_training_samples = min_training_samples
        self.test_size = test_size
        self.validation_size = validation_size
        self.random_state = random_state
        self.cv_folds = cv_folds
        self.enable_optuna = enable_optuna and OPTUNA_AVAILABLE
        self.optuna_trials = optuna_trials

        # Create models directory
        self.models_dir.mkdir(parents=True, exist_ok=True)


class ModelTrainer:
    """Main trainer class for anomaly detection models."""

    def __init__(self, db: Session, config: Optional[TrainingConfig] = None):
        """
        Initialize model trainer.

        Args:
            db: Database session
            config: Training configuration
        """
        self.db = db
        self.config = config or TrainingConfig()
        self.training_history: Dict[str, Any] = {}

    def prepare_entity_data(
        self, limit: Optional[int] = None
    ) -> Tuple[np.ndarray, np.ndarray, List[str]]:
        """
        Prepare entity data for training.

        Args:
            limit: Maximum number of entities to fetch (None for all)

        Returns:
            Tuple of (features, labels, feature_names)
        """
        logger.info("Preparing entity training data...")

        # Fetch entities
        query = self.db.query(Entity).filter(Entity.is_active == True)
        if limit:
            query = query.limit(limit)

        entities = query.all()

        if len(entities) < self.config.min_training_samples:
            raise ValueError(
                f"Insufficient training data: {len(entities)} entities "
                f"(minimum: {self.config.min_training_samples})"
            )

        logger.info(f"Fetched {len(entities)} entities for training")

        # Extract features
        extractor = EntityFeatureExtractor(self.db)
        features = extractor.extract_batch(entities)

        # Generate labels (for training, we need labeled anomalies)
        # In production, this should come from expert labeling or known anomalies
        # For now, we use a heuristic: high risk score + low confidence = anomaly
        labels = np.array(
            [
                1
                if (e.risk_score > 0.7 and e.confidence < 0.5)
                or e.get_tags()
                and "anomaly" in ",".join(e.get_tags()).lower()
                else 0
                for e in entities
            ]
        )

        # Handle class imbalance: oversample anomalies to 20%
        anomaly_indices = np.where(labels == 1)[0]
        normal_indices = np.where(labels == 0)[0]

        anomaly_ratio = len(anomaly_indices) / len(labels)
        logger.info(f"Original anomaly ratio: {anomaly_ratio:.2%}")

        if anomaly_ratio < 0.05:
            logger.warning("Very low anomaly ratio, oversampling anomalies...")
            # Oversample anomalies
            target_anomaly_count = int(len(normal_indices) * 0.25)
            if len(anomaly_indices) > 0:
                oversample_indices = np.random.choice(
                    anomaly_indices,
                    size=target_anomaly_count - len(anomaly_indices),
                    replace=True,
                )
                features = np.vstack([features, features[oversample_indices]])
                labels = np.concatenate([labels, labels[oversample_indices]])
                logger.info(f"Oversampled to {len(labels)} total samples")

        feature_names = get_feature_names("entity")

        return features, labels, feature_names

    def train_entity_detector(
        self, n_estimators: int = 100, contamination: float = 0.1
    ) -> EntityAnomalyDetector:
        """
        Train entity anomaly detector.

        Args:
            n_estimators: Number of trees in isolation forest
            contamination: Expected proportion of anomalies

        Returns:
            Trained detector
        """
        logger.info("Training Entity Anomaly Detector...")

        # Prepare data
        X, y, feature_names = self.prepare_entity_data()

        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X,
            y,
            test_size=self.config.test_size,
            random_state=self.config.random_state,
            stratify=y if len(np.unique(y)) > 1 else None,
        )

        # Train model
        detector = EntityAnomalyDetector(
            n_estimators=n_estimators,
            contamination=contamination,
            random_state=self.config.random_state,
        )
        detector.fit(X_train, feature_names)

        # Evaluate
        metrics = self._evaluate_detector(detector, X_test, y_test, "Entity")

        # Save model
        metadata = {
            "model_type": "entity_anomaly_detector",
            "training_samples": len(X_train),
            "test_samples": len(X_test),
            "features": feature_names,
            "metrics": metrics,
            "hyperparameters": {
                "n_estimators": n_estimators,
                "contamination": contamination,
            },
        }

        model_path = self.config.models_dir / "isolation_forest_entity.pkl"
        ModelPersistence.save_sklearn_model(
            detector.model, detector.scaler, model_path, metadata
        )

        # Save metadata separately
        metadata_path = self.config.models_dir / "entity_detector_metadata.json"
        with open(metadata_path, "w") as f:
            json.dump(metadata, f, indent=2)

        self.training_history["entity_detector"] = metadata

        return detector

    def train_relationship_detector(
        self, n_estimators: int = 100, contamination: float = 0.1
    ) -> RelationshipAnomalyDetector:
        """
        Train relationship anomaly detector.

        Args:
            n_estimators: Number of trees
            contamination: Expected proportion of anomalies

        Returns:
            Trained detector
        """
        logger.info("Training Relationship Anomaly Detector...")

        # Fetch relationships
        relationships = self.db.query(Relationship).limit(5000).all()

        if len(relationships) < self.config.min_training_samples:
            logger.warning(
                f"Insufficient relationship data: {len(relationships)}. "
                f"Training with available data."
            )
            if len(relationships) < 10:
                raise ValueError("Cannot train with fewer than 10 relationships")

        # Extract features
        extractor = RelationshipFeatureExtractor(self.db)
        X = extractor.extract_batch(relationships)

        # Generate labels (heuristic)
        y = np.array([1 if r.confidence < 0.3 else 0 for r in relationships])

        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=self.config.test_size, random_state=self.config.random_state
        )

        # Train model
        detector = RelationshipAnomalyDetector(
            n_estimators=n_estimators,
            contamination=contamination,
            random_state=self.config.random_state,
        )
        feature_names = get_feature_names("relationship")
        detector.fit(X_train, feature_names)

        # Evaluate
        metrics = self._evaluate_detector(detector, X_test, y_test, "Relationship")

        # Save model
        metadata = {
            "model_type": "relationship_anomaly_detector",
            "training_samples": len(X_train),
            "test_samples": len(X_test),
            "features": feature_names,
            "metrics": metrics,
        }

        model_path = self.config.models_dir / "isolation_forest_relationship.pkl"
        ModelPersistence.save_sklearn_model(
            detector.model, detector.scaler, model_path, metadata
        )

        self.training_history["relationship_detector"] = metadata

        return detector

    def train_behavioral_detector(
        self, epochs: int = 50, batch_size: int = 32, learning_rate: float = 0.001
    ) -> BehavioralAnomalyDetector:
        """
        Train behavioral anomaly detector (LSTM Autoencoder).

        Args:
            epochs: Number of training epochs
            batch_size: Batch size
            learning_rate: Learning rate

        Returns:
            Trained detector
        """
        logger.info("Training Behavioral Anomaly Detector...")

        # Fetch entities
        entities = (
            self.db.query(Entity).filter(Entity.is_active == True).limit(1000).all()
        )

        if len(entities) < self.config.min_training_samples:
            logger.warning(
                f"Insufficient entity data for behavioral training: {len(entities)}"
            )
            if len(entities) < 10:
                raise ValueError("Cannot train with fewer than 10 entities")

        # Extract sequences
        extractor = SequenceFeatureExtractor(self.db)
        X = extractor.extract_batch(entities)

        # Split data
        X_train, X_test = train_test_split(
            X, test_size=self.config.test_size, random_state=self.config.random_state
        )

        # Train model
        detector = BehavioralAnomalyDetector(sequence_length=50, n_features=15)
        detector.fit(
            X_train, epochs=epochs, batch_size=batch_size, learning_rate=learning_rate
        )

        # Evaluate
        anomaly_count = 0
        scores = []
        for seq in X_test:
            is_anomaly, score = detector.predict_single(seq)
            if is_anomaly:
                anomaly_count += 1
            scores.append(score)

        metrics = {
            "test_samples": len(X_test),
            "detected_anomalies": anomaly_count,
            "anomaly_rate": anomaly_count / len(X_test),
            "avg_anomaly_score": float(np.mean(scores)),
            "threshold": float(detector.threshold),
        }

        logger.info(f"Behavioral detector metrics: {metrics}")

        # Save model
        metadata = {
            "model_type": "behavioral_anomaly_detector",
            "training_samples": len(X_train),
            "test_samples": len(X_test),
            "metrics": metrics,
            "hyperparameters": {
                "epochs": epochs,
                "batch_size": batch_size,
                "learning_rate": learning_rate,
                "sequence_length": 50,
                "n_features": 15,
            },
        }

        model_path = self.config.models_dir / "lstm_autoencoder.pt"
        ModelPersistence.save_pytorch_model(
            detector.model, detector.scaler, model_path, metadata
        )

        # Also save detector threshold
        threshold_path = self.config.models_dir / "lstm_threshold.json"
        with open(threshold_path, "w") as f:
            json.dump({"threshold": float(detector.threshold)}, f)

        self.training_history["behavioral_detector"] = metadata

        return detector

    def train_all_models(self) -> Dict[str, Any]:
        """
        Train all anomaly detection models.

        Returns:
            Dictionary with training results
        """
        logger.info("Starting training of all anomaly detection models...")

        results = {}

        try:
            # Train entity detector
            entity_detector = self.train_entity_detector()
            results["entity_detector"] = "success"
        except Exception as e:
            logger.error(f"Entity detector training failed: {e}")
            results["entity_detector"] = f"failed: {str(e)}"

        try:
            # Train relationship detector
            rel_detector = self.train_relationship_detector()
            results["relationship_detector"] = "success"
        except Exception as e:
            logger.error(f"Relationship detector training failed: {e}")
            results["relationship_detector"] = f"failed: {str(e)}"

        try:
            # Train behavioral detector
            behavioral_detector = self.train_behavioral_detector()
            results["behavioral_detector"] = "success"
        except Exception as e:
            logger.error(f"Behavioral detector training failed: {e}")
            results["behavioral_detector"] = f"failed: {str(e)}"

        # Save training metadata
        training_metadata = {
            "training_date": datetime.utcnow().isoformat(),
            "model_version": self.config.model_version,
            "results": results,
            "history": self.training_history,
        }

        metadata_path = self.config.models_dir / "training_metadata.json"
        with open(metadata_path, "w") as f:
            json.dump(training_metadata, f, indent=2)

        logger.info("All models training complete")
        logger.info(f"Results: {results}")

        return training_metadata

    def _evaluate_detector(
        self, detector: Any, X_test: np.ndarray, y_test: np.ndarray, detector_name: str
    ) -> Dict[str, float]:
        """
        Evaluate anomaly detector.

        Args:
            detector: Trained detector
            X_test: Test features
            y_test: Test labels
            detector_name: Name for logging

        Returns:
            Dictionary of evaluation metrics
        """
        logger.info(f"Evaluating {detector_name} detector...")

        # Predict
        predictions, scores = detector.predict(X_test)

        # Convert predictions: -1 (anomaly) -> 1, 1 (normal) -> 0
        y_pred = np.where(predictions == -1, 1, 0)

        # Calculate metrics
        try:
            precision = precision_score(y_test, y_pred, zero_division=0)
            recall = recall_score(y_test, y_pred, zero_division=0)
            f1 = f1_score(y_test, y_pred, zero_division=0)

            # ROC-AUC (if we have both classes)
            if len(np.unique(y_test)) > 1:
                # Use anomaly scores for ROC-AUC
                roc_auc = roc_auc_score(
                    y_test, -scores
                )  # Negative because lower score = more anomalous
            else:
                roc_auc = 0.0

            metrics = {
                "precision": float(precision),
                "recall": float(recall),
                "f1_score": float(f1),
                "roc_auc": float(roc_auc),
            }

            logger.info(f"{detector_name} detector metrics: {metrics}")

            return metrics

        except Exception as e:
            logger.error(f"Error calculating metrics: {e}")
            return {
                "precision": 0.0,
                "recall": 0.0,
                "f1_score": 0.0,
                "roc_auc": 0.0,
                "error": str(e),
            }


def train_models_cli(db: Session, model_version: str = "v1.0") -> None:
    """
    CLI function to train all models.

    Args:
        db: Database session
        model_version: Model version string
    """
    config = TrainingConfig(model_version=model_version)
    trainer = ModelTrainer(db, config)

    try:
        results = trainer.train_all_models()
        logger.info("Training completed successfully!")
        logger.info(f"Models saved to: {config.models_dir}")
        return results
    except Exception as e:
        logger.error(f"Training failed: {e}")
        raise
