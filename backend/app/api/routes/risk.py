"""
Risk Assessment API routes for ReconVault backend.

This module provides REST API endpoints for risk assessment management.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional
from uuid import UUID
import logging
from datetime import datetime

from app.api.dependencies import get_database
from app.schemas.risk import (
    RiskAssessmentResponse,
    RiskAssessmentListResponse,
    RiskSummary,
    RiskAssessRequest,
    RiskAssessResponse
)
from app.models.risk_assessment import RiskAssessment
from app.models.entity import Entity

# Configure logging
logger = logging.getLogger("reconvault.api.risk")

# Create router
router = APIRouter(prefix="/risk", tags=["risk"])


@router.get("/assessments", response_model=RiskAssessmentListResponse)
def get_risk_assessments(
    limit: int = Query(50, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    entity_id: Optional[UUID] = Query(None),
    level: Optional[str] = Query(None),
    db: Session = Depends(get_database)
):
    """
    Get list of risk assessments with optional filters.
    
    Args:
        limit: Maximum number of results
        offset: Number of results to skip
        entity_id: Filter by entity ID
        level: Filter by risk level
        db: Database session
        
    Returns:
        RiskAssessmentListResponse: List of assessments with pagination
    """
    try:
        query = db.query(RiskAssessment)
        
        if entity_id:
            query = query.filter(RiskAssessment.entity_id == entity_id)
        
        if level:
            query = query.filter(RiskAssessment.level == level)
        
        total = query.count()
        assessments = query.offset(offset).limit(limit).all()
        
        pages = (total + limit - 1) // limit
        
        return RiskAssessmentListResponse(
            assessments=[RiskAssessmentResponse.from_orm(a) for a in assessments],
            total=total,
            page=(offset // limit) + 1,
            per_page=limit,
            pages=pages
        )
        
    except Exception as e:
        logger.error(f"Failed to get risk assessments: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.get("/assessments/{entity_id}", response_model=RiskAssessmentResponse)
def get_entity_risk_assessment(
    entity_id: UUID,
    db: Session = Depends(get_database)
):
    """
    Get risk assessment for a specific entity.
    
    Args:
        entity_id: Entity UUID
        db: Database session
        
    Returns:
        RiskAssessmentResponse: Latest risk assessment for entity
    """
    try:
        assessment = db.query(RiskAssessment).filter(
            RiskAssessment.entity_id == entity_id
        ).order_by(RiskAssessment.assessed_at.desc()).first()
        
        if not assessment:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Risk assessment not found")
        
        return RiskAssessmentResponse.from_orm(assessment)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get entity risk assessment: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.post("/assess", response_model=RiskAssessResponse)
def trigger_risk_assessment(
    request: RiskAssessRequest,
    db: Session = Depends(get_database)
):
    """
    Trigger risk assessment for entities.
    
    Args:
        request: Assessment request data
        db: Database session
        
    Returns:
        RiskAssessResponse: Assessment job details
    """
    try:
        # Count entities to assess
        if request.assess_all:
            entity_count = db.query(Entity).count()
        elif request.entity_ids:
            entity_count = len(request.entity_ids)
        else:
            entity_count = 0
        
        # Create placeholder job
        job_id = f"risk_assess_{datetime.utcnow().timestamp()}"
        
        logger.info(f"Triggered risk assessment job: {job_id} for {entity_count} entities")
        
        return RiskAssessResponse(
            job_id=job_id,
            status="queued",
            entities_queued=entity_count,
            estimated_completion=None
        )
        
    except Exception as e:
        logger.error(f"Failed to trigger risk assessment: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.get("/summary", response_model=RiskSummary)
def get_risk_summary(
    db: Session = Depends(get_database)
):
    """
    Get overall risk summary.
    
    Args:
        db: Database session
        
    Returns:
        RiskSummary: Overall risk statistics
    """
    try:
        total_entities = db.query(Entity).count()
        
        # Count assessments by level
        critical_count = db.query(RiskAssessment).filter(RiskAssessment.level == "critical").count()
        high_count = db.query(RiskAssessment).filter(RiskAssessment.level == "high").count()
        medium_count = db.query(RiskAssessment).filter(RiskAssessment.level == "medium").count()
        low_count = db.query(RiskAssessment).filter(RiskAssessment.level == "low").count()
        info_count = db.query(RiskAssessment).filter(RiskAssessment.level == "info").count()
        
        # Calculate average risk score
        from sqlalchemy import func
        avg_score = db.query(func.avg(RiskAssessment.score)).scalar() or 0.0
        
        return RiskSummary(
            total_entities=total_entities,
            critical_count=critical_count,
            high_count=high_count,
            medium_count=medium_count,
            low_count=low_count,
            info_count=info_count,
            average_risk_score=float(avg_score),
            highest_risk_entities=[],
            risk_trend=None
        )
        
    except Exception as e:
        logger.error(f"Failed to get risk summary: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")
