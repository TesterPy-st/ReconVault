"""
ReconVault Models Module

This module contains all data models and schemas for the ReconVault
cyber reconnaissance intelligence system.
"""

from typing import Any, Dict, Optional

# Import base Pydantic models
from pydantic import BaseModel

# Import base database components
from app.database import Base

# Import all SQLAlchemy models
from .audit import AuditAction, AuditLog, AuditSeverity, AuditStatus
from .entity import Entity, EntityType
from .intelligence import (
    ComplianceAuditTrail,
    ComplianceViolation,
    Intelligence,
    IntelligencePriority,
    IntelligenceStatus,
    IntelligenceType,
)
from .relationship import Relationship, RelationshipType
from .target import Target, TargetStatus, TargetType
from .user import User, UserRole, UserStatus


class BaseResponse(BaseModel):
    """Base response model"""

    status: str
    message: Optional[str] = None
    data: Optional[Dict[str, Any]] = None


class HealthResponse(BaseModel):
    """Health check response model"""

    status: str
    timestamp: str
    service: str
    version: str


class ErrorResponse(BaseModel):
    """Error response model"""

    message: str
    error: Optional[str] = None
    code: Optional[int] = None


# Export all models and enums
__all__ = [
    # Database models
    "Base",
    "Target",
    "Entity",
    "Relationship",
    "Intelligence",
    "ComplianceViolation",
    "ComplianceAuditTrail",
    "User",
    "AuditLog",
    # Enums
    "TargetType",
    "TargetStatus",
    "EntityType",
    "RelationshipType",
    "IntelligenceType",
    "IntelligencePriority",
    "IntelligenceStatus",
    "UserRole",
    "UserStatus",
    "AuditAction",
    "AuditSeverity",
    "AuditStatus",
    # Base models
    "BaseResponse",
    "HealthResponse",
    "ErrorResponse",
]
