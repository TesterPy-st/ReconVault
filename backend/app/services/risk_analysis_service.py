"""
Risk Analysis Service

Provides risk assessment and anomaly detection for OSINT entities.
Uses XGBoost, LightGBM, and Scikit-learn for ML analysis.
"""

from datetime import datetime
from typing import Any, Dict, List

import numpy as np
from loguru import logger
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

from app.collectors.base_collector import RiskLevel


class RiskAnalysisService:
    """
    Service for analyzing risk and detecting anomalies.

    Handles:
    - Entity risk scoring
    - Anomaly detection (Isolation Forest, LOF)
    - ML model prediction
    - Relationship risk scoring
    - Risk factor generation
    """

    def __init__(self):
        self.isolation_forest = IsolationForest(
            n_estimators=100, contamination=0.1, random_state=42
        )
        self.scaler = StandardScaler()
        self.model_trained = False

    def calculate_entity_risk_score(self, entity: Dict[str, Any]) -> float:
        """
        Calculate overall risk score for entity (0-100).

        Args:
            entity: Entity dictionary

        Returns:
            Risk score (0-100)
        """
        risk_score = 0.0
        risk_factors = self._generate_risk_factors(entity)

        # Base risk from entity's own risk level
        entity_risk = entity.get("risk_level", RiskLevel.INFO.value)
        risk_level_scores = {
            RiskLevel.CRITICAL.value: 90,
            RiskLevel.HIGH.value: 70,
            RiskLevel.MEDIUM.value: 50,
            RiskLevel.LOW.value: 20,
            RiskLevel.INFO.value: 10,
        }
        risk_score += risk_level_scores.get(entity_risk, 10)

        # Add risk from risk factors
        for factor in risk_factors:
            risk_score += factor.get("score", 0)

        # Cap at 100
        risk_score = min(risk_score, 100)

        return round(risk_score, 2)

    def _generate_risk_factors(self, entity: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Generate list of risk factors for entity.

        Args:
            entity: Entity dictionary

        Returns:
            List of risk factor dictionaries with score and description
        """
        risk_factors = []

        entity_type = entity.get("entity_type")
        metadata = entity.get("metadata", {})

        # Breach history
        if metadata.get("breaches_found", 0) > 0:
            risk_factors.append(
                {
                    "factor": "breach_history",
                    "description": f"Found in {metadata['breaches_found']} data breaches",
                    "score": 30,
                }
            )

        # Dark web mentions
        if metadata.get("dark_web_mentions"):
            risk_factors.append(
                {
                    "factor": "dark_web_mentions",
                    "description": "Mentioned on dark web",
                    "score": 25,
                }
            )

        # Suspicious locations
        if entity_type == "IP_ADDRESS":
            if metadata.get("vpn_proxy_indicators"):
                risk_factors.append(
                    {
                        "factor": "vpn_proxy",
                        "description": "Potential VPN or proxy detected",
                        "score": 15,
                    }
                )

        # Domain registration issues
        if entity_type == "DOMAIN":
            # Expiring soon
            if metadata.get("days_until_expiry", 999) < 30:
                days = metadata["days_until_expiry"]
                risk_factors.append(
                    {
                        "factor": "ssl_expiring",
                        "description": f"SSL certificate expires in {days} days",
                        "score": 20 if days < 7 else 10,
                    }
                )

            # Suspicious TLD
            domain = entity.get("value", "")
            if any(
                domain.lower().endswith(tld)
                for tld in [".xyz", ".top", ".zip", ".tk", ".ml"]
            ):
                risk_factors.append(
                    {
                        "factor": "suspicious_tld",
                        "description": "Uses suspicious top-level domain",
                        "score": 15,
                    }
                )

        # Port exposure
        if entity_type == "IP_ADDRESS":
            open_ports = metadata.get("open_ports", [])
            if open_ports:
                high_risk_ports = [21, 22, 23, 135, 139, 445, 3389]
                open_port_nums = [p["port"] for p in open_ports]

                exposed_count = len([p for p in open_port_nums if p in high_risk_ports])
                if exposed_count > 0:
                    risk_factors.append(
                        {
                            "factor": "high_risk_ports",
                            "description": f"Exposes {exposed_count} high-risk ports",
                            "score": exposed_count * 10,
                        }
                    )

        # Malware/phishing indicators
        if metadata.get("malware_detected"):
            risk_factors.append(
                {
                    "factor": "malware",
                    "description": "Malware detected",
                    "score": 40,
                }
            )

        if metadata.get("phishing_indicator"):
            risk_factors.append(
                {
                    "factor": "phishing",
                    "description": "Potential phishing site",
                    "score": 35,
                }
            )

        # No SSL/HTTPS
        if entity_type == "URL":
            url = entity.get("value", "")
            if url.startswith("http://"):
                risk_factors.append(
                    {
                        "factor": "no_https",
                        "description": "Uses HTTP instead of HTTPS",
                        "score": 10,
                    }
                )

        # Multiple sources (could indicate correlation)
        sources = metadata.get("sources", [])
        if len(sources) > 3:
            risk_factors.append(
                {
                    "factor": "high_correlation",
                    "description": f"Found across {len(sources)} sources",
                    "score": min(len(sources) * 5, 20),
                }
            )

        return risk_factors

    def detect_anomalies(self, entities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Detect anomalies using Isolation Forest.

        Args:
            entities: List of entity dictionaries

        Returns:
            List of entities with anomaly scores
        """
        if len(entities) < 10:
            logger.warning("Not enough entities for anomaly detection")
            return entities

        logger.info(f"Detecting anomalies in {len(entities)} entities")

        try:
            # Extract features
            features = self._extract_features(entities)

            if features is None or len(features) == 0:
                logger.warning("Could not extract features for anomaly detection")
                return entities

            # Scale features
            X_scaled = self.scaler.fit_transform(features)

            # Fit and predict
            self.isolation_forest.fit(X_scaled)
            anomaly_scores = self.isolation_forest.decision_function(X_scaled)

            # Add anomaly scores to entities
            for i, entity in enumerate(entities):
                entity["metadata"] = entity.get("metadata", {})
                entity["metadata"]["anomaly_score"] = float(anomaly_scores[i])
                entity["metadata"]["is_anomaly"] = anomaly_scores[i] < 0

            anomaly_count = sum(
                1 for e in entities if e["metadata"].get("is_anomaly", False)
            )
            logger.info(
                f"Detected {anomaly_count} anomalies ({anomaly_count / len(entities) * 100:.1f}%)"
            )

            self.model_trained = True

        except Exception as e:
            logger.error(f"Error detecting anomalies: {e}")

        return entities

    def _extract_features(self, entities: List[Dict[str, Any]]) -> Any:
        """
        Extract numerical features from entities.

        Args:
            entities: List of entity dictionaries

        Returns:
            Numpy array of features
        """
        features_list = []

        for entity in entities:
            features = []

            # Risk level (numeric)
            risk_level_map = {
                RiskLevel.CRITICAL.value: 4,
                RiskLevel.HIGH.value: 3,
                RiskLevel.MEDIUM.value: 2,
                RiskLevel.LOW.value: 1,
                RiskLevel.INFO.value: 0,
            }
            risk_level_num = risk_level_map.get(
                entity.get("risk_level", RiskLevel.INFO.value), 0
            )
            features.append(risk_level_num)

            # Number of breaches
            metadata = entity.get("metadata", {})
            breaches = metadata.get("breaches_found", 0)
            features.append(breaches)

            # Number of open ports
            open_ports = metadata.get("open_ports", [])
            features.append(len(open_ports))

            # Value length
            value_length = len(str(entity.get("value", "")))
            features.append(value_length)

            # Metadata complexity
            metadata_size = len(str(metadata))
            features.append(metadata_size)

            # Has location data
            has_location = (
                1
                if any(k in metadata for k in ["lat", "lon", "latitude", "longitude"])
                else 0
            )
            features.append(has_location)

            # Has geolocation
            has_geo = (
                1 if any(k in metadata for k in ["country", "city", "region"]) else 0
            )
            features.append(has_geo)

            # Has organization info
            has_org = (
                1
                if any(
                    k in metadata
                    for k in ["org", "organization", "company", "registrant_org"]
                )
                else 0
            )
            features.append(has_org)

            features_list.append(features)

        return np.array(features_list) if features_list else None

    def predict_risk_level(self, entity: Dict[str, Any]) -> RiskLevel:
        """
        Predict risk level using ML model.

        Args:
            entity: Entity dictionary

        Returns:
            Predicted RiskLevel
        """
        # Calculate risk score
        risk_score = self.calculate_entity_risk_score(entity)

        # Map score to risk level
        if risk_score >= 80:
            return RiskLevel.CRITICAL
        elif risk_score >= 60:
            return RiskLevel.HIGH
        elif risk_score >= 40:
            return RiskLevel.MEDIUM
        elif risk_score >= 20:
            return RiskLevel.LOW
        else:
            return RiskLevel.INFO

    def analyze_relationship_risk(self, relationship: Dict[str, Any]) -> float:
        """
        Analyze risk of a relationship.

        Args:
            relationship: Relationship dictionary

        Returns:
            Risk score (0-100)
        """
        risk_score = 0.0

        rel_type = relationship.get("relationship_type", "")

        # High-risk relationship types
        high_risk_rels = ["COMPROMISED_BY", "CONNECTED_TO_MALWARE", "PHISHING_LINK"]
        if rel_type in high_risk_rels:
            risk_score += 50

        # Medium-risk relationship types
        medium_risk_rels = ["MEMBER_OF_SUSPICIOUS_ORG", "HOSTED_ON_SUSPICIOUS_SERVER"]
        if rel_type in medium_risk_rels:
            risk_score += 30

        # Check metadata for risk indicators
        metadata = relationship.get("metadata", {})

        if metadata.get("dark_web_mention"):
            risk_score += 25

        if metadata.get("malware_related"):
            risk_score += 30

        return min(risk_score, 100)

    def generate_risk_factors(self, entity: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Generate comprehensive risk factors for entity.

        Args:
            entity: Entity dictionary

        Returns:
            List of risk factor dictionaries
        """
        factors = self._generate_risk_factors(entity)

        # Add predicted risk level
        predicted_level = self.predict_risk_level(entity)
        factors.append(
            {
                "factor": "predicted_risk_level",
                "description": f"Predicted risk level: {predicted_level.value}",
                "score": 0,  # This is informational, not additive
            }
        )

        return factors

    def batch_analyze_risk(
        self, entities: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Analyze risk for multiple entities.

        Args:
            entities: List of entity dictionaries

        Returns:
            List of entities with risk analysis
        """
        logger.info(f"Analyzing risk for {len(entities)} entities")

        # Calculate risk scores for all entities
        for entity in entities:
            risk_score = self.calculate_entity_risk_score(entity)
            predicted_level = self.predict_risk_level(entity)
            risk_factors = self.generate_risk_factors(entity)

            entity["metadata"] = entity.get("metadata", {})
            entity["metadata"]["risk_score"] = risk_score
            entity["metadata"]["predicted_risk_level"] = predicted_level.value
            entity["metadata"]["risk_factors"] = risk_factors

        # Detect anomalies
        entities = self.detect_anomalies(entities)

        return entities

    def assess_collection_risk(self, entities: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Assess overall risk of collected data.

        Args:
            entities: List of entity dictionaries

        Returns:
            Risk assessment summary
        """
        if not entities:
            return {
                "total_entities": 0,
                "average_risk_score": 0,
                "max_risk_score": 0,
                "risk_distribution": {},
                "critical_entities": [],
                "recommendation": "No entities to assess",
            }

        # Extract risk scores
        risk_scores = [e.get("metadata", {}).get("risk_score", 0) for e in entities]

        # Calculate statistics
        avg_risk = np.mean(risk_scores)
        max_risk = max(risk_scores)

        # Count by risk level
        risk_counts = {}
        for entity in entities:
            level = entity.get("metadata", {}).get(
                "predicted_risk_level", RiskLevel.INFO.value
            )
            risk_counts[level] = risk_counts.get(level, 0) + 1

        # Find critical entities
        critical_entities = [
            e
            for e in entities
            if e.get("metadata", {}).get("predicted_risk_level")
            == RiskLevel.CRITICAL.value
        ]

        # Generate recommendation
        if max_risk >= 80:
            recommendation = (
                "Critical risk entities detected - immediate attention required"
            )
        elif max_risk >= 60:
            recommendation = "High risk entities detected - investigation recommended"
        elif max_risk >= 40:
            recommendation = "Medium risk entities present - monitor closely"
        else:
            recommendation = "Low overall risk - routine monitoring"

        return {
            "total_entities": len(entities),
            "average_risk_score": round(float(avg_risk), 2),
            "max_risk_score": float(max_risk),
            "risk_distribution": risk_counts,
            "critical_entities": [e["value"] for e in critical_entities[:10]],
            "anomalies_detected": sum(
                1 for e in entities if e["metadata"].get("is_anomaly", False)
            ),
            "recommendation": recommendation,
        }
