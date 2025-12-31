"""
ReconVault API Module

This module will contain all API endpoints and routers for the ReconVault system.
Currently a placeholder for Phase 1 infrastructure setup.
"""

from fastapi import APIRouter

router = APIRouter(prefix="/api", tags=["api"])

@router.get("/")
async def api_root():
    """
    API root endpoint
    
    Returns:
        dict: API information
    """
    return {
        "message": "ReconVault API v0.1.0",
        "endpoints": [
            "/health",
            "/api/docs",
            "/api/redoc"
        ]
    }
