"""
ReconVault Anomalies API Routes

API endpoints for anomaly detection and management.
"""

import json
import uuid
from datetime import datetime, timezone
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from loguru import logger
from pydantic import BaseModel, Field
from sqlalchemy import desc, func
from sqlalchemy.orm import Session

from app.ai_engine.anomaly_classifier import get_anomaly_classifier
from app.ai_engine.inference import get_inference_engine
from app.database import get_db
from app.models.entity import Entity
from app.models.intelligence import Anomaly
from app.models.relationship import Relationship

router = APIRouter()


# Pydantic schemas
class AnomalyDetectRequest(BaseModel):
    """Request schema for anomaly detection."""

    entity_id: int = Field(..., description="Entity ID to analyze")


class AnomalyBatchDetectRequest(BaseModel):
    """Request schema for batch anomaly detection."""

    entity_ids: List[int] = Field(..., description="List of entity IDs to analyze")
    limit: Optional[int] = Field(
        100, description="Maximum number of entities to process"
    )


class AnomalyResponse(BaseModel):
    """Response schema for anomaly."""

    id: str
    entity_id: Optional[int]
    relationship_id: Optional[int]
    anomaly_type: str
    anomaly_score: float
    confidence: float
    severity: str
    explanation: dict
    detection_method: Optional[str]
    indicators: List[str]
    description: Optional[str]
    recommendations: List[str]
    reviewed: bool
    review_notes: Optional[str]
    reviewed_by: Optional[str]
    reviewed_at: Optional[str]
    created_at: str
    updated_at: str
    is_active: bool


class AnomalyStatsResponse(BaseModel):
    """Response schema for anomaly statistics."""

    total_anomalies: int
    unreviewed_count: int
    by_severity: dict
    by_type: dict
    recent_anomalies: int
    avg_anomaly_score: float


@router.post("/detect-anomalies", response_model=dict, tags=["AI Anomaly Detection"])
async def detect_anomalies(
    request: AnomalyDetectRequest, db: Session = Depends(get_db)
):
    """
    Analyze a single entity for anomalies using ML models.

    **Process:**
    1. Extract features from entity
    2. Run through anomaly detection models
    3. Classify anomaly type and severity
    4. Generate recommendations
    5. Store anomaly record

    **Returns:**
    - Anomaly detection results with score, type, and recommendations
    """
    try:
        # Fetch entity
        entity = db.query(Entity).filter(Entity.id == request.entity_id).first()
        if not entity:
            raise HTTPException(
                status_code=404, detail=f"Entity {request.entity_id} not found"
            )

        # Get inference engine
        inference_engine = get_inference_engine(db)

        # Detect anomalies
        detection_result = inference_engine.detect_entity_anomaly(
            entity, use_cache=True
        )

        if detection_result["is_anomalous"]:
            # Classify anomaly
            classifier = get_anomaly_classifier()
            classification = classifier.classify_entity_anomaly(
                entity,
                detection_result["anomaly_score"],
                detection_result.get("explanation", {}).get("all_features"),
            )

            # Create anomaly record
            anomaly = Anomaly(
                id=str(uuid.uuid4()),
                entity_id=entity.id,
                anomaly_type=classification["primary_type"],
                anomaly_score=detection_result["anomaly_score"],
                confidence=detection_result["confidence"],
                severity=classification["severity"],
                explanation=json.dumps(detection_result.get("explanation", {})),
                detection_method=detection_result["detection_method"],
                indicators=",".join(classification["indicators"]),
                description=classification["description"],
                recommendations=json.dumps(classification["recommendations"]),
                reviewed=False,
                is_active=True,
            )

            db.add(anomaly)
            db.commit()
            db.refresh(anomaly)

            logger.info(
                f"Anomaly detected for entity {entity.id}: "
                f"{classification['primary_type']} ({classification['severity']})"
            )

            return {
                "success": True,
                "anomaly_detected": True,
                "anomaly": anomaly.to_dict(),
                "detection_result": detection_result,
                "classification": classification,
            }
        else:
            return {
                "success": True,
                "anomaly_detected": False,
                "detection_result": detection_result,
                "message": "No anomaly detected",
            }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Anomaly detection failed: {e}")
        raise HTTPException(
            status_code=500, detail=f"Anomaly detection failed: {str(e)}"
        )


