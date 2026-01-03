"""
ReconVault Feature Engineering for Anomaly Detection

This module extracts features from entities and relationships for ML models.
"""

import json
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
from loguru import logger
from sqlalchemy.orm import Session

from app.models.entity import Entity
from app.models.relationship import Relationship


class EntityFeatureExtractor:
    """Extract features from entities for anomaly detection."""

    FEATURE_NAMES = [
        "degree_centrality",
        "betweenness_centrality",
        "closeness_centrality",
        "eigenvector_centrality",
        "clustering_coefficient",
        "source_count",
        "update_frequency",
        "confidence_score",
        "risk_score",
        "first_seen_age_days",
        "last_updated_age_days",
        "update_frequency_std",
        "relationship_count",
        "entity_type_encoded",
        "is_verified",
        "metadata_richness",
        "tag_count",
        "temporal_activity_score",
    ]

    def __init__(self, db: Session):
        """
        Initialize feature extractor.

        Args:
            db: Database session
        """
        self.db = db
        self.entity_type_encoding = {
            "domain": 0,
            "ip_address": 1,
            "email": 2,
            "phone": 3,
            "social_handle": 4,
            "person": 5,
            "company": 6,
            "website": 7,
            "service": 8,
            "location": 9,
            "device": 10,
            "network": 11,
            "vulnerability": 12,
            "threat_actor": 13,
            "malware": 14,
            "indicator": 15,
        }

    def extract(self, entity: Entity) -> np.ndarray:
        """
        Extract feature vector from entity.

        Args:
            entity: Entity to extract features from

        Returns:
            Feature vector as numpy array
        """
        features = []

        # Graph centrality features (computed from relationships)
        centrality_features = self._compute_centrality_features(entity)
        features.extend(
            [
                centrality_features.get("degree", 0.0),
                centrality_features.get("betweenness", 0.0),
                centrality_features.get("closeness", 0.0),
                centrality_features.get("eigenvector", 0.0),
                centrality_features.get("clustering", 0.0),
            ]
        )

        # Metadata features
        source_count = self._extract_source_count(entity)
        features.append(source_count)

        update_freq = self._compute_update_frequency(entity)
        features.append(update_freq)

        features.append(entity.confidence)
        features.append(entity.risk_score)

        # Temporal features
        first_seen_age = (
            self._compute_age_days(entity.first_seen) if entity.first_seen else 0
        )
        last_updated_age = self._compute_age_days(entity.updated_at)
        features.append(first_seen_age)
        features.append(last_updated_age)

        # Update frequency std deviation (requires history - placeholder)
        features.append(0.5)  # TODO: Compute from historical data

        # Network features
        relationship_count = entity.relationship_count
        features.append(relationship_count)

        # Entity type encoding
        entity_type_encoded = self.entity_type_encoding.get(entity.type, -1)
        features.append(entity_type_encoded)

        # Verification status
        features.append(1.0 if entity.is_verified else 0.0)

        # Metadata richness
        metadata_richness = self._compute_metadata_richness(entity)
        features.append(metadata_richness)

        # Tag count
        tag_count = len(entity.get_tags())
        features.append(tag_count)

        # Temporal activity score
        temporal_score = self._compute_temporal_activity(entity)
        features.append(temporal_score)

        return np.array(features, dtype=np.float32)

    def extract_batch(self, entities: List[Entity]) -> np.ndarray:
        """
        Extract features from multiple entities.

        Args:
            entities: List of entities

        Returns:
            Feature matrix (n_entities, n_features)
        """
        features = [self.extract(entity) for entity in entities]
        return np.array(features, dtype=np.float32)

    def _compute_centrality_features(self, entity: Entity) -> Dict[str, float]:
        """
        Compute graph centrality features.

        Note: For production, these should be computed from Neo4j graph.
        For now, we use simplified approximations.
        """
        relationship_count = entity.relationship_count

        # Simplified approximations
        degree = relationship_count / 100.0  # Normalize
        betweenness = min(1.0, degree * 0.5)  # Approximate
        closeness = min(1.0, degree * 0.3)
        eigenvector = min(1.0, degree * 0.4)
        clustering = max(0.0, 1.0 - degree * 0.5)  # Inverse relationship

        return {
            "degree": degree,
            "betweenness": betweenness,
            "closeness": closeness,
            "eigenvector": eigenvector,
            "clustering": clustering,
        }

    def _extract_source_count(self, entity: Entity) -> float:
        """Extract number of sources (from metadata or source field)."""
        if entity.metadata:
            try:
                metadata = json.loads(entity.metadata)
                sources = metadata.get("sources", [])
                if isinstance(sources, list):
                    return float(len(sources))
            except (json.JSONDecodeError, TypeError):
                pass
        return 1.0  # At least one source (the primary source)

    def _compute_update_frequency(self, entity: Entity) -> float:
        """
        Compute update frequency (updates per day).

        Simplified calculation based on age and update timestamps.
        """
        if not entity.first_seen:
            return 0.0

        now = datetime.now(timezone.utc)
        age_seconds = (now - entity.first_seen).total_seconds()
        age_days = max(1, age_seconds / 86400)

        # Simplified: assume one update
        return 1.0 / age_days

    def _compute_age_days(self, timestamp: datetime) -> float:
        """Compute age in days from timestamp."""
        if not timestamp:
            return 0.0

        now = datetime.now(timezone.utc)
        age_seconds = (now - timestamp).total_seconds()
        return age_seconds / 86400

    def _compute_metadata_richness(self, entity: Entity) -> float:
        """
        Compute metadata richness score (0-1).

        Measures how much metadata is present.
        """
        score = 0.0

        if entity.name:
            score += 0.2
        if entity.description:
            score += 0.2
        if entity.metadata:
            try:
                metadata = json.loads(entity.metadata)
                score += min(0.4, len(metadata) * 0.1)
            except (json.JSONDecodeError, TypeError):
                pass
        if entity.tags:
            score += 0.2

        return min(1.0, score)

    def _compute_temporal_activity(self, entity: Entity) -> float:
        """
        Compute temporal activity score based on recent updates.

        Higher score = more recent activity
        """
        if not entity.last_seen:
            return 0.0

        now = datetime.now(timezone.utc)
        days_since_update = (now - entity.last_seen).total_seconds() / 86400

        # Exponential decay: active recently = higher score
        activity_score = np.exp(-days_since_update / 30.0)  # 30-day half-life
        return activity_score


