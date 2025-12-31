"""
API routes package for ReconVault.

This package contains all API route handlers for the
ReconVault intelligence system.
"""

# Import all routers
from fastapi import APIRouter

# Import route modules
from . import health, targets, entities, graph, audit

# Create main API router
api_router = APIRouter(prefix="/api")

# Include all route routers
api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(targets.router, prefix="/targets", tags=["targets"])
api_router.include_router(entities.router, prefix="/entities", tags=["entities"])
api_router.include_router(graph.router, prefix="/graph", tags=["graph"])
api_router.include_router(audit.router, prefix="/audit", tags=["audit"])


__all__ = ["api_router"]