@router.post("/detect-batch", response_model=dict, tags=["AI Anomaly Detection"])
async def detect_batch_anomalies(
    request: AnomalyBatchDetectRequest, db: Session = Depends(get_db)
):
    """
    Batch anomaly detection for multiple entities.

    **Performance:**
    - Processes up to 100 entities per request
    - Uses caching for improved performance
    - Target: < 500ms for 100 entities

    **Returns:**
    - List of detected anomalies
    - Processing statistics
    """
    try:
        # Fetch entities
        entity_ids = request.entity_ids[: request.limit]
        entities = db.query(Entity).filter(Entity.id.in_(entity_ids)).all()

        if not entities:
            raise HTTPException(status_code=404, detail="No entities found")

        # Get inference engine
        inference_engine = get_inference_engine(db)
        classifier = get_anomaly_classifier()

        # Batch detection
        detection_results = inference_engine.detect_batch(entities)

        # Process results
        anomalies_detected = []
        anomalies_created = []

        for i, result in enumerate(detection_results):
            if result["is_anomalous"]:
                entity = entities[i]

                # Classify
                classification = classifier.classify_entity_anomaly(
                    entity,
                    result["anomaly_score"],
                    result.get("explanation", {}).get("all_features"),
                )

                # Create anomaly record
                anomaly = Anomaly(
                    id=str(uuid.uuid4()),
                    entity_id=entity.id,
                    anomaly_type=classification["primary_type"],
                    anomaly_score=result["anomaly_score"],
                    confidence=result["confidence"],
                    severity=classification["severity"],
                    explanation=json.dumps(result.get("explanation", {})),
                    detection_method=result["detection_method"],
                    indicators=",".join(classification["indicators"]),
                    description=classification["description"],
                    recommendations=json.dumps(classification["recommendations"]),
                    reviewed=False,
                    is_active=True,
                )

                db.add(anomaly)
                anomalies_detected.append(result)
                anomalies_created.append(anomaly.id)

        db.commit()

        logger.info(
            f"Batch detection complete: {len(entities)} entities processed, "
            f"{len(anomalies_detected)} anomalies found"
        )

        return {
            "success": True,
            "entities_processed": len(entities),
            "anomalies_detected": len(anomalies_detected),
            "anomaly_ids": anomalies_created,
            "detection_results": anomalies_detected,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Batch anomaly detection failed: {e}")
        raise HTTPException(status_code=500, detail=f"Batch detection failed: {str(e)}")


@router.get("/anomalies", response_model=dict, tags=["AI Anomaly Detection"])
async def list_anomalies(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(50, ge=1, le=1000, description="Number of records to return"),
    severity: Optional[str] = Query(None, description="Filter by severity"),
    anomaly_type: Optional[str] = Query(None, description="Filter by anomaly type"),
    reviewed: Optional[bool] = Query(None, description="Filter by review status"),
    db: Session = Depends(get_db),
):
    """
    List all detected anomalies with pagination and filtering.

    **Filters:**
    - severity: low, medium, high, critical
    - anomaly_type: behavioral, relationship, infrastructure, data_quality, temporal, semantic
    - reviewed: true/false

    **Returns:**
    - Paginated list of anomalies
    - Total count
    """
    try:
        # Build query
        query = db.query(Anomaly).filter(Anomaly.is_active == True)

        if severity:
            query = query.filter(Anomaly.severity == severity)

        if anomaly_type:
            query = query.filter(Anomaly.anomaly_type == anomaly_type)

        if reviewed is not None:
            query = query.filter(Anomaly.reviewed == reviewed)

        # Get total count
        total = query.count()

        # Get paginated results
        anomalies = (
            query.order_by(desc(Anomaly.created_at)).offset(skip).limit(limit).all()
        )

        return {
            "success": True,
            "total": total,
            "skip": skip,
            "limit": limit,
            "anomalies": [a.to_dict() for a in anomalies],
        }

    except Exception as e:
        logger.error(f"Failed to list anomalies: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to list anomalies: {str(e)}"
        )


@router.get(
    "/anomalies/{entity_id}", response_model=dict, tags=["AI Anomaly Detection"]
)
async def get_entity_anomalies(entity_id: int, db: Session = Depends(get_db)):
    """
    Get all anomalies for a specific entity.

    **Returns:**
    - List of anomalies associated with the entity
    - Entity information
    """
    try:
        # Verify entity exists
        entity = db.query(Entity).filter(Entity.id == entity_id).first()
        if not entity:
            raise HTTPException(status_code=404, detail=f"Entity {entity_id} not found")

        # Get anomalies
        anomalies = (
            db.query(Anomaly)
            .filter(Anomaly.entity_id == entity_id, Anomaly.is_active == True)
            .order_by(desc(Anomaly.created_at))
            .all()
        )

        return {
            "success": True,
            "entity_id": entity_id,
            "entity": entity.to_dict(),
            "anomaly_count": len(anomalies),
            "anomalies": [a.to_dict() for a in anomalies],
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get entity anomalies: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to get entity anomalies: {str(e)}"
        )


@router.get("/anomaly/{anomaly_id}", response_model=dict, tags=["AI Anomaly Detection"])
async def get_anomaly_details(anomaly_id: str, db: Session = Depends(get_db)):
    """
    Get detailed information about a specific anomaly.

    **Includes:**
    - Full anomaly details
    - SHAP explanation
    - Associated entity/relationship
    - Recommendations

    **Returns:**
    - Complete anomaly information with context
    """
    try:
        anomaly = db.query(Anomaly).filter(Anomaly.id == anomaly_id).first()
        if not anomaly:
            raise HTTPException(
                status_code=404, detail=f"Anomaly {anomaly_id} not found"
            )

        # Get associated entity
        entity_data = None
        if anomaly.entity_id:
            entity = db.query(Entity).filter(Entity.id == anomaly.entity_id).first()
            if entity:
                entity_data = entity.to_dict()

        return {"success": True, "anomaly": anomaly.to_dict(), "entity": entity_data}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get anomaly details: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to get anomaly details: {str(e)}"
        )


