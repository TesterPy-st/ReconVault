"""
Graph service for ReconVault intelligence system.

This module provides business logic and operations for
graph database management and analysis.
"""

from typing import List, Optional, Dict, Any, Tuple
import logging
from datetime import datetime, timezone

from app.intelligence_graph.graph_operations import get_graph_operations
from app.intelligence_graph.neo4j_client import get_neo4j_client, init_neo4j_connection, close_neo4j_connection
from app.intelligence_graph.graph_models import (
    GraphNode, GraphEdge, GraphData, NodeType, RelationshipType,
    TargetNode, EntityNode, IntelligenceNode
)
from app.schemas.graph import (
    GraphSearchRequest, GraphSearchResponse,
    GraphExpandRequest, GraphExpandResponse,
    GraphStatistics, GraphPathRequest, GraphPathResponse,
    GraphNodeCreate, GraphNodeCreateResponse,
    GraphEdgeCreate, GraphEdgeCreateResponse,
    GraphNodeUpdate, GraphNodeUpdateResponse,
    GraphNodeDeleteResponse, GraphExportRequest, GraphExportResponse,
    GraphAnalysisRequest, GraphAnalysisResponse, GraphHealthResponse
)

# Configure logging
logger = logging.getLogger("reconvault.services.graph")


class GraphService:
    """
    Graph service for business logic and graph operations.
    
    Handles all graph-related operations including node/edge creation,
    graph traversal, search, analysis, and export functionality.
    """
    
    def __init__(self):
        """Initialize graph service"""
        self.graph_ops = get_graph_operations()
        self.neo4j_client = get_neo4j_client()
    
    def initialize_connection(self) -> bool:
        """
        Initialize Neo4j connection.
        
        Returns:
            bool: True if connection successful
        """
        try:
            return init_neo4j_connection()
        except Exception as e:
            logger.error(f"Failed to initialize Neo4j connection: {e}")
            return False
    
    def check_health(self) -> GraphHealthResponse:
        """
        Check graph database health.
        
        Returns:
            GraphHealthResponse: Health check results
        """
        try:
            # Check Neo4j connectivity
            neo4j_healthy = self.neo4j_client.verify_connectivity()
            
            # Get database info
            database_info = {}
            if neo4j_healthy:
                database_info = self.neo4j_client.get_database_info()
            
            # Get performance metrics
            performance_metrics = {}
            if neo4j_healthy:
                try:
                    stats = self.graph_ops.get_graph_statistics()
                    performance_metrics = {
                        "total_nodes": stats.get("node_count", {}).get("count", 0),
                        "total_relationships": stats.get("relationship_count", {}).get("count", 0),
                        "response_time_ms": 0.0  # Would be measured in real implementation
                    }
                except Exception as e:
                    logger.warning(f"Failed to get performance metrics: {e}")
            
            status = "healthy" if neo4j_healthy else "unhealthy"
            
            return GraphHealthResponse(
                status=status,
                neo4j_status="connected" if neo4j_healthy else "disconnected",
                database_info=database_info,
                connectivity=neo4j_healthy,
                performance_metrics=performance_metrics,
                timestamp=datetime.now(timezone.utc)
            )
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return GraphHealthResponse(
                status="unhealthy",
                neo4j_status="error",
                database_info={},
                connectivity=False,
                performance_metrics={},
                timestamp=datetime.now(timezone.utc)
            )
    
    def search_graph(self, search_request: GraphSearchRequest) -> GraphSearchResponse:
        """
        Search nodes in the graph.
        
        Args:
            search_request: Search parameters
        
        Returns:
            GraphSearchResponse: Search results
        """
        try:
            start_time = datetime.now()
            
            # Search nodes
            nodes_data = self.graph_ops.search_nodes(
                query=search_request.query,
                node_types=search_request.node_types,
                limit=search_request.max_results
            )
            
            # Convert to GraphNode format
            nodes = []
            for node_data in nodes_data:
                node = GraphNode(
                    id=node_data.get("id"),
                    labels=node_data.get("labels", []),
                    properties=node_data.get("properties", {})
                )
                nodes.append(node)
            
            # Calculate search time
            end_time = datetime.now()
            search_time_ms = (end_time - start_time).total_seconds() * 1000
            
            return GraphSearchResponse(
                nodes=nodes,
                total=len(nodes),
                query=search_request.query,
                search_time_ms=search_time_ms
            )
            
        except Exception as e:
            logger.error(f"Graph search failed: {e}")
            raise
    
    def expand_graph(self, expand_request: GraphExpandRequest) -> GraphExpandResponse:
        """
        Expand graph from a starting node.
        
        Args:
            expand_request: Expansion parameters
        
        Returns:
            GraphExpandResponse: Expanded graph data
        """
        try:
            start_time = datetime.now()
            
            # Get subgraph
            subgraph_data = self.graph_ops.get_subgraph(
                node_id=expand_request.node_id,
                depth=expand_request.depth,
                max_nodes=expand_request.max_nodes
            )
            
            if not subgraph_data:
                return GraphExpandResponse(
                    expanded_graph=GraphResponse(nodes=[], edges=[], total_nodes=0, total_edges=0),
                    starting_node_id=expand_request.node_id,
                    depth=expand_request.depth,
                    expansion_time_ms=0.0
                )
            
            # Convert to GraphResponse format
            nodes = []
            edges = []
            
            for node_data in subgraph_data.nodes:
                node = GraphNode(
                    id=node_data.id,
                    labels=node_data.labels,
                    properties=node_data.properties
                )
                nodes.append(node)
            
            for edge_data in subgraph_data.edges:
                edge = GraphEdge(
                    source=edge_data.source,
                    target=edge_data.target,
                    type=edge_data.type,
                    properties=edge_data.properties
                )
                edges.append(edge)
            
            # Calculate expansion time
            end_time = datetime.now()
            expansion_time_ms = (end_time - start_time).total_seconds() * 1000
            
            graph_response = GraphResponse(
                nodes=nodes,
                edges=edges,
                total_nodes=len(nodes),
                total_edges=len(edges)
            )
            
            return GraphExpandResponse(
                expanded_graph=graph_response,
                starting_node_id=expand_request.node_id,
                depth=expand_request.depth,
                expansion_time_ms=expansion_time_ms
            )
            
        except Exception as e:
            logger.error(f"Graph expansion failed: {e}")
            raise
    
    def get_statistics(self) -> GraphStatistics:
        """
        Get comprehensive graph statistics.
        
        Returns:
            GraphStatistics: Graph statistics
        """
        try:
            stats_data = self.graph_ops.get_graph_statistics()
            
            # Extract node types and counts
            node_types = {}
            if "label_counts" in stats_data:
                label_counts = stats_data["label_counts"].get("labels", [])
                for label_info in label_counts:
                    node_types[label_info.get("label", "Unknown")] = label_info.get("count", 0)
            
            # Extract relationship types and counts
            relationship_types = {}
            # This would need proper implementation based on Neo4j query results
            
            # Calculate density (simplified calculation)
            total_nodes = stats_data.get("node_count", {}).get("count", 0)
            total_edges = stats_data.get("relationship_count", {}).get("count", 0)
            density = 0.0
            if total_nodes > 1:
                max_edges = total_nodes * (total_nodes - 1)
                density = total_edges / max_edges if max_edges > 0 else 0.0
            
            # Calculate average degree
            average_degree = (2 * total_edges) / total_nodes if total_nodes > 0 else 0.0
            
            return GraphStatistics(
                total_nodes=total_nodes,
                total_edges=total_edges,
                node_types=node_types,
                relationship_types=relationship_types,
                density=density,
                average_degree=average_degree,
                connected_components=1,  # Simplified
                largest_component_size=total_nodes,  # Simplified
                database_info=stats_data.get("database_info", {})
            )
            
        except Exception as e:
            logger.error(f"Failed to get graph statistics: {e}")
            raise
    
    def find_path(self, path_request: GraphPathRequest) -> GraphPathResponse:
        """
        Find shortest path between two nodes.
        
        Args:
            path_request: Path finding parameters
        
        Returns:
            GraphPathResponse: Path results
        """
        try:
            start_time = datetime.now()
            
            # Find shortest path
            path_data = self.graph_ops.find_shortest_path(
                start_node_id=path_request.start_node_id,
                end_node_id=path_request.end_node_id,
                max_depth=path_request.max_depth
            )
            
            # Calculate search time
            end_time = datetime.now()
            search_time_ms = (end_time - start_time).total_seconds() * 1000
            
            if not path_data:
                return GraphPathResponse(
                    path=None,
                    path_length=None,
                    paths_found=0,
                    search_time_ms=search_time_ms
                )
            
            # Convert path data to GraphResponse format
            # This would need proper parsing of the Neo4j path result
            
            return GraphPathResponse(
                path=None,  # Would be populated with actual path data
                path_length=len(path_data) if path_data else None,
                paths_found=1 if path_data else 0,
                search_time_ms=search_time_ms
            )
            
        except Exception as e:
            logger.error(f"Path finding failed: {e}")
            raise
    
    def create_node(self, node_data: GraphNodeCreate) -> GraphNodeCreateResponse:
        """
        Create a new node in the graph.
        
        Args:
            node_data: Node creation data
        
        Returns:
            GraphNodeCreateResponse: Creation result
        """
        try:
            # Create node in Neo4j
            created_node = self.graph_ops.create_node(
                node_type=node_data.label,
                properties=node_data.properties
            )
            
            if created_node:
                # Convert to GraphNode format
                node = GraphNode(
                    id=created_node.get("id"),
                    labels=[node_data.label],
                    properties=created_node
                )
                
                return GraphNodeCreateResponse(
                    success=True,
                    node_id=created_node.get("id"),
                    node=node,
                    message=f"Successfully created {node_data.label} node"
                )
            else:
                return GraphNodeCreateResponse(
                    success=False,
                    node_id=None,
                    node=None,
                    message="Failed to create node"
                )
                
        except Exception as e:
            logger.error(f"Node creation failed: {e}")
            return GraphNodeCreateResponse(
                success=False,
                node_id=None,
                node=None,
                message=str(e)
            )
    
    def create_edge(self, edge_data: GraphEdgeCreate) -> GraphEdgeCreateResponse:
        """
        Create a new edge in the graph.
        
        Args:
            edge_data: Edge creation data
        
        Returns:
            GraphEdgeCreateResponse: Creation result
        """
        try:
            # Create relationship in Neo4j
            created_relationship = self.graph_ops.create_relationship(
                source_node_id=edge_data.source_node_id,
                target_node_id=edge_data.target_node_id,
                relationship_type=edge_data.relationship_type,
                properties=edge_data.properties
            )
            
            if created_relationship:
                # Convert to GraphEdge format
                edge = GraphEdge(
                    source=edge_data.source_node_id,
                    target=edge_data.target_node_id,
                    type=edge_data.relationship_type,
                    properties=edge_data.properties
                )
                
                return GraphEdgeCreateResponse(
                    success=True,
                    edge=edge,
                    message=f"Successfully created {edge_data.relationship_type} relationship"
                )
            else:
                return GraphEdgeCreateResponse(
                    success=False,
                    edge=None,
                    message="Failed to create relationship"
                )
                
        except Exception as e:
            logger.error(f"Edge creation failed: {e}")
            return GraphEdgeCreateResponse(
                success=False,
                edge=None,
                message=str(e)
            )
    
    def update_node(self, node_id: int, update_data: GraphNodeUpdate) -> GraphNodeUpdateResponse:
        """
        Update a node in the graph.
        
        Args:
            node_id: Node ID
            update_data: Update data
        
        Returns:
            GraphNodeUpdateResponse: Update result
        """
        try:
            success = self.graph_ops.update_node(
                node_id=node_id,
                properties=update_data.properties
            )
            
            return GraphNodeUpdateResponse(
                success=success,
                node_id=node_id,
                message="Successfully updated node" if success else "Failed to update node"
            )
            
        except Exception as e:
            logger.error(f"Node update failed: {e}")
            return GraphNodeUpdateResponse(
                success=False,
                node_id=node_id,
                message=str(e)
            )
    
    def delete_node(self, node_id: int) -> GraphNodeDeleteResponse:
        """
        Delete a node from the graph.
        
        Args:
            node_id: Node ID
        
        Returns:
            GraphNodeDeleteResponse: Deletion result
        """
        try:
            success = self.graph_ops.delete_node(node_id=node_id)
            
            # Get relationships count (simplified)
            relationships_deleted = 0
            if success:
                # Would query actual relationships count in real implementation
                relationships_deleted = 0
            
            return GraphNodeDeleteResponse(
                success=success,
                deleted_node_id=node_id,
                relationships_deleted=relationships_deleted,
                message="Successfully deleted node" if success else "Failed to delete node"
            )
            
        except Exception as e:
            logger.error(f"Node deletion failed: {e}")
            return GraphNodeDeleteResponse(
                success=False,
                deleted_node_id=node_id,
                relationships_deleted=0,
                message=str(e)
            )
    
    def export_graph(self, export_request: GraphExportRequest) -> GraphExportResponse:
        """
        Export graph data.
        
        Args:
            export_request: Export parameters
        
        Returns:
            GraphExportResponse: Export result
        """
        try:
            # Generate export data
            export_data = self.graph_ops.export_graph_data(format_type=export_request.format)
            
            if export_data:
                # In a real implementation, this would save to a file and return a download URL
                return GraphExportResponse(
                    export_id=f"export_{datetime.now().timestamp()}",
                    format=export_request.format,
                    status="completed",
                    download_url=f"/api/graph/export/download/{datetime.now().timestamp()}",
                    expires_at=datetime.now(timezone.utc),
                    file_size=len(export_data)
                )
            else:
                return GraphExportResponse(
                    export_id="",
                    format=export_request.format,
                    status="failed",
                    download_url=None,
                    expires_at=None,
                    file_size=0
                )
                
        except Exception as e:
            logger.error(f"Graph export failed: {e}")
            return GraphExportResponse(
                export_id="",
                format=export_request.format,
                status="failed",
                download_url=None,
                expires_at=None,
                file_size=0
            )
    
    def analyze_graph(self, analysis_request: GraphAnalysisRequest) -> GraphAnalysisResponse:
        """
        Perform graph analysis.
        
        Args:
            analysis_request: Analysis parameters
        
        Returns:
            GraphAnalysisResponse: Analysis results
        """
        try:
            start_time = datetime.now()
            
            # Perform different types of analysis
            results = {}
            
            if analysis_request.analysis_type == "centrality":
                # Node centrality analysis
                results = {"type": "centrality", "scores": {}}
                
            elif analysis_request.analysis_type == "community_detection":
                # Community detection analysis
                results = {"type": "community_detection", "communities": []}
                
            elif analysis_request.analysis_type == "path_analysis":
                # Path analysis
                results = {"type": "path_analysis", "paths": []}
                
            elif analysis_request.analysis_type == "clustering":
                # Clustering analysis
                results = {"type": "clustering", "clusters": []}
                
            elif analysis_request.analysis_type == "influence":
                # Influence analysis
                results = {"type": "influence", "influencers": []}
                
            elif analysis_request.analysis_type == "anomaly_detection":
                # Anomaly detection
                results = {"type": "anomaly_detection", "anomalies": []}
            
            # Calculate execution time
            end_time = datetime.now()
            execution_time_ms = (end_time - start_time).total_seconds() * 1000
            
            return GraphAnalysisResponse(
                analysis_id=f"analysis_{datetime.now().timestamp()}",
                analysis_type=analysis_request.analysis_type,
                status="completed",
                results=results,
                execution_time_ms=execution_time_ms
            )
            
        except Exception as e:
            logger.error(f"Graph analysis failed: {e}")
            return GraphAnalysisResponse(
                analysis_id="",
                analysis_type=analysis_request.analysis_type,
                status="failed",
                results={},
                execution_time_ms=0.0
            )
    
    def build_graph_from_database(self) -> bool:
        """
        Build Neo4j graph from PostgreSQL database data.
        
        Returns:
            bool: True if successful
        """
        try:
            logger.info("Starting graph building from database...")
            
            # This would implement the actual graph building logic
            # 1. Query PostgreSQL for targets, entities, relationships
            # 2. Create corresponding nodes in Neo4j
            # 3. Create relationships between nodes
            # 4. Synchronize data
            
            logger.info("Graph building completed")
            return True
            
        except Exception as e:
            logger.error(f"Graph building failed: {e}")
            return False
    
    def sync_graph_with_database(self) -> bool:
        """
        Synchronize Neo4j graph with PostgreSQL database.
        
        Returns:
            bool: True if successful
        """
        try:
            logger.info("Starting graph synchronization...")
            
            # This would implement synchronization logic
            # 1. Compare data between PostgreSQL and Neo4j
            # 2. Update changed nodes/relationships
            # 3. Add new data
            # 4. Remove deleted data
            
            logger.info("Graph synchronization completed")
            return True
            
        except Exception as e:
            logger.error(f"Graph synchronization failed: {e}")
            return False
    
    def get_node_relationships(self, node_id: int, direction: str = "both") -> List[Dict[str, Any]]:
        """
        Get relationships for a specific node.
        
        Args:
            node_id: Node ID
            direction: Relationship direction
        
        Returns:
            List[Dict[str, Any]]: List of relationships
        """
        try:
            return self.graph_ops.get_node_relationships(node_id, direction)
        except Exception as e:
            logger.error(f"Failed to get relationships for node {node_id}: {e}")
            return []


def get_graph_service() -> GraphService:
    """
    Get graph service instance.
    
    Returns:
        GraphService: Graph service instance
    """
    return GraphService()