"""
Entity API routes for ReconVault.

This module provides REST API endpoints for entity management
including CRUD operations, search, verification, and enrichment.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
import logging
from datetime import datetime, timezone

from app.database import get_db
from app.services.entity_service import get_entity_service
from app.schemas.entity import (
    EntityCreate, EntityUpdate, EntityResponse, EntityListResponse,
    EntitySearchRequest, EntitySearchResponse, EntityStats,
    EntityBulkRequest, EntityBulkResponse, EntityDeleteResponse,
    EntityVerificationRequest, EntityVerificationResponse,
    EntityEnrichmentRequest, EntityEnrichmentResponse,
    EntityTagRequest, EntityTagResponse
)
from app.models.audit import AuditLog, AuditAction

# Configure logging
logger = logging.getLogger("reconvault.api.entities")

# Create router
router = APIRouter()


@router.post("/", response_model=EntityResponse, status_code=status.HTTP_201_CREATED)
async def create_entity(
    entity_data: EntityCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new entity.
    
    Args:
        entity_data: Entity creation data
        db: Database session
    
    Returns:
        EntityResponse: Created entity
    
    Raises:
        HTTPException: If creation fails
    """
    try:
        entity_service = get_entity_service(db)
        entity = entity_service.create_entity(entity_data)
        
        logger.info(f"Created entity: {entity.id}")
        return entity
        
    except Exception as e:
        logger.error(f"Failed to create entity: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create entity: {str(e)}"
        )


@router.get("/{entity_id}", response_model=EntityResponse)
async def get_entity(entity_id: int, db: Session = Depends(get_db)):
    """
    Get entity by ID.
    
    Args:
        entity_id: Entity database ID
        db: Database session
    
    Returns:
        EntityResponse: Entity data
    
    Raises:
        HTTPException: If entity not found
    """
    try:
        entity_service = get_entity_service(db)
        entity = entity_service.get_entity(entity_id)
        
        if not entity:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Entity {entity_id} not found"
            )
        
        return entity
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get entity {entity_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get entity: {str(e)}"
        )


@router.get("/", response_model=EntityListResponse)
async def get_entities(
    skip: int = Query(0, ge=0, description="Number of entities to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of entities to return"),
    active_only: bool = Query(True, description="Only return active entities"),
    target_id: Optional[int] = Query(None, description="Filter by target ID"),
    db: Session = Depends(get_db)
):
    """
    Get list of entities with pagination.
    
    Args:
        skip: Number of entities to skip
        limit: Maximum number of entities to return
        active_only: Whether to return only active entities
        target_id: Filter by target ID
        db: Database session
    
    Returns:
        EntityListResponse: Paginated list of entities
    """
    try:
        entity_service = get_entity_service(db)
        entities = entity_service.get_entities(
            skip=skip, 
            limit=limit, 
            active_only=active_only, 
            target_id=target_id
        )
        
        return entities
        
    except Exception as e:
        logger.error(f"Failed to get entities: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get entities: {str(e)}"
        )


@router.put("/{entity_id}", response_model=EntityResponse)
async def update_entity(
    entity_id: int,
    entity_data: EntityUpdate,
    db: Session = Depends(get_db)
):
    """
    Update an existing entity.
    
    Args:
        entity_id: Entity database ID
        entity_data: Entity update data
        db: Database session
    
    Returns:
        EntityResponse: Updated entity
    
    Raises:
        HTTPException: If entity not found or update fails
    """
    try:
        entity_service = get_entity_service(db)
        entity = entity_service.update_entity(entity_id, entity_data)
        
        if not entity:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Entity {entity_id} not found"
            )
        
        logger.info(f"Updated entity: {entity_id}")
        return entity
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update entity {entity_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update entity: {str(e)}"
        )


@router.delete("/{entity_id}", response_model=EntityDeleteResponse)
async def delete_entity(entity_id: int, db: Session = Depends(get_db)):
    """
    Delete an entity (soft delete).
    
    Args:
        entity_id: Entity database ID
        db: Database session
    
    Returns:
        EntityDeleteResponse: Deletion result
    
    Raises:
        HTTPException: If entity not found
    """
    try:
        entity_service = get_entity_service(db)
        success = entity_service.delete_entity(entity_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Entity {entity_id} not found"
            )
        
        return EntityDeleteResponse(
            success=True,
            deleted_id=entity_id,
            message=f"Entity {entity_id} deleted successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete entity {entity_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete entity: {str(e)}"
        )


