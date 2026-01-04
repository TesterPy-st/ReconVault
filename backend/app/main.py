"""
ReconVault FastAPI Main Application

This module contains the main FastAPI application setup, configuration,
and route registration for the ReconVault cyber reconnaissance system.
"""

import os
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
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

# Import configuration and database
from app.config import settings
from app.database import init_db, close_db_connections, test_db_connection
from app.intelligence_graph.neo4j_client import init_neo4j_connection, close_neo4j_connection

# Import API routers
from app.api.routes import api_router
from app.api.websockets import router as websocket_router

# Create FastAPI application
description = """
ReconVault - Cyber Reconnaissance Intelligence System

A next-generation OSINT platform with graph-based visualization and modular intelligence pipelines.

**Features:**
- Modular OSINT collectors
- Intelligence graph construction with Neo4j
- AI-powered threat detection
- Ethical compliance monitoring
- Real-time data processing with WebSockets
- Comprehensive audit logging
- PostgreSQL and Neo4j integration
"""

app = FastAPI(
    title=settings.API_TITLE,
    description=description,
    version=settings.API_VERSION,
    contact={
        "name": "ReconVault Team",
        "email": "contact@reconvault.com"
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT"
    }
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add GZIP middleware
app.add_middleware(GZipMiddleware, minimum_size=1000)

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
        "version": settings.APP_VERSION
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
        "version": settings.APP_VERSION,
        "status": "operational",
        "documentation": "/docs",
        "api_prefix": settings.API_PREFIX
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

# Global exception handler
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """
    Global HTTP exception handler
    
    Args:
        request: FastAPI request
        exc: HTTP exception
    
    Returns:
        JSON response with error details
    """
    logger.warning(f"HTTP exception: {exc.status_code} - {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": True,
            "message": exc.detail,
            "status_code": exc.status_code,
            "timestamp": datetime.utcnow().isoformat()
        }
    )

# Generic exception handler
@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """
    Global exception handler for unhandled exceptions
    
    Args:
        request: FastAPI request
        exc: Unhandled exception
    
    Returns:
        JSON response with error details
    """
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": True,
            "message": "Internal server error",
            "status_code": 500,
            "timestamp": datetime.utcnow().isoformat()
        }
    )

# Include API routers
app.include_router(api_router)

# Include WebSocket router
app.include_router(websocket_router, prefix="/ws")

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
        title=settings.API_TITLE,
        version=settings.API_VERSION,
        description=description,
        routes=app.routes,
    )
    
    openapi_schema["info"]["x-logo"] = {
        "url": "https://raw.githubusercontent.com/reconvault/assets/main/logo.png"
    }
    
    # Add security schemes
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "description": "JWT authorization header using the Bearer scheme"
        }
    }
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

# Database initialization
@app.on_event("startup")
async def startup_event():
    """
    Startup event handler for application initialization
    """
    logger.info("Starting ReconVault backend service...")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"Backend version: {settings.APP_VERSION}")
    
    try:
        # Initialize database
        logger.info("Initializing database...")
        init_db()
        logger.info("Database initialized successfully")
        
        # Test database connection
        if test_db_connection():
            logger.info("Database connection verified")
        else:
            logger.warning("Database connection test failed")
        
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        # Don't fail startup for database issues in development
    
    try:
        # Initialize Neo4j connection
        logger.info("Initializing Neo4j connection...")
        if init_neo4j_connection():
            logger.info("Neo4j connection established successfully")
        else:
            logger.warning("Neo4j connection failed")
    except Exception as e:
        logger.error(f"Neo4j initialization failed: {e}")
        # Don't fail startup for Neo4j issues in development
    
    logger.info("ReconVault backend service started successfully")

# Shutdown event handler
@app.on_event("shutdown")
async def shutdown_event():
    """
    Shutdown event handler for cleanup
    """
    logger.info("Shutting down ReconVault backend service...")
    
    try:
        # Close database connections
        close_db_connections()
        logger.info("Database connections closed")
    except Exception as e:
        logger.error(f"Error closing database connections: {e}")
    
    try:
        # Close Neo4j connection
        close_neo4j_connection()
        logger.info("Neo4j connection closed")
    except Exception as e:
        logger.error(f"Error closing Neo4j connection: {e}")
    
    logger.info("Graceful shutdown complete")

# Health check for Docker
@app.get("/healthz", tags=["system"])
@app.get("/health/live", tags=["system"])
async def healthz():
    """
    Live check endpoint
    """
    return {"status": "ok"}

# Readiness check for Docker
@app.get("/readyz", tags=["system"])
@app.get("/health/ready", tags=["system"])
async def readyz():
    """
    Kubernetes readiness check endpoint
    """
    try:
        # Check if database is ready
        db_ready = test_db_connection()

        if db_ready:
            return {"status": "ready", "database": "connected"}
        else:
            raise HTTPException(status_code=503, detail="Database not ready")
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Service not ready: {str(e)}")

# Startup check for Docker
@app.get("/startupz")
async def startupz():
    """
    Kubernetes startup check endpoint
    """
    try:
        db_ready = test_db_connection()
        if db_ready:
            return {"status": "startup_complete", "database": "connected"}
        else:
            return {"status": "starting", "database": "not_ready"}
    except Exception as e:
        return {"status": "starting", "error": str(e)}

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
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower(),
        access_log=True
    )