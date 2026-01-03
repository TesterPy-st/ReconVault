"""
Entity schemas for ReconVault API.

This module contains Pydantic schemas for entity-related
API requests and responses.
"""

from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field, validator
from datetime import datetime
from uuid import UUID
from enum import Enum


class EntityType(str, Enum):
    """Enumeration of entity types"""
    USERNAME = "username"
    EMAIL = "email"
    DOMAIN = "domain"
    IP_ADDRESS = "ip_address"
    ORG = "org"
    PHONE = "phone"
    HASH = "hash"
    URL = "url"
    SOCIAL_PROFILE = "social_profile"
    # Keep existing types for backward compatibility
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


class EntityBase(BaseModel):
    """Base entity schema with common fields"""
    
    id: Optional[UUID] = Field(None, description="Entity ID")
    type: EntityType = Field(..., description="Entity type")
    value: str = Field(..., min_length=1, max_length=500, description="Entity value")
    source: str = Field(..., max_length=100, description="Discovery source")
    confidence: float = Field(1.0, ge=0.0, le=1.0, description="Confidence score")
    discovered_at: Optional[datetime] = Field(None, description="Discovery timestamp")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")
    
    @validator("value")
    def validate_value(cls, v):
        """Validate entity value"""
        if not v or not v.strip():
            raise ValueError("Entity value cannot be empty")
        return v.strip()
    
    @validator("source")
    def validate_source(cls, v):
        """Validate source field"""
        if not v or not v.strip():
            raise ValueError("Source cannot be empty")
        return v.strip()


class EntityCreate(BaseModel):
    """Schema for creating a new entity"""
    
    type: EntityType = Field(..., description="Entity type")
    value: str = Field(..., min_length=1, max_length=500, description="Entity value")
    source: str = Field(..., max_length=100, description="Discovery source")
    confidence: Optional[float] = Field(1.0, ge=0.0, le=1.0, description="Confidence score")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")
    
    @validator("value")
    def validate_value(cls, v):
        """Validate entity value"""
        if not v or not v.strip():
            raise ValueError("Entity value cannot be empty")
        return v.strip()
    
    @validator("source")
    def validate_source(cls, v):
        """Validate source field"""
        if not v or not v.strip():
            raise ValueError("Source cannot be empty")
        return v.strip()


class EntityUpdate(BaseModel):
    """Schema for updating an existing entity"""
    
    type: Optional[EntityType] = Field(None, description="Entity type")
    name: Optional[str] = Field(None, max_length=200, description="Entity name")
    value: Optional[str] = Field(None, min_length=1, max_length=500, description="Entity value")
    risk_score: Optional[float] = Field(None, ge=0.0, le=1.0, description="Risk assessment score")
    confidence: Optional[float] = Field(None, ge=0.0, le=1.0, description="Confidence score")
    source: Optional[str] = Field(None, max_length=100, description="Discovery source")
    target_id: Optional[int] = Field(None, description="Associated target ID")
    description: Optional[str] = Field(None, max_length=1000, description="Entity description")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")
    tags: Optional[List[str]] = Field(None, description="Entity tags")
    first_seen: Optional[datetime] = Field(None, description="First seen timestamp")
    last_seen: Optional[datetime] = Field(None, description="Last seen timestamp")
    is_verified: Optional[bool] = Field(None, description="Whether entity is verified")
    is_active: Optional[bool] = Field(None, description="Whether entity is active")
    
    @validator("value")
    def validate_value(cls, v):
        """Validate entity value if provided"""
        if v is not None:
            if not v or not v.strip():
                raise ValueError("Entity value cannot be empty")
            return v.strip()
        return v
    
    @validator("source")
    def validate_source(cls, v):
        """Validate source field if provided"""
        if v is not None:
            if not v or not v.strip():
                raise ValueError("Source cannot be empty")
            return v.strip()
        return v


class EntityResponse(EntityBase):
    """Schema for entity API responses"""
    
    id: UUID = Field(..., description="Entity database ID")
    type: EntityType = Field(..., description="Entity type")
    value: str = Field(..., description="Entity value")
    source: str = Field(..., description="Discovery source")
    confidence: float = Field(..., description="Confidence score")
    discovered_at: datetime = Field(..., description="Discovery timestamp")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")
    
    class Config:
        orm_mode = True


class EntityWithRelations(EntityResponse):
    """Schema for entity with relationship count"""
    
    relationship_count: int = Field(0, description="Number of relationships")


class EntityListResponse(BaseModel):
    """Schema for entity list responses"""
    
    entities: list[EntityResponse] = Field(..., description="List of entities")
    total: int = Field(..., description="Total number of entities")
    page: int = Field(1, description="Current page number")
    per_page: int = Field(50, description="Number of items per page")
    pages: int = Field(..., description="Total number of pages")


class EntityStats(BaseModel):
    """Schema for entity statistics"""
    
    total_entities: int = Field(..., description="Total number of entities")
    active_entities: int = Field(..., description="Number of active entities")
    verified_entities: int = Field(..., description="Number of verified entities")
    entities_by_type: Dict[str, int] = Field(..., description="Entities grouped by type")
    entities_by_source: Dict[str, int] = Field(..., description="Entities grouped by source")
    entities_by_risk_level: Dict[str, int] = Field(..., description="Entities grouped by risk level")
    average_risk_score: float = Field(..., description="Average risk score")
    entities_with_target: int = Field(..., description="Number of entities linked to targets")