class RelationshipFeatureExtractor:
    """Extract features from relationships for anomaly detection."""

    FEATURE_NAMES = [
        "confidence_score",
        "confidence_variance",
        "source_diversity",
        "temporal_clustering",
        "strength_metric",
        "bidirectionality",
        "relationship_type_encoded",
        "age_days",
        "update_frequency",
        "entity_degree_product",
        "risk_score_diff",
        "confidence_agreement",
    ]

    def __init__(self, db: Session):
        """
        Initialize relationship feature extractor.

        Args:
            db: Database session
        """
        self.db = db
        self.relationship_type_encoding = {
            "connected_to": 0,
            "owns": 1,
            "uses": 2,
            "located_at": 3,
            "associated_with": 4,
            "communicates_with": 5,
            "targets": 6,
            "similar_to": 7,
            "derives_from": 8,
            "hosts": 9,
        }

    def extract(self, relationship: Relationship) -> np.ndarray:
        """
        Extract feature vector from relationship.

        Args:
            relationship: Relationship to extract features from

        Returns:
            Feature vector as numpy array
        """
        features = []

        # Confidence features
        features.append(relationship.confidence)

        # Confidence variance (requires history - placeholder)
        features.append(0.1)  # TODO: Compute from historical data

        # Source diversity
        source_div = self._compute_source_diversity(relationship)
        features.append(source_div)

        # Temporal clustering (placeholder)
        features.append(0.5)  # TODO: Analyze temporal patterns

        # Strength metric (how many supporting evidence)
        strength = self._compute_strength_metric(relationship)
        features.append(strength)

        # Bidirectionality (check if reverse relationship exists)
        bidirectional = self._check_bidirectionality(relationship)
        features.append(1.0 if bidirectional else 0.0)

        # Relationship type encoding
        rel_type_encoded = self.relationship_type_encoding.get(relationship.type, -1)
        features.append(rel_type_encoded)

        # Age in days
        age_days = self._compute_age_days(relationship.created_at)
        features.append(age_days)

        # Update frequency
        update_freq = self._compute_update_frequency(relationship)
        features.append(update_freq)

        # Entity degree product (approximation of importance)
        degree_product = self._compute_degree_product(relationship)
        features.append(degree_product)

        # Risk score difference between entities
        risk_diff = self._compute_risk_diff(relationship)
        features.append(risk_diff)

        # Confidence agreement with entity confidences
        conf_agreement = self._compute_confidence_agreement(relationship)
        features.append(conf_agreement)

        return np.array(features, dtype=np.float32)

    def extract_batch(self, relationships: List[Relationship]) -> np.ndarray:
        """Extract features from multiple relationships."""
        features = [self.extract(rel) for rel in relationships]
        return np.array(features, dtype=np.float32)

    def _compute_source_diversity(self, relationship: Relationship) -> float:
        """Compute diversity of sources reporting this relationship."""
        if relationship.metadata:
            try:
                metadata = json.loads(relationship.metadata)
                sources = metadata.get("sources", [])
                if isinstance(sources, list):
                    return min(1.0, len(sources) / 5.0)  # Normalize to 5 sources
            except (json.JSONDecodeError, TypeError):
                pass
        return 0.2  # Low diversity if no metadata

    def _compute_strength_metric(self, relationship: Relationship) -> float:
        """Compute strength of relationship based on supporting evidence."""
        # Base strength from confidence
        strength = relationship.confidence

        # Boost from metadata
        if relationship.metadata:
            try:
                metadata = json.loads(relationship.metadata)
                evidence_count = len(metadata.get("evidence", []))
                strength += min(0.5, evidence_count * 0.1)
            except (json.JSONDecodeError, TypeError):
                pass

        return min(1.0, strength)

    def _check_bidirectionality(self, relationship: Relationship) -> bool:
        """Check if reverse relationship exists."""
        # Query for reverse relationship
        reverse = (
            self.db.query(Relationship)
            .filter(
                Relationship.source_entity_id == relationship.target_entity_id,
                Relationship.target_entity_id == relationship.source_entity_id,
            )
            .first()
        )

        return reverse is not None

    def _compute_age_days(self, timestamp: datetime) -> float:
        """Compute age in days."""
        if not timestamp:
            return 0.0

        now = datetime.now(timezone.utc)
        age_seconds = (now - timestamp).total_seconds()
        return age_seconds / 86400

    def _compute_update_frequency(self, relationship: Relationship) -> float:
        """Compute update frequency."""
        age_days = self._compute_age_days(relationship.created_at)
        if age_days < 1:
            return 0.0

        # Simplified: assume one update
        return 1.0 / age_days

    def _compute_degree_product(self, relationship: Relationship) -> float:
        """Compute product of entity degrees (normalized)."""
        source_entity = relationship.source_entity
        target_entity = relationship.target_entity

        if not source_entity or not target_entity:
            return 0.0

        source_degree = source_entity.relationship_count
        target_degree = target_entity.relationship_count

        # Normalize to 0-1 range (assuming max degree of 100)
        normalized_product = (source_degree * target_degree) / (100.0 * 100.0)
        return min(1.0, normalized_product)

    def _compute_risk_diff(self, relationship: Relationship) -> float:
        """Compute absolute difference in risk scores."""
        source_entity = relationship.source_entity
        target_entity = relationship.target_entity

        if not source_entity or not target_entity:
            return 0.0

        return abs(source_entity.risk_score - target_entity.risk_score)

    def _compute_confidence_agreement(self, relationship: Relationship) -> float:
        """Compute agreement between relationship and entity confidences."""
        source_entity = relationship.source_entity
        target_entity = relationship.target_entity

        if not source_entity or not target_entity:
            return relationship.confidence

        avg_entity_conf = (source_entity.confidence + target_entity.confidence) / 2.0
        agreement = 1.0 - abs(relationship.confidence - avg_entity_conf)

        return agreement


