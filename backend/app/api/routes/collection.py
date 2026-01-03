"""
Enhanced Collection API Routes for ReconVault OSINT Pipeline

This module provides REST endpoints for:
- Starting comprehensive OSINT collections
- Managing collection tasks
- Retrieving collection results
- Collection history and analytics
- Task status tracking and cancellation
"""

from fastapi import APIRouter, HTTPException, Query, Path, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel, validator, Field  # Updated import for pydantic v2
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from enum import Enum
import asyncio
import logging
import json
from celery.result import AsyncResult
from celery import group

# Import Celery tasks
from ...automation.celery_tasks import (
    collect_web_osint, collect_social_osint, collect_domain_osint,
    collect_ip_osint, collect_email_osint, collect_media_osint,
    collect_darkweb_osint, collect_geo_osint, full_reconnaissance,
    normalize_collected_data
)
from ...automation.celery_config import app as celery_app, get_task_queue, get_collector_priority
from ...services.normalization_service import NormalizationService


# Configure logging
logger = logging.getLogger(__name__)

# API Router
router = APIRouter(tags=["OSINT Collection"], prefix="/api/v1/collection")


# Data Models
class CollectionType(str, Enum):
    """Available collection types"""
    WEB = "web"
    SOCIAL = "social"
    DOMAIN = "domain"
    IP = "ip"
    EMAIL = "email"
    MEDIA = "media"
    DARKWEB = "darkweb"
    GEO = "geo"
    FULL = "full_recon"


