"""
Relationships API routes for ReconVault backend.

This module provides REST API endpoints for managing relationships
between entities in the intelligence graph.
"""

import logging
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_database, get_neo4j_session
from app.exceptions import (EntityNotFoundError, InvalidRelationshipError,
                            RelationshipNotFoundError)
from app.intelligence_graph.neo4j_client import Neo4jClient
from app.schemas.relationship import (RelationshipCreate,
                                      RelationshipDeleteResponse,
                                      RelationshipListResponse,
                                      RelationshipResponse,
                                      RelationshipSearchRequest,
                                      RelationshipUpdate,
                                      RelationshipWithEntities)
from app.services.relationship_service import RelationshipService

# Configure logging
logger = logging.getLogger("reconvault.api.relationships")

# Create router
router = APIRouter(prefix="/relationships", tags=["relationships"])


@router.post(
    "/", response_model=RelationshipResponse, status_code=status.HTTP_201_CREATED
)
def create_relationship(
    relationship_data: RelationshipCreate,
    db: Session = Depends(get_database),
    neo4j: Neo4jClient = Depends(get_neo4j_session),
):
    """
    Create a new relationship between two entities.

    Args:
        relationship_data: Relationship creation data
        db: Database session
        neo4j: Neo4j client

    Returns:
        RelationshipResponse: Created relationship

    Raises:
        HTTPException: If entities not found or relationship invalid
    """
    try:
        service = RelationshipService(db, neo4j)
        relationship = service.create_relationship(
            source_entity_id=relationship_data.source_entity_id,
            target_entity_id=relationship_data.target_entity_id,
            relationship_type=relationship_data.type,
            confidence=relationship_data.confidence,
            metadata=relationship_data.metadata,
        )

        return RelationshipResponse.model_validate(relationship)

    except EntityNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except InvalidRelationshipError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to create relationship: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@router.get("/", response_model=RelationshipListResponse)
def get_relationships(
    limit: int = Query(50, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    entity_id: Optional[UUID] = Query(None),
    source_entity_id: Optional[UUID] = Query(None),
    target_entity_id: Optional[UUID] = Query(None),
    relationship_type: Optional[str] = Query(None),
    min_confidence: Optional[float] = Query(None, ge=0.0, le=1.0),
    db: Session = Depends(get_database),
):
    """
    Get list of relationships with optional filters.

    Args:
        limit: Maximum number of results
        offset: Number of results to skip
        entity_id: Filter by entity (source or target)
        source_entity_id: Filter by source entity
        target_entity_id: Filter by target entity
        relationship_type: Filter by relationship type
        min_confidence: Minimum confidence score
        db: Database session

    Returns:
        RelationshipListResponse: List of relationships with pagination
    """
    try:
        service = RelationshipService(db)
        relationships, total = service.get_relationships(
            limit=limit,
            offset=offset,
            entity_id=entity_id,
            source_entity_id=source_entity_id,
            target_entity_id=target_entity_id,
            relationship_type=relationship_type,
            min_confidence=min_confidence,
        )

        pages = (total + limit - 1) // limit

        return RelationshipListResponse(
            relationships=[
                RelationshipResponse.model_validate(r) for r in relationships
            ],
            total=total,
            page=(offset // limit) + 1,
            per_page=limit,
            pages=pages,
        )

    except Exception as e:
        logger.error(f"Failed to get relationships: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@router.get("/{relationship_id}", response_model=RelationshipResponse)
def get_relationship(relationship_id: UUID, db: Session = Depends(get_database)):
    """
    Get a specific relationship by ID.

    Args:
        relationship_id: Relationship UUID
        db: Database session

    Returns:
        RelationshipResponse: Relationship details

    Raises:
        HTTPException: If relationship not found
    """
    try:
        service = RelationshipService(db)
        relationship = service.get_relationship(relationship_id)

        return RelationshipResponse.model_validate(relationship)

    except RelationshipNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to get relationship: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@router.put("/{relationship_id}", response_model=RelationshipResponse)
def update_relationship(
    relationship_id: UUID,
    update_data: RelationshipUpdate,
    db: Session = Depends(get_database),
    neo4j: Neo4jClient = Depends(get_neo4j_session),
):
    """
    Update a relationship.

    Args:
        relationship_id: Relationship UUID
        update_data: Updated relationship data
        db: Database session
        neo4j: Neo4j client

    Returns:
        RelationshipResponse: Updated relationship

    Raises:
        HTTPException: If relationship not found
    """
    try:
        service = RelationshipService(db, neo4j)
        relationship = service.update_relationship(
            relationship_id=relationship_id,
            relationship_type=update_data.type,
            confidence=update_data.confidence,
            metadata=update_data.metadata,
        )

        return RelationshipResponse.model_validate(relationship)

    except RelationshipNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to update relationship: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@router.delete("/{relationship_id}", response_model=RelationshipDeleteResponse)
def delete_relationship(
    relationship_id: UUID,
    db: Session = Depends(get_database),
    neo4j: Neo4jClient = Depends(get_neo4j_session),
):
    """
    Delete a relationship.

    Args:
        relationship_id: Relationship UUID
        db: Database session
        neo4j: Neo4j client

    Returns:
        RelationshipDeleteResponse: Deletion confirmation

    Raises:
        HTTPException: If relationship not found
    """
    try:
        service = RelationshipService(db, neo4j)
        success = service.delete_relationship(relationship_id)

        return RelationshipDeleteResponse(
            success=success,
            deleted_id=relationship_id,
            message="Relationship deleted successfully",
        )

    except RelationshipNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to delete relationship: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@router.get("/graph", response_model=dict)
def get_relationship_graph(
    entity_id: Optional[UUID] = Query(None),
    depth: int = Query(2, ge=1, le=5),
    db: Session = Depends(get_database),
):
    """
    Get graph structure for visualization.

    Args:
        entity_id: Starting entity ID
        depth: Graph depth to traverse
        db: Database session

    Returns:
        dict: Graph structure with nodes and edges
    """
    try:
        service = RelationshipService(db)

        if entity_id:
            relationships = service.get_entity_relationships(entity_id)
        else:
            relationships, _ = service.get_relationships(limit=1000)

        # Build nodes and edges for visualization
        nodes_dict = {}
        edges = []

        for rel in relationships:
            # Add source node
            if str(rel.source_entity_id) not in nodes_dict:
                nodes_dict[str(rel.source_entity_id)] = {
                    "id": str(rel.source_entity_id),
                    "label": "Entity",
                }

            # Add target node
            if str(rel.target_entity_id) not in nodes_dict:
                nodes_dict[str(rel.target_entity_id)] = {
                    "id": str(rel.target_entity_id),
                    "label": "Entity",
                }

            # Add edge
            edges.append(
                {
                    "source": str(rel.source_entity_id),
                    "target": str(rel.target_entity_id),
                    "type": rel.type,
                    "confidence": rel.confidence,
                }
            )

        nodes = list(nodes_dict.values())

        return {
            "nodes": nodes,
            "edges": edges,
            "node_count": len(nodes),
            "edge_count": len(edges),
        }

    except Exception as e:
        logger.error(f"Failed to get relationship graph: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )
