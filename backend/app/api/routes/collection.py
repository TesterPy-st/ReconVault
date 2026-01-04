"""
Collection API Routes

Endpoints for OSINT data collection and task management.
"""

import asyncio
from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, BackgroundTasks, HTTPException, Query
from loguru import logger
from pydantic import BaseModel, Field

from app.services.collection_pipeline_service import (
    CollectionPipelineService, TaskStatus)

router = APIRouter(prefix="/collection", tags=["collection"])

# Global pipeline service instance
pipeline_service = CollectionPipelineService()


# Pydantic models for request/response
class CollectionRequest(BaseModel):
    """Request model for starting collection"""

    target: str = Field(..., description="Target to collect (domain, email, IP, etc.)")
    collection_types: Optional[List[str]] = Field(
        None,
        description="Specific collection types (web, social, domain, ip, email, geo). If not provided, auto-detected.",
    )
    include_dark_web: bool = Field(False, description="Include dark web collection")
    include_media: bool = Field(False, description="Include media collection")


class CollectionResponse(BaseModel):
    """Response model for starting collection"""

    task_id: str
    target: str
    status: str
    estimated_time: int = Field(None, description="Estimated time in seconds")


class TaskStatusResponse(BaseModel):
    """Response model for task status"""

    task_id: str
    target: str
    status: str
    progress_percent: int
    collectors_completed: List[str]
    collectors_failed: List[str]
    entities_collected: int = 0
    relationships_collected: int = 0
    start_time: str
    end_time: Optional[str] = None
    errors: List[str] = []
    include_dark_web: bool = False
    include_media: bool = False


class CollectionResultsResponse(BaseModel):
    """Response model for collection results"""

    task_id: str
    entities_created: int
    relationships_created: int
    data_sources: List[str]


class CollectionHistoryResponse(BaseModel):
    """Response model for collection history"""

    tasks: List[Dict[str, Any]]
    total: int


class DataSourceResponse(BaseModel):
    """Response model for available data sources"""

    sources: Dict[str, Any]


@router.on_event("startup")
async def startup_event():
    """Initialize pipeline service on startup"""
    await pipeline_service.initialize()
    logger.info("Collection API routes initialized")


@router.post("/start", response_model=CollectionResponse, status_code=202)
async def start_collection(request: CollectionRequest) -> CollectionResponse:
    """
    Start comprehensive OSINT collection.

    Queues collection tasks for the target and returns task ID for tracking.
    """
    try:
        logger.info(f"Starting collection for target: {request.target}")

        # Start collection task
        task = await pipeline_service.start_collection_task(
            target=request.target,
            collection_types=request.collection_types,
            include_dark_web=request.include_dark_web,
            include_media=request.include_media,
        )

        return CollectionResponse(
            task_id=task["task_id"],
            target=request.target,
            status=task["status"],
            estimated_time=60,  # Estimate 60 seconds
        )

    except Exception as e:
        logger.exception(f"Failed to start collection: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tasks/{task_id}", response_model=TaskStatusResponse)