class EntitySearchRequest(BaseModel):
    """Schema for entity search requests"""
    
    query: Optional[str] = Field(None, description="Text search query")
    type: Optional[EntityType] = Field(None, description="Filter by entity type")
    source: Optional[str] = Field(None, description="Filter by source")
    target_id: Optional[int] = Field(None, description="Filter by target ID")
    risk_level: Optional[str] = Field(None, description="Filter by risk level")
    verified: Optional[bool] = Field(None, description="Filter by verification status")
    tags: Optional[List[str]] = Field(None, description="Filter by tags")
    created_after: Optional[datetime] = Field(None, description="Filter by creation date")
    created_before: Optional[datetime] = Field(None, description="Filter by creation date")
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


class EntitySearchResponse(BaseModel):
    """Schema for entity search responses"""
    
    entities: list[EntityResponse] = Field(..., description="Matching entities")
    total: int = Field(..., description="Total number of matching entities")
    query: Optional[str] = Field(None, description="Search query used")
    filters: Optional[Dict[str, Any]] = Field(None, description="Filters applied")


class EntityEnrichmentRequest(BaseModel):
    """Schema for entity enrichment requests"""
    
    entity_ids: List[int] = Field(..., min_items=1, max_items=100, description="Entity IDs to enrich")
    enrichment_sources: List[str] = Field(..., min_items=1, description="Enrichment sources to use")
    include_metadata: bool = Field(True, description="Whether to include metadata")


class EntityEnrichmentResponse(BaseModel):
    """Schema for entity enrichment responses"""
    
    enrichment_id: str = Field(..., description="Enrichment job ID")
    status: str = Field(..., description="Enrichment status")
    processed_entities: int = Field(..., description="Number of entities processed")
    enriched_entities: int = Field(..., description="Number of entities enriched")
    failed_entities: int = Field(..., description="Number of entities failed")
    results: Optional[Dict[int, Dict[str, Any]]] = Field(None, description="Enrichment results")


class EntityVerificationRequest(BaseModel):
    """Schema for entity verification requests"""
    
    entity_ids: List[int] = Field(..., min_items=1, max_items=100, description="Entity IDs to verify")
    verification_method: str = Field(..., description="Verification method used")
    verified_by: str = Field(..., description="Who performed verification")
    notes: Optional[str] = Field(None, description="Verification notes")


class EntityVerificationResponse(BaseModel):
    """Schema for entity verification responses"""
    
    verified_count: int = Field(..., description="Number of entities verified")
    failed_count: int = Field(..., description="Number of entities failed verification")
    results: List[Dict[str, Any]] = Field(..., description="Verification results")


class EntityBulkRequest(BaseModel):
    """Schema for bulk entity operations"""
    
    entities: list[EntityCreate] = Field(..., min_items=1, max_items=100, description="Entities to create")
    skip_duplicates: bool = Field(True, description="Whether to skip duplicates")
    link_to_target: Optional[int] = Field(None, description="Target ID to link all entities to")


class EntityBulkResponse(BaseModel):
    """Schema for bulk entity operation responses"""
    
    created: list[EntityResponse] = Field(..., description="Successfully created entities")
    skipped: list[Dict[str, Any]] = Field(default_factory=list, description="Skipped entities")
    failed: list[Dict[str, Any]] = Field(default_factory=list, description="Failed entities")


class EntityExportRequest(BaseModel):
    """Schema for entity export requests"""
    
    format: str = Field("json", description="Export format")
    include_metadata: bool = Field(True, description="Whether to include metadata")
    include_relationships: bool = Field(False, description="Whether to include relationship data")
    filters: Optional[Dict[str, Any]] = Field(None, description="Filters to apply")
    
    @validator("format")
    def validate_format(cls, v):
        """Validate export format"""
        valid_formats = ["json", "csv", "xml"]
        if v not in valid_formats:
            raise ValueError(f"Invalid format. Must be one of: {valid_formats}")
        return v


class EntityExportResponse(BaseModel):
    """Schema for entity export responses"""
    
    export_id: str = Field(..., description="Export job ID")
    format: str = Field(..., description="Export format used")
    status: str = Field(..., description="Export status")
    download_url: Optional[str] = Field(None, description="Download URL when ready")
    expires_at: Optional[datetime] = Field(None, description="Download URL expiration")


class EntityDeleteResponse(BaseModel):
    """Schema for entity deletion responses"""
    
    success: bool = Field(..., description="Whether deletion was successful")
    deleted_id: int = Field(..., description="ID of deleted entity")
    message: Optional[str] = Field(None, description="Deletion message")


class EntityTagRequest(BaseModel):
    """Schema for entity tagging requests"""
    
    entity_ids: List[int] = Field(..., min_items=1, max_items=100, description="Entity IDs to tag")
    tags: List[str] = Field(..., min_items=1, description="Tags to add")
    action: str = Field("add", description="Tag action (add/remove)")


class EntityTagResponse(BaseModel):
    """Schema for entity tagging responses"""
    
    updated_count: int = Field(..., description="Number of entities updated")
    tags_added: List[str] = Field(..., description="Tags that were added")
    tags_removed: List[str] = Field(..., description="Tags that were removed")


# Export all schemas
__all__ = [
    "EntityType",
    "EntityBase",
    "EntityCreate",
    "EntityUpdate",
    "EntityResponse",
    "EntityWithRelations",
    "EntityListResponse",
    "EntityStats",
    "EntitySearchRequest",
    "EntitySearchResponse",
    "EntityEnrichmentRequest",
    "EntityEnrichmentResponse",
    "EntityVerificationRequest",
    "EntityVerificationResponse",
    "EntityBulkRequest",
    "EntityBulkResponse",
    "EntityExportRequest",
    "EntityExportResponse",
    "EntityDeleteResponse",
    "EntityTagRequest",
    "EntityTagResponse"
]