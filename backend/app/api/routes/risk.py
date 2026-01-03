"""
Risk Assessment API Routes

Endpoints for risk analysis, scoring, and reporting.
"""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from loguru import logger
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.entity import Entity
from app.models.relationship import Relationship
from app.models.target import Target
from app.risk_engine.exposure_models import ExposureAnalyzer
from app.risk_engine.risk_analyzer import RiskAnalyzer
from app.schemas.risk import (
    AnalyzeBatchRequest,
    AnalyzeBatchResponse,
    AnalyzeEntityRequest,
    AnalyzeResponse,
    ComprehensiveExposureSchema,
    DataExposureSchema,
    EntityMetricsSchema,
    EntityRiskSchema,
    ErrorResponse,
    IdentityExposureSchema,
    InfrastructureExposureSchema,
    NetworkExposureSchema,
    PatternLibrarySchema,
    RecalculateRequest,
    RecalculateResponse,
    RelationshipRiskSchema,
    RiskPatternSchema,
    RiskReportSchema,
)

router = APIRouter()


@router.post("/analyze", response_model=AnalyzeResponse, tags=["risk"])
def analyze_entity_risk(
    request: AnalyzeEntityRequest,
    db: Session = Depends(get_db),
    include_exposure: bool = Query(default=True, description="Include exposure analysis")
):
    """
    Analyze risk for a single entity.
    
    Args:
        request: Analysis request with entity ID
        db: Database session
        include_exposure: Whether to include detailed exposure analysis
        
    Returns:
        Risk assessment results
    """
    try:
        logger.info(f"Analyzing risk for entity {request.entity_id}")
        
        # Get entity from database
        entity = db.query(Entity).filter(Entity.id == request.entity_id).first()
        
        if not entity:
            raise HTTPException(status_code=404, detail=f"Entity {request.entity_id} not found")
        
        # Convert to dictionary
        entity_dict = entity.to_dict()
        
        # Initialize risk analyzer
        analyzer = RiskAnalyzer(db=db)
        
        # Calculate risk
        risk_assessment = analyzer.calculate_entity_risk(entity_dict)
        
        # Get exposure analysis if requested
        exposure_analysis = None
        if include_exposure:
            exposure_analyzer = ExposureAnalyzer()
            comprehensive = exposure_analyzer.get_comprehensive_exposure(entity_dict)
            
            exposure_analysis = ComprehensiveExposureSchema(
                total_exposure=comprehensive["total_exposure"],
                data_exposure=DataExposureSchema(**comprehensive["data_exposure"]),
                network_exposure=NetworkExposureSchema(**comprehensive["network_exposure"]),
                identity_exposure=IdentityExposureSchema(**comprehensive["identity_exposure"]),
                infrastructure_exposure=InfrastructureExposureSchema(**comprehensive["infrastructure_exposure"])
            )
        
        # Update entity risk score in database
        entity.risk_score = risk_assessment["risk_score"]
        db.commit()
        
        logger.info(f"Risk analysis complete for entity {request.entity_id}: {risk_assessment['risk_level']}")
        
        return AnalyzeResponse(
            success=True,
            risk_assessment=EntityRiskSchema(**risk_assessment),
            exposure_analysis=exposure_analysis
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing entity risk: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Risk analysis failed: {str(e)}")


@router.post("/analyze-batch", response_model=AnalyzeBatchResponse, tags=["risk"])
def analyze_batch_risk(
    request: AnalyzeBatchRequest,
    db: Session = Depends(get_db)
):
    """
    Analyze risk for multiple entities in batch.
    
    Args:
        request: Batch analysis request with entity IDs
        db: Database session
        
    Returns:
        Batch risk assessment results
    """
    try:
        logger.info(f"Batch risk analysis for {len(request.entity_ids)} entities")
        
        # Get entities from database
        entities = db.query(Entity).filter(Entity.id.in_(request.entity_ids)).all()
        
        if not entities:
            raise HTTPException(status_code=404, detail="No entities found")
        
        # Convert to dictionaries
        entity_dicts = [e.to_dict() for e in entities]
        
        # Initialize risk analyzer
        analyzer = RiskAnalyzer(db=db)
        
        # Calculate risk for each entity
        results = []
        for entity_dict in entity_dicts:
            risk_assessment = analyzer.calculate_entity_risk(entity_dict)
            results.append(EntityRiskSchema(**risk_assessment))
            
            # Update database
            entity_id = entity_dict["id"]
            entity = db.query(Entity).filter(Entity.id == entity_id).first()
            if entity:
                entity.risk_score = risk_assessment["risk_score"]
        
        db.commit()
        
        # Analyze relationships if requested
        relationship_risks = None
        if request.include_relationships:
            relationships = db.query(Relationship).filter(
                (Relationship.source_entity_id.in_(request.entity_ids)) |
                (Relationship.target_entity_id.in_(request.entity_ids))
            ).all()
            
            relationship_dicts = [r.to_dict() for r in relationships]
            relationship_risks = []
            
            for rel_dict in relationship_dicts:
                rel_risk = analyzer.calculate_relationship_risk(rel_dict)
                relationship_risks.append(RelationshipRiskSchema(**rel_risk))
        
        # Detect patterns
        patterns_detected = None
        if len(entity_dicts) >= 3:
            relationship_dicts = []
            if request.include_relationships:
                relationships = db.query(Relationship).filter(
                    (Relationship.source_entity_id.in_(request.entity_ids)) |
                    (Relationship.target_entity_id.in_(request.entity_ids))
                ).all()
                relationship_dicts = [r.to_dict() for r in relationships]
            
            patterns = analyzer.detect_risk_patterns(entity_dicts, relationship_dicts)
            patterns_detected = [RiskPatternSchema(**p) for p in patterns]
        
        # Calculate summary statistics
        risk_scores = [r.risk_score for r in results]
        summary = {
            "total_entities": len(results),
            "average_risk_score": round(sum(risk_scores) / len(risk_scores), 2) if risk_scores else 0,
            "max_risk_score": max(risk_scores) if risk_scores else 0,
            "min_risk_score": min(risk_scores) if risk_scores else 0,
            "critical_count": sum(1 for r in results if r.risk_level == "critical"),
            "high_count": sum(1 for r in results if r.risk_level == "high"),
            "medium_count": sum(1 for r in results if r.risk_level == "medium"),
            "low_count": sum(1 for r in results if r.risk_level == "low")
        }
        
        logger.info(f"Batch analysis complete: {len(results)} entities processed")
        
        return AnalyzeBatchResponse(
            success=True,
            results=results,
            relationship_risks=relationship_risks,
            patterns_detected=patterns_detected,
            summary=summary
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in batch risk analysis: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Batch analysis failed: {str(e)}")


@router.get("/report/{target_id}", response_model=RiskReportSchema, tags=["risk"])
def get_risk_report(
    target_id: int,
    db: Session = Depends(get_db)
):
    """
    Generate comprehensive risk report for a target.
    
    Args:
        target_id: Target ID
        db: Database session
        
    Returns:
        Comprehensive risk report
    """
    try:
        logger.info(f"Generating risk report for target {target_id}")
        
        # Check if target exists
        target = db.query(Target).filter(Target.id == target_id).first()
        if not target:
            raise HTTPException(status_code=404, detail=f"Target {target_id} not found")
        
        # Initialize risk analyzer
        analyzer = RiskAnalyzer(db=db)
        
        # Generate report
        report = analyzer.generate_risk_report(target_id)
        
        if report.get("status") == "error":
            raise HTTPException(status_code=500, detail=report.get("message", "Report generation failed"))
        
        if report.get("status") == "no_data":
            raise HTTPException(status_code=404, detail="No entities found for target")
        
        logger.info(f"Risk report generated for target {target_id}")
        
        return RiskReportSchema(**report)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating risk report: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Report generation failed: {str(e)}")


@router.get("/patterns", response_model=PatternLibrarySchema, tags=["risk"])
def get_pattern_library():
    """
    Get library of known risk patterns.
    
    Returns:
        Pattern library
    """
    patterns = [
        {
            "pattern_type": "breach_cluster",
            "description": "Multiple entities found in data breaches",
            "severity": "high"
        },
        {
            "pattern_type": "dark_web_exposure",
            "description": "Entities found on dark web",
            "severity": "critical"
        },
        {
            "pattern_type": "high_connectivity",
            "description": "Entity with many connections (potential pivot point)",
            "severity": "medium"
        },
        {
            "pattern_type": "malware_infrastructure",
            "description": "Malware-related infrastructure detected",
            "severity": "critical"
        },
        {
            "pattern_type": "vulnerability_chain",
            "description": "Chain of vulnerable entities",
            "severity": "high"
        },
        {
            "pattern_type": "anomaly_cluster",
            "description": "Cluster of anomalous entities",
            "severity": "medium"
        }
    ]
    
    return PatternLibrarySchema(
        patterns=patterns,
        total_patterns=len(patterns)
    )


@router.post("/recalculate", response_model=RecalculateResponse, tags=["risk"])
def recalculate_risks(
    request: RecalculateRequest,
    db: Session = Depends(get_db),
    async_mode: bool = Query(default=True, description="Run asynchronously via Celery")
):
    """
    Recalculate risk scores for entities.
    
    Args:
        request: Recalculation request
        db: Database session
        async_mode: Whether to run asynchronously
        
    Returns:
        Recalculation status
    """
    try:
        logger.info(f"Recalculating risks (target_id={request.target_id}, async={async_mode})")
        
        # Get entities to process
        query = db.query(Entity).filter(Entity.is_active == True)
        
        if request.target_id:
            # Check if target exists
            target = db.query(Target).filter(Target.id == request.target_id).first()
            if not target:
                raise HTTPException(status_code=404, detail=f"Target {request.target_id} not found")
            
            query = query.filter(Entity.target_id == request.target_id)
        
        entities = query.all()
        
        if not entities:
            return RecalculateResponse(
                success=True,
                message="No entities to process",
                entities_processed=0
            )
        
        if async_mode:
            # Queue async task
            from app.automation.celery_tasks import calculate_risks_async
            
            entity_ids = [e.id for e in entities]
            task = calculate_risks_async.delay(entity_ids)
            
            logger.info(f"Queued async risk recalculation: task_id={task.id}")
            
            return RecalculateResponse(
                success=True,
                message=f"Risk recalculation queued for {len(entities)} entities",
                entities_processed=len(entities),
                task_id=task.id
            )
        else:
            # Synchronous recalculation
            analyzer = RiskAnalyzer(db=db)
            
            for entity in entities:
                entity_dict = entity.to_dict()
                risk_assessment = analyzer.calculate_entity_risk(entity_dict)
                entity.risk_score = risk_assessment["risk_score"]
            
            db.commit()
            
            logger.info(f"Recalculated risks for {len(entities)} entities")
            
            return RecalculateResponse(
                success=True,
                message=f"Recalculated risks for {len(entities)} entities",
                entities_processed=len(entities)
            )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error recalculating risks: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Recalculation failed: {str(e)}")


@router.get("/metrics/{entity_id}", response_model=EntityMetricsSchema, tags=["risk"])
def get_entity_metrics(
    entity_id: int,
    db: Session = Depends(get_db)
):
    """
    Get comprehensive risk metrics for an entity.
    
    Args:
        entity_id: Entity ID
        db: Database session
        
    Returns:
        Entity risk metrics
    """
    try:
        logger.info(f"Getting risk metrics for entity {entity_id}")
        
        # Get entity
        entity = db.query(Entity).filter(Entity.id == entity_id).first()
        
        if not entity:
            raise HTTPException(status_code=404, detail=f"Entity {entity_id} not found")
        
        # Convert to dictionary
        entity_dict = entity.to_dict()
        
        # Initialize analyzers
        risk_analyzer = RiskAnalyzer(db=db)
        exposure_analyzer = ExposureAnalyzer()
        
        # Calculate current risk
        risk_assessment = risk_analyzer.calculate_entity_risk(entity_dict)
        
        # Get exposure analysis
        comprehensive = exposure_analyzer.get_comprehensive_exposure(entity_dict)
        
        exposure_analysis = ComprehensiveExposureSchema(
            total_exposure=comprehensive["total_exposure"],
            data_exposure=DataExposureSchema(**comprehensive["data_exposure"]),
            network_exposure=NetworkExposureSchema(**comprehensive["network_exposure"]),
            identity_exposure=IdentityExposureSchema(**comprehensive["identity_exposure"]),
            infrastructure_exposure=InfrastructureExposureSchema(**comprehensive["infrastructure_exposure"])
        )
        
        # Historical data (placeholder - would need risk_history table)
        historical_risk_scores = None
        
        logger.info(f"Retrieved metrics for entity {entity_id}")
        
        return EntityMetricsSchema(
            entity_id=entity_id,
            current_risk=EntityRiskSchema(**risk_assessment),
            exposure_analysis=exposure_analysis,
            historical_risk_scores=historical_risk_scores
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting entity metrics: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to get metrics: {str(e)}")
