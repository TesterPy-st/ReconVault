"""
Risk Assessment schemas for ReconVault API.

This module contains Pydantic schemas for risk assessment
and risk management operations.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field, validator


class RiskLevel(str, Enum):
    """Enumeration of risk levels"""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class RiskAssessmentBase(BaseModel):
    """Base risk assessment schema"""

    entity_id: UUID = Field(..., description="Entity ID being assessed")
    level: RiskLevel = Field(..., description="Risk level")
    score: float = Field(..., ge=0.0, le=1.0, description="Numeric risk score (0-1)")
    factors: List[str] = Field(
        default_factory=list, description="Risk factors contributing to score"
    )
    assessed_at: datetime = Field(..., description="Assessment timestamp")

    @validator("score")
    def validate_score_level_consistency(cls, v, values):
        """Ensure score and level are consistent"""
        if "level" in values:
            level = values["level"]
            if level == RiskLevel.CRITICAL and v < 0.8:
                raise ValueError("Critical risk level requires score >= 0.8")
            elif level == RiskLevel.HIGH and not (0.6 <= v < 0.8):
                raise ValueError("High risk level requires score between 0.6 and 0.8")
            elif level == RiskLevel.MEDIUM and not (0.4 <= v < 0.6):
                raise ValueError("Medium risk level requires score between 0.4 and 0.6")
            elif level == RiskLevel.LOW and not (0.2 <= v < 0.4):
                raise ValueError("Low risk level requires score between 0.2 and 0.4")
            elif level == RiskLevel.INFO and v >= 0.2:
                raise ValueError("Info risk level requires score < 0.2")
        return v


class RiskAssessmentCreate(BaseModel):
    """Schema for creating risk assessment"""

    entity_id: UUID = Field(..., description="Entity ID being assessed")
    level: RiskLevel = Field(..., description="Risk level")
    score: float = Field(..., ge=0.0, le=1.0, description="Numeric risk score (0-1)")
    factors: List[str] = Field(default_factory=list, description="Risk factors")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


class RiskAssessmentUpdate(BaseModel):
    """Schema for updating risk assessment"""

    level: Optional[RiskLevel] = Field(None, description="Risk level")
    score: Optional[float] = Field(
        None, ge=0.0, le=1.0, description="Numeric risk score (0-1)"
    )
    factors: Optional[List[str]] = Field(None, description="Risk factors")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


class RiskAssessmentResponse(RiskAssessmentBase):
    """Schema for risk assessment responses"""

    id: UUID = Field(..., description="Assessment ID")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")

    class Config:
        from_attributes = True


class RiskAssessmentListResponse(BaseModel):
    """Schema for risk assessment list responses"""

    assessments: list[RiskAssessmentResponse] = Field(
        ..., description="List of risk assessments"
    )
    total: int = Field(..., description="Total number of assessments")
    page: int = Field(1, description="Current page number")
    per_page: int = Field(50, description="Number of items per page")
    pages: int = Field(..., description="Total number of pages")


class RiskSummary(BaseModel):
    """Schema for overall risk summary"""

    total_entities: int = Field(..., description="Total entities assessed")
    critical_count: int = Field(0, description="Number of critical risk entities")
    high_count: int = Field(0, description="Number of high risk entities")
    medium_count: int = Field(0, description="Number of medium risk entities")
    low_count: int = Field(0, description="Number of low risk entities")
    info_count: int = Field(0, description="Number of info level entities")
    average_risk_score: float = Field(
        ..., description="Average risk score across all entities"
    )
    highest_risk_entities: List[Dict[str, Any]] = Field(
        default_factory=list, description="Top risk entities"
    )
    risk_trend: Optional[str] = Field(
        None, description="Risk trend (increasing/decreasing/stable)"
    )


class RiskFactorAnalysis(BaseModel):
    """Schema for risk factor analysis"""

    factor: str = Field(..., description="Risk factor name")
    count: int = Field(..., description="Number of entities with this factor")
    average_score: float = Field(..., description="Average risk score for this factor")
    severity: RiskLevel = Field(..., description="Overall severity for this factor")


class RiskTrendData(BaseModel):
    """Schema for risk trend data"""

    date: datetime = Field(..., description="Date of measurement")
    average_score: float = Field(..., description="Average risk score")
    critical_count: int = Field(..., description="Count of critical entities")
    high_count: int = Field(..., description="Count of high risk entities")
    total_assessed: int = Field(..., description="Total entities assessed")


class RiskTrendResponse(BaseModel):
    """Schema for risk trend response"""

    trends: List[RiskTrendData] = Field(..., description="Risk trend data points")
    period: str = Field(..., description="Time period covered")
    change_percentage: float = Field(..., description="Percentage change in risk")


class RiskSearchRequest(BaseModel):
    """Schema for risk assessment search requests"""

    entity_id: Optional[UUID] = Field(None, description="Filter by entity ID")
    level: Optional[RiskLevel] = Field(None, description="Filter by risk level")
    min_score: Optional[float] = Field(
        None, ge=0.0, le=1.0, description="Minimum risk score"
    )
    max_score: Optional[float] = Field(
        None, ge=0.0, le=1.0, description="Maximum risk score"
    )
    factors: Optional[List[str]] = Field(None, description="Filter by risk factors")
    assessed_after: Optional[datetime] = Field(
        None, description="Filter by assessment date"
    )
    assessed_before: Optional[datetime] = Field(
        None, description="Filter by assessment date"
    )
    limit: int = Field(100, ge=1, le=1000, description="Maximum results to return")
    offset: int = Field(0, ge=0, description="Number of results to skip")


class RiskAssessRequest(BaseModel):
    """Schema for triggering risk assessment"""

    entity_ids: Optional[List[UUID]] = Field(
        None, description="Specific entity IDs to assess"
    )
    assess_all: bool = Field(False, description="Assess all entities")
    force_reassess: bool = Field(
        False, description="Force reassessment even if recent assessment exists"
    )


class RiskAssessResponse(BaseModel):
    """Schema for risk assessment trigger response"""

    job_id: str = Field(..., description="Assessment job ID")
    status: str = Field(..., description="Job status")
    entities_queued: int = Field(
        ..., description="Number of entities queued for assessment"
    )
    estimated_completion: Optional[datetime] = Field(
        None, description="Estimated completion time"
    )


__all__ = [
    "RiskLevel",
    "RiskAssessmentBase",
    "RiskAssessmentCreate",
    "RiskAssessmentUpdate",
    "RiskAssessmentResponse",
    "RiskAssessmentListResponse",
    "RiskSummary",
    "RiskFactorAnalysis",
    "RiskTrendData",
    "RiskTrendResponse",
    "RiskSearchRequest",
    "RiskAssessRequest",
    "RiskAssessResponse",
]
