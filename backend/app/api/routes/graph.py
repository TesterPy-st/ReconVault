"""
Graph API routes for ReconVault.

This module provides REST API endpoints for graph database operations
including search, expansion, analysis, and export functionality.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query, BackgroundTasks
from typing import List, Optional
import logging
from datetime import datetime, timezone

from app.services.graph_service import get_graph_service
from app.schemas.graph import (
    GraphSearchRequest, GraphSearchResponse,
    GraphExpandRequest, GraphExpandResponse,
    GraphStatistics, GraphPathRequest, GraphPathResponse,
    GraphNodeCreate, GraphNodeCreateResponse,
    GraphEdgeCreate, GraphEdgeCreateResponse,
    GraphNodeUpdate, GraphNodeUpdateResponse,
    GraphNodeDeleteResponse, GraphExportRequest, GraphExportResponse,
    GraphAnalysisRequest, GraphAnalysisResponse,
    GraphHealthResponse, GraphRecommendationsResponse
)

# Configure logging
logger = logging.getLogger("reconvault.api.graph")

# Create router
router = APIRouter()


@router.get("/health", response_model=GraphHealthResponse)
async def get_graph_health():
    """
    Get graph service health status.
    
    Returns:
        GraphHealthResponse: Graph health information
    """
    try:
        graph_service = get_graph_service()
        health = graph_service.check_health()
        
        return health
        
    except Exception as e:
        logger.error(f"Failed to get graph health: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get graph health: {str(e)}"
        )


@router.get("/statistics", response_model=GraphStatistics)
async def get_graph_statistics():
    """
    Get comprehensive graph statistics.
    
    Returns:
        GraphStatistics: Graph statistics
    """
    try:
        graph_service = get_graph_service()
        stats = graph_service.get_statistics()
        
        return stats
        
    except Exception as e:
        logger.error(f"Failed to get graph statistics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get graph statistics: {str(e)}"
        )


@router.post("/search", response_model=GraphSearchResponse)
async def search_graph(
    search_request: GraphSearchRequest
):
    """
    Search nodes in the graph.
    
    Args:
        search_request: Search parameters
    
    Returns:
        GraphSearchResponse: Search results
    """
    try:
        graph_service = get_graph_service()
        results = graph_service.search_graph(search_request)
        
        logger.info(f"Graph search completed: {results.total} results")
        return results
        
    except Exception as e:
        logger.error(f"Graph search failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Graph search failed: {str(e)}"
        )


@router.post("/expand", response_model=GraphExpandResponse)
async def expand_graph(
    expand_request: GraphExpandRequest
):
    """
    Expand graph from a starting node.
    
    Args:
        expand_request: Expansion parameters
    
    Returns:
        GraphExpandResponse: Expanded graph data
    """
    try:
        graph_service = get_graph_service()
        results = graph_service.expand_graph(expand_request)
        
        logger.info(f"Graph expansion completed: {results.expanded_graph.total_nodes} nodes")
        return results
        
    except Exception as e:
        logger.error(f"Graph expansion failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Graph expansion failed: {str(e)}"
        )


@router.post("/path", response_model=GraphPathResponse)
async def find_path(
    path_request: GraphPathRequest
):
    """
    Find shortest path between two nodes.
    
    Args:
        path_request: Path finding parameters
    
    Returns:
        GraphPathResponse: Path results
    """
    try:
        graph_service = get_graph_service()
        results = graph_service.find_path(path_request)
        
        if results.path_length:
            logger.info(f"Path found: {results.path_length} hops")
        else:
            logger.info("No path found")
        
        return results
        
    except Exception as e:
        logger.error(f"Path finding failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Path finding failed: {str(e)}"
        )


@router.post("/nodes", response_model=GraphNodeCreateResponse)
async def create_graph_node(
    node_data: GraphNodeCreate
):
    """
    Create a new node in the graph.
    
    Args:
        node_data: Node creation data
    
    Returns:
        GraphNodeCreateResponse: Creation result
    """
    try:
        graph_service = get_graph_service()
        result = graph_service.create_node(node_data)
        
        if result.success:
            logger.info(f"Created graph node: {result.node_id}")
        else:
            logger.warning(f"Failed to create graph node: {result.message}")
        
        return result
        
    except Exception as e:
        logger.error(f"Graph node creation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Graph node creation failed: {str(e)}"
        )


@router.post("/edges", response_model=GraphEdgeCreateResponse)
async def create_graph_edge(
    edge_data: GraphEdgeCreate
):
    """
    Create a new edge in the graph.
    
    Args:
        edge_data: Edge creation data
    
    Returns:
        GraphEdgeCreateResponse: Creation result
    """
    try:
        graph_service = get_graph_service()
        result = graph_service.create_edge(edge_data)
        
        if result.success:
            logger.info(f"Created graph edge: {edge_data.relationship_type}")
        else:
            logger.warning(f"Failed to create graph edge: {result.message}")
        
        return result
        
    except Exception as e:
        logger.error(f"Graph edge creation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Graph edge creation failed: {str(e)}"
        )


@router.put("/nodes/{node_id}", response_model=GraphNodeUpdateResponse)
async def update_graph_node(
    node_id: int,
    update_data: GraphNodeUpdate
):
    """
    Update a node in the graph.
    
    Args:
        node_id: Node ID
        update_data: Update data
    
    Returns:
        GraphNodeUpdateResponse: Update result
    """
    try:
        graph_service = get_graph_service()
        result = graph_service.update_node(node_id, update_data)
        
        if result.success:
            logger.info(f"Updated graph node: {node_id}")
        else:
            logger.warning(f"Failed to update graph node {node_id}: {result.message}")
        
        return result
        
    except Exception as e:
        logger.error(f"Graph node update failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Graph node update failed: {str(e)}"
        )


@router.delete("/nodes/{node_id}", response_model=GraphNodeDeleteResponse)
async def delete_graph_node(node_id: int):
    """
    Delete a node from the graph.
    
    Args:
        node_id: Node ID
    
    Returns:
        GraphNodeDeleteResponse: Deletion result
    """
    try:
        graph_service = get_graph_service()
        result = graph_service.delete_node(node_id)
        
        if result.success:
            logger.info(f"Deleted graph node: {node_id}")
        else:
            logger.warning(f"Failed to delete graph node {node_id}: {result.message}")
        
        return result
        
    except Exception as e:
        logger.error(f"Graph node deletion failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Graph node deletion failed: {str(e)}"
        )


@router.post("/export", response_model=GraphExportResponse)
async def export_graph(
    export_request: GraphExportRequest,
    background_tasks: BackgroundTasks = None
):
    """
    Export graph data.
    
    Args:
        export_request: Export parameters
        background_tasks: Background tasks
    
    Returns:
        GraphExportResponse: Export result
    """
    try:
        graph_service = get_graph_service()
        result = graph_service.export_graph(export_request)
        
        if result.status == "completed":
            logger.info(f"Graph export completed: {result.export_id}")
        else:
            logger.warning(f"Graph export failed: {result.status}")
        
        return result
        
    except Exception as e:
        logger.error(f"Graph export failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Graph export failed: {str(e)}"
        )


@router.post("/analyze", response_model=GraphAnalysisResponse)
async def analyze_graph(
    analysis_request: GraphAnalysisRequest,
    background_tasks: BackgroundTasks = None
):
    """
    Perform graph analysis.
    
    Args:
        analysis_request: Analysis parameters
        background_tasks: Background tasks
    
    Returns:
        GraphAnalysisResponse: Analysis results
    """
    try:
        graph_service = get_graph_service()
        result = graph_service.analyze_graph(analysis_request)
        
        logger.info(f"Graph analysis completed: {result.analysis_type}")
        return result
        
    except Exception as e:
        logger.error(f"Graph analysis failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Graph analysis failed: {str(e)}"
        )


@router.post("/build-from-db", response_model=dict)
async def build_graph_from_database(
    background_tasks: BackgroundTasks = None
):
    """
    Build Neo4j graph from PostgreSQL database data.
    
    Args:
        background_tasks: Background tasks
    
    Returns:
        dict: Build result
    """
    try:
        graph_service = get_graph_service()
        success = graph_service.build_graph_from_database()
        
        result = {
            "status": "completed" if success else "failed",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "message": "Graph built from database successfully" if success else "Graph building failed"
        }
        
        logger.info("Graph building from database completed")
        return result
        
    except Exception as e:
        logger.error(f"Graph building from database failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Graph building failed: {str(e)}"
        )


@router.post("/sync-db", response_model=dict)
async def sync_graph_with_database():
    """
    Synchronize Neo4j graph with PostgreSQL database.
    
    Returns:
        dict: Sync result
    """
    try:
        graph_service = get_graph_service()
        success = graph_service.sync_graph_with_database()
        
        result = {
            "status": "completed" if success else "failed",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "message": "Graph synchronized with database successfully" if success else "Graph synchronization failed"
        }
        
        logger.info("Graph synchronization with database completed")
        return result
        
    except Exception as e:
        logger.error(f"Graph synchronization failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Graph synchronization failed: {str(e)}"
        )


@router.get("/nodes/{node_id}/relationships", response_model=List[dict])
async def get_node_relationships(
    node_id: int,
    direction: str = Query("both", description="Relationship direction (in/out/both)")
):
    """
    Get relationships for a specific node.
    
    Args:
        node_id: Node ID
        direction: Relationship direction
    
    Returns:
        List[dict]: Node relationships
    """
    try:
        graph_service = get_graph_service()
        relationships = graph_service.get_node_relationships(node_id, direction)
        
        logger.info(f"Retrieved {len(relationships)} relationships for node {node_id}")
        return relationships
        
    except Exception as e:
        logger.error(f"Failed to get relationships for node {node_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get node relationships: {str(e)}"
        )


@router.get("/recommendations", response_model=GraphRecommendationsResponse)
async def get_graph_recommendations():
    """
    Get graph-based recommendations.
    
    Returns:
        GraphRecommendationsResponse: Recommendations
    """
    try:
        # In a real implementation, this would analyze the graph and provide recommendations
        recommendations = {
            "recommendations": [],
            "analysis_scope": {"total_nodes": 0, "total_edges": 0},
            "generated_at": datetime.now(timezone.utc)
        }
        
        return recommendations
        
    except Exception as e:
        logger.error(f"Failed to get graph recommendations: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get graph recommendations: {str(e)}"
        )


@router.post("/initialize", response_model=dict)
async def initialize_graph_service():
    """
    Initialize graph service and connections.
    
    Returns:
        dict: Initialization result
    """
    try:
        graph_service = get_graph_service()
        success = graph_service.initialize_connection()
        
        result = {
            "status": "initialized" if success else "failed",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "message": "Graph service initialized successfully" if success else "Graph service initialization failed"
        }
        
        logger.info("Graph service initialization completed")
        return result
        
    except Exception as e:
        logger.error(f"Graph service initialization failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Graph service initialization failed: {str(e)}"
        )