class SequenceFeatureExtractor:
    """Extract time-series features for LSTM autoencoder."""

    def __init__(self, db: Session, sequence_length: int = 50):
        """
        Initialize sequence feature extractor.

        Args:
            db: Database session
            sequence_length: Length of sequences to extract
        """
        self.db = db
        self.sequence_length = sequence_length
        self.n_features = 15

    def extract(self, entity: Entity) -> np.ndarray:
        """
        Extract time-series feature sequence from entity.

        Args:
            entity: Entity to extract sequence from

        Returns:
            Sequence array (sequence_length, n_features)
        """
        # TODO: In production, this should query historical data
        # For now, we generate a synthetic sequence based on current state

        sequence = np.zeros((self.sequence_length, self.n_features))

        # Current feature vector
        entity_extractor = EntityFeatureExtractor(self.db)
        current_features = entity_extractor.extract(entity)

        # Replicate with some noise (placeholder for actual time series)
        for i in range(self.sequence_length):
            noise = np.random.normal(0, 0.05, self.n_features)
            sequence[i] = current_features[: self.n_features] + noise

        return sequence

    def extract_batch(self, entities: List[Entity]) -> np.ndarray:
        """
        Extract sequences from multiple entities.

        Args:
            entities: List of entities

        Returns:
            Sequence array (n_entities, sequence_length, n_features)
        """
        sequences = [self.extract(entity) for entity in entities]
        return np.array(sequences, dtype=np.float32)


def get_feature_names(feature_type: str) -> List[str]:
    """
    Get feature names for a specific feature type.

    Args:
        feature_type: One of 'entity', 'relationship', 'sequence'

    Returns:
        List of feature names
    """
    if feature_type == "entity":
        return EntityFeatureExtractor.FEATURE_NAMES
    elif feature_type == "relationship":
        return RelationshipFeatureExtractor.FEATURE_NAMES
    elif feature_type == "sequence":
        return [f"seq_feature_{i}" for i in range(15)]
    else:
        raise ValueError(f"Unknown feature type: {feature_type}")
