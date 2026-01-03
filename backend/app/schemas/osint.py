"""
OSINT Collection schemas for ReconVault API.

This module contains Pydantic schemas for OSINT collection
task and result management.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field, validator


class CollectionStatus(str, Enum):
    """Enumeration of collection task statuses"""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class CollectionType(str, Enum):
    """Enumeration of collection types"""

    DOMAIN = "domain"
    EMAIL = "email"
    USERNAME = "username"
    PHONE = "phone"
    IP_ADDRESS = "ip_address"
    SOCIAL_MEDIA = "social_media"
    WHOIS = "whois"
    DNS = "dns"
    SUBDOMAIN = "subdomain"
    PORT_SCAN = "port_scan"
    WEB_SCRAPE = "web_scrape"
    BREACH_DATA = "breach_data"
    DARK_WEB = "dark_web"


class CollectionTaskBase(BaseModel):
    """Base collection task schema"""

    target: str = Field(
        ..., min_length=1, max_length=500, description="Collection target"
    )
    collection_type: CollectionType = Field(
        ..., description="Type of collection to perform"
    )
    status: CollectionStatus = Field(
        CollectionStatus.PENDING, description="Task status"
    )

    @validator("target")
    def validate_target(cls, v):
        """Validate target field"""
        if not v or not v.strip():
            raise ValueError("Target cannot be empty")
        return v.strip()


class CollectionTaskCreate(BaseModel):
    """Schema for creating a new collection task"""

    target: str = Field(
        ..., min_length=1, max_length=500, description="Collection target"
    )
    collection_type: CollectionType = Field(
        ..., description="Type of collection to perform"
    )
    metadata: Optional[Dict[str, Any]] = Field(
        None, description="Additional task metadata"
    )


class CollectionTaskUpdate(BaseModel):
    """Schema for updating collection task"""

    status: Optional[CollectionStatus] = Field(None, description="Task status")
    error_message: Optional[str] = Field(None, description="Error message if failed")
    result_count: Optional[int] = Field(
        None, ge=0, description="Number of results found"
    )
    metadata: Optional[Dict[str, Any]] = Field(
        None, description="Additional task metadata"
    )


class CollectionTaskResponse(CollectionTaskBase):
    """Schema for collection task responses"""

    id: UUID = Field(..., description="Task ID")
    started_at: Optional[datetime] = Field(None, description="Task start timestamp")
    completed_at: Optional[datetime] = Field(
        None, description="Task completion timestamp"
    )
    result_count: int = Field(0, description="Number of results collected")
    error_message: Optional[str] = Field(None, description="Error message if failed")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")

    class Config:
        from_attributes = True


class CollectionTaskListResponse(BaseModel):
    """Schema for collection task list responses"""

    tasks: list[CollectionTaskResponse] = Field(
        ..., description="List of collection tasks"
    )
    total: int = Field(..., description="Total number of tasks")
    page: int = Field(1, description="Current page number")
    per_page: int = Field(50, description="Number of items per page")
    pages: int = Field(..., description="Total number of pages")


class CollectionResultBase(BaseModel):
    """Base collection result schema"""

    task_id: UUID = Field(..., description="Associated task ID")
    entity_id: UUID = Field(..., description="Discovered entity ID")
    raw_data: Dict[str, Any] = Field(..., description="Raw collection data")
    processed_at: datetime = Field(..., description="Processing timestamp")


class CollectionResultCreate(BaseModel):
    """Schema for creating collection result"""

    task_id: UUID = Field(..., description="Associated task ID")
    entity_id: UUID = Field(..., description="Discovered entity ID")
    raw_data: Dict[str, Any] = Field(..., description="Raw collection data")


class CollectionResultResponse(CollectionResultBase):
    """Schema for collection result responses"""

    id: UUID = Field(..., description="Result ID")
    created_at: datetime = Field(..., description="Creation timestamp")

    class Config:
        from_attributes = True


class CollectionResultListResponse(BaseModel):
    """Schema for collection result list responses"""

    results: list[CollectionResultResponse] = Field(
        ..., description="List of collection results"
    )
    total: int = Field(..., description="Total number of results")
    page: int = Field(1, description="Current page number")
    per_page: int = Field(50, description="Number of items per page")
    pages: int = Field(..., description="Total number of pages")


class CollectionStats(BaseModel):
    """Schema for collection statistics"""

    total_tasks: int = Field(..., description="Total number of tasks")
    pending_tasks: int = Field(..., description="Number of pending tasks")
    running_tasks: int = Field(..., description="Number of running tasks")
    completed_tasks: int = Field(..., description="Number of completed tasks")
    failed_tasks: int = Field(..., description="Number of failed tasks")
    total_results: int = Field(..., description="Total number of results")
    tasks_by_type: Dict[str, int] = Field(..., description="Tasks grouped by type")
    average_results_per_task: float = Field(..., description="Average results per task")


class CollectionSearchRequest(BaseModel):
    """Schema for collection search requests"""

    status: Optional[CollectionStatus] = Field(None, description="Filter by status")
    collection_type: Optional[CollectionType] = Field(
        None, description="Filter by type"
    )
    target: Optional[str] = Field(None, description="Filter by target (partial match)")
    created_after: Optional[datetime] = Field(
        None, description="Filter by creation date"
    )
    created_before: Optional[datetime] = Field(
        None, description="Filter by creation date"
    )
    limit: int = Field(100, ge=1, le=1000, description="Maximum results to return")
    offset: int = Field(0, ge=0, description="Number of results to skip")


__all__ = [
    "CollectionStatus",
    "CollectionType",
    "CollectionTaskBase",
    "CollectionTaskCreate",
    "CollectionTaskUpdate",
    "CollectionTaskResponse",
    "CollectionTaskListResponse",
    "CollectionResultBase",
    "CollectionResultCreate",
    "CollectionResultResponse",
    "CollectionResultListResponse",
    "CollectionStats",
    "CollectionSearchRequest",
]
