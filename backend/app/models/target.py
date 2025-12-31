"""
Target model for ReconVault intelligence system.

This module defines the Target SQLAlchemy model for storing
target information including type, value, status, and risk assessment.
"""

from sqlalchemy import Column, Integer, String, DateTime, Float, Text, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base
import enum
from typing import Optional


class TargetType(str, enum.Enum):
    """Enumeration of target types"""
    DOMAIN = "domain"
    IP_ADDRESS = "ip_address"
    EMAIL = "email"
    PHONE = "phone"
    SOCIAL_HANDLE = "social_handle"
    COMPANY = "company"
    PERSON = "person"
    NETWORK = "network"
    WEBSITE = "website"
    SERVICE = "service"


class TargetStatus(str, enum.Enum):
    """Enumeration of target status values"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    INVESTIGATING = "investigating"
    CONFIRMED = "confirmed"
    FALSE_POSITIVE = "false_positive"
    ARCHIVED = "archived"


class Target(Base):
    """
    Target model representing entities for intelligence gathering.
    
    Attributes:
        id (int): Primary key
        type (TargetType): Type of target (domain, ip, email, etc.)
        value (str): The actual target value (domain name, IP address, etc.)
        status (TargetStatus): Current investigation status
        risk_score (float): Risk assessment score (0.0 to 1.0)
        description (str): Optional description of the target
        metadata (str): JSON string for additional target information
        created_at (datetime): Creation timestamp
        updated_at (datetime): Last update timestamp
        is_active (bool): Whether target is active for investigation
    """
    
    __tablename__ = "targets"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Target identification
    type = Column(String(50), nullable=False, index=True)
    value = Column(String(500), nullable=False, index=True)
    
    # Status and assessment
    status = Column(String(50), default=TargetStatus.ACTIVE, nullable=False)
    risk_score = Column(Float, default=0.0, nullable=False)
    
    # Additional information
    description = Column(Text, nullable=True)
    metadata = Column(Text, nullable=True)  # JSON string for flexible metadata
    
    # Timestamps
    created_at = Column(
        DateTime(timezone=True), 
        server_default=func.now(), 
        nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True), 
        server_default=func.now(), 
        onupdate=func.now(),
        nullable=False
    )
    
    # Status flags
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Relationships
    entities = relationship(
        "Entity",
        back_populates="target",
        cascade="all, delete-orphan",
        foreign_keys="Entity.target_id"
    )
    
    # Audit relationships
    audit_logs = relationship("AuditLog", back_populates="target")
    
    def __repr__(self) -> str:
        """String representation of Target instance"""
        return f"<Target(id={self.id}, type='{self.type}', value='{self.value}')>"
    
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
    
    def to_dict(self) -> dict:
        """
        Convert Target instance to dictionary.
        
        Returns:
            dict: Dictionary representation of target
        """
        return {
            "id": self.id,
            "type": self.type,
            "value": self.value,
            "status": self.status,
            "risk_score": self.risk_score,
            "risk_level": self.risk_level,
            "description": self.description,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "is_active": self.is_active
        }


# Indexes for performance optimization
Target.__table__.append_column(
    Column("idx_target_type_value", String(100), index=True)
)

# Create composite index for type and value
Target.__table__.append_column(
    Column("idx_target_type_value_composite", String(550), index=True)
)