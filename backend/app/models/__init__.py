"""
ReconVault Models Module

This module will contain data models and schemas.
Currently a placeholder for Phase 1 infrastructure setup.

Future functionality will include:
- Pydantic models for API requests/responses
- Database models
- Data validation schemas
"""

from pydantic import BaseModel
from typing import Optional, List, Dict, Any

class BaseResponse(BaseModel):
    """Base response model"""
    status: str
    message: Optional[str] = None
    data: Optional[Dict[str, Any]] = None

class HealthResponse(BaseModel):
    """Health check response model"""
    status: str
    timestamp: str
    service: str
    version: str

class ErrorResponse(BaseModel):
    """Error response model"""
    message: str
    error: Optional[str] = None
    code: Optional[int] = None
