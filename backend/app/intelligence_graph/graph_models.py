"""
Graph models for Neo4j intelligence graph.

This module defines Neo4j node and relationship type definitions
for the ReconVault intelligence graph system.
"""

from typing import Dict, List, Any, Optional, Union
from pydantic import BaseModel, Field
from datetime import datetime
import json


class NodeType:
    """Node type constants for Neo4j graph"""
    TARGET = "Target"
    ENTITY = "Entity"
    INTELLIGENCE = "Intelligence"
    USER = "User"
    LOCATION = "Location"
    THREAT_ACTOR = "ThreatActor"
    CAMPAIGN = "Campaign"
    MALWARE = "Malware"
    VULNERABILITY = "Vulnerability"
    INDICATOR = "Indicator"


class RelationshipType:
    """Relationship type constants for Neo4j graph"""
    # Network relationships
    RESOLVES_TO = "RESOLVES_TO"
    HOSTED_ON = "HOSTED_ON"
    CONNECTED_TO = "CONNECTED_TO"
    COMMUNICATES_WITH = "COMMUNICATES_WITH"
    
    # Social relationships
    OWNS = "OWNS"
    MANAGES = "MANAGES"
    WORKS_FOR = "WORKS_FOR"
    FRIEND_OF = "FRIEND_OF"
    FOLLOWS = "FOLLOWS"
    
    # Technical relationships
    DEPENDS_ON = "DEPENDS_ON"
    VULNERABLE_TO = "VULNERABLE_TO"
    USES = "USES"
    RUNS = "RUNS"
    CONTAINS = "CONTAINS"
    
    # Intelligence relationships
    SIMILAR_TO = "SIMILAR_TO"
    PART_OF = "PART_OF"
    RELATED_TO = "RELATED_TO"
    SAME_AS = "SAME_AS"
    REFERENCES = "REFERENCES"
    
    # Threat relationships
    ATTRIBUTED_TO = "ATTRIBUTED_TO"
    THREATENS = "THREATENS"
    TARGETS = "TARGETS"
    INDICATOR_OF = "INDICATOR_OF"
    
    # Attribution relationships
    LOCATED_IN = "LOCATED_IN"
    REGISTERED_BY = "REGISTERED_BY"
    CREATED_BY = "CREATED_BY"
    ANALYZED_BY = "ANALYZED_BY"


class BaseNode(BaseModel):
    """Base model for all Neo4j nodes"""
    
    id: Optional[int] = Field(None, description="Neo4j internal node ID")
    created_at: Optional[datetime] = Field(None, description="Node creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Node last update timestamp")
    labels: Optional[List[str]] = Field(None, description="Neo4j node labels")
    
    class Config:
        arbitrary_types_allowed = True
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }
    
    def to_neo4j_properties(self) -> Dict[str, Any]:
        """
        Convert model to Neo4j properties dictionary.
        
        Returns:
            Dict[str, Any]: Properties for Neo4j
        """
        properties = self.dict(exclude={'id', 'labels'})
        
        # Convert datetime objects to ISO strings
        for key, value in properties.items():
            if isinstance(value, datetime):
                properties[key] = value.isoformat()
            elif isinstance(value, dict):
                properties[key] = json.dumps(value)
            elif isinstance(value, list):
                properties[key] = json.dumps(value)
        
        return properties
    
    @classmethod
    def from_neo4j_node(cls, node_data: Dict[str, Any]) -> "BaseNode":
        """
        Create model instance from Neo4j node data.
        
        Args:
            node_data: Neo4j node data
        
        Returns:
            BaseNode: Model instance
        """
        properties = dict(node_data)
        
        # Parse JSON strings back to objects
        for key, value in properties.items():
            if isinstance(value, str):
                try:
                    # Try to parse as JSON
                    parsed = json.loads(value)
                    properties[key] = parsed
                except (json.JSONDecodeError, TypeError):
                    # Keep as string if not valid JSON
                    pass
        
        return cls(**properties)


class TargetNode(BaseNode):
    """Neo4j node for Target entities"""
    
    # Target properties
    target_id: int = Field(..., description="Target database ID")
    type: str = Field(..., description="Target type")
    value: str = Field(..., description="Target value")
    status: str = Field(..., description="Target status")
    risk_score: float = Field(..., description="Risk assessment score")
    description: Optional[str] = Field(None, description="Target description")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")
    
    @property
    def primary_label(self) -> str:
        """Primary Neo4j label for Target nodes"""
        return NodeType.TARGET


class EntityNode(BaseNode):
    """Neo4j node for Entity objects"""
    
    # Entity properties
    entity_id: int = Field(..., description="Entity database ID")
    type: str = Field(..., description="Entity type")
    name: Optional[str] = Field(None, description="Entity name")
    value: str = Field(..., description="Entity value")
    risk_score: float = Field(..., description="Risk assessment score")
    confidence: float = Field(..., description="Confidence score")
    source: str = Field(..., description="Discovery source")
    description: Optional[str] = Field(None, description="Entity description")
    tags: Optional[List[str]] = Field(None, description="Entity tags")
    first_seen: Optional[datetime] = Field(None, description="First seen timestamp")
    last_seen: Optional[datetime] = Field(None, description="Last seen timestamp")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")
    
    @property
    def primary_label(self) -> str:
        """Primary Neo4j label for Entity nodes"""
        return NodeType.ENTITY


class IntelligenceNode(BaseNode):
    """Neo4j node for Intelligence findings"""
    
    # Intelligence properties
    intelligence_id: int = Field(..., description="Intelligence database ID")
    type: str = Field(..., description="Intelligence type")
    priority: str = Field(..., description="Intelligence priority")
    title: str = Field(..., description="Intelligence title")
    content: str = Field(..., description="Intelligence content")
    source: str = Field(..., description="Intelligence source")
    confidence: float = Field(..., description="Confidence score")
    status: str = Field(..., description="Processing status")
    tags: Optional[List[str]] = Field(None, description="Intelligence tags")
    recommendations: Optional[str] = Field(None, description="Recommendations")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")
    
    @property
    def primary_label(self) -> str:
        """Primary Neo4j label for Intelligence nodes"""
        return NodeType.INTELLIGENCE


class UserNode(BaseNode):
    """Neo4j node for User entities"""
    
    # User properties
    user_id: int = Field(..., description="User database ID")
    username: str = Field(..., description="Username")
    email: str = Field(..., description="Email address")
    full_name: Optional[str] = Field(None, description="Full name")
    role: str = Field(..., description="User role")
    status: str = Field(..., description="Account status")
    
    @property
    def primary_label(self) -> str:
        """Primary Neo4j label for User nodes"""
        return NodeType.USER


class ThreatActorNode(BaseNode):
    """Neo4j node for Threat Actor entities"""
    
    # Threat actor properties
    actor_id: str = Field(..., description="Threat actor identifier")
    name: str = Field(..., description="Actor name")
    alias: Optional[str] = Field(None, description="Known aliases")
    motivation: Optional[str] = Field(None, description="Attack motivation")
    capabilities: Optional[List[str]] = Field(None, description="Known capabilities")
    origin: Optional[str] = Field(None, description="Suspected origin")
    first_seen: Optional[datetime] = Field(None, description="First observed")
    last_seen: Optional[datetime] = Field(None, description="Last observed")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")
    
    @property
    def primary_label(self) -> str:
        """Primary Neo4j label for ThreatActor nodes"""
        return NodeType.THREAT_ACTOR


class LocationNode(BaseNode):
    """Neo4j node for Geographic locations"""
    
    # Location properties
    location_id: str = Field(..., description="Location identifier")
    name: str = Field(..., description="Location name")
    type: str = Field(..., description="Location type")
    country: Optional[str] = Field(None, description="Country code/name")
    region: Optional[str] = Field(None, description="Region")
    coordinates: Optional[Dict[str, float]] = Field(None, description="Geographic coordinates")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")
    
    @property
    def primary_label(self) -> str:
        """Primary Neo4j label for Location nodes"""
        return NodeType.LOCATION


class BaseRelationship(BaseModel):
    """Base model for all Neo4j relationships"""
    
    type: str = Field(..., description="Relationship type")
    confidence: float = Field(1.0, description="Relationship confidence")
    weight: float = Field(1.0, description="Relationship weight")
    description: Optional[str] = Field(None, description="Relationship description")
    first_observed: Optional[datetime] = Field(None, description="First observed timestamp")
    last_observed: Optional[datetime] = Field(None, description="Last observed timestamp")
    verified: bool = Field(False, description="Whether verified")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")
    
    class Config:
        arbitrary_types_allowed = True
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }
    
    def to_neo4j_properties(self) -> Dict[str, Any]:
        """
        Convert model to Neo4j properties dictionary.
        
        Returns:
            Dict[str, Any]: Properties for Neo4j
        """
        properties = self.dict()
        
        # Convert datetime objects to ISO strings
        for key, value in properties.items():
            if isinstance(value, datetime):
                properties[key] = value.isoformat()
            elif isinstance(value, dict):
                properties[key] = json.dumps(value)
            elif isinstance(value, list):
                properties[key] = json.dumps(value)
        
        return properties


