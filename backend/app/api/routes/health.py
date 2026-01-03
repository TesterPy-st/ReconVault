"""
Health check routes for ReconVault API.

This module provides health check endpoints for monitoring
the status of the API and its dependencies.
"""

import logging
from datetime import datetime, timezone
from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db, get_db_info, test_db_connection
from app.intelligence_graph.neo4j_client import get_neo4j_client
from app.models import HealthResponse
from app.services.graph_service import get_graph_service

# Configure logging
logger = logging.getLogger("reconvault.api.health")

# Create router
router = APIRouter()


@router.get("/", response_model=HealthResponse)
async def basic_health_check():
    """
    Basic health check endpoint.

    Returns:
        HealthResponse: Basic health status
    """
    logger.info("Basic health check requested")

    return HealthResponse(
        status="healthy",
        timestamp=datetime.now(timezone.utc).isoformat(),
        service="reconvault-backend",
        version=settings.APP_VERSION,
    )


@router.get("/db", response_model=Dict[str, Any])
async def database_health_check(db: Session = Depends(get_db)):
    """
    Database health check endpoint.

    Args:
        db: Database session dependency

    Returns:
        Dict[str, Any]: Database health information

    Raises:
        HTTPException: If database is unhealthy
    """
    logger.info("Database health check requested")

    try:
        # Test database connection
        db_healthy = test_db_connection()

        if not db_healthy:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Database connection failed",
            )

        # Get database information
        db_info = get_db_info()

        return {
            "status": "healthy",
            "database": "postgresql",
            "connection_test": True,
            "connection_pool": db_info,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Database health check failed: {str(e)}",
        )


@router.get("/neo4j", response_model=Dict[str, Any])
async def neo4j_health_check():
    """
    Neo4j health check endpoint.

    Returns:
        Dict[str, Any]: Neo4j health information

    Raises:
        HTTPException: If Neo4j is unhealthy
    """
    logger.info("Neo4j health check requested")

    try:
        # Get Neo4j client
        neo4j_client = get_neo4j_client()

        # Test connectivity
        neo4j_healthy = neo4j_client.verify_connectivity()

        if not neo4j_healthy:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Neo4j connection failed",
            )

        # Get database information
        db_info = neo4j_client.get_database_info()

        return {
            "status": "healthy",
            "database": "neo4j",
            "connection_test": True,
            "database_info": db_info,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    except Exception as e:
        logger.error(f"Neo4j health check failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Neo4j health check failed: {str(e)}",
        )


@router.get("/graph", response_model=Dict[str, Any])
async def graph_health_check():
    """
    Graph service health check endpoint.

    Returns:
        Dict[str, Any]: Graph service health information

    Raises:
        HTTPException: If graph service is unhealthy
    """
    logger.info("Graph service health check requested")

    try:
        # Get graph service
        graph_service = get_graph_service()

        # Check health
        health_response = graph_service.check_health()

        if not health_response.connectivity:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Graph service connectivity failed",
            )

        return {
            "status": health_response.status,
            "neo4j_status": health_response.neo4j_status,
            "connectivity": health_response.connectivity,
            "database_info": health_response.database_info,
            "performance_metrics": health_response.performance_metrics,
            "timestamp": health_response.timestamp.isoformat(),
        }

    except Exception as e:
        logger.error(f"Graph service health check failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Graph service health check failed: {str(e)}",
        )


@router.get("/full", response_model=Dict[str, Any])
async def full_health_check(db: Session = Depends(get_db)):
    """
    Comprehensive health check endpoint.

    Args:
        db: Database session dependency

    Returns:
        Dict[str, Any]: Comprehensive health information

    Raises:
        HTTPException: If any service is unhealthy
    """
    logger.info("Full health check requested")

    health_status = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "overall_status": "healthy",
        "services": {},
    }

    # Check API service
    health_status["services"]["api"] = {
        "status": "healthy",
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
    }

    # Check database
    try:
        db_healthy = test_db_connection()
        db_info = get_db_info() if db_healthy else {}

        health_status["services"]["postgresql"] = {
            "status": "healthy" if db_healthy else "unhealthy",
            "connection_test": db_healthy,
            "connection_pool": db_info,
        }

        if not db_healthy:
            health_status["overall_status"] = "unhealthy"

    except Exception as e:
        health_status["services"]["postgresql"] = {"status": "error", "error": str(e)}
        health_status["overall_status"] = "degraded"
        logger.error(f"Database health check error: {e}")

    # Check Neo4j
    try:
        neo4j_client = get_neo4j_client()
        neo4j_healthy = neo4j_client.verify_connectivity()
        db_info = neo4j_client.get_database_info() if neo4j_healthy else {}

        health_status["services"]["neo4j"] = {
            "status": "healthy" if neo4j_healthy else "unhealthy",
            "connection_test": neo4j_healthy,
            "database_info": db_info,
        }

        if not neo4j_healthy:
            health_status["overall_status"] = "degraded"

    except Exception as e:
        health_status["services"]["neo4j"] = {"status": "error", "error": str(e)}
        health_status["overall_status"] = "degraded"
        logger.error(f"Neo4j health check error: {e}")

    # Check graph service
    try:
        graph_service = get_graph_service()
        graph_health = graph_service.check_health()

        health_status["services"]["graph"] = {
            "status": graph_health.status,
            "connectivity": graph_health.connectivity,
            "performance_metrics": graph_health.performance_metrics,
        }

        if graph_health.status != "healthy":
            health_status["overall_status"] = "degraded"

    except Exception as e:
        health_status["services"]["graph"] = {"status": "error", "error": str(e)}
        health_status["overall_status"] = "degraded"
        logger.error(f"Graph service health check error: {e}")

    # Return appropriate status code
    if health_status["overall_status"] == "unhealthy":
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=health_status
        )

    return health_status


@router.get("/metrics", response_model=Dict[str, Any])
async def health_metrics(db: Session = Depends(get_db)):
    """
    Health metrics endpoint for monitoring.

    Args:
        db: Database session dependency

    Returns:
        Dict[str, Any]: Health metrics
    """
    logger.info("Health metrics requested")

    metrics = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "uptime": "unknown",  # Would track actual uptime
        "memory_usage": "unknown",  # Would track actual memory usage
        "cpu_usage": "unknown",  # Would track actual CPU usage
        "active_connections": 0,  # Would track actual connections
    }

    # Database metrics
    try:
        db_info = get_db_info()
        metrics["database"] = {
            "pool_size": db_info.get("pool_size", 0),
            "checked_in": db_info.get("checked_in", 0),
            "checked_out": db_info.get("checked_out", 0),
            "overflow": db_info.get("overflow", 0),
        }
    except Exception as e:
        metrics["database"] = {"error": str(e)}

    # Graph metrics
    try:
        graph_service = get_graph_service()
        graph_health = graph_service.check_health()
        metrics["graph"] = {
            "status": graph_health.status,
            "neo4j_connected": graph_health.connectivity,
            "total_nodes": graph_health.performance_metrics.get("total_nodes", 0),
            "total_relationships": graph_health.performance_metrics.get(
                "total_relationships", 0
            ),
        }
    except Exception as e:
        metrics["graph"] = {"error": str(e)}

    return metrics
