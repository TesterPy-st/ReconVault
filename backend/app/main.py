"""
ReconVault FastAPI Main Application

This module contains the main FastAPI application setup, configuration,
and root endpoints for the ReconVault cyber reconnaissance system.
"""

import os
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.openapi.utils import get_openapi
from dotenv import load_dotenv
import logging
from datetime import datetime

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("reconvault")

# Create FastAPI application
description = """
ReconVault - Cyber Reconnaissance Intelligence System

A next-generation OSINT platform with graph-based visualization and modular intelligence pipelines.

**Features:**
- Modular OSINT collectors
- Intelligence graph construction
- AI-powered threat detection
- Ethical compliance monitoring
- Real-time data processing
"""

app = FastAPI(
    title="ReconVault API",
    description=description,
    version="0.1.0",
    contact={
        "name": "ReconVault Team",
        "email": "contact@reconvault.com"
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT"
    }
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health Check Endpoint
@app.get("/health", tags=["system"])
async def health_check():
    """
    Health check endpoint to verify API is running
    
    Returns:
        dict: System health status
    """
    logger.info("Health check endpoint called")
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "reconvault-backend",
        "version": "0.1.0"
    }

# Root Endpoint
@app.get("/", tags=["system"])
async def root():
    """
    Root endpoint providing basic system information
    
    Returns:
        dict: System information
    """
    return {
        "message": "Welcome to ReconVault API",
        "version": "0.1.0",
        "status": "operational",
        "documentation": "/docs"
    }

# Error Handling Middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """
    Middleware to log all incoming requests
    
    Args:
        request: Incoming HTTP request
        call_next: Next middleware/function to call
    
    Returns:
        Response from downstream handlers
    """
    logger.info(f"Incoming request: {request.method} {request.url}")
    
    try:
        response = await call_next(request)
        logger.info(f"Response status: {response.status_code}")
        return response
    except Exception as e:
        logger.error(f"Request failed: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"message": "Internal server error", "error": str(e)}
        )

# Custom OpenAPI schema
def custom_openapi():
    """
    Custom OpenAPI schema configuration
    
    Returns:
        dict: Customized OpenAPI schema
    """
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title="ReconVault API",
        version="0.1.0",
        description=description,
        routes=app.routes,
    )
    
    openapi_schema["info"]["x-logo"] = {
        "url": "https://raw.githubusercontent.com/reconvault/assets/main/logo.png"
    }
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

# Initialize application
@app.on_event("startup")
async def startup_event():
    """
    Startup event handler
    """
    logger.info("Starting ReconVault backend service...")
    logger.info(f"Environment: {os.getenv('ENVIRONMENT', 'development')}")
    logger.info(f"Backend version: 0.1.0")
    logger.info("All systems operational")

@app.on_event("shutdown")
async def shutdown_event():
    """
    Shutdown event handler
    """
    logger.info("Shutting down ReconVault backend service...")
    logger.info("Graceful shutdown complete")

if __name__ == "__main__":
    import uvicorn
    
    # Get configuration from environment
    host = os.getenv("BACKEND_HOST", "0.0.0.0")
    port = int(os.getenv("BACKEND_PORT", "8000"))
    
    logger.info(f"Starting server on {host}:{port}")
    
    uvicorn.run(
        "app.main:app",
        host=host,
        port=port,
        reload=os.getenv("RELOAD", "true").lower() == "true",
        log_level="info"
    )