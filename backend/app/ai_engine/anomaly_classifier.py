"""
ReconVault Anomaly Classifier

This module classifies detected anomalies into categories and assigns severity levels.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from loguru import logger

from app.models.entity import Entity
from app.models.relationship import Relationship


class AnomalyType(str, Enum):
    """Types of anomalies that can be detected."""

    BEHAVIORAL = "behavioral"
    RELATIONSHIP = "relationship"
    INFRASTRUCTURE = "infrastructure"
    DATA_QUALITY = "data_quality"
    TEMPORAL = "temporal"
    SEMANTIC = "semantic"


class AnomalySeverity(str, Enum):
    """Severity levels for anomalies."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AnomalyClassifier:
    """Classifier for categorizing and assessing anomalies."""

    def __init__(self):
        """Initialize anomaly classifier."""
        self.classification_rules = self._initialize_rules()

    def classify_entity_anomaly(
        self,
        entity: Entity,
        anomaly_score: float,
        features: Optional[Dict[str, float]] = None,
    ) -> Dict[str, Any]:
        """
        Classify an entity anomaly.

        Args:
            entity: Entity with anomaly
            anomaly_score: Anomaly score (0-1)
            features: Feature values that contributed to anomaly

        Returns:
            Classification result with type, severity, and recommendations
        """
        classifications = []

        # Behavioral anomaly checks
        behavioral = self._check_behavioral_anomaly(entity, features)
        if behavioral["detected"]:
            classifications.append(behavioral)

        # Infrastructure anomaly checks
        infrastructure = self._check_infrastructure_anomaly(entity, features)
        if infrastructure["detected"]:
            classifications.append(infrastructure)

        # Data quality anomaly checks
        data_quality = self._check_data_quality_anomaly(entity, features)
        if data_quality["detected"]:
            classifications.append(data_quality)

        # Temporal anomaly checks
        temporal = self._check_temporal_anomaly(entity, features)
        if temporal["detected"]:
            classifications.append(temporal)

        # Semantic anomaly checks
        semantic = self._check_semantic_anomaly(entity, features)
        if semantic["detected"]:
            classifications.append(semantic)

        # Determine primary type and severity
        if classifications:
            primary = self._select_primary_classification(
                classifications, anomaly_score
            )
        else:
            # Generic classification
            primary = {
                "type": AnomalyType.BEHAVIORAL.value,
                "severity": self._calculate_severity(anomaly_score),
                "confidence": 0.5,
                "indicators": ["high_anomaly_score"],
                "description": "General anomalous pattern detected",
            }

        # Generate recommendations
        recommendations = self._generate_recommendations(
            primary["type"], primary["severity"], entity
        )

        return {
            "primary_type": primary["type"],
            "severity": primary["severity"],
            "confidence": primary["confidence"],
            "all_types": [c["type"] for c in classifications],
            "indicators": primary["indicators"],
            "description": primary["description"],
            "affected_entities": [entity.id],
            "recommendations": recommendations,
            "classified_at": datetime.utcnow().isoformat(),
        }

    def classify_relationship_anomaly(
        self, relationship: Relationship, anomaly_score: float
    ) -> Dict[str, Any]:
        """
        Classify a relationship anomaly.

        Args:
            relationship: Relationship with anomaly
            anomaly_score: Anomaly score (0-1)

        Returns:
            Classification result
        """
        # Check for suspicious relationship patterns
        indicators = []
        anomaly_type = AnomalyType.RELATIONSHIP.value

        # Low confidence relationship
        if relationship.confidence < 0.3:
            indicators.append("low_confidence")

        # Mismatched entity risk levels
        if relationship.source_entity and relationship.target_entity:
            risk_diff = abs(
                relationship.source_entity.risk_score
                - relationship.target_entity.risk_score
            )
            if risk_diff > 0.6:
                indicators.append("risk_mismatch")
                anomaly_type = AnomalyType.INFRASTRUCTURE.value

        # Unusual relationship type
        unusual_types = ["targets", "exploits", "compromises"]
        if relationship.type in unusual_types:
            indicators.append("unusual_relationship_type")
            anomaly_type = AnomalyType.INFRASTRUCTURE.value

        # Bridging node detection (connects disparate clusters)
        if self._is_bridging_relationship(relationship):
            indicators.append("bridging_node")
            anomaly_type = AnomalyType.RELATIONSHIP.value

        severity = self._calculate_severity(anomaly_score)

        description = self._generate_relationship_description(relationship, indicators)

        recommendations = self._generate_recommendations(
            anomaly_type, severity, relationship
        )

        return {
            "primary_type": anomaly_type,
            "severity": severity,
            "confidence": 0.8,
            "all_types": [anomaly_type],
            "indicators": indicators,
            "description": description,
            "affected_entities": [
                relationship.source_entity_id,
                relationship.target_entity_id,
            ],
            "recommendations": recommendations,
            "classified_at": datetime.utcnow().isoformat(),
        }

    def _check_behavioral_anomaly(
        self, entity: Entity, features: Optional[Dict[str, float]]
    ) -> Dict[str, Any]:
        """Check for behavioral anomalies."""
        indicators = []
        detected = False

        # Unusual collection patterns
        if features and features.get("update_frequency", 0) > 10.0:
            indicators.append("high_update_frequency")
            detected = True

        # Sudden risk score changes
        if entity.risk_score > 0.8:
            indicators.append("high_risk_score")
            detected = True

        # Unusual relationship count
        if entity.relationship_count > 50:
            indicators.append("high_degree")
            detected = True

        return {
            "detected": detected,
            "type": AnomalyType.BEHAVIORAL.value,
            "confidence": 0.75 if detected else 0.0,
            "indicators": indicators,
            "description": "Unusual behavioral patterns detected in entity activity",
        }

    def _check_infrastructure_anomaly(
        self, entity: Entity, features: Optional[Dict[str, float]]
    ) -> Dict[str, Any]:
        """Check for infrastructure-related anomalies (honeypots, sinkholes)."""
        indicators = []
        detected = False

        # Domain/IP infrastructure checks
        if entity.type in ["domain", "ip_address"]:
            # High risk + low confidence = possible honeypot
            if entity.risk_score > 0.7 and entity.confidence < 0.4:
                indicators.append("possible_honeypot")
                detected = True

            # Unusual metadata patterns
            if not entity.metadata:
                indicators.append("missing_metadata")
                detected = True

        # Service infrastructure
        if entity.type == "service":
            if entity.risk_score > 0.6:
                indicators.append("suspicious_service")
                detected = True

        return {
            "detected": detected,
            "type": AnomalyType.INFRASTRUCTURE.value,
            "confidence": 0.70 if detected else 0.0,
            "indicators": indicators,
            "description": "Infrastructure anomaly detected (possible honeypot/sinkhole/decoy)",
        }

    def _check_data_quality_anomaly(
        self, entity: Entity, features: Optional[Dict[str, float]]
    ) -> Dict[str, Any]:
        """Check for data quality issues."""
        indicators = []
        detected = False

        # Low metadata richness
        if features and features.get("metadata_richness", 1.0) < 0.3:
            indicators.append("low_metadata_richness")
            detected = True

        # Missing critical fields
        if not entity.name and entity.type in ["person", "company"]:
            indicators.append("missing_name")
            detected = True

        # Low confidence
        if entity.confidence < 0.3:
            indicators.append("low_confidence")
            detected = True

        return {
            "detected": detected,
            "type": AnomalyType.DATA_QUALITY.value,
            "confidence": 0.85 if detected else 0.0,
            "indicators": indicators,
            "description": "Data quality issues detected (inconsistent or missing data)",
        }

    def _check_temporal_anomaly(
        self, entity: Entity, features: Optional[Dict[str, float]]
    ) -> Dict[str, Any]:
        """Check for temporal anomalies."""
        indicators = []
        detected = False

        # Recent entity with high activity
        if features:
            first_seen_age = features.get("first_seen_age_days", 999)
            if first_seen_age < 7 and entity.relationship_count > 20:
                indicators.append("rapid_growth")
                detected = True

            # Long dormancy followed by activity
            last_updated_age = features.get("last_updated_age_days", 0)
            if last_updated_age < 1 and first_seen_age > 90:
                indicators.append("reactivation_after_dormancy")
                detected = True

        return {
            "detected": detected,
            "type": AnomalyType.TEMPORAL.value,
            "confidence": 0.65 if detected else 0.0,
            "indicators": indicators,
            "description": "Unusual timing patterns detected",
        }

    def _check_semantic_anomaly(
        self, entity: Entity, features: Optional[Dict[str, float]]
    ) -> Dict[str, Any]:
        """Check for semantic anomalies (out-of-context data)."""
        indicators = []
        detected = False

        # Entity type mismatch with relationships
        # This would require analyzing relationship types - simplified for now

        # Unusual tags for entity type
        tags = entity.get_tags()
        if tags:
            threat_tags = ["malware", "threat", "attack"]
            if entity.type in ["person", "company"] and any(
                t in threat_tags for t in tags
            ):
                indicators.append("semantic_mismatch")
                detected = True

        return {
            "detected": detected,
            "type": AnomalyType.SEMANTIC.value,
            "confidence": 0.60 if detected else 0.0,
            "indicators": indicators,
            "description": "Semantic inconsistencies detected (out-of-context data)",
        }

    def _select_primary_classification(
        self, classifications: List[Dict[str, Any]], anomaly_score: float
    ) -> Dict[str, Any]:
        """Select the primary classification from multiple candidates."""
        # Sort by confidence
        classifications.sort(key=lambda x: x["confidence"], reverse=True)

        primary = classifications[0]

        # Calculate severity based on anomaly score
        primary["severity"] = self._calculate_severity(anomaly_score)

        return primary

    def _calculate_severity(self, anomaly_score: float) -> str:
        """Calculate severity level from anomaly score."""
        if anomaly_score >= 0.8:
            return AnomalySeverity.CRITICAL.value
        elif anomaly_score >= 0.6:
            return AnomalySeverity.HIGH.value
        elif anomaly_score >= 0.4:
            return AnomalySeverity.MEDIUM.value
        else:
            return AnomalySeverity.LOW.value

    def _is_bridging_relationship(self, relationship: Relationship) -> bool:
        """Check if relationship connects disparate clusters (bridging node)."""
        # Simplified check: if entities have very different relationship counts
        if relationship.source_entity and relationship.target_entity:
            source_degree = relationship.source_entity.relationship_count
            target_degree = relationship.target_entity.relationship_count

            # One highly connected, one isolated = potential bridge
            if (source_degree > 30 and target_degree < 5) or (
                target_degree > 30 and source_degree < 5
            ):
                return True

        return False

    def _generate_relationship_description(
        self, relationship: Relationship, indicators: List[str]
    ) -> str:
        """Generate human-readable description of relationship anomaly."""
        descriptions = []

        if "low_confidence" in indicators:
            descriptions.append("Low confidence relationship")

        if "risk_mismatch" in indicators:
            descriptions.append("Significant risk score mismatch between entities")

        if "unusual_relationship_type" in indicators:
            descriptions.append(f"Unusual relationship type: {relationship.type}")

        if "bridging_node" in indicators:
            descriptions.append("Potential bridging node connecting disparate clusters")

        if descriptions:
            return "; ".join(descriptions)
        else:
            return "Anomalous relationship pattern detected"

    def _generate_recommendations(
        self, anomaly_type: str, severity: str, entity_or_relationship: Any
    ) -> List[str]:
        """Generate actionable recommendations based on anomaly."""
        recommendations = []

        # Severity-based recommendations
        if severity == AnomalySeverity.CRITICAL.value:
            recommendations.append("Immediate investigation required")
            recommendations.append("Consider quarantine or isolation")
        elif severity == AnomalySeverity.HIGH.value:
            recommendations.append("Priority investigation recommended")
            recommendations.append("Verify data sources")
        elif severity == AnomalySeverity.MEDIUM.value:
            recommendations.append("Schedule review within 24 hours")
        else:
            recommendations.append("Monitor for additional anomalies")

        # Type-specific recommendations
        if anomaly_type == AnomalyType.BEHAVIORAL.value:
            recommendations.append("Analyze activity timeline")
            recommendations.append("Check for coordinated patterns")

        elif anomaly_type == AnomalyType.INFRASTRUCTURE.value:
            recommendations.append("Verify infrastructure authenticity")
            recommendations.append("Check threat intelligence feeds")
            recommendations.append("Consider honeypot detection")

        elif anomaly_type == AnomalyType.DATA_QUALITY.value:
            recommendations.append("Validate data sources")
            recommendations.append("Enrich with additional collection")

        elif anomaly_type == AnomalyType.TEMPORAL.value:
            recommendations.append("Review temporal activity patterns")
            recommendations.append("Check for coordinated timing")

        elif anomaly_type == AnomalyType.RELATIONSHIP.value:
            recommendations.append("Analyze relationship graph context")
            recommendations.append("Verify relationship authenticity")

        elif anomaly_type == AnomalyType.SEMANTIC.value:
            recommendations.append("Review entity classification")
            recommendations.append("Check for data correlation errors")

        return recommendations

    def _initialize_rules(self) -> Dict[str, Any]:
        """Initialize classification rules."""
        return {
            "behavioral_thresholds": {
                "high_update_frequency": 10.0,
                "high_risk_score": 0.8,
                "high_degree": 50,
            },
            "infrastructure_thresholds": {
                "honeypot_risk": 0.7,
                "honeypot_confidence": 0.4,
            },
            "data_quality_thresholds": {"metadata_richness": 0.3, "confidence": 0.3},
        }


# Global classifier instance
_classifier: Optional[AnomalyClassifier] = None


def get_anomaly_classifier() -> AnomalyClassifier:
    """Get or create global classifier instance."""
    global _classifier

    if _classifier is None:
        _classifier = AnomalyClassifier()

    return _classifier
