"""
Relationship schemas for ReconVault API.

This module contains Pydantic schemas for relationship-related
API requests and responses.
"""

from typing import Optional, Dict, Any
from pydantic import BaseModel, Field, validator
from datetime import datetime
from uuid import UUID
from enum import Enum


class RelationType(str, Enum):
    """Enumeration of relationship types"""
    MENTIONS = "mentions"
    ASSOCIATES_WITH = "associates_with"
    LOCATED_AT = "located_at"
    OWNS = "owns"
    REGISTERED_TO = "registered_to"
    RELATED_TO = "related_to"
    COMMUNICATES_WITH = "communicates_with"
    COMPROMISED_BY = "compromised_by"
    RESOLVES_TO = "resolves_to"
    HOSTED_ON = "hosted_on"
    CONNECTED_TO = "connected_to"
    DEPENDS_ON = "depends_on"
    VULNERABLE_TO = "vulnerable_to"
    USES = "uses"
    RUNS = "runs"
    CONTAINS = "contains"
    SIMILAR_TO = "similar_to"
    PART_OF = "part_of"
    SAME_AS = "same_as"
    REFERENCES = "references"
    ATTRIBUTED_TO = "attributed_to"
    THREATENS = "threatens"
    TARGETS = "targets"
    CAMPAIGN = "campaign"
    INDICATOR_OF = "indicator_of"
    LOCATED_IN = "located_in"
    REGISTERED_BY = "registered_by"
    CREATED_BY = "created_by"
    ANALYZED_BY = "analyzed_by"


class RelationshipBase(BaseModel):
    """Base relationship schema with common fields"""
    
    source_entity_id: UUID = Field(..., description="Source entity ID")
    target_entity_id: UUID = Field(..., description="Target entity ID")
    type: RelationType = Field(..., description="Relationship type")
    confidence: float = Field(1.0, ge=0.0, le=1.0, description="Confidence score")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")
    
    @validator("source_entity_id", "target_entity_id")
    def validate_entity_ids(cls, v):
        """Validate entity IDs are not null"""
        if v is None:
            raise ValueError("Entity ID cannot be null")
        return v
    
    @validator("target_entity_id")
    def validate_not_circular(cls, v, values):
        """Prevent circular self-relationships"""
        if "source_entity_id" in values and v == values["source_entity_id"]:
            raise ValueError("Cannot create self-referential relationship")
        return v


class RelationshipCreate(RelationshipBase):
    """Schema for creating a new relationship"""
    pass


class RelationshipUpdate(BaseModel):
    """Schema for updating an existing relationship"""
    
    type: Optional[RelationType] = Field(None, description="Relationship type")
    confidence: Optional[float] = Field(None, ge=0.0, le=1.0, description="Confidence score")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


class RelationshipResponse(RelationshipBase):
    """Schema for relationship API responses"""
    
    id: UUID = Field(..., description="Relationship ID")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")
    
    class Config:
        orm_mode = True


class RelationshipWithEntities(RelationshipResponse):
    """Schema for relationship with full entity data"""
    
    source_entity: Optional[Dict[str, Any]] = Field(None, description="Source entity data")
    target_entity: Optional[Dict[str, Any]] = Field(None, description="Target entity data")


class RelationshipListResponse(BaseModel):
    """Schema for relationship list responses"""
    
    relationships: list[RelationshipResponse] = Field(..., description="List of relationships")
    total: int = Field(..., description="Total number of relationships")
    page: int = Field(1, description="Current page number")
    per_page: int = Field(50, description="Number of items per page")
    pages: int = Field(..., description="Total number of pages")


class RelationshipStats(BaseModel):
    """Schema for relationship statistics"""
    
    total_relationships: int = Field(..., description="Total number of relationships")
    relationships_by_type: Dict[str, int] = Field(..., description="Relationships grouped by type")
    average_confidence: float = Field(..., description="Average confidence score")
    most_connected_entities: list[Dict[str, Any]] = Field(..., description="Most connected entities")


class RelationshipSearchRequest(BaseModel):
    """Schema for relationship search requests"""
    
    entity_id: Optional[UUID] = Field(None, description="Filter by entity ID (source or target)")
    source_entity_id: Optional[UUID] = Field(None, description="Filter by source entity ID")
    target_entity_id: Optional[UUID] = Field(None, description="Filter by target entity ID")
    type: Optional[RelationType] = Field(None, description="Filter by relationship type")
    min_confidence: Optional[float] = Field(None, ge=0.0, le=1.0, description="Minimum confidence score")
    created_after: Optional[datetime] = Field(None, description="Filter by creation date")
    created_before: Optional[datetime] = Field(None, description="Filter by creation date")
    limit: int = Field(100, ge=1, le=1000, description="Maximum results to return")
    offset: int = Field(0, ge=0, description="Number of results to skip")


class RelationshipDeleteResponse(BaseModel):
    """Schema for relationship deletion responses"""
    
    success: bool = Field(..., description="Whether deletion was successful")
    deleted_id: UUID = Field(..., description="ID of deleted relationship")
    message: Optional[str] = Field(None, description="Deletion message")


class RelationshipBulkCreate(BaseModel):
    """Schema for bulk relationship creation"""
    
    relationships: list[RelationshipCreate] = Field(..., min_items=1, max_items=100, description="Relationships to create")
    skip_duplicates: bool = Field(True, description="Whether to skip duplicates")


class RelationshipBulkResponse(BaseModel):
    """Schema for bulk relationship operation responses"""
    
    created: list[RelationshipResponse] = Field(..., description="Successfully created relationships")
    skipped: list[Dict[str, Any]] = Field(default_factory=list, description="Skipped relationships")
    failed: list[Dict[str, Any]] = Field(default_factory=list, description="Failed relationships")


__all__ = [
    "RelationType",
    "RelationshipBase",
    "RelationshipCreate",
    "RelationshipUpdate",
    "RelationshipResponse",
    "RelationshipWithEntities",
    "RelationshipListResponse",
    "RelationshipStats",
    "RelationshipSearchRequest",
    "RelationshipDeleteResponse",
    "RelationshipBulkCreate",
    "RelationshipBulkResponse",
]
