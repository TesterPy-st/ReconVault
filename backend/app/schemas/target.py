"""
Target schemas for ReconVault API.

This module contains Pydantic schemas for target-related
API requests and responses.
"""

from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field, validator

from app.models import TargetStatus, TargetType


class TargetBase(BaseModel):
    """Base target schema with common fields"""

    type: TargetType = Field(..., description="Target type")
    value: str = Field(..., min_length=1, max_length=500, description="Target value")
    status: TargetStatus = Field(TargetStatus.ACTIVE, description="Target status")
    risk_score: float = Field(0.0, ge=0.0, le=1.0, description="Risk assessment score")
    description: Optional[str] = Field(
        None, max_length=1000, description="Target description"
    )
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")

    @validator("value")
    def validate_value(cls, v):
        """Validate target value based on type"""
        if not v or not v.strip():
            raise ValueError("Target value cannot be empty")
        return v.strip()


class TargetCreate(TargetBase):
    """Schema for creating a new target"""

    pass


class TargetUpdate(BaseModel):
    """Schema for updating an existing target"""

    type: Optional[TargetType] = Field(None, description="Target type")
    value: Optional[str] = Field(
        None, min_length=1, max_length=500, description="Target value"
    )
    status: Optional[TargetStatus] = Field(None, description="Target status")
    risk_score: Optional[float] = Field(
        None, ge=0.0, le=1.0, description="Risk assessment score"
    )
    description: Optional[str] = Field(
        None, max_length=1000, description="Target description"
    )
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")
    is_active: Optional[bool] = Field(None, description="Whether target is active")

    @validator("value")
    def validate_value(cls, v):
        """Validate target value if provided"""
        if v is not None:
            if not v or not v.strip():
                raise ValueError("Target value cannot be empty")
            return v.strip()
        return v


class TargetResponse(TargetBase):
    """Schema for target API responses"""

    id: int = Field(..., description="Target database ID")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    is_active: bool = Field(..., description="Whether target is active")

    # Computed fields
    risk_level: str = Field(..., description="Human-readable risk level")

    class Config:
        from_attributes = True

    @classmethod
    def from_orm(cls, target) -> "TargetResponse":
        """Create response from SQLAlchemy model"""
        return cls(
            id=target.id,
            type=target.type,
            value=target.value,
            status=target.status,
            risk_score=target.risk_score,
            description=target.description,
            metadata=target.meta if hasattr(target, "meta") else target.metadata,
            created_at=target.created_at,
            updated_at=target.updated_at,
            is_active=target.is_active,
            risk_level=target.risk_level,
        )


class TargetListResponse(BaseModel):
    """Schema for target list responses"""

    targets: list[TargetResponse] = Field(..., description="List of targets")
    total: int = Field(..., description="Total number of targets")
    page: int = Field(1, description="Current page number")
    per_page: int = Field(50, description="Number of items per page")
    pages: int = Field(..., description="Total number of pages")


class TargetStats(BaseModel):
    """Schema for target statistics"""

    total_targets: int = Field(..., description="Total number of targets")
    active_targets: int = Field(..., description="Number of active targets")
    targets_by_type: Dict[str, int] = Field(..., description="Targets grouped by type")
    targets_by_status: Dict[str, int] = Field(
        ..., description="Targets grouped by status"
    )
    targets_by_risk_level: Dict[str, int] = Field(
        ..., description="Targets grouped by risk level"
    )
    average_risk_score: float = Field(..., description="Average risk score")


class TargetSearchRequest(BaseModel):
    """Schema for target search requests"""

    query: Optional[str] = Field(None, description="Text search query")
    type: Optional[TargetType] = Field(None, description="Filter by target type")
    status: Optional[TargetStatus] = Field(None, description="Filter by status")
    risk_level: Optional[str] = Field(None, description="Filter by risk level")
    created_after: Optional[datetime] = Field(
        None, description="Filter by creation date"
    )
    created_before: Optional[datetime] = Field(
        None, description="Filter by creation date"
    )
    limit: int = Field(100, ge=1, le=1000, description="Maximum results to return")
    offset: int = Field(0, ge=0, description="Number of results to skip")

    @validator("risk_level")
    def validate_risk_level(cls, v):
        """Validate risk level filter"""
        if v is not None:
            valid_levels = ["critical", "high", "medium", "low", "minimal"]
            if v not in valid_levels:
                raise ValueError(f"Invalid risk level. Must be one of: {valid_levels}")
        return v