async def get_task_status(task_id: str) -> TaskStatusResponse:
    """
    Get collection task status with progress.

    Returns detailed status including progress percentage and completed collectors.
    """
    try:
        task = pipeline_service.get_task_status(task_id)

        if not task:
            raise HTTPException(status_code=404, detail=f"Task {task_id} not found")

        return TaskStatusResponse(
            task_id=task["task_id"],
            target=task["target"],
            status=task["status"],
            progress_percent=task.get("progress", 0),
            collectors_completed=task.get("collectors_completed", []),
            collectors_failed=task.get("collectors_failed", []),
            entities_collected=task.get("entities_collected", 0),
            relationships_collected=task.get("relationships_collected", 0),
            start_time=task["start_time"],
            end_time=task.get("end_time"),
            errors=task.get("errors", []),
            include_dark_web=task.get("include_dark_web", False),
            include_media=task.get("include_media", False),
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Failed to get task status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/results/{task_id}", response_model=CollectionResultsResponse)
async def get_collection_results(task_id: str) -> CollectionResultsResponse:
    """
    Get collected data for a task.

    Returns summary of entities and relationships created.
    """
    try:
        task = pipeline_service.get_task_status(task_id)

        if not task:
            raise HTTPException(status_code=404, detail=f"Task {task_id} not found")

        if task["status"] != TaskStatus.COMPLETED.value:
            raise HTTPException(
                status_code=400,
                detail=f"Task {task_id} has not completed. Status: {task['status']}",
            )

        return CollectionResultsResponse(
            task_id=task["task_id"],
            entities_created=task.get("entities_collected", 0),
            relationships_created=task.get("relationships_collected", 0),
            data_sources=task.get("data_sources", []),
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Failed to get collection results: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/cancel/{task_id}", status_code=200)
async def cancel_task(task_id: str) -> Dict[str, Any]:
    """
    Cancel a running collection task.

    Returns success status.
    """
    try:
        success = await pipeline_service.cancel_task(task_id)

        if not success:
            raise HTTPException(
                status_code=400,
                detail=f"Task {task_id} could not be cancelled or is not running",
            )

        return {
            "task_id": task_id,
            "status": "CANCELLED",
            "message": "Task cancelled successfully",
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Failed to cancel task: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history", response_model=CollectionHistoryResponse)
async def get_collection_history(
    target: Optional[str] = Query(None, description="Filter by target"),
    status: Optional[str] = Query(None, description="Filter by status"),
    limit: int = Query(
        50, ge=1, le=200, description="Maximum number of tasks to return"
    ),
) -> CollectionHistoryResponse:
    """
    Get collection history with optional filters.

    Returns list of collection tasks with metadata.
    """
    try:
        all_tasks = pipeline_service.get_all_tasks()

        # Apply filters
        filtered_tasks = all_tasks

        if target:
            filtered_tasks = [t for t in filtered_tasks if t.get("target") == target]

        if status:
            filtered_tasks = [t for t in filtered_tasks if t.get("status") == status]

        # Sort by start time (newest first)
        filtered_tasks.sort(key=lambda x: x.get("start_time", ""), reverse=True)

        # Apply limit
        filtered_tasks = filtered_tasks[:limit]

        return CollectionHistoryResponse(
            tasks=filtered_tasks, total=len(filtered_tasks)
        )

    except Exception as e:
        logger.exception(f"Failed to get collection history: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sources", response_model=DataSourceResponse)
async def get_data_sources() -> DataSourceResponse:
    """
    List available data sources and collectors.

    Returns information about all available OSINT collectors.
    """
    try:
        sources = {
            "web": {
                "name": "Web Collector",
                "description": "Website scraping, subdomain discovery, SSL certificates",
                "capabilities": [
                    "scrape_website",
                    "extract_subdomains",
                    "scan_ssl_certificate",
                    "crawl_site_structure",
                    "extract_emails",
                    "detect_technologies",
                    "check_dns_records",
                ],
            },
            "social": {
                "name": "Social Collector",
                "description": "Social media profile analysis and username search",
                "capabilities": [
                    "search_username",
                    "extract_twitter_profile",
                    "extract_github_profile",
                    "search_email",
                    "extract_social_connections",
                    "analyze_posting_patterns",
                ],
            },
            "domain": {
                "name": "Domain Collector",
                "description": "Domain WHOIS, DNS enumeration, and reputation",
                "capabilities": [
                    "whois_lookup",
                    "dns_enumeration",
                    "get_historical_data",
                    "check_reputation",
                    "get_nameservers",
                    "detect_mail_servers",
                ],
            },
            "ip": {
                "name": "IP Collector",
                "description": "IP geolocation, port scanning, and reputation",
                "capabilities": [
                    "geolocate_ip",
                    "scan_ports",
                    "reverse_dns",
                    "check_ip_reputation",
                    "get_whois_ip",
                    "detect_vpn_proxy",
                ],
            },
            "email": {
                "name": "Email Collector",
                "description": "Email verification and breach checking",
                "capabilities": [
                    "verify_email",
                    "check_breaches",
                    "extract_domain",
                    "find_associated_accounts",
                    "get_email_provider_info",
                    "check_common_variants",
                ],
            },
            "media": {
                "name": "Media Collector",
                "description": "Image and audio metadata extraction",
                "capabilities": [
                    "extract_image_metadata",
                    "extract_text_from_image",
                    "detect_faces",
                    "analyze_image_objects",
                    "extract_audio_metadata",
                    "extract_audio_transcript",
                ],
            },
            "darkweb": {
                "name": "Dark Web Collector",
                "description": "Tor-based dark web searching",
                "capabilities": [
                    "initialize_tor_session",
                    "search_darkweb",
                    "extract_onion_data",
                    "check_dark_web_mentions",
                ],
                "requires_tor": True,
            },
            "geo": {
                "name": "Geolocation Collector",
                "description": "Geocoding and location-based intelligence",
                "capabilities": [
                    "reverse_geocode",
                    "forward_geocode",
                    "get_nearby_businesses",
                    "extract_location_relationships",
                ],
            },
        }

        return DataSourceResponse(sources=sources)

    except Exception as e:
        logger.exception(f"Failed to get data sources: {e}")
        raise HTTPException(status_code=500, detail=str(e))
