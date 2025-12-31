"""
ReconVault Main Application
FastAPI application with cyber reconnaissance capabilities
"""

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(
    title="ReconVault API",
    description="Cyber Reconnaissance Intelligence System - Graph-based OSINT Pipeline",
    version="0.1.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check():
    """
    Health check endpoint for monitoring
    Returns system status and basic information
    """
    return {
        "status": "healthy",
        "service": "reconvault-backend",
        "version": "0.1.0",
        "message": "ReconVault API is operational"
    }


@app.get("/")
async def root():
    """
    Root endpoint
    Returns API information
    """
    return {
        "name": "ReconVault API",
        "description": "Cyber Reconnaissance Intelligence System",
        "version": "0.1.0",
        "endpoints": {
            "health": "/health",
            "docs": "/api/docs",
            "redoc": "/api/redoc"
        }
    }


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("BACKEND_PORT", 8000))
    host = os.getenv("BACKEND_HOST", "0.0.0.0")
    
    print(f"🚀 Starting ReconVault Backend on {host}:{port}")
    uvicorn.run(app, host=host, port=port)
