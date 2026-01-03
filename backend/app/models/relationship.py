"""
Relationship model for ReconVault intelligence system.

This module defines the Relationship SQLAlchemy model for storing
relationships between entities in the intelligence graph.
"""

import enum
import uuid
from typing import Optional

from sqlalchemy import (JSON, Boolean, Column, DateTime, Float, ForeignKey,
                        Index, Integer, String, Text, UniqueConstraint)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class RelationshipType(str, enum.Enum):
    """Enumeration of relationship types"""

    # Network relationships
    RESOLVES_TO = "resolves_to"
    HOSTED_ON = "hosted_on"
    CONNECTED_TO = "connected_to"
    COMMUNICATES_WITH = "communicates_with"

    # Social relationships
    OWNS = "owns"
    MANAGES = "manages"
    WORKS_FOR = "works_for"
    FRIEND_OF = "friend_of"
    FOLLOWS = "follows"

    # Technical relationships
    DEPENDS_ON = "depends_on"
    VULNERABLE_TO = "vulnerable_to"
    USES = "uses"
    RUNS = "runs"
    CONTAINS = "contains"

    # Intelligence relationships
    SIMILAR_TO = "similar_to"
    PART_OF = "part_of"
    RELATED_TO = "related_to"
    SAME_AS = "same_as"
    REFERENCES = "references"

    # Threat relationships
    ATTRIBUTED_TO = "attributed_to"
    THREATENS = "threatens"
    TARGETS = "targets"
    CAMPAIGN = "campaign"
    INDICATOR_OF = "indicator_of"

    # Attribution relationships
    LOCATED_IN = "located_in"
    REGISTERED_BY = "registered_by"
    CREATED_BY = "created_by"
    ANALYZED_BY = "analyzed_by"


class Relationship(Base):
    """
    Relationship model representing connections between entities.

    Attributes:
        id (UUID): Primary key
        source_entity_id (UUID): Foreign key to source entity
        target_entity_id (UUID): Foreign key to target entity
        type (RelationshipType): Type of relationship
        confidence (float): Confidence in relationship accuracy (0.0 to 1.0)
        weight (float): Relationship weight/strength (0.0 to 1.0)
        description (str): Optional relationship description
        metadata (dict): JSON for additional relationship information
        first_observed (datetime): When relationship was first observed
        last_observed (datetime): When relationship was last observed
        verified (bool): Whether relationship has been verified
        created_at (datetime): Creation timestamp
        updated_at (datetime): Last update timestamp
        is_active (bool): Whether relationship is currently active
    """

    __tablename__ = "relationships"
    __table_args__ = (
        UniqueConstraint(
            "source_entity_id",
            "target_entity_id",
            "type",
            name="uq_relationship_entities_type",
        ),
    )

    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)

    # Entity relationship (bidirectional)
    source_entity_id = Column(
        UUID(as_uuid=True),
        ForeignKey("entities.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    target_entity_id = Column(
        UUID(as_uuid=True),
        ForeignKey("entities.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Relationship type and properties
    type = Column(String(100), nullable=False, index=True)
    confidence = Column(Float, default=1.0, nullable=False, index=True)
    weight = Column(Float, default=1.0, nullable=False)

    # Additional information
    description = Column(Text, nullable=True)
    meta = Column(JSON, nullable=True)  # JSON for flexible metadata

    # Timestamps
    first_observed = Column(DateTime(timezone=True), nullable=True)
    last_observed = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # Status flags
    verified = Column(Boolean, default=False, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

    # Relationships
    source_entity = relationship(
        "Entity", foreign_keys=[source_entity_id], back_populates="source_relationships"
    )
    target_entity = relationship(
        "Entity", foreign_keys=[target_entity_id], back_populates="target_relationships"
    )

    # Self-referential relationship for bidirectional access
    def __repr__(self) -> str:
        """String representation of Relationship instance"""
        return f"<Relationship(id={self.id}, source={self.source_entity_id}, target={self.target_entity_id}, type='{self.type}')>"

    @property
    def risk_score(self) -> float:
        """
        Calculate risk score based on relationship properties.

        Returns:
            float: Calculated risk score
        """
        base_score = self.confidence * self.weight

        # Adjust based on relationship type
        high_risk_types = [
            "vulnerable_to",
            "threatens",
            "targets",
            "attributed_to",
            "indicator_of",
            "threat_actor",
        ]

        if self.type in high_risk_types:
            base_score *= 1.5

        return min(base_score, 1.0)  # Cap at 1.0

    @property
    def risk_level(self) -> str:
        """
        Get human-readable risk level based on risk_score.

        Returns:
            str: Risk level category
        """
        risk_score = self.risk_score

        if risk_score >= 0.8:
            return "critical"
        elif risk_score >= 0.6:
            return "high"
        elif risk_score >= 0.4:
            return "medium"
        elif risk_score >= 0.2:
            return "low"
        else:
            return "minimal"

    def to_dict(self) -> dict:
        """
        Convert Relationship instance to dictionary.

        Returns:
            dict: Dictionary representation of relationship
        """
        return {
            "id": self.id,
            "source_entity_id": self.source_entity_id,
            "target_entity_id": self.target_entity_id,
            "type": self.type,
            "confidence": self.confidence,
            "weight": self.weight,
            "risk_score": self.risk_score,
            "risk_level": self.risk_level,
            "description": self.description,
            "metadata": self.meta,
            "first_observed": self.first_observed.isoformat()
            if self.first_observed
            else None,
            "last_observed": self.last_observed.isoformat()
            if self.last_observed
            else None,
            "verified": self.verified,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "is_active": self.is_active,
        }

    def reverse_relationship(self) -> dict:
        """
        Get reverse relationship information.

        Returns:
            dict: Reversed relationship data
        """
        return {
            "source_entity_id": self.target_entity_id,
            "target_entity_id": self.source_entity_id,
            "type": f"reverse_{self.type}",
            "confidence": self.confidence,
            "weight": self.weight,
            "original_relationship_id": self.id,
        }


# Create compound indexes for performance
Index("idx_relationship_type_confidence", Relationship.type, Relationship.confidence)
Index(
    "idx_relationship_source_target",
    Relationship.source_entity_id,
    Relationship.target_entity_id,
)
