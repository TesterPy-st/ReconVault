"""
Risk Assessment ML Models

Implements machine learning models for risk classification using XGBoost.
Handles model training, inference, and persistence.
"""

import os
import pickle
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

import joblib
import numpy as np
import pandas as pd
import xgboost as xgb
from loguru import logger
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, f1_score
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler


class RiskMLModel:
    """
    XGBoost-based risk classification model.
    
    Predicts risk levels (low/medium/high/critical) based on entity features.
    """
    
    def __init__(self, model_dir: Optional[str] = None):
        """
        Initialize risk ML model.
        
        Args:
            model_dir: Directory for model storage
        """
        self.model_dir = model_dir or os.path.join(
            os.path.dirname(__file__), "models"
        )
        os.makedirs(self.model_dir, exist_ok=True)
        
        self.xgb_model: Optional[xgb.XGBClassifier] = None
        self.scaler: Optional[StandardScaler] = None
        self.feature_names: List[str] = []
        self.model_trained = False
        self.model_version = "1.0.0"
        
    def extract_features(self, entity: Dict[str, Any]) -> List[float]:
        """
        Extract numerical features from entity for ML model.
        
        Args:
            entity: Entity dictionary with metadata
            
        Returns:
            List of numerical features
        """
        metadata = entity.get("metadata", {})
        if isinstance(metadata, str):
            import json
            try:
                metadata = json.loads(metadata)
            except:
                metadata = {}
        
        features = []
        
        # Entity type encoding (0-15)
        entity_type_map = {
            "domain": 1, "ip_address": 2, "email": 3, "phone": 4,
            "social_handle": 5, "person": 6, "company": 7, "website": 8,
            "service": 9, "location": 10, "device": 11, "network": 12,
            "vulnerability": 13, "threat_actor": 14, "malware": 15, "indicator": 16
        }
        features.append(entity_type_map.get(entity.get("type", "").lower(), 0))
        
        # Data source count
        sources = metadata.get("sources", [])
        if isinstance(sources, list):
            features.append(len(sources))
        else:
            features.append(1)
        
        # Collection frequency (times seen)
        features.append(metadata.get("collection_count", 1))
        
        # Relationship density (if available)
        features.append(entity.get("relationship_count", 0))
        
        # Anomaly indicators
        features.append(1 if metadata.get("is_anomaly", False) else 0)
        features.append(metadata.get("anomaly_score", 0.0))
        
        # Breach history
        features.append(metadata.get("breaches_found", 0))
        
        # Dark web mentions
        features.append(1 if metadata.get("dark_web_mentions") else 0)
        
        # Malware detected
        features.append(1 if metadata.get("malware_detected") else 0)
        
        # Phishing indicator
        features.append(1 if metadata.get("phishing_indicator") else 0)
        
        # Geolocation risk factors
        high_risk_countries = ["RU", "CN", "KP", "IR"]
        country = metadata.get("country", "")
        features.append(1 if country in high_risk_countries else 0)
        
        # Domain age (days, 0 if not applicable)
        features.append(metadata.get("domain_age_days", 0))
        
        # SSL/Security indicators
        features.append(metadata.get("days_until_expiry", 365))
        features.append(1 if metadata.get("has_ssl", True) else 0)
        
        # Port exposure
        open_ports = metadata.get("open_ports", [])
        if isinstance(open_ports, list):
            features.append(len(open_ports))
            # High-risk ports exposed
            high_risk_ports = [21, 22, 23, 135, 139, 445, 3389]
            if open_ports:
                try:
                    port_nums = [p.get("port", 0) if isinstance(p, dict) else p for p in open_ports]
                    exposed_count = len([p for p in port_nums if p in high_risk_ports])
                    features.append(exposed_count)
                except:
                    features.append(0)
            else:
                features.append(0)
        else:
            features.append(0)
            features.append(0)
        
        # Confidence score
        features.append(entity.get("confidence", 1.0))
        
        # Existing risk score (if available)
        features.append(entity.get("risk_score", 0.0))
        
        # Data quality score
        features.append(metadata.get("data_quality", 0.7))
        
        return features
    
    def _get_feature_names(self) -> List[str]:
        """Get feature names for the model."""
        return [
            "entity_type_encoded",
            "data_source_count",
            "collection_frequency",
            "relationship_density",
            "is_anomaly",
            "anomaly_score",
            "breaches_found",
            "dark_web_mentions",
            "malware_detected",
            "phishing_indicator",
            "high_risk_country",
            "domain_age_days",
            "ssl_expiry_days",
            "has_ssl",
            "open_ports_count",
            "high_risk_ports_exposed",
            "confidence",
            "existing_risk_score",
            "data_quality"
        ]
    
    def train_model(
        self,
        entities: List[Dict[str, Any]],
        labels: Optional[List[int]] = None
    ) -> Dict[str, Any]:
        """
        Train XGBoost model on entity data.
        
        Args:
            entities: List of entity dictionaries
            labels: Optional risk labels (0=low, 1=medium, 2=high, 3=critical)
                   If not provided, will be generated from entity risk scores
            
        Returns:
            Training results with metrics
        """
        logger.info(f"Training risk model on {len(entities)} entities")
        
        # Extract features
        X = []
        for entity in entities:
            features = self.extract_features(entity)
            X.append(features)
        
        X = np.array(X)
        self.feature_names = self._get_feature_names()
        
        # Generate labels if not provided
        if labels is None:
            labels = []
            for entity in entities:
                risk_score = entity.get("risk_score", 0.0)
                metadata = entity.get("metadata", {})
                if isinstance(metadata, str):
                    import json
                    try:
                        metadata = json.loads(metadata)
                    except:
                        metadata = {}
                
                # Use existing risk score or calculate from metadata
                if risk_score == 0.0:
                    risk_score = metadata.get("risk_score", 0.0)
                
                # Map risk score to class (0-3)
                if risk_score >= 76:
                    label = 3  # Critical
                elif risk_score >= 51:
                    label = 2  # High
                elif risk_score >= 26:
                    label = 1  # Medium
                else:
                    label = 0  # Low
                labels.append(label)
        
        y = np.array(labels)
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        # Scale features
        self.scaler = StandardScaler()
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Train XGBoost model
        self.xgb_model = xgb.XGBClassifier(
            n_estimators=100,
            max_depth=6,
            learning_rate=0.1,
            objective="multi:softmax",
            num_class=4,
            random_state=42,
            eval_metric="mlogloss"
        )
        
        logger.info("Training XGBoost model...")
        self.xgb_model.fit(
            X_train_scaled,
            y_train,
            eval_set=[(X_test_scaled, y_test)],
            verbose=False
        )
        
        # Evaluate model
        y_pred = self.xgb_model.predict(X_test_scaled)
        accuracy = accuracy_score(y_test, y_pred)
        f1 = f1_score(y_test, y_pred, average="weighted")
        
        # Cross-validation
        cv_scores = cross_val_score(
            self.xgb_model, X_train_scaled, y_train, cv=5, scoring="f1_weighted"
        )
        
        self.model_trained = True
        
        results = {
            "success": True,
            "model_type": "XGBoost",
            "training_samples": len(X_train),
            "test_samples": len(X_test),
            "accuracy": float(accuracy),
            "f1_score": float(f1),
            "cv_mean_score": float(cv_scores.mean()),
            "cv_std_score": float(cv_scores.std()),
            "features_count": len(self.feature_names),
            "classes": ["low", "medium", "high", "critical"],
            "trained_at": datetime.utcnow().isoformat()
        }
        
        logger.info(f"Model trained successfully: accuracy={accuracy:.3f}, f1={f1:.3f}")
        return results
    
    def predict_risk(self, entity: Dict[str, Any]) -> Dict[str, Any]:
        """
        Predict risk level for an entity.
        
        Args:
            entity: Entity dictionary
            
        Returns:
            Prediction results with probabilities
        """
        if not self.model_trained or self.xgb_model is None:
            logger.warning("Model not trained, returning default prediction")
            return {
                "risk_class": 0,
                "risk_level": "low",
                "confidence": 0.5,
                "probabilities": [0.25, 0.25, 0.25, 0.25]
            }
        
        # Extract features
        features = self.extract_features(entity)
        X = np.array([features])
        
        # Scale features
        X_scaled = self.scaler.transform(X)
        
        # Predict
        risk_class = int(self.xgb_model.predict(X_scaled)[0])
        probabilities = self.xgb_model.predict_proba(X_scaled)[0].tolist()
        
        risk_levels = ["low", "medium", "high", "critical"]
        
        return {
            "risk_class": risk_class,
            "risk_level": risk_levels[risk_class],
            "confidence": float(probabilities[risk_class]),
            "probabilities": probabilities
        }
    
    def batch_predict(self, entities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Predict risk for multiple entities efficiently.
        
        Args:
            entities: List of entity dictionaries
            
        Returns:
            List of predictions
        """
        if not self.model_trained or self.xgb_model is None:
            logger.warning("Model not trained")
            return []
        
        # Extract all features
        X = []
        for entity in entities:
            features = self.extract_features(entity)
            X.append(features)
        
        X = np.array(X)
        X_scaled = self.scaler.transform(X)
        
        # Batch prediction
        risk_classes = self.xgb_model.predict(X_scaled)
        probabilities = self.xgb_model.predict_proba(X_scaled)
        
        risk_levels = ["low", "medium", "high", "critical"]
        
        results = []
        for i, entity in enumerate(entities):
            results.append({
                "entity_id": entity.get("id"),
                "risk_class": int(risk_classes[i]),
                "risk_level": risk_levels[int(risk_classes[i])],
                "confidence": float(probabilities[i][int(risk_classes[i])]),
                "probabilities": probabilities[i].tolist()
            })
        
        return results
    
    def get_feature_importance(self) -> Dict[str, float]:
        """
        Get feature importance scores.
        
        Returns:
            Dictionary of feature names to importance scores
        """
        if not self.model_trained or self.xgb_model is None:
            return {}
        
        importance = self.xgb_model.feature_importances_
        return dict(zip(self.feature_names, importance.tolist()))
    
    def save_model(self, filename: Optional[str] = None) -> str:
        """
        Save trained model to disk.
        
        Args:
            filename: Optional custom filename
            
        Returns:
            Path to saved model
        """
        if not self.model_trained:
            raise ValueError("No trained model to save")
        
        model_path = os.path.join(
            self.model_dir,
            filename or "xgboost_model.pkl"
        )
        scaler_path = os.path.join(self.model_dir, "feature_scaler.pkl")
        
        # Save model and scaler
        joblib.dump(self.xgb_model, model_path)
        joblib.dump(self.scaler, scaler_path)
        
        # Save metadata
        metadata = {
            "feature_names": self.feature_names,
            "model_version": self.model_version,
            "saved_at": datetime.utcnow().isoformat(),
            "model_type": "XGBoost"
        }
        metadata_path = os.path.join(self.model_dir, "model_metadata.pkl")
        joblib.dump(metadata, metadata_path)
        
        logger.info(f"Model saved to {model_path}")
        return model_path
    
    def load_model(self, filename: Optional[str] = None) -> bool:
        """
        Load trained model from disk.
        
        Args:
            filename: Optional custom filename
            
        Returns:
            Success status
        """
        try:
            model_path = os.path.join(
                self.model_dir,
                filename or "xgboost_model.pkl"
            )
            scaler_path = os.path.join(self.model_dir, "feature_scaler.pkl")
            metadata_path = os.path.join(self.model_dir, "model_metadata.pkl")
            
            if not os.path.exists(model_path):
                logger.warning(f"Model file not found: {model_path}")
                return False
            
            # Load model and scaler
            self.xgb_model = joblib.load(model_path)
            self.scaler = joblib.load(scaler_path)
            
            # Load metadata if available
            if os.path.exists(metadata_path):
                metadata = joblib.load(metadata_path)
                self.feature_names = metadata.get("feature_names", [])
                self.model_version = metadata.get("model_version", "1.0.0")
            
            self.model_trained = True
            logger.info(f"Model loaded from {model_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            return False


def generate_synthetic_training_data(n_samples: int = 1000) -> Tuple[List[Dict[str, Any]], List[int]]:
    """
    Generate synthetic training data for model development.
    
    Args:
        n_samples: Number of samples to generate
        
    Returns:
        Tuple of (entities, labels)
    """
    entities = []
    labels = []
    
    entity_types = ["domain", "ip_address", "email", "phone", "social_handle", "person"]
    
    for i in range(n_samples):
        # Randomly generate risk level
        risk_level = np.random.choice([0, 1, 2, 3], p=[0.4, 0.3, 0.2, 0.1])
        
        # Generate features based on risk level
        entity = {
            "id": i,
            "type": np.random.choice(entity_types),
            "value": f"entity_{i}",
            "confidence": np.random.uniform(0.6, 1.0),
            "risk_score": risk_level * 25 + np.random.uniform(0, 20),
            "relationship_count": np.random.randint(0, 20),
            "metadata": {
                "sources": ["source"] * np.random.randint(1, 5),
                "collection_count": np.random.randint(1, 10),
                "is_anomaly": risk_level >= 2 and np.random.random() > 0.5,
                "anomaly_score": np.random.uniform(-1, 1) if risk_level >= 2 else 0,
                "breaches_found": np.random.randint(0, 5) if risk_level >= 1 else 0,
                "dark_web_mentions": risk_level >= 2 and np.random.random() > 0.6,
                "malware_detected": risk_level >= 3 and np.random.random() > 0.7,
                "phishing_indicator": risk_level >= 2 and np.random.random() > 0.5,
                "country": np.random.choice(["US", "GB", "DE", "RU", "CN"]),
                "domain_age_days": np.random.randint(0, 3650),
                "days_until_expiry": np.random.randint(0, 365),
                "has_ssl": np.random.random() > 0.2,
                "open_ports": [{"port": p} for p in np.random.choice([80, 443, 22, 3389], size=np.random.randint(0, 4), replace=False).tolist()],
                "data_quality": np.random.uniform(0.5, 1.0)
            }
        }
        
        entities.append(entity)
        labels.append(risk_level)
    
    return entities, labels
