"""
Risk Assessment model for ReconVault intelligence system.

This module defines the RiskAssessment SQLAlchemy model for storing
entity risk assessments.
"""

import uuid

from sqlalchemy import JSON, Column, DateTime, Float, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class RiskAssessment(Base):
    """
    RiskAssessment model representing risk evaluations of entities.

    Attributes:
        id (UUID): Primary key
        entity_id (UUID): Foreign key to entity being assessed
        level (str): Risk level (critical/high/medium/low/info)
        score (float): Numeric risk score (0.0 to 1.0)
        factors (list): Risk factors contributing to score
        assessed_at (datetime): Assessment timestamp
        created_at (datetime): Creation timestamp
        updated_at (datetime): Last update timestamp
    """

    __tablename__ = "risk_assessments"

    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)

    # Foreign key
    entity_id = Column(
        UUID(as_uuid=True),
        ForeignKey("entities.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Risk assessment data
    level = Column(String(50), nullable=False, index=True)
    score = Column(Float, nullable=False, index=True)
    factors = Column(JSON, nullable=False, default=list)

    # Timestamps
    assessed_at = Column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # Relationships
    entity = relationship("Entity")

    def __repr__(self) -> str:
        """String representation of RiskAssessment instance"""
        return f"<RiskAssessment(id={self.id}, entity_id={self.entity_id}, level='{self.level}', score={self.score})>"

    @property
    def risk_category(self) -> str:
        """
        Get risk category based on score.

        Returns:
            str: Risk category
        """
        if self.score >= 0.8:
            return "critical"
        elif self.score >= 0.6:
            return "high"
        elif self.score >= 0.4:
            return "medium"
        elif self.score >= 0.2:
            return "low"
        else:
            return "info"

    def to_dict(self) -> dict:
        """
        Convert RiskAssessment instance to dictionary.

        Returns:
            dict: Dictionary representation of risk assessment
        """
        return {
            "id": str(self.id),
            "entity_id": str(self.entity_id),
            "level": self.level,
            "score": self.score,
            "factors": self.factors,
            "assessed_at": self.assessed_at.isoformat() if self.assessed_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