class CollectionPriority(str, Enum):
    """Collection priority levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class StartCollectionRequest(BaseModel):
    """Request model for starting OSINT collection"""
    target: str = Field(..., description="Target to collect intelligence on (domain, IP, email, username, etc.)")
    collection_types: List[CollectionType] = Field(
        default=[CollectionType.FULL],
        description="Types of collection to perform"
    )
    include_dark_web: bool = Field(default=False, description="Include dark web collection (requires Tor)")
    include_media: bool = Field(default=False, description="Include media file analysis if URLs are present")
    priority: CollectionPriority = Field(default=CollectionPriority.MEDIUM, description="Collection priority")
    timeout: Optional[int] = Field(default=180, description="Collection timeout in seconds")
    callback_url: Optional[str] = Field(None, description="Webhook URL for completion notification")

    @validator('target')
    def validate_target(cls, v):
        if not v or len(v.strip()) < 3:
            raise ValueError("Target must be at least 3 characters")
        return v.strip()

    @validator('collection_types')
    def validate_collection_types(cls, v):
        if not v:
            raise ValueError("At least one collection type must be specified")
        return v

    class Config:
        schema_extra = {
            "example": {
                "target": "example.com",
                "collection_types": ["domain", "web", "email"],
                "include_dark_web": False,
                "priority": "medium"
            }
        }


class CollectionTaskResponse(BaseModel):
    """Response model for collection task"""
    task_id: str
    target: str
    status: str
    collection_types: List[str]
    estimated_time: int
    started_at: str
    result_url: str


class TaskStatusResponse(BaseModel):
    """Response model for task status"""
    task_id: str
    target: str
    status: str
    progress_percent: float
    collectors_completed: List[str]
    collectors_pending: List[str]
    entities_created: int
    started_at: str
    completed_at: Optional[str] = None
    runtime_seconds: Optional[float] = None
    error: Optional[str] = None


class CollectionResultsResponse(BaseModel):
    """Response model for collection results"""
    task_id: str
    target: str
    status: str
    entities_created: int
    relationships_created: int
    data_sources: List[str]
    entities: List[Dict[str, Any]]
    errors: List[str] = []
    metadata: Dict[str, Any]


class CollectionHistoryFilter(BaseModel):
    """Filter options for collection history"""
    target: Optional[str] = None
    status: Optional[str] = None
    collection_type: Optional[str] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    limit: int = 100
    offset: int = 0


class DataSourceInfo(BaseModel):
    """Data source information"""
    name: str
    description: str
    entity_types: List[str]
    rate_limit: str
    requires_auth: bool
    cost_tier: str


# In-memory task tracking (in production, use Redis/database)
# This is a simple implementation for demonstration
_task_tracker: Dict[str, Dict[str, Any]] = {}

# Initialize normalization service
normalization_service = NormalizationService(use_dask=True, use_minhash=True)


# API Endpoints
@router.post("/start", response_model=CollectionTaskResponse, status_code=202)
async def start_collection(request: StartCollectionRequest):
    """
    Start comprehensive OSINT collection for a target
    
    This endpoint initiates one or more collectors to gather intelligence
    on the specified target. Supports various target types:
    - Domains (example.com)
    - IP addresses (1.2.3.4)
    - Email addresses (user@example.com)
    - Usernames (for social media)
    - URLs (https://example.com)
    
    Process:
    1. Validates target and collection types
    2. Routes to appropriate collector(s)
    3. Queues tasks via Celery
    4. Returns task ID for status tracking
    """
    try:
        logger.info(f"Starting collection for target: {request.target} with types: {request.collection_types}")
        
        # Determine which collectors to use
        collectors_to_use = _determine_collectors(request)
        
        if CollectionType.FULL in collectors_to_use:
            # Use full reconnaissance task
            logger.info(f"Executing full reconnaissance for: {request.target}")
            
            # Map priority
            priority_mapping = {
                CollectionPriority.LOW: 3,
                CollectionPriority.MEDIUM: 5,
                CollectionPriority.HIGH: 8,
                CollectionPriority.CRITICAL: 10
            }
            task_priority = priority_mapping.get(request.priority, 5)
            
            # Launch full reconnaissance
            task = full_reconnaissance.apply_async(
                args=[request.target],
                kwargs={
                    'collection_types': [ct.value for ct in collectors_to_use if ct != CollectionType.FULL],
                    'timeout': request.timeout
                },
                priority=task_priority,
                queue='osint_high_priority'
            )
            
        else:
            # Launch individual collector tasks
            tasks = []
            
            # Map collection types to tasks
            task_mapping = {
                CollectionType.WEB: collect_web_osint,
                CollectionType.SOCIAL: collect_social_osint,
                CollectionType.DOMAIN: collect_domain_osint,
                CollectionType.IP: collect_ip_osint,
                CollectionType.EMAIL: collect_email_osint,
                CollectionType.MEDIA: collect_media_osint,
                CollectionType.DARKWEB: collect_darkweb_osint,
                CollectionType.GEO: collect_geo_osint
            }
            
            for collection_type in collectors_to_use:
                if collection_type in task_mapping:
                    task_func = task_mapping[collection_type]
                    
                    # Determine queue based on type
                    queue_name = get_task_queue(collection_type.value)
                    priority = get_collector_priority(collection_type.value)
                    
                    # Create task signature
                    task_sig = task_func.s(request.target, timeout=request.timeout)
                    tasks.append(task_sig)
            
            if not tasks:
                raise HTTPException(status_code=400, detail="No valid collectors found for specified types")
            
            # Group tasks for parallel execution
            job = group(tasks)
            task = job.apply_async()
        
        # Store task metadata
        _track_task(
            task_id=task.id,
            target=request.target,
            types=[ct.value for ct in collectors_to_use],
            priority=request.priority.value
        )
        
        # Estimate time based on collectors
        estimated_time = _estimate_collection_time(collectors_to_use)
        
        logger.info(f"Collection task created: {task.id} with estimated time: {estimated_time}s")
        
        return CollectionTaskResponse(
            task_id=task.id,
            target=request.target,
            status="QUEUED",
            collection_types=[ct.value for ct in collectors_to_use],
            estimated_time=estimated_time,
            started_at=datetime.utcnow().isoformat(),
            result_url=f"/api/v1/collection/results/{task.id}"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to start collection: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to start collection: {str(e)}")


@router.get("/tasks/{task_id}", response_model=TaskStatusResponse)
async def get_task_status(task_id: str = Path(..., description="Task ID to retrieve status for")):
    """
    Get collection task status with progress information
    
    Returns real-time progress:
    - Overall completion percentage
- Individual collector completion
    - Entities found so far
    - Runtime and estimated remaining time
    - Any errors encountered
    """
    try:
        # Check if this is a Celery task
        if task_id and len(task_id) > 10:  # Basic validation
            task_result = AsyncResult(task_id, app=celery_app)
            
            if task_result:
                state = task_result.state
                
                # Parse task info
                if hasattr(task_result, 'info') and task_result.info:
                    info = task_result.info
                    
                    # Handle different task types (full recon vs individual)
                    if isinstance(info, dict):
                        # Full reconnaissance task
                        if 'collectors_completed' in info:
                            completed = info.get('collectors_completed', 0)
                            pending = info.get('collectors_pending', 0)
                            progress = (completed / max(pending + completed, 1)) * 100
                            
                            return TaskStatusResponse(
                                task_id=task_id,
                                target=info.get('target', 'unknown'),
                                status=state,
                                progress_percent=progress,
                                collectors_completed=info.get('collectors_completed_list', []),
                                collectors_pending=[],  # Would be calculated
                                entities_created=info.get('total_entities', 0),
                                started_at=info.get('started_at', ''),
                                runtime_seconds=(datetime.utcnow() - datetime.fromisoformat(info.get('started_at', datetime.utcnow().isoformat()))).total_seconds() if info.get('started_at') else 0
                            )
                        
                        # Individual collector task
                        else:
                            entities_count = info.get('entities_created', 0) if isinstance(info, dict) else 0
                            return TaskStatusResponse(
                                task_id=task_id,
                                target=info.get('target', 'unknown') if isinstance(info, dict) else 'unknown',
                                status=state,
                                progress_percent=100 if state == 'SUCCESS' else 50,
                                collectors_completed=[info.get('collector_type', 'unknown')] if isinstance(info, dict) else [],
                                collectors_pending=[],
                                entities_created=entities_count,
                                started_at='',  # Would parse from task metadata
                                error=str(info) if state == 'FAILURE' else None
                            )
        
        # Check local task tracker
        task_info = _get_tracked_task(task_id)
        if task_info:
            return TaskStatusResponse(
                task_id=task_id,
                target=task_info.get('target', 'unknown'),
                status=task_info.get('status', 'UNKNOWN'),
                progress_percent=task_info.get('progress', 0),
                collectors_completed=task_info.get('completed', []),
                collectors_pending=task_info.get('pending', []),
                entities_created=task_info.get('entities_found', 0),
                started_at=task_info.get('started_at', ''),
                completed_at=task_info.get('completed_at')
            )
        
        # Task not found
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found or has expired")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving task status: {e}")
        return TaskStatusResponse(
            task_id=task_id,
            target="unknown",
            status="UNKNOWN",
            progress_percent=0,
            collectors_completed=[],
            collectors_pending=[],
            entities_created=0,
            started_at="",
            error=f"Failed to retrieve status: {str(e)}"
        )


@router.get("/results/{task_id}", response_model=CollectionResultsResponse)
async def get_collection_results(task_id: str = Path(..., description="Task ID to retrieve results for")):
    """
    Get collection results for completed task
    
    Returns:
    - All entities discovered
    - Relationships between entities
    - Data sources used
    - Processing errors if any
    - Risk analysis results
    """
    try:
        # Get task result
        task_result = AsyncResult(task_id, app=celery_app)
        
        if not task_result.ready():
            raise HTTPException(status_code=409, detail="Task not yet completed. Use /tasks/{task_id} to check status.")
        
        if task_result.failed():
            raise HTTPException(status_code=500, detail=f"Task failed: {str(task_result.result)}")
        
        # Get task result data
        result_data = task_result.get()
        
        if not result_data or not isinstance(result_data, dict):
            raise HTTPException(status_code=500, detail="Invalid or empty task result")
        
        # Extract entity data (handle both full recon and individual collector results)
        if 'entities' in result_data:
            entities = result_data['entities']
            errors = result_data.get('errors', [])
            sources = list(set(e.get('source', 'unknown') for e in entities))
            relationship_count = sum(1 for e in entities if 'relationship_type' in e.get('type', ''))
        else:
            # This might be a full recon result with different structure
            entities = []
            errors = result_data.get('errors', [])
            sources = result_data.get('data_sources', [])
            relationship_count = 0
        
        # Normalize results
        if entities:
            normalized = await _normalize_results(entities)
            entities = normalized['entities']
            sources = normalized['sources']
        
        return CollectionResultsResponse(
            task_id=task_id,
            target=result_data.get('target', 'unknown'),
            status=result_data.get('status', 'COMPLETED'),
            entities_created=len(entities),
            relationships_created=relationship_count,
            data_sources=sources,
            entities=entities,
            errors=errors,
            metadata=result_data.get('metadata', {})
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving collection results: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve results: {str(e)}")


@router.post("/cancel/{task_id}")
async def cancel_collection_task(task_id: str = Path(..., description="Task ID to cancel")):
    """
    Cancel a running collection task
    
    Note: Only works for tasks that haven't already started processing.
    Some collectors may not be interruptible mid-collection.
    """
    try:
        task_result = AsyncResult(task_id, app=celery_app)
        
        if task_result.state not in ['PENDING', 'RECEIVED', 'STARTED']:
            return {
                "task_id": task_id,
                "status": "COMPLETED",
                "message": "Task already completed or failed"
            }
        
        # Revoke the task
        task_result.revoke(terminate=True, signal='SIGUSR1')
        
        # Update task tracking
        _update_task_status(task_id, 'CANCELLED')
        
        logger.info(f"Task {task_id} cancelled")
        
        return {
            "task_id": task_id,
            "status": "CANCELLED",
            "message": "Task cancellation requested"
        }
        
    except Exception as e:
        logger.error(f"Error cancelling task: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to cancel task: {str(e)}")


@router.get("/history")
async def get_collection_history(
    target: Optional[str] = Query(None, description="Filter by target"),
    status: Optional[str] = Query(None, description="Filter by status (queued, processing, completed, failed, cancelled)"),
    collection_type: Optional[str] = Query(None, description="Filter by collection type"),
    date_from: Optional[datetime] = Query(None, description="Filter by date from"),
    date_to: Optional[datetime] = Query(None, description="Filter by date to"),
    limit: int = Query(100, ge=1, le=1000, description="Number of results to return (1-1000)"),
    offset: int = Query(0, ge=0, description="Number of results to skip")
):
    """
    Get collection history with filtering options
    
    Returns paginated list of collection tasks with metadata
    """
    try:
        # In production, this would query a database
        # For now, return from in-memory tracker and Celery result backend
        
        tasks = []
        
        # Get tasks from tracker
        for task_id, task_info in _task_tracker.items():
            # Apply filters
            if target and target.lower() not in task_info.get('target', '').lower():
                continue
            if status and task_info.get('status', '').lower() != status.lower():
                continue
            if collection_type and collection_type.lower() not in [ct.lower() for ct in task_info.get('types', [])]:
                continue
            if date_from and datetime.fromisoformat(task_info.get('started_at', '')) < date_from:
                continue
            if date_to and datetime.fromisoformat(task_info.get('started_at', '')) > date_to:
                continue
            
            tasks.append({
                "task_id": task_id,
                "target": task_info.get('target'),
                "status": task_info.get('status'),
                "collection_types": task_info.get('types', []),
                "priority": task_info.get('priority'),
                "started_at": task_info.get('started_at'),
                "completed_at": task_info.get('completed_at'),
                "entities_found": task_info.get('entities_found', 0),
                "runtime_seconds": task_info.get('runtime_seconds')
            })
        
        # Apply pagination
        total = len(tasks)
        tasks = tasks[offset:offset + limit]
        
        return {
            "total": total,
            "offset": offset,
            "limit": limit,
            "tasks": tasks
        }
        
    except Exception as e:
        logger.error(f"Error retrieving collection history: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve history: {str(e)}")


@router.get("/sources")
async def get_available_data_sources():
    """
    List available data sources and their capabilities
    
    Returns information about what each collector can provide,
    rate limits, and any requirements (API keys, etc.)
    """
    sources = [
        {
            "name": "Web Collector",
            "collector_type": "web",
            "description": "Website scraping, subdomain enumeration, technology detection",
            "entity_types": ["DOMAIN", "SUBDOMAIN", "EMAIL", "SSL_CERTIFICATE", "WEB_TECHNOLOGY"],
            "rate_limit": "1 request per 2 seconds per domain",
            "requires_auth": False,
            "cost_tier": "free",
            "timeout": 180,
            "max_entities": 50
        },
        {
            "name": "Social Media Collector", 
            "collector_type": "social",
            "description": "Social media profile extraction and analysis (Twitter/X, GitHub)",
            "entity_types": ["SOCIAL_PROFILE", "USERNAME", "EMAIL", "ORG"],
            "rate_limit": "API-dependent (Twitter: 900 req/15min, GitHub: 60 req/hour)",
            "requires_auth": True,
            "cost_tier": "free_tier",
            "timeout": 150,
            "max_entities": 25,
            "notes": "Requires API keys: TWITTER_API_KEY, TWITTER_API_SECRET, GITHUB_TOKEN"
        },
        {
            "name": "Domain Intelligence Collector",
            "collector_type": "domain", 
            "description": "WHOIS lookups, DNS enumeration, domain reputation analysis",
            "entity_types": ["DOMAIN", "NAMESERVER", "MAIL_SERVER", "DNS_RECORD", "ORG"],
            "rate_limit": "1 request per 1.5 seconds per domain",
            "requires_auth": False,
            "cost_tier": "free",
            "timeout": 120,
            "max_entities": 40
        },
        {
            "name": "IP Intelligence Collector",
            "collector_type": "ip",
            "description": "IP geolocation, port scanning, threat intelligence",
            "entity_types": ["IP_ADDRESS", "HOSTNAME", "NETWORK_SERVICE", "LOCATION"],
            "rate_limit": "1 request per second per IP",
            "requires_auth": False,
            "cost_tier": "free_tier",
            "timeout": 200,
            "max_entities": 30,
            "notes": "Nmap requires root/admin for full functionality"
        },
        {
            "name": "Email Intelligence Collector",
            "collector_type": "email",
            "description": "Email verification, breach checking, provider analysis",
            "entity_types": ["EMAIL", "DOMAIN", "USERNAME", "DATA_BREACH"],
            "rate_limit": "3 requests per second per domain",
            "requires_auth": False,
            "cost_tier": "free_tier",
            "timeout": 100,
            "max_entities": 20,
            "notes": "HaveIBeenPwned free tier allows 1 request per 1500ms"
        },
        {
            "name": "Media Analysis Collector",
            "collector_type": "media",
            "description": "Image/audio analysis with EXIF extraction, OCR, face detection",
            "entity_types": ["FACE", "OBJECT", "TEXT", "GPS_COORDINATES", "DEVICE"],
            "rate_limit": "0.5 requests per second",
            "requires_auth": False,
            "cost_tier": "free",
            "timeout": 300,
            "max_entities": 15,
            "notes": "ML models loaded on first use, may take extra time"
        },
        {
            "name": "Dark Web Collector",
            "collector_type": "darkweb",
            "description": "Tor-based dark web scraping, paste monitoring, leak detection",
            "entity_types": ["ONION_SITE", "DARK_WEB_MENTION", "CRYPTOCURRENCY_ADDRESS", "PGP_KEY"],
            "rate_limit": "0.3 requests per second (Tor network limited)",
            "requires_auth": False,
            "cost_tier": "free",
            "timeout": 240,
            "max_entities": 10,
            "notes": "Requires Tor to be running. Much slower than clearnet collectors."
        },
        {
            "name": "Geolocation Collector",
            "collector_type": "geo",
            "description": "Forward/reverse geocoding, location relationships, POI discovery",
            "entity_types": ["LOCATION", "COUNTRY", "STATE", "CITY"],
            "rate_limit": "1 request per second",
            "requires_auth": False,
            "cost_tier": "free",
            "timeout": 90,
            "max_entities": 25
        }
    ]
    
    return {"sources": sources, "total": len(sources)}


# Helper Functions
def _determine_collectors(request: StartCollectionRequest) -> list:
    """Determine which collectors to use based on request"""
    # If FULL is specified, use all collectors except optional ones
    if CollectionType.FULL in request.collection_types:
        collectors = [
            CollectionType.WEB,
            CollectionType.DOMAIN,
            CollectionType.IP,
            CollectionType.EMAIL,
            CollectionType.GEO
        ]
        
        # Add optional collectors if requested
        if request.include_dark_web:
            collectors.append(CollectionType.DARKWEB)
        if request.include_media:
            collectors.append(CollectionType.MEDIA)
        
        # Try to determine social from target
        if request.target.startswith('@') or (not '.' in request.target and len(request.target) < 30):
            collectors.append(CollectionType.SOCIAL)
        
        return list(set(collectors))  # Remove duplicates
    
    # Otherwise, use exactly what was requested
    collectors = request.collection_types.copy()
    
    # Add optional collectors if requested in flags
    if request.include_dark_web and CollectionType.DARKWEB not in collectors:
        collectors.append(CollectionType.DARKWEB)
    
    if request.include_media and CollectionType.MEDIA not in collectors:
        collectors.append(CollectionType.MEDIA)
    
    return collectors


def _track_task(task_id: str, target: str, types: List[str], priority: str):
    """Track task metadata in memory"""
    _task_tracker[task_id] = {
        'target': target,
        'types': types,
        'priority': priority,
        'status': 'QUEUED',
        'started_at': datetime.utcnow().isoformat(),
        'progress': 0,
        'entities_found': 0
    }


def _get_tracked_task(task_id: str) -> Optional[Dict[str, Any]]:
    """Get tracked task metadata"""
    return _task_tracker.get(task_id)


def _update_task_status(task_id: str, status: str, **kwargs):
    """Update tracked task status"""
    if task_id in _task_tracker:
        _task_tracker[task_id]['status'] = status
        for key, value in kwargs.items():
            _task_tracker[task_id][key] = value


def _estimate_collection_time(collectors: List[str]) -> int:
    """Estimate collection time in seconds based on collector types"""
    estimated_seconds = 30  # Base overhead
    
    collector_times = {
        'web': 60,
        'social': 80,
        'domain': 45,
        'ip': 90,
        'email': 30,
        'media': 150,
        'darkweb': 180,  # Tor is slower
        'geo': 40
    }
    
    for collector in collectors:
        collector_str = collector.value if hasattr(collector, 'value') else str(collector)
        estimated_seconds += collector_times.get(collector_str, 30)
    
    return estimated_seconds


async def _normalize_results(entities: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Normalize and deduplicate collection results"""
    try:
        # Deduplicate entities
        deduped, duplicates = normalization_service.deduplicate_entities(entities)
        
        # Merge metadata
        merged = normalization_service.merge_entity_data(deduped)
        
        # Validate
        valid, invalid = normalization_service.validate_entity_data(merged)
        
        # Enrich metadata
        enriched = [normalization_service.enrich_entity_metadata(entity) for entity in valid]
        
        # Enrich timestamps
        final_entities = normalization_service.enrich_timestamps(enriched)
        
        # Extract sources
        sources = list(set(e.get('source', 'unknown') for e in final_entities))
        
        return {
            'entities': final_entities,
            'sources': sources,
            'normalized_count': len(entities),
            'duplicates_removed': len(duplicates),
            'invalid_entities': len(invalid)
        }
        
    except Exception as e:
        logger.error(f"Normalization failed: {e}")
        return {'entities': entities, 'sources': [], 'error': str(e)}