@router.delete(
    "/anomalies/{anomaly_id}", response_model=dict, tags=["AI Anomaly Detection"]
)
async def mark_anomaly_reviewed(
    anomaly_id: str,
    analyst: str = Query(..., description="Analyst name"),
    notes: Optional[str] = Query(None, description="Review notes"),
    db: Session = Depends(get_db),
):
    """
    Mark an anomaly as reviewed by an analyst.

    **Parameters:**
    - analyst: Name of the analyst reviewing
    - notes: Optional review notes

    **Returns:**
    - Updated anomaly information
    """
    try:
        anomaly = db.query(Anomaly).filter(Anomaly.id == anomaly_id).first()
        if not anomaly:
            raise HTTPException(
                status_code=404, detail=f"Anomaly {anomaly_id} not found"
            )

        anomaly.mark_reviewed(analyst, notes)
        db.commit()
        db.refresh(anomaly)

        logger.info(f"Anomaly {anomaly_id} marked as reviewed by {analyst}")

        return {
            "success": True,
            "message": "Anomaly marked as reviewed",
            "anomaly": anomaly.to_dict(),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to mark anomaly as reviewed: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to mark anomaly as reviewed: {str(e)}"
        )


@router.get("/anomaly-stats", response_model=dict, tags=["AI Anomaly Detection"])
async def get_anomaly_statistics(
    days: int = Query(30, ge=1, le=365, description="Number of days to analyze"),
    db: Session = Depends(get_db),
):
    """
    Get anomaly detection statistics and trends.

    **Statistics include:**
    - Total anomalies detected
    - Count by severity level
    - Count by anomaly type
    - Review status
    - Trends over time

    **Returns:**
    - Comprehensive anomaly statistics
    """
    try:
        # Calculate date threshold
        from datetime import timedelta

        threshold_date = datetime.now(timezone.utc) - timedelta(days=days)

        # Total anomalies
        total = db.query(Anomaly).filter(Anomaly.is_active == True).count()

        # Unreviewed count
        unreviewed = (
            db.query(Anomaly)
            .filter(Anomaly.is_active == True, Anomaly.reviewed == False)
            .count()
        )

        # By severity
        by_severity = {}
        for severity in ["low", "medium", "high", "critical"]:
            count = (
                db.query(Anomaly)
                .filter(Anomaly.is_active == True, Anomaly.severity == severity)
                .count()
            )
            by_severity[severity] = count

        # By type
        by_type = {}
        for anom_type in [
            "behavioral",
            "relationship",
            "infrastructure",
            "data_quality",
            "temporal",
            "semantic",
        ]:
            count = (
                db.query(Anomaly)
                .filter(Anomaly.is_active == True, Anomaly.anomaly_type == anom_type)
                .count()
            )
            by_type[anom_type] = count

        # Recent anomalies
        recent = (
            db.query(Anomaly)
            .filter(Anomaly.is_active == True, Anomaly.created_at >= threshold_date)
            .count()
        )

        # Average anomaly score
        avg_score = (
            db.query(func.avg(Anomaly.anomaly_score))
            .filter(Anomaly.is_active == True)
            .scalar()
            or 0.0
        )

        return {
            "success": True,
            "period_days": days,
            "total_anomalies": total,
            "unreviewed_count": unreviewed,
            "by_severity": by_severity,
            "by_type": by_type,
            "recent_anomalies": recent,
            "avg_anomaly_score": float(avg_score),
        }

    except Exception as e:
        logger.error(f"Failed to get anomaly statistics: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to get anomaly statistics: {str(e)}"
        )


@router.post("/retrain", response_model=dict, tags=["AI Anomaly Detection"])
async def trigger_model_retraining(
    model_version: str = Query("v1.0", description="Model version to create"),
    db: Session = Depends(get_db),
):
    """
    Trigger retraining of anomaly detection models.

    **Admin only endpoint**

    **Process:**
    1. Collect training data from database
    2. Train Isolation Forest models
    3. Train LSTM Autoencoder
    4. Evaluate models
    5. Save new model versions

    **Returns:**
    - Training status and metrics
    """
    try:
        from app.ai_engine.training import ModelTrainer, TrainingConfig

        logger.info(f"Model retraining triggered for version {model_version}")

        # Create training config
        config = TrainingConfig(model_version=model_version)

        # Initialize trainer
        trainer = ModelTrainer(db, config)

        # Train all models
        results = trainer.train_all_models()

        return {
            "success": True,
            "message": "Model retraining completed",
            "model_version": model_version,
            "training_results": results,
        }

    except Exception as e:
        logger.error(f"Model retraining failed: {e}")
        raise HTTPException(
            status_code=500, detail=f"Model retraining failed: {str(e)}"
        )