@router.post("/search", response_model=EntitySearchResponse)
async def search_entities(
    search_request: EntitySearchRequest,
    db: Session = Depends(get_db)
):
    """
    Search entities based on criteria.
    
    Args:
        search_request: Search criteria
        db: Database session
    
    Returns:
        EntitySearchResponse: Search results
    """
    try:
        entity_service = get_entity_service(db)
        results = entity_service.search_entities(search_request)
        
        return results
        
    except Exception as e:
        logger.error(f"Failed to search entities: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to search entities: {str(e)}"
        )


@router.get("/statistics/overview", response_model=EntityStats)
async def get_entity_statistics(db: Session = Depends(get_db)):
    """
    Get entity statistics.
    
    Args:
        db: Database session
    
    Returns:
        EntityStats: Entity statistics
    """
    try:
        entity_service = get_entity_service(db)
        stats = entity_service.get_entity_statistics()
        
        return stats
        
    except Exception as e:
        logger.error(f"Failed to get entity statistics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get entity statistics: {str(e)}"
        )


@router.post("/bulk", response_model=EntityBulkResponse)
async def bulk_create_entities(
    bulk_request: EntityBulkRequest,
    db: Session = Depends(get_db)
):
    """
    Create multiple entities in bulk.
    
    Args:
        bulk_request: Bulk entity creation request
        db: Database session
    
    Returns:
        EntityBulkResponse: Bulk operation results
    """
    try:
        entity_service = get_entity_service(db)
        results = entity_service.bulk_create_entities(bulk_request)
        
        logger.info(f"Bulk created {len(results.created)} entities")
        return results
        
    except Exception as e:
        logger.error(f"Failed to bulk create entities: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to bulk create entities: {str(e)}"
        )


@router.post("/verify", response_model=EntityVerificationResponse)
async def verify_entities(
    verification_request: EntityVerificationRequest,
    db: Session = Depends(get_db)
):
    """
    Verify multiple entities.
    
    Args:
        verification_request: Entity verification request
        db: Database session
    
    Returns:
        EntityVerificationResponse: Verification results
    """
    try:
        entity_service = get_entity_service(db)
        
        verified_count = 0
        failed_count = 0
        results = []
        
        for entity_id in verification_request.entity_ids:
            success = entity_service.verify_entity(
                entity_id, 
                verified=True, 
                user_id=None  # Would get from auth context
            )
            
            if success:
                verified_count += 1
                results.append({"entity_id": entity_id, "status": "verified"})
            else:
                failed_count += 1
                results.append({"entity_id": entity_id, "status": "failed"})
        
        return EntityVerificationResponse(
            verified_count=verified_count,
            failed_count=failed_count,
            results=results
        )
        
    except Exception as e:
        logger.error(f"Failed to verify entities: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to verify entities: {str(e)}"
        )


@router.post("/enrich", response_model=EntityEnrichmentResponse)
async def enrich_entities(
    enrichment_request: EntityEnrichmentRequest,
    db: Session = Depends(get_db),
    background_tasks: BackgroundTasks = None
):
    """
    Enrich entities with external data.
    
    Args:
        enrichment_request: Entity enrichment request
        db: Database session
        background_tasks: Background tasks
    
    Returns:
        EntityEnrichmentResponse: Enrichment results
    """
    try:
        # In a real implementation, this would trigger enrichment workflows
        # For now, return a basic enrichment response
        
        enrichment_id = f"enrich_{datetime.now().timestamp()}"
        
        # Simulate enrichment process
        results = {}
        for entity_id in enrichment_request.entity_ids:
            results[entity_id] = {
                "enriched": True,
                "sources_used": enrichment_request.enrichment_sources,
                "metadata": {"confidence_boost": 0.1}
            }
        
        return EntityEnrichmentResponse(
            enrichment_id=enrichment_id,
            status="completed",
            processed_entities=len(enrichment_request.entity_ids),
            enriched_entities=len(enrichment_request.entity_ids),
            failed_entities=0,
            results=results
        )
        
    except Exception as e:
        logger.error(f"Failed to enrich entities: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to enrich entities: {str(e)}"
        )


