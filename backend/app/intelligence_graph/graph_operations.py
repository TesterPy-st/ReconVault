"""
Graph operations for Neo4j intelligence graph.

This module provides CRUD operations and advanced graph queries
for the ReconVault intelligence graph system.
"""

from typing import Dict, List, Any, Optional, Tuple
import logging
from neo4j.exceptions import ConstraintError, CypherSyntaxError

from .neo4j_client import get_neo4j_client
from .graph_models import (
    GraphNode, GraphEdge, GraphData,
    NodeType, RelationshipType,
    TargetNode, EntityNode, IntelligenceNode,
    UserNode, ThreatActorNode, LocationNode
)

# Configure logging
logger = logging.getLogger("reconvault.graph")


class GraphOperations:
    """
    Graph operations handler for Neo4j intelligence graph.
    
    Provides CRUD operations and advanced graph queries for
    managing the intelligence graph data.
    """
    
    def __init__(self):
        """Initialize graph operations with Neo4j client"""
        self.client = get_neo4j_client()
    
    # Node Operations
    
    def create_node(self, node_type: str, properties: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Create a new node in the graph.
        
        Args:
            node_type: Type of node to create
            properties: Node properties
        
        Returns:
            Optional[Dict[str, Any]]: Created node data or None
        """
        try:
            logger.info(f"Creating {node_type} node with properties: {properties}")
            
            # Add timestamp properties
            from datetime import datetime, timezone
            properties.update({
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat()
            })
            
            result = self.client.create_node(node_type, properties)
            logger.info(f"Successfully created {node_type} node")
            return result
            
        except Exception as e:
            logger.error(f"Failed to create {node_type} node: {e}")
            return None
    
    def get_node_by_id(self, node_id: int) -> Optional[Dict[str, Any]]:
        """
        Get node by Neo4j internal ID.
        
        Args:
            node_id: Neo4j internal node ID
        
        Returns:
            Optional[Dict[str, Any]]: Node data or None
        """
        try:
            node = self.client.get_node_by_id(node_id)
            if node:
                return GraphNode(
                    id=node_id,
                    labels=list(node.keys()),
                    properties=dict(node)
                ).to_dict()
            return None
        except Exception as e:
            logger.error(f"Failed to get node {node_id}: {e}")
            return None
    
    def find_node_by_property(self, node_type: str, property_name: str, property_value: Any) -> Optional[Dict[str, Any]]:
        """
        Find node by a specific property value.
        
        Args:
            node_type: Type of node to search
            property_name: Property name to search
            property_value: Property value to match
        
        Returns:
            Optional[Dict[str, Any]]: Found node or None
        """
        try:
            properties = {property_name: property_value}
            node_data = self.client.find_node(node_type, properties)
            
            if node_data:
                return GraphNode(
                    id=None,  # Will be set if we have the actual Neo4j ID
                    labels=[node_type],
                    properties=node_data
                ).to_dict()
            return None
        except Exception as e:
            logger.error(f"Failed to find {node_type} node with {property_name}={property_value}: {e}")
            return None
    
    def update_node(self, node_id: int, properties: Dict[str, Any]) -> bool:
        """
        Update node properties.
        
        Args:
            node_id: Neo4j internal node ID
            properties: Properties to update
        
        Returns:
            bool: True if update successful
        """
        try:
            # Get current node to determine type
            current_node = self.get_node_by_id(node_id)
            if not current_node:
                logger.error(f"Node {node_id} not found")
                return False
            
            # Add updated timestamp
            from datetime import datetime, timezone
            properties["updated_at"] = datetime.now(timezone.utc).isoformat()
            
            # Extract primary label for the update query
            primary_label = current_node["labels"][0]
            
            # Build match properties (exclude Neo4j internal properties)
            match_properties = {k: v for k, v in current_node["properties"].items() 
                              if not k.startswith('_')}
            
            success = self.client.update_node(primary_label, match_properties, properties)
            
            if success:
                logger.info(f"Successfully updated node {node_id}")
            else:
                logger.error(f"Failed to update node {node_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to update node {node_id}: {e}")
            return False
    
    def delete_node(self, node_id: int) -> bool:
        """
        Delete a node and all its relationships.
        
        Args:
            node_id: Neo4j internal node ID
        
        Returns:
            bool: True if deletion successful
        """
        try:
            # Get node info first
            node = self.get_node_by_id(node_id)
            if not node:
                logger.error(f"Node {node_id} not found")
                return False
            
            primary_label = node["labels"][0]
            match_properties = {k: v for k, v in node["properties"].items() 
                              if not k.startswith('_')}
            
            success = self.client.delete_node(primary_label, match_properties)
            
            if success:
                logger.info(f"Successfully deleted node {node_id}")
            else:
                logger.error(f"Failed to delete node {node_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to delete node {node_id}: {e}")
            return False
    
    # Relationship Operations
    
    def create_relationship(
        self,
        source_node_id: int,
        target_node_id: int,
        relationship_type: str,
        properties: Dict[str, Any] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Create a relationship between two nodes.
        
        Args:
            source_node_id: Source node ID
            target_node_id: Target node ID
            relationship_type: Type of relationship
            properties: Relationship properties
        
        Returns:
            Optional[Dict[str, Any]]: Created relationship data or None
        """
        try:
            # Get node information
            source_node = self.get_node_by_id(source_node_id)
            target_node = self.get_node_by_id(target_node_id)
            
            if not source_node or not target_node:
                logger.error(f"Source or target node not found: {source_node_id}, {target_node_id}")
                return None
            
            # Add timestamp properties
            from datetime import datetime, timezone
            if properties is None:
                properties = {}
            properties.update({
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat()
            })
            
            # Create relationship
            result = self.client.create_relationship(
                source_node["labels"][0],
                source_node["properties"],
                relationship_type,
                target_node["labels"][0],
                target_node["properties"],
                properties
            )
            
            logger.info(f"Successfully created {relationship_type} relationship")
            return result
            
        except Exception as e:
            logger.error(f"Failed to create relationship: {e}")
            return None
    
    def get_node_relationships(self, node_id: int, direction: str = "both") -> List[Dict[str, Any]]:
        """
        Get all relationships for a node.
        
        Args:
            node_id: Node ID
            direction: Relationship direction ("in", "out", "both")
        
        Returns:
            List[Dict[str, Any]]: List of relationships
        """
        try:
            relationships = self.client.get_relationships(node_id, direction)
            
            # Convert to GraphEdge format
            edges = []
            for rel in relationships:
                edge = GraphEdge(
                    source=rel["source_id"],
                    target=rel["target_id"],
                    type=rel["relationship_type"],
                    properties=rel["properties"]
                )
                edges.append(edge.to_dict())
            
            return edges
            
        except Exception as e:
            logger.error(f"Failed to get relationships for node {node_id}: {e}")
            return []
    
    # Graph Traversal Operations
    
    def get_subgraph(self, node_id: int, depth: int = 2, max_nodes: int = 1000) -> Optional[GraphData]:
        """
        Get subgraph starting from a node.
        
        Args:
            node_id: Starting node ID
            depth: Maximum traversal depth
            max_nodes: Maximum number of nodes to return
        
        Returns:
            Optional[GraphData]: Subgraph data or None
        """
        try:
            # Get subgraph from Neo4j
            subgraph_data = self.client.get_subgraph(node_id, depth)
            
            if not subgraph_data:
                return None
            
            # Convert nodes
            nodes = []
            for node in subgraph_data.get("nodes", []):
                graph_node = GraphNode(
                    id=None,  # Neo4j doesn't return internal IDs in this query
                    labels=[k for k in node.keys() if k.startswith('_') == False],
                    properties=node
                )
                nodes.append(graph_node)
            
            # Convert relationships
            edges = []
            for rel in subgraph_data.get("relationships", []):
                # Parse relationship data (Neo4j returns this in a specific format)
                edge = GraphEdge(
                    source=rel.get("start", 0),  # These would need proper parsing
                    target=rel.get("end", 0),
                    type=rel.get("type", "UNKNOWN"),
                    properties=rel.get("properties", {})
                )
                edges.append(edge)
            
            # Limit results if needed
            if len(nodes) > max_nodes:
                nodes = nodes[:max_nodes]
            
            graph_data = GraphData(nodes=nodes, edges=edges)
            
            logger.info(f"Retrieved subgraph with {len(nodes)} nodes and {len(edges)} edges")
            return graph_data
            
        except Exception as e:
            logger.error(f"Failed to get subgraph for node {node_id}: {e}")
            return None
    
    def search_nodes(self, query: str, node_types: List[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Search nodes by text query.
        
        Args:
            query: Text search query
            node_types: List of node types to search (None for all)
            limit: Maximum results to return
        
        Returns:
            List[Dict[str, Any]]: List of matching nodes
        """
        try:
            # Build Cypher query
            if node_types:
                labels_filter = ":".join([f":{label}" for label in node_types])
                where_clause = f"WHERE any(key IN keys(n) WHERE toString(n[key]) CONTAINS $query)"
                match_clause = f"MATCH (n{labels_filter})"
            else:
                where_clause = f"WHERE any(key IN keys(n) WHERE toString(n[key]) CONTAINS $query)"
                match_clause = "MATCH (n)"
            
            cypher_query = f"""
            {match_clause}
            {where_clause}
            RETURN n LIMIT $limit
            """
            
            results = self.client.run_query(cypher_query, {"query": query, "limit": limit})
            
            nodes = []
            for result in results:
                node_data = result["n"]
                graph_node = GraphNode(
                    id=None,
                    labels=[k for k in node_data.keys() if k.startswith('_') == False],
                    properties=node_data
                )
                nodes.append(graph_node.to_dict())
            
            logger.info(f"Found {len(nodes)} nodes matching query: {query}")
            return nodes
            
        except Exception as e:
            logger.error(f"Failed to search nodes with query '{query}': {e}")
            return []
    
    def get_graph_statistics(self) -> Dict[str, Any]:
        """
        Get comprehensive graph statistics.
        
        Returns:
            Dict[str, Any]: Graph statistics
        """
        try:
            stats = self.client.get_graph_stats()
            
            # Add additional statistics
            queries = {
                "node_types": "CALL db.labels() YIELD label RETURN collect(label) as labels",
                "relationship_types": "CALL db.relationshipTypes() YIELD relationshipType RETURN collect(relationshipType) as types",
                "total_nodes": "MATCH (n) RETURN count(n) as count",
                "total_relationships": "MATCH ()-[r]->() RETURN count(r) as count"
            }
            
            for key, query in queries.items():
                try:
                    results = self.client.run_query(query)
                    if results:
                        stats[key] = results[0]
                except Exception as e:
                    logger.warning(f"Failed to get {key} statistics: {e}")
                    stats[key] = {}
            
            logger.info("Retrieved graph statistics")
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get graph statistics: {e}")
            return {}
    
    def find_shortest_path(self, start_node_id: int, end_node_id: int, max_depth: int = 10) -> Optional[List[Dict[str, Any]]]:
        """
        Find shortest path between two nodes.
        
        Args:
            start_node_id: Starting node ID
            end_node_id: Ending node ID
            max_depth: Maximum path length
        
        Returns:
            Optional[List[Dict[str, Any]]]: Shortest path or None
        """
        try:
            query = """
            MATCH (start), (end)
            WHERE ID(start) = $start_id AND ID(end) = $end_id
            MATCH path = shortestPath((start)-[*..$max_depth]-(end))
            RETURN path
            """
            
            results = self.client.run_query(query, {
                "start_id": start_node_id,
                "end_id": end_node_id,
                "max_depth": max_depth
            })
            
            if results:
                # Parse the path (this would need proper Neo4j path parsing)
                logger.info(f"Found shortest path between {start_node_id} and {end_node_id}")
                return results[0]  # Simplified for now
            else:
                logger.info(f"No path found between {start_node_id} and {end_node_id}")
                return None
            
        except Exception as e:
            logger.error(f"Failed to find shortest path: {e}")
            return None
    
    def export_graph_data(self, format_type: str = "json") -> str:
        """
        Export graph data in specified format.
        
        Args:
            format_type: Export format ("json", "cypher", "graphml")
        
        Returns:
            str: Exported graph data
        """
        try:
            if format_type == "json":
                # Get all nodes and relationships
                nodes_query = "MATCH (n) RETURN collect(n) as nodes"
                relationships_query = "MATCH ()-[r]->() RETURN collect(r) as relationships"
                
                nodes_result = self.client.run_query(nodes_query)
                relationships_result = self.client.run_query(relationships_query)
                
                export_data = {
                    "nodes": nodes_result[0]["nodes"] if nodes_result else [],
                    "relationships": relationships_result[0]["relationships"] if relationships_result else [],
                    "exported_at": "2024-01-01T00:00:00Z"  # Would use current timestamp
                }
                
                import json
                return json.dumps(export_data, indent=2)
            
            elif format_type == "cypher":
                # Generate Cypher statements
                return "// Graph export in Cypher format\n// (Implementation would generate CREATE statements)"
            
            else:
                raise ValueError(f"Unsupported export format: {format_type}")
                
        except Exception as e:
            logger.error(f"Failed to export graph data: {e}")
            return ""
    
    def import_graph_data(self, data: str, format_type: str = "json") -> bool:
        """
        Import graph data from specified format.
        
        Args:
            data: Graph data to import
            format_type: Import format ("json", "cypher", "graphml")
        
        Returns:
            bool: True if import successful
        """
        try:
            if format_type == "json":
                import json
                graph_data = json.loads(data)
                
                # Import nodes
                for node in graph_data.get("nodes", []):
                    labels = node.get("labels", ["Unknown"])
                    properties = dict(node)
                    self.create_node(labels[0], properties)
                
                # Import relationships would go here
                logger.info(f"Imported {len(graph_data.get('nodes', []))} nodes")
                return True
            
            else:
                raise ValueError(f"Unsupported import format: {format_type}")
                
        except Exception as e:
            logger.error(f"Failed to import graph data: {e}")
            return False


# Global graph operations instance
graph_operations = GraphOperations()


def get_graph_operations() -> GraphOperations:
    """
    Get global graph operations instance.
    
    Returns:
        GraphOperations: Global graph operations handler
    """
    return graph_operations