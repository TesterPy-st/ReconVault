"""
API routes package for ReconVault.

This package contains all API route handlers for the
ReconVault intelligence system.
"""

# Import all routers
from fastapi import APIRouter

# Import route modules
from . import health, targets, entities, graph, audit, relationships, collection, risk

# Create main API router with v1 prefix
api_router = APIRouter(prefix="/api/v1")

# Include all route routers
api_router.include_router(health.router, tags=["health"])
api_router.include_router(targets.router, tags=["targets"])
api_router.include_router(entities.router, tags=["entities"])
api_router.include_router(relationships.router, tags=["relationships"])
api_router.include_router(collection.router, tags=["collection"])
api_router.include_router(risk.router, tags=["risk"])
api_router.include_router(graph.router, tags=["graph"])
api_router.include_router(audit.router, tags=["audit"])


__all__ = ["api_router"]