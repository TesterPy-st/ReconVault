"""
Entity model for ReconVault intelligence system.

This module defines the Entity SQLAlchemy model for storing
entity information discovered during intelligence gathering.
"""

import enum
import uuid
from typing import Any, Dict, Optional

from sqlalchemy import (JSON, Boolean, Column, DateTime, Float, ForeignKey,
                        Index, Integer, String, Text)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class EntityType(str, enum.Enum):
    """Enumeration of entity types"""

    DOMAIN = "domain"
    IP_ADDRESS = "ip_address"
    EMAIL = "email"
    PHONE = "phone"
    SOCIAL_HANDLE = "social_handle"
    PERSON = "person"
    COMPANY = "company"
    WEBSITE = "website"
    SERVICE = "service"
    LOCATION = "location"
    DEVICE = "device"
    NETWORK = "network"
    VULNERABILITY = "vulnerability"
    THREAT_ACTOR = "threat_actor"
    MALWARE = "malware"
    INDICATOR = "indicator"


class Entity(Base):
    """
    Entity model representing discovered intelligence entities.

    Attributes:
        id (int): Primary key
        type (EntityType): Type of entity
        name (str): Entity name or identifier
        value (str): Actual entity value
        risk_score (float): Risk assessment score (0.0 to 1.0)
        target_id (int): Foreign key to associated target
        source (str): Source of the entity discovery
        confidence (float): Confidence in entity accuracy (0.0 to 1.0)
        description (str): Optional description
        metadata (str): JSON string for flexible metadata storage
        tags (str): Comma-separated tags for categorization
        first_seen (datetime): When entity was first discovered
        last_seen (datetime): When entity was last observed
        is_verified (bool): Whether entity has been verified
        created_at (datetime): Creation timestamp
        updated_at (datetime): Last update timestamp
        is_active (bool): Whether entity is currently active
    """

    __tablename__ = "entities"

    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)

    # Entity identification
    type = Column(String(50), nullable=False, index=True)
    name = Column(String(200), nullable=True, index=True)
    value = Column(String(500), nullable=False, index=True)

    # Risk and confidence assessment
    risk_score = Column(Float, default=0.0, nullable=False, index=True)
    confidence = Column(Float, default=1.0, nullable=False)

    # Relationships
    target_id = Column(Integer, ForeignKey("targets.id"), nullable=True, index=True)

    # Source and verification
    source = Column(String(100), nullable=False, index=True)
    is_verified = Column(Boolean, default=False, nullable=False)

    # Additional information
    description = Column(Text, nullable=True)
    meta = Column(JSON, nullable=True)  # JSON for flexible metadata
    tags = Column(String(500), nullable=True)  # Comma-separated tags

    # Timestamps
    discovered_at = Column(
        DateTime(timezone=True), nullable=True, server_default=func.now()
    )
    first_seen = Column(DateTime(timezone=True), nullable=True)
    last_seen = Column(DateTime(timezone=True), nullable=True)
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
    is_active = Column(Boolean, default=True, nullable=False)

    # Relationships
    target = relationship("Target", back_populates="entities")

    # Relationship mappings
    source_relationships = relationship(
        "Relationship",
        foreign_keys="Relationship.source_entity_id",
        back_populates="source_entity",
    )
    target_relationships = relationship(
        "Relationship",
        foreign_keys="Relationship.target_entity_id",
        back_populates="target_entity",
    )

    def __repr__(self) -> str:
        """String representation of Entity instance"""
        return f"<Entity(id={self.id}, type='{self.type}', name='{self.name}', value='{self.value}')>"

    @property
    def risk_level(self) -> str:
        """
        Get human-readable risk level based on risk_score.

        Returns:
            str: Risk level category
        """
        if self.risk_score >= 0.8:
            return "critical"
        elif self.risk_score >= 0.6:
            return "high"
        elif self.risk_score >= 0.4:
            return "medium"
        elif self.risk_score >= 0.2:
            return "low"
        else:
            return "minimal"

    @property
    def relationship_count(self) -> int:
        """
        Get total number of relationships for this entity.

        Returns:
            int: Count of relationships
        """
        return len(self.source_relationships) + len(self.target_relationships)

    def to_dict(self) -> dict:
        """
        Convert Entity instance to dictionary.

        Returns:
            dict: Dictionary representation of entity
        """
        return {
            "id": self.id,
            "type": self.type,
            "name": self.name,
            "value": self.value,
            "risk_score": self.risk_score,
            "risk_level": self.risk_level,
            "confidence": self.confidence,
            "target_id": self.target_id,
            "source": self.source,
            "is_verified": self.is_verified,
            "description": self.description,
            "metadata": self.meta,
            "tags": self.tags,
            "first_seen": self.first_seen.isoformat() if self.first_seen else None,
            "last_seen": self.last_seen.isoformat() if self.last_seen else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "is_active": self.is_active,
            "relationship_count": self.relationship_count,
        }

    def add_tag(self, tag: str) -> None:
        """
        Add a tag to the entity.

        Args:
            tag (str): Tag to add
        """
        if not self.tags:
            self.tags = tag
        elif tag not in self.tags.split(","):
            self.tags = f"{self.tags},{tag}"

    def remove_tag(self, tag: str) -> None:
        """
        Remove a tag from the entity.

        Args:
            tag (str): Tag to remove
        """
        if self.tags and tag in self.tags:
            tags_list = [t.strip() for t in self.tags.split(",")]
            tags_list.remove(tag)
            self.tags = ",".join(tags_list)

    def get_tags(self) -> list:
        """
        Get list of tags for the entity.

        Returns:
            list: List of tags
        """
        if not self.tags:
            return []
        return [tag.strip() for tag in self.tags.split(",")]


# Create compound indexes for performance
Index("idx_entity_type_value", Entity.type, Entity.value)
Index("idx_entity_source_type", Entity.source, Entity.type)