class TargetSearchResponse(BaseModel):
    """Schema for target search responses"""

    targets: list[TargetResponse] = Field(..., description="Matching targets")
    total: int = Field(..., description="Total number of matching targets")
    query: Optional[str] = Field(None, description="Search query used")
    filters: Optional[Dict[str, Any]] = Field(None, description="Filters applied")


class TargetBulkRequest(BaseModel):
    """Schema for bulk target operations"""

    targets: list[TargetCreate] = Field(
        ..., min_items=1, max_items=100, description="Targets to create"
    )
    skip_duplicates: bool = Field(True, description="Whether to skip duplicate targets")


class TargetBulkResponse(BaseModel):
    """Schema for bulk target operation responses"""

    created: list[TargetResponse] = Field(
        ..., description="Successfully created targets"
    )
    skipped: list[Dict[str, Any]] = Field(
        default_factory=list, description="Skipped targets"
    )
    failed: list[Dict[str, Any]] = Field(
        default_factory=list, description="Failed targets"
    )


class TargetExportRequest(BaseModel):
    """Schema for target export requests"""

    format: str = Field("json", description="Export format")
    include_metadata: bool = Field(True, description="Whether to include metadata")
    filters: Optional[Dict[str, Any]] = Field(None, description="Filters to apply")

    @validator("format")
    def validate_format(cls, v):
        """Validate export format"""
        valid_formats = ["json", "csv", "xml"]
        if v not in valid_formats:
            raise ValueError(f"Invalid format. Must be one of: {valid_formats}")
        return v


class TargetExportResponse(BaseModel):
    """Schema for target export responses"""

    export_id: str = Field(..., description="Export job ID")
    format: str = Field(..., description="Export format used")
    status: str = Field(..., description="Export status")
    download_url: Optional[str] = Field(None, description="Download URL when ready")
    expires_at: Optional[datetime] = Field(None, description="Download URL expiration")


class TargetDeleteResponse(BaseModel):
    """Schema for target deletion responses"""

    success: bool = Field(..., description="Whether deletion was successful")
    deleted_id: int = Field(..., description="ID of deleted target")
    message: Optional[str] = Field(None, description="Deletion message")


class TargetImportRequest(BaseModel):
    """Schema for target import requests"""

    format: str = Field("json", description="Import format")
    data: str = Field(..., description="Import data")
    skip_duplicates: bool = Field(True, description="Whether to skip duplicates")
    update_existing: bool = Field(
        False, description="Whether to update existing targets"
    )

    @validator("format")
    def validate_format(cls, v):
        """Validate import format"""
        valid_formats = ["json", "csv"]
        if v not in valid_formats:
            raise ValueError(f"Invalid format. Must be one of: {valid_formats}")
        return v


class TargetImportResponse(BaseModel):
    """Schema for target import responses"""

    import_id: str = Field(..., description="Import job ID")
    status: str = Field(..., description="Import status")
    processed: int = Field(..., description="Number of targets processed")
    created: int = Field(..., description="Number of targets created")
    updated: int = Field(..., description="Number of targets updated")
    skipped: int = Field(..., description="Number of targets skipped")
    failed: int = Field(..., description="Number of targets failed")
    errors: list[str] = Field(default_factory=list, description="Import errors")


# Export all schemas
__all__ = [
    "TargetBase",
    "TargetCreate",
    "TargetUpdate",
    "TargetResponse",
    "TargetListResponse",
    "TargetStats",
    "TargetSearchRequest",
    "TargetSearchResponse",
    "TargetBulkRequest",
    "TargetBulkResponse",
    "TargetExportRequest",
    "TargetExportResponse",
    "TargetDeleteResponse",
    "TargetImportRequest",
    "TargetImportResponse",
]
