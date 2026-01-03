"""
Graph schemas for ReconVault API.

This module contains Pydantic schemas for graph-related
API requests and responses for Neo4j intelligence graph.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field, validator

try:
    from app.intelligence_graph.graph_models import NodeType, RelationshipType
except ImportError:
    NodeType = None
    RelationshipType = None


class NodeData(BaseModel):
    """Schema for graph node data"""

    id: Optional[int] = Field(None, description="Neo4j node ID")
    labels: List[str] = Field(..., description="Node labels")
    properties: Dict[str, Any] = Field(..., description="Node properties")

    def get_primary_label(self) -> str:
        """Get primary label for the node"""
        return self.labels[0] if self.labels else "Unknown"


class EdgeData(BaseModel):
    """Schema for graph edge data"""

    source: int = Field(..., description="Source node ID")
    target: int = Field(..., description="Target node ID")
    type: str = Field(..., description="Edge type")
    properties: Dict[str, Any] = Field(
        default_factory=dict, description="Edge properties"
    )


class GraphResponse(BaseModel):
    """Schema for graph data responses"""

    nodes: List[NodeData] = Field(default_factory=list, description="Graph nodes")
    edges: List[EdgeData] = Field(default_factory=list, description="Graph edges")
    total_nodes: int = Field(..., description="Total number of nodes")
    total_edges: int = Field(..., description="Total number of edges")


class GraphSearchRequest(BaseModel):
    """Schema for graph search requests"""

    query: str = Field(..., description="Search query")
    node_types: Optional[List[str]] = Field(None, description="Node types to search")
    max_results: int = Field(100, ge=1, le=1000, description="Maximum results")

    @validator("node_types")
    def validate_node_types(cls, v):
        """Validate node types"""
        if v is not None:
            valid_types = list(NodeType.__dict__.values())
            for node_type in v:
                if node_type not in valid_types:
                    raise ValueError(f"Invalid node type: {node_type}")
        return v


class GraphSearchResponse(BaseModel):
    """Schema for graph search responses"""

    nodes: List[NodeData] = Field(..., description="Found nodes")
    total: int = Field(..., description="Total number of results")
    query: str = Field(..., description="Search query used")
    search_time_ms: float = Field(..., description="Search execution time")


class GraphExpandRequest(BaseModel):
    """Schema for graph expansion requests"""

    node_id: int = Field(..., description="Starting node ID")
    depth: int = Field(2, ge=1, le=5, description="Expansion depth")
    relationship_types: Optional[List[str]] = Field(
        None, description="Relationship types to include"
    )
    node_types: Optional[List[str]] = Field(None, description="Node types to include")
    max_nodes: int = Field(1000, ge=1, le=10000, description="Maximum nodes to return")

    @validator("relationship_types")
    def validate_relationship_types(cls, v):
        """Validate relationship types"""
        if v is not None:
            valid_types = list(RelationshipType.__dict__.values())
            for rel_type in v:
                if rel_type not in valid_types:
                    raise ValueError(f"Invalid relationship type: {rel_type}")
        return v


class GraphExpandResponse(BaseModel):
    """Schema for graph expansion responses"""

    expanded_graph: GraphResponse = Field(..., description="Expanded graph data")
    starting_node_id: int = Field(..., description="Starting node ID")
    depth: int = Field(..., description="Expansion depth used")
    expansion_time_ms: float = Field(..., description="Expansion execution time")


class GraphStatistics(BaseModel):
    """Schema for graph statistics"""

    total_nodes: int = Field(..., description="Total number of nodes")
    total_edges: int = Field(..., description="Total number of edges")
    node_types: Dict[str, int] = Field(..., description="Node counts by type")
    relationship_types: Dict[str, int] = Field(
        ..., description="Relationship counts by type"
    )
    density: float = Field(..., description="Graph density")
    average_degree: float = Field(..., description="Average node degree")
    connected_components: int = Field(..., description="Number of connected components")
    largest_component_size: int = Field(..., description="Size of largest component")
    database_info: Dict[str, Any] = Field(..., description="Neo4j database information")


class GraphPathRequest(BaseModel):
    """Schema for path finding requests"""

    start_node_id: int = Field(..., description="Starting node ID")
    end_node_id: int = Field(..., description="Ending node ID")
    max_depth: int = Field(10, ge=1, le=50, description="Maximum path length")
    relationship_types: Optional[List[str]] = Field(
        None, description="Allowed relationship types"
    )

    @validator("relationship_types")
    def validate_relationship_types(cls, v):
        """Validate relationship types"""
        if v is not None:
            valid_types = list(RelationshipType.__dict__.values())
            for rel_type in v:
                if rel_type not in valid_types:
                    raise ValueError(f"Invalid relationship type: {rel_type}")
        return v


class GraphPathResponse(BaseModel):
    """Schema for path finding responses"""

    path: Optional[GraphResponse] = Field(None, description="Path graph data")
    path_length: Optional[int] = Field(None, description="Length of shortest path")
    paths_found: int = Field(..., description="Number of paths found")
    search_time_ms: float = Field(..., description="Search execution time")


class GraphNodeCreate(BaseModel):
    """Schema for creating graph nodes"""

    label: str = Field(..., description="Node label")
    properties: Dict[str, Any] = Field(..., description="Node properties")

    @validator("label")
    def validate_label(cls, v):
        """Validate node label"""
        valid_labels = list(NodeType.__dict__.values())
        if v not in valid_labels:
            raise ValueError(f"Invalid node label: {v}. Valid labels: {valid_labels}")
        return v


class GraphNodeCreateResponse(BaseModel):
    """Schema for node creation responses"""

    success: bool = Field(..., description="Whether creation was successful")
    node_id: Optional[int] = Field(None, description="Created node ID")
    node: Optional[NodeData] = Field(None, description="Created node data")
    message: Optional[str] = Field(None, description="Creation message")


class GraphEdgeCreate(BaseModel):
    """Schema for creating graph edges"""

    source_node_id: int = Field(..., description="Source node ID")
    target_node_id: int = Field(..., description="Target node ID")
    relationship_type: str = Field(..., description="Relationship type")
    properties: Dict[str, Any] = Field(
        default_factory=dict, description="Relationship properties"
    )

    @validator("relationship_type")
    def validate_relationship_type(cls, v):
        """Validate relationship type"""
        valid_types = list(RelationshipType.__dict__.values())
        if v not in valid_types:
            raise ValueError(
                f"Invalid relationship type: {v}. Valid types: {valid_types}"
            )
        return v


class GraphEdgeCreateResponse(BaseModel):
    """Schema for edge creation responses"""

    success: bool = Field(..., description="Whether creation was successful")
    edge: Optional[EdgeData] = Field(None, description="Created edge data")
    message: Optional[str] = Field(None, description="Creation message")


class GraphNodeUpdate(BaseModel):
    """Schema for updating graph nodes"""

    properties: Dict[str, Any] = Field(..., description="Properties to update")
    node_id: Optional[int] = Field(None, description="Node ID (if not in properties)")


class GraphNodeUpdateResponse(BaseModel):
    """Schema for node update responses"""

    success: bool = Field(..., description="Whether update was successful")
    node_id: int = Field(..., description="Updated node ID")
    message: Optional[str] = Field(None, description="Update message")


class GraphNodeDeleteResponse(BaseModel):
    """Schema for node deletion responses"""

    success: bool = Field(..., description="Whether deletion was successful")
    deleted_node_id: int = Field(..., description="Deleted node ID")
    relationships_deleted: int = Field(
        ..., description="Number of relationships deleted"
    )
    message: Optional[str] = Field(None, description="Deletion message")


class GraphExportRequest(BaseModel):
    """Schema for graph export requests"""

    format: str = Field("json", description="Export format")
    include_properties: bool = Field(True, description="Whether to include properties")
    node_types: Optional[List[str]] = Field(None, description="Node types to include")
    relationship_types: Optional[List[str]] = Field(
        None, description="Relationship types to include"
    )
    filters: Optional[Dict[str, Any]] = Field(None, description="Additional filters")

    @validator("format")
    def validate_format(cls, v):
        """Validate export format"""
        valid_formats = ["json", "cypher", "graphml"]
        if v not in valid_formats:
            raise ValueError(f"Invalid format. Must be one of: {valid_formats}")
        return v


class GraphExportResponse(BaseModel):
    """Schema for graph export responses"""

    export_id: str = Field(..., description="Export job ID")
    format: str = Field(..., description="Export format used")
    status: str = Field(..., description="Export status")
    download_url: Optional[str] = Field(None, description="Download URL when ready")
    expires_at: Optional[datetime] = Field(None, description="Download URL expiration")
    file_size: Optional[int] = Field(None, description="Export file size in bytes")


class GraphImportRequest(BaseModel):
    """Schema for graph import requests"""

    format: str = Field("json", description="Import format")
    data: str = Field(..., description="Import data")
    merge_mode: bool = Field(True, description="Whether to merge with existing data")
    node_types: Optional[List[str]] = Field(None, description="Expected node types")

    @validator("format")
    def validate_format(cls, v):
        """Validate import format"""
        valid_formats = ["json", "cypher", "graphml"]
        if v not in valid_formats:
            raise ValueError(f"Invalid format. Must be one of: {valid_formats}")
        return v


class GraphImportResponse(BaseModel):
    """Schema for graph import responses"""

    import_id: str = Field(..., description="Import job ID")
    status: str = Field(..., description="Import status")
    nodes_imported: int = Field(..., description="Number of nodes imported")
    edges_imported: int = Field(..., description="Number of edges imported")
    errors: List[str] = Field(default_factory=list, description="Import errors")


class GraphAnalysisRequest(BaseModel):
    """Schema for graph analysis requests"""

    analysis_type: str = Field(..., description="Type of analysis")
    node_ids: Optional[List[int]] = Field(None, description="Node IDs to analyze")
    parameters: Optional[Dict[str, Any]] = Field(
        None, description="Analysis parameters"
    )

    @validator("analysis_type")
    def validate_analysis_type(cls, v):
        """Validate analysis type"""
        valid_types = [
            "centrality",
            "community_detection",
            "path_analysis",
            "clustering",
            "influence",
            "anomaly_detection",
        ]
        if v not in valid_types:
            raise ValueError(f"Invalid analysis type. Must be one of: {valid_types}")
        return v


class GraphAnalysisResponse(BaseModel):
    """Schema for graph analysis responses"""

    analysis_id: str = Field(..., description="Analysis job ID")
    analysis_type: str = Field(..., description="Type of analysis performed")
    status: str = Field(..., description="Analysis status")
    results: Optional[Dict[str, Any]] = Field(None, description="Analysis results")
    execution_time_ms: float = Field(..., description="Analysis execution time")


class GraphHealthResponse(BaseModel):
    """Schema for graph health check responses"""

    status: str = Field(..., description="Overall health status")
    neo4j_status: str = Field(..., description="Neo4j connection status")
    database_info: Dict[str, Any] = Field(..., description="Database information")
    connectivity: bool = Field(..., description="Whether database is reachable")
    performance_metrics: Dict[str, float] = Field(
        ..., description="Performance metrics"
    )
    timestamp: datetime = Field(..., description="Health check timestamp")


class GraphRecommendation(BaseModel):
    """Schema for graph recommendations"""

    type: str = Field(..., description="Recommendation type")
    description: str = Field(..., description="Recommendation description")
    priority: str = Field(..., description="Priority level")
    impact: str = Field(..., description="Expected impact")
    nodes_affected: Optional[List[int]] = Field(
        None, description="Node IDs that would be affected"
    )


class GraphRecommendationsResponse(BaseModel):
    """Schema for graph recommendations responses"""

    recommendations: List[GraphRecommendation] = Field(
        ..., description="List of recommendations"
    )
    analysis_scope: Dict[str, Any] = Field(..., description="Scope of analysis")
    generated_at: datetime = Field(
        ..., description="When recommendations were generated"
    )


class GraphSnapshot(BaseModel):
    """Schema for graph snapshot"""

    timestamp: datetime = Field(..., description="Snapshot timestamp")
    node_count: int = Field(..., description="Number of nodes in graph")
    edge_count: int = Field(..., description="Number of edges in graph")
    risk_score: Optional[float] = Field(None, description="Overall graph risk score")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


class GraphQuery(BaseModel):
    """Schema for graph query with filters"""

    entity_types: Optional[List[str]] = Field(
        None, description="Filter by entity types"
    )
    relationship_types: Optional[List[str]] = Field(
        None, description="Filter by relationship types"
    )
    date_from: Optional[datetime] = Field(None, description="Filter entities from date")
    date_to: Optional[datetime] = Field(None, description="Filter entities to date")
    min_confidence: Optional[float] = Field(
        0.0, ge=0.0, le=1.0, description="Minimum confidence score"
    )
    limit: int = Field(1000, ge=1, le=10000, description="Maximum results to return")


# Export all schemas
__all__ = [
    "NodeData",
    "EdgeData",
    "GraphResponse",
    "GraphSearchRequest",
    "GraphSearchResponse",
    "GraphExpandRequest",
    "GraphExpandResponse",
    "GraphStatistics",
    "GraphPathRequest",
    "GraphPathResponse",
    "GraphNodeCreate",
    "GraphNodeCreateResponse",
    "GraphEdgeCreate",
    "GraphEdgeCreateResponse",
    "GraphNodeUpdate",
    "GraphNodeUpdateResponse",
    "GraphNodeDeleteResponse",
    "GraphExportRequest",
    "GraphExportResponse",
    "GraphImportRequest",
    "GraphImportResponse",
    "GraphAnalysisRequest",
    "GraphAnalysisResponse",
    "GraphHealthResponse",
    "GraphRecommendation",
    "GraphRecommendationsResponse",
    "GraphSnapshot",
    "GraphQuery",
]