class Relationship(BaseModel):
    """Model representing a relationship between two nodes"""
    
    source_node_id: int = Field(..., description="Source node ID")
    target_node_id: int = Field(..., description="Target node ID")
    relationship_type: str = Field(..., description="Relationship type")
    properties: BaseRelationship = Field(..., description="Relationship properties")
    
    def to_cypher(self) -> str:
        """
        Convert relationship to Cypher CREATE statement.
        
        Returns:
            str: Cypher relationship creation statement
        """
        props = self.properties.to_neo4j_properties()
        props_str = ", ".join([f"{k}: ${k}" for k in props.keys()])
        
        return f"""
        (source)-[:{self.relationship_type} {{{props_str}}}]->(target)
        """.strip()


class GraphNode(BaseModel):
    """Model representing a node in the intelligence graph"""
    
    id: int = Field(..., description="Neo4j node ID")
    labels: List[str] = Field(..., description="Node labels")
    properties: Dict[str, Any] = Field(..., description="Node properties")
    
    def get_primary_label(self) -> str:
        """
        Get primary label for the node.
        
        Returns:
            str: Primary node label
        """
        return self.labels[0] if self.labels else "Unknown"
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert to dictionary representation.
        
        Returns:
            Dict[str, Any]: Node data
        """
        return {
            "id": self.id,
            "labels": self.labels,
            "properties": self.properties
        }


class GraphEdge(BaseModel):
    """Model representing an edge in the intelligence graph"""
    
    source: int = Field(..., description="Source node ID")
    target: int = Field(..., description="Target node ID")
    type: str = Field(..., description="Edge type")
    properties: Dict[str, Any] = Field(..., description="Edge properties")
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert to dictionary representation.
        
        Returns:
            Dict[str, Any]: Edge data
        """
        return {
            "source": self.source,
            "target": self.target,
            "type": self.type,
            "properties": self.properties
        }


class GraphData(BaseModel):
    """Model representing the complete graph data"""
    
    nodes: List[GraphNode] = Field(default_factory=list, description="Graph nodes")
    edges: List[GraphEdge] = Field(default_factory=list, description="Graph edges")
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert to dictionary representation.
        
        Returns:
            Dict[str, Any]: Graph data
        """
        return {
            "nodes": [node.to_dict() for node in self.nodes],
            "edges": [edge.to_dict() for edge in self.edges]
        }
    
    def add_node(self, node: GraphNode) -> None:
        """
        Add a node to the graph.
        
        Args:
            node: Node to add
        """
        self.nodes.append(node)
    
    def add_edge(self, edge: GraphEdge) -> None:
        """
        Add an edge to the graph.
        
        Args:
            edge: Edge to add
        """
        self.edges.append(edge)
    
    def get_node_by_id(self, node_id: int) -> Optional[GraphNode]:
        """
        Get node by ID.
        
        Args:
            node_id: Node ID
        
        Returns:
            Optional[GraphNode]: Found node or None
        """
        for node in self.nodes:
            if node.id == node_id:
                return node
        return None
    
    def get_edges_by_node(self, node_id: int) -> List[GraphEdge]:
        """
        Get all edges connected to a node.
        
        Args:
            node_id: Node ID
        
        Returns:
            List[GraphEdge]: Connected edges
        """
        return [
            edge for edge in self.edges
            if edge.source == node_id or edge.target == node_id
        ]


# Export all models and constants
__all__ = [
    # Node types
    "NodeType",
    "RelationshipType",
    
    # Node models
    "BaseNode",
    "TargetNode",
    "EntityNode", 
    "IntelligenceNode",
    "UserNode",
    "ThreatActorNode",
    "LocationNode",
    
    # Relationship models
    "BaseRelationship",
    "Relationship",
    
    # Graph models
    "GraphNode",
    "GraphEdge",
    "GraphData"
]