@router.post("/tags", response_model=EntityTagResponse)
async def manage_entity_tags(
    tag_request: EntityTagRequest,
    db: Session = Depends(get_db)
):
    """
    Add or remove tags from entities.
    
    Args:
        tag_request: Entity tagging request
        db: Database session
    
    Returns:
        EntityTagResponse: Tag operation results
    """
    try:
        entity_service = get_entity_service(db)
        
        updated_count = 0
        
        for entity_id in tag_request.entity_ids:
            if tag_request.action == "add":
                success = entity_service.add_tags(entity_id, tag_request.tags)
            elif tag_request.action == "remove":
                success = entity_service.remove_tags(entity_id, tag_request.tags)
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid tag action. Must be 'add' or 'remove'"
                )
            
            if success:
                updated_count += 1
        
        return EntityTagResponse(
            updated_count=updated_count,
            tags_added=tag_request.tags if tag_request.action == "add" else [],
            tags_removed=tag_request.tags if tag_request.action == "remove" else []
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to manage entity tags: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to manage entity tags: {str(e)}"
        )


@router.get("/{entity_id}/relationships", response_model=List[dict])
async def get_entity_relationships(
    entity_id: int,
    direction: str = Query("both", description="Relationship direction (in/out/both)"),
    db: Session = Depends(get_db)
):
    """
    Get relationships for an entity.
    
    Args:
        entity_id: Entity database ID
        direction: Relationship direction
        db: Database session
    
    Returns:
        List[dict]: Entity relationships
    
    Raises:
        HTTPException: If entity not found
    """
    try:
        # Verify entity exists
        entity_service = get_entity_service(db)
        entity = entity_service.get_entity(entity_id)
        
        if not entity:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Entity {entity_id} not found"
            )
        
        # Get relationships from graph service
        from app.services.graph_service import get_graph_service
        graph_service = get_graph_service()
        
        # This would get relationships from Neo4j
        relationships = graph_service.get_node_relationships(entity_id, direction)
        
        return relationships
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get relationships for entity {entity_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get entity relationships: {str(e)}"
        )


@router.post("/{entity_id}/risk-recalculate", response_model=dict)
async def recalculate_entity_risk(
    entity_id: int,
    db: Session = Depends(get_db)
):
    """
    Recalculate risk score for an entity.
    
    Args:
        entity_id: Entity database ID
        db: Database session
    
    Returns:
        dict: Risk recalculation result
    
    Raises:
        HTTPException: If entity not found
    """
    try:
        # Get entity
        entity_service = get_entity_service(db)
        entity = entity_service.get_entity(entity_id)
        
        if not entity:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Entity {entity_id} not found"
            )
        
        # Recalculate risk score
        entity_dict = entity.dict()
        new_risk_score = entity_service.calculate_risk_score(entity_dict)
        
        # Update entity
        update_data = EntityUpdate(risk_score=new_risk_score)
        updated_entity = entity_service.update_entity(entity_id, update_data)
        
        return {
            "entity_id": entity_id,
            "old_risk_score": entity.risk_score,
            "new_risk_score": new_risk_score,
            "risk_level": updated_entity.risk_level,
            "recalculated_at": datetime.now(timezone.utc).isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to recalculate risk for entity {entity_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to recalculate risk: {str(e)}"
        )


@router.get("/{entity_id}/enrichment-history", response_model=List[dict])
async def get_entity_enrichment_history(
    entity_id: int,
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db)
):
    """
    Get enrichment history for an entity.
    
    Args:
        entity_id: Entity database ID
        limit: Maximum number of history entries
        db: Database session
    
    Returns:
        List[dict]: Enrichment history
    
    Raises:
        HTTPException: If entity not found
    """
    try:
        # Verify entity exists
        entity_service = get_entity_service(db)
        entity = entity_service.get_entity(entity_id)
        
        if not entity:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Entity {entity_id} not found"
            )
        
        # In a real implementation, this would query enrichment history
        # For now, return empty list
        return []
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get enrichment history for entity {entity_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get enrichment history: {str(e)}"
        )