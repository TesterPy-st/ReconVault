"""
API routes package for ReconVault.

This package contains all API route handlers for the
ReconVault intelligence system.
"""

# Import all routers
from fastapi import APIRouter

# Import route modules
from . import anomalies, audit, collection, compliance, entities, graph, health, risk, targets

# Create main API router
api_router = APIRouter(prefix="/api")

# Include all route routers
api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(targets.router, prefix="/targets", tags=["targets"])
api_router.include_router(entities.router, prefix="/entities", tags=["entities"])
api_router.include_router(graph.router, prefix="/graph", tags=["graph"])
api_router.include_router(audit.router, prefix="/audit", tags=["audit"])
api_router.include_router(collection.router, tags=["collection"])
api_router.include_router(risk.router, prefix="/risk", tags=["risk"])
api_router.include_router(anomalies.router, prefix="/ai", tags=["anomalies"])
api_router.include_router(compliance.router, prefix="/compliance", tags=["compliance"])


__all__ = ["api_router"]
