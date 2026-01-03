"""
Collection API routes for ReconVault backend.

This module provides REST API endpoints for managing OSINT collection tasks.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional
from uuid import UUID
import logging
from datetime import datetime

from app.api.dependencies import get_database
from app.schemas.osint import (
    CollectionTaskCreate,
    CollectionTaskResponse,
    CollectionTaskListResponse,
    CollectionStats
)
from app.models.collection_task import CollectionTask

# Configure logging
logger = logging.getLogger("reconvault.api.collection")

# Create router
router = APIRouter(prefix="/collection", tags=["collection"])


@router.post("/start", response_model=CollectionTaskResponse, status_code=status.HTTP_201_CREATED)
def start_collection_task(
    task_data: CollectionTaskCreate,
    db: Session = Depends(get_database)
):
    """
    Start a new OSINT collection task.
    
    Args:
        task_data: Collection task creation data
        db: Database session
        
    Returns:
        CollectionTaskResponse: Created task
    """
    try:
        task = CollectionTask(
            target=task_data.target,
            collection_type=task_data.collection_type,
            status="pending"
        )
        
        db.add(task)
        db.commit()
        db.refresh(task)
        
        logger.info(f"Created collection task: {task.id}")
        
        return CollectionTaskResponse.from_orm(task)
        
    except Exception as e:
        logger.error(f"Failed to create collection task: {e}")
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.get("/tasks", response_model=CollectionTaskListResponse)
def get_collection_tasks(
    limit: int = Query(50, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    status: Optional[str] = Query(None),
    collection_type: Optional[str] = Query(None),
    db: Session = Depends(get_database)
):
    """
    Get list of collection tasks with optional filters.
    
    Args:
        limit: Maximum number of results
        offset: Number of results to skip
        status: Filter by status
        collection_type: Filter by collection type
        db: Database session
        
    Returns:
        CollectionTaskListResponse: List of tasks with pagination
    """
    try:
        query = db.query(CollectionTask)
        
        if status:
            query = query.filter(CollectionTask.status == status)
        
        if collection_type:
            query = query.filter(CollectionTask.collection_type == collection_type)
        
        total = query.count()
        tasks = query.offset(offset).limit(limit).all()
        
        pages = (total + limit - 1) // limit
        
        return CollectionTaskListResponse(
            tasks=[CollectionTaskResponse.from_orm(t) for t in tasks],
            total=total,
            page=(offset // limit) + 1,
            per_page=limit,
            pages=pages
        )
        
    except Exception as e:
        logger.error(f"Failed to get collection tasks: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.get("/tasks/{task_id}", response_model=CollectionTaskResponse)
def get_collection_task(
    task_id: UUID,
    db: Session = Depends(get_database)
):
    """
    Get a specific collection task by ID.
    
    Args:
        task_id: Task UUID
        db: Database session
        
    Returns:
        CollectionTaskResponse: Task details
    """
    try:
        task = db.query(CollectionTask).filter(CollectionTask.id == task_id).first()
        
        if not task:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
        
        return CollectionTaskResponse.from_orm(task)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get collection task: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.get("/results/{task_id}", response_model=dict)
def get_collection_results(
    task_id: UUID,
    db: Session = Depends(get_database)
):
    """
    Get results for a collection task.
    
    Args:
        task_id: Task UUID
        db: Database session
        
    Returns:
        dict: Task results
    """
    try:
        task = db.query(CollectionTask).filter(CollectionTask.id == task_id).first()
        
        if not task:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
        
        return {
            "task_id": str(task.id),
            "status": task.status,
            "result_count": task.result_count,
            "results": []  # Placeholder - would load from collection_results table
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get collection results: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")
