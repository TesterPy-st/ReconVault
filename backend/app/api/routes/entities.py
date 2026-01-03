"""
Entity API routes for ReconVault.

This module provides REST API endpoints for entity management
including CRUD operations, search, and statistics.
"""

import logging
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_database
from app.exceptions import (DatabaseError, DuplicateEntityError,
                            EntityNotFoundError)
from app.schemas.entity import (EntityBulkRequest, EntityBulkResponse,
                                EntityCreate, EntityDeleteResponse,
                                EntityListResponse, EntityResponse,
                                EntityUpdate)
from app.services.entity_service import EntityService

# Configure logging
logger = logging.getLogger("reconvault.api.entities")

# Create router
router = APIRouter(prefix="/entities", tags=["entities"])


@router.post("/", response_model=EntityResponse, status_code=status.HTTP_201_CREATED)
def create_entity(entity_data: EntityCreate, db: Session = Depends(get_database)):
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
        service = EntityService(db)
        entity = service.create_entity(entity_data)

        return EntityResponse.model_validate(entity)

    except DuplicateEntityError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except DatabaseError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )
    except Exception as e:
        logger.error(f"Failed to create entity: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@router.get("/", response_model=EntityListResponse)
def get_entities(
    limit: int = Query(50, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    entity_type: Optional[str] = Query(None),
    source: Optional[str] = Query(None),
    db: Session = Depends(get_database),
):
    """
    Get list of entities with pagination.

    Args:
        limit: Maximum number of entities to return
        offset: Number of entities to skip
        entity_type: Filter by entity type
        source: Filter by source
        db: Database session

    Returns:
        EntityListResponse: Paginated list of entities
    """
    try:
        service = EntityService(db)
        entities, total = service.get_entities(
            limit=limit, offset=offset, entity_type=entity_type, source=source
        )

        pages = (total + limit - 1) // limit

        return EntityListResponse(
            entities=[EntityResponse.model_validate(e) for e in entities],
            total=total,
            page=(offset // limit) + 1,
            per_page=limit,
            pages=pages,
        )

    except Exception as e:
        logger.error(f"Failed to get entities: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@router.get("/{entity_id}", response_model=EntityResponse)
def get_entity(entity_id: UUID, db: Session = Depends(get_database)):
    """
    Get entity by ID.

    Args:
        entity_id: Entity UUID
        db: Database session

    Returns:
        EntityResponse: Entity data

    Raises:
        HTTPException: If entity not found
    """
    try:
        service = EntityService(db)
        entity = service.get_entity(entity_id)

        return EntityResponse.model_validate(entity)

    except EntityNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to get entity {entity_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@router.put("/{entity_id}", response_model=EntityResponse)
def update_entity(
    entity_id: UUID, entity_data: EntityUpdate, db: Session = Depends(get_database)
):
    """
    Update an existing entity.

    Args:
        entity_id: Entity UUID
        entity_data: Entity update data
        db: Database session

    Returns:
        EntityResponse: Updated entity

    Raises:
        HTTPException: If entity not found or update fails
    """
    try:
        service = EntityService(db)
        entity = service.update_entity(entity_id, entity_data)

        return EntityResponse.model_validate(entity)

    except EntityNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except DatabaseError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )
    except Exception as e:
        logger.error(f"Failed to update entity {entity_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@router.delete("/{entity_id}", response_model=EntityDeleteResponse)
def delete_entity(entity_id: UUID, db: Session = Depends(get_database)):
    """
    Delete an entity.

    Args:
        entity_id: Entity UUID
        db: Database session

    Returns:
        EntityDeleteResponse: Deletion result

    Raises:
        HTTPException: If entity not found
    """
    try:
        service = EntityService(db)
        success = service.delete_entity(entity_id)

        return EntityDeleteResponse(
            success=success,
            deleted_id=entity_id,
            message=f"Entity {entity_id} deleted successfully",
        )

    except EntityNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except DatabaseError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )
    except Exception as e:
        logger.error(f"Failed to delete entity {entity_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@router.get("/search", response_model=EntityListResponse)
def search_entities(
    query: Optional[str] = Query(None),
    entity_type: Optional[str] = Query(None),
    source: Optional[str] = Query(None),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_database),
):
    """
    Search entities based on criteria.

    Args:
        query: Text search query
        entity_type: Filter by entity type
        source: Filter by source
        limit: Maximum results
        offset: Number of results to skip
        db: Database session

    Returns:
        EntityListResponse: Search results
    """
    try:
        service = EntityService(db)
        entities, total = service.search_entities(
            query=query,
            entity_type=entity_type,
            source=source,
            limit=limit,
            offset=offset,
        )

        pages = (total + limit - 1) // limit

        return EntityListResponse(
            entities=[EntityResponse.model_validate(e) for e in entities],
            total=total,
            page=(offset // limit) + 1,
            per_page=limit,
            pages=pages,
        )

    except Exception as e:
        logger.error(f"Failed to search entities: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@router.get("/{entity_id}/relationships", response_model=list)
def get_entity_relationships(
    entity_id: UUID,
    direction: str = Query("both", description="Relationship direction (in/out/both)"),
    db: Session = Depends(get_database),
):
    """
    Get relationships for an entity.

    Args:
        entity_id: Entity UUID
        direction: Relationship direction
        db: Database session

    Returns:
        list: Entity relationships

    Raises:
        HTTPException: If entity not found
    """
    try:
        service = EntityService(db)
        entity = service.get_entity(entity_id)

        # Get relationships from relationship service
        from app.services.relationship_service import RelationshipService

        rel_service = RelationshipService(db)

        relationships = rel_service.get_entity_relationships(entity_id, direction)

        return [r.to_dict() for r in relationships]

    except EntityNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to get entity relationships: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@router.post("/bulk", response_model=EntityBulkResponse)
def bulk_create_entities(
    bulk_request: EntityBulkRequest, db: Session = Depends(get_database)
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
        service = EntityService(db)
        created, skipped, failed = service.bulk_create_entities(
            bulk_request.entities, bulk_request.skip_duplicates
        )

        logger.info(f"Bulk created {len(created)} entities")

        return EntityBulkResponse(
            created=[EntityResponse.model_validate(e) for e in created],
            skipped=skipped,
            failed=failed,
        )

    except Exception as e:
        logger.error(f"Failed to bulk create entities: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@router.get("/statistics/overview", response_model=dict)
def get_entity_statistics(db: Session = Depends(get_database)):
    """
    Get entity statistics.

    Args:
        db: Database session

    Returns:
        dict: Entity statistics
    """
    try:
        service = EntityService(db)
        stats = service.get_entity_statistics()

        return stats

    except Exception as e:
        logger.error(f"Failed to get entity statistics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )
