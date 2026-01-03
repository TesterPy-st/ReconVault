"""
ReconVault Models Module

This module contains all data models and schemas for the ReconVault
cyber reconnaissance intelligence system.
"""

from typing import Any, Dict, List, Optional

# Import base Pydantic models
from pydantic import BaseModel

# Import base database components
from app.database import Base, metadata

from .audit import AuditAction, AuditLog, AuditSeverity, AuditStatus
from .collection_result import CollectionResult
from .collection_task import CollectionTask
from .entity import Entity, EntityType
from .intelligence import (Intelligence, IntelligencePriority,
                           IntelligenceStatus, IntelligenceType)
from .relationship import Relationship, RelationshipType
from .risk_assessment import RiskAssessment
# Import all SQLAlchemy models
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
    "User",
    "AuditLog",
    "CollectionTask",
    "CollectionResult",
    "RiskAssessment",
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
