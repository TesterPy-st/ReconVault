"""
Target API routes for ReconVault.

This module provides REST API endpoints for target management
including CRUD operations, search, and bulk operations.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
import logging
from datetime import datetime, timezone

from app.database import get_db
from app.services.target_service import get_target_service
from app.schemas.target import (
    TargetCreate, TargetUpdate, TargetResponse, TargetListResponse,
    TargetSearchRequest, TargetSearchResponse, TargetStats,
    TargetBulkRequest, TargetBulkResponse, TargetDeleteResponse
)
from app.models.audit import AuditLog, AuditAction

# Configure logging
logger = logging.getLogger("reconvault.api.targets")

# Create router
router = APIRouter()


@router.post("/", response_model=TargetResponse, status_code=status.HTTP_201_CREATED)
async def create_target(
    target_data: TargetCreate,
    db: Session = Depends(get_db),
    background_tasks: BackgroundTasks = None
):
    """
    Create a new target.
    
    Args:
        target_data: Target creation data
        db: Database session
        background_tasks: Background tasks
    
    Returns:
        TargetResponse: Created target
    
    Raises:
        HTTPException: If creation fails
    """
    try:
        target_service = get_target_service(db)
        target = target_service.create_target(target_data)
        
        logger.info(f"Created target: {target.id}")
        return target
        
    except Exception as e:
        logger.error(f"Failed to create target: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create target: {str(e)}"
        )


@router.get("/{target_id}", response_model=TargetResponse)
async def get_target(target_id: int, db: Session = Depends(get_db)):
    """
    Get target by ID.
    
    Args:
        target_id: Target database ID
        db: Database session
    
    Returns:
        TargetResponse: Target data
    
    Raises:
        HTTPException: If target not found
    """
    try:
        target_service = get_target_service(db)
        target = target_service.get_target(target_id)
        
        if not target:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Target {target_id} not found"
            )
        
        return target
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get target {target_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get target: {str(e)}"
        )


@router.get("/", response_model=TargetListResponse)
async def get_targets(
    skip: int = Query(0, ge=0, description="Number of targets to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of targets to return"),
    active_only: bool = Query(True, description="Only return active targets"),
    db: Session = Depends(get_db)
):
    """
    Get list of targets with pagination.
    
    Args:
        skip: Number of targets to skip
        limit: Maximum number of targets to return
        active_only: Whether to return only active targets
        db: Database session
    
    Returns:
        TargetListResponse: Paginated list of targets
    """
    try:
        target_service = get_target_service(db)
        targets = target_service.get_targets(skip=skip, limit=limit, active_only=active_only)
        
        return targets
        
    except Exception as e:
        logger.error(f"Failed to get targets: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get targets: {str(e)}"
        )


@router.put("/{target_id}", response_model=TargetResponse)
async def update_target(
    target_id: int,
    target_data: TargetUpdate,
    db: Session = Depends(get_db)
):
    """
    Update an existing target.
    
    Args:
        target_id: Target database ID
        target_data: Target update data
        db: Database session
    
    Returns:
        TargetResponse: Updated target
    
    Raises:
        HTTPException: If target not found or update fails
    """
    try:
        target_service = get_target_service(db)
        target = target_service.update_target(target_id, target_data)
        
        if not target:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Target {target_id} not found"
            )
        
        logger.info(f"Updated target: {target_id}")
        return target
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update target {target_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update target: {str(e)}"
        )


@router.delete("/{target_id}", response_model=TargetDeleteResponse)
async def delete_target(target_id: int, db: Session = Depends(get_db)):
    """
    Delete a target (soft delete).
    
    Args:
        target_id: Target database ID
        db: Database session
    
    Returns:
        TargetDeleteResponse: Deletion result
    
    Raises:
        HTTPException: If target not found
    """
    try:
        target_service = get_target_service(db)
        success = target_service.delete_target(target_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Target {target_id} not found"
            )
        
        return TargetDeleteResponse(
            success=True,
            deleted_id=target_id,
            message=f"Target {target_id} deleted successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete target {target_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete target: {str(e)}"
        )


@router.post("/search", response_model=TargetSearchResponse)
async def search_targets(
    search_request: TargetSearchRequest,
    db: Session = Depends(get_db)
):
    """
    Search targets based on criteria.
    
    Args:
        search_request: Search criteria
        db: Database session
    
    Returns:
        TargetSearchResponse: Search results
    """
    try:
        target_service = get_target_service(db)
        results = target_service.search_targets(search_request)
        
        return results
        
    except Exception as e:
        logger.error(f"Failed to search targets: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to search targets: {str(e)}"
        )


@router.get("/statistics/overview", response_model=TargetStats)
async def get_target_statistics(db: Session = Depends(get_db)):
    """
    Get target statistics.
    
    Args:
        db: Database session
    
    Returns:
        TargetStats: Target statistics
    """
    try:
        target_service = get_target_service(db)
        stats = target_service.get_target_statistics()
        
        return stats
        
    except Exception as e:
        logger.error(f"Failed to get target statistics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get target statistics: {str(e)}"
        )


@router.post("/bulk", response_model=TargetBulkResponse)
async def bulk_create_targets(
    bulk_request: TargetBulkRequest,
    db: Session = Depends(get_db),
    background_tasks: BackgroundTasks = None
):
    """
    Create multiple targets in bulk.
    
    Args:
        bulk_request: Bulk target creation request
        db: Database session
        background_tasks: Background tasks
    
    Returns:
        TargetBulkResponse: Bulk operation results
    """
    try:
        target_service = get_target_service(db)
        results = target_service.bulk_create_targets(bulk_request)
        
        logger.info(f"Bulk created {len(results.created)} targets")
        return results
        
    except Exception as e:
        logger.error(f"Failed to bulk create targets: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to bulk create targets: {str(e)}"
        )


@router.get("/{target_id}/entities", response_model=List[dict])
async def get_target_entities(
    target_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """
    Get entities associated with a target.
    
    Args:
        target_id: Target database ID
        skip: Number of entities to skip
        limit: Maximum number of entities to return
        db: Database session
    
    Returns:
        List[dict]: Associated entities
    
    Raises:
        HTTPException: If target not found
    """
    try:
        # First verify target exists
        target_service = get_target_service(db)
        target = target_service.get_target(target_id)
        
        if not target:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Target {target_id} not found"
            )
        
        # Get entities for this target
        from app.services.entity_service import get_entity_service
        entity_service = get_entity_service(db)
        entities_response = entity_service.get_entities(
            skip=skip, 
            limit=limit, 
            active_only=True, 
            target_id=target_id
        )
        
        return entities_response.entities
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get entities for target {target_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get target entities: {str(e)}"
        )


@router.post("/{target_id}/analyze", response_model=dict)
async def analyze_target(
    target_id: int,
    db: Session = Depends(get_db),
    background_tasks: BackgroundTasks = None
):
    """
    Trigger analysis for a target.
    
    Args:
        target_id: Target database ID
        db: Database session
        background_tasks: Background tasks
    
    Returns:
        dict: Analysis result
    
    Raises:
        HTTPException: If target not found
    """
    try:
        # Verify target exists
        target_service = get_target_service(db)
        target = target_service.get_target(target_id)
        
        if not target:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Target {target_id} not found"
            )
        
        # In a real implementation, this would trigger analysis workflows
        # For now, return a basic analysis result
        analysis_result = {
            "target_id": target_id,
            "analysis_status": "initiated",
            "analysis_type": "comprehensive",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "estimated_completion": "2024-01-01T12:00:00Z"  # Would be calculated
        }
        
        # Log audit event
        try:
            audit_log = AuditLog.create_log(
                action=AuditAction.TARGET_UPDATE,
                description=f"Analysis initiated for target {target_id}",
                target_id=target_id,
                severity=AuditSeverity.INFO
            )
            db.add(audit_log)
            db.commit()
        except Exception as audit_error:
            logger.warning(f"Failed to log audit event: {audit_error}")
        
        return analysis_result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to analyze target {target_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to analyze target: {str(e)}"
        )


@router.get("/{target_id}/risk-assessment", response_model=dict)
async def get_target_risk_assessment(target_id: int, db: Session = Depends(get_db)):
    """
    Get risk assessment for a target.
    
    Args:
        target_id: Target database ID
        db: Database session
    
    Returns:
        dict: Risk assessment data
    
    Raises:
        HTTPException: If target not found
    """
    try:
        # Get target
        target_service = get_target_service(db)
        target = target_service.get_target(target_id)
        
        if not target:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Target {target_id} not found"
            )
        
        # Get associated entities for additional risk context
        from app.services.entity_service import get_entity_service
        entity_service = get_entity_service(db)
        entities_response = entity_service.get_entities(
            limit=1000, 
            active_only=True, 
            target_id=target_id
        )
        
        # Calculate risk metrics
        risk_assessment = {
            "target_id": target_id,
            "overall_risk_score": target.risk_score,
            "risk_level": target.risk_level,
            "risk_factors": [],
            "associated_entities": len(entities_response.entities),
            "high_risk_entities": len([
                e for e in entities_response.entities 
                if e.risk_score >= 0.7
            ]),
            "assessment_timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        # Add risk factors based on target properties
        risk_factors = []
        
        if target.risk_score >= 0.8:
            risk_factors.append("High base risk score")
        
        if target.type in ["ip_address", "domain"]:
            risk_factors.append("Network infrastructure target")
        
        if target.status == "investigating":
            risk_factors.append("Active investigation")
        
        risk_assessment["risk_factors"] = risk_factors
        
        return risk_assessment
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get risk assessment for target {target_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get risk assessment: {str(e)}"
        )