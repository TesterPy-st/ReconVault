"""
Relationship service for ReconVault backend application.

This module provides business logic for relationship CRUD operations,
validation, and Neo4j synchronization.
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from sqlalchemy import and_, or_
from sqlalchemy.orm import Session

from app.exceptions import (DatabaseError, EntityNotFoundError,
                            InvalidRelationshipError, Neo4jError,
                            RelationshipNotFoundError)
from app.intelligence_graph.neo4j_client import Neo4jClient
from app.models.entity import Entity
from app.models.relationship import Relationship

# Configure logging
logger = logging.getLogger("reconvault.services.relationship")


class RelationshipService:
    """Service class for relationship management operations"""

    def __init__(self, db: Session, neo4j_client: Optional[Neo4jClient] = None):
        """
        Initialize relationship service.

        Args:
            db: SQLAlchemy database session
            neo4j_client: Neo4j client for graph operations
        """
        self.db = db
        self.neo4j_client = neo4j_client

    def create_relationship(
        self,
        source_entity_id: UUID,
        target_entity_id: UUID,
        relationship_type: str,
        confidence: float = 1.0,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Relationship:
        """
        Create a new relationship between entities.

        Args:
            source_entity_id: Source entity UUID
            target_entity_id: Target entity UUID
            relationship_type: Type of relationship
            confidence: Confidence score (0.0 to 1.0)
            metadata: Additional metadata

        Returns:
            Relationship: Created relationship

        Raises:
            EntityNotFoundError: If either entity doesn't exist
            InvalidRelationshipError: If relationship is invalid
            DatabaseError: If database operation fails
        """
        try:
            # Validate entities exist
            source_entity = (
                self.db.query(Entity).filter(Entity.id == source_entity_id).first()
            )
            if not source_entity:
                raise EntityNotFoundError(str(source_entity_id))

            target_entity = (
                self.db.query(Entity).filter(Entity.id == target_entity_id).first()
            )
            if not target_entity:
                raise EntityNotFoundError(str(target_entity_id))

            # Prevent circular self-relationships
            if source_entity_id == target_entity_id:
                raise InvalidRelationshipError(
                    "Cannot create self-referential relationship"
                )

            # Check for duplicate relationship
            existing = (
                self.db.query(Relationship)
                .filter(
                    and_(
                        Relationship.source_entity_id == source_entity_id,
                        Relationship.target_entity_id == target_entity_id,
                        Relationship.type == relationship_type,
                    )
                )
                .first()
            )

            if existing:
                logger.info(f"Relationship already exists: {existing.id}")
                return existing

            # Create relationship
            relationship = Relationship(
                source_entity_id=source_entity_id,
                target_entity_id=target_entity_id,
                type=relationship_type,
                confidence=confidence,
                metadata=metadata,
                first_observed=datetime.utcnow(),
                last_observed=datetime.utcnow(),
            )

            self.db.add(relationship)
            self.db.commit()
            self.db.refresh(relationship)

            logger.info(f"Created relationship: {relationship.id}")

            # Sync to Neo4j
            if self.neo4j_client:
                self._sync_to_neo4j(relationship)

            return relationship

        except (EntityNotFoundError, InvalidRelationshipError):
            raise
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to create relationship: {e}")
            raise DatabaseError("create_relationship", str(e))

    def get_relationship(self, relationship_id: UUID) -> Relationship:
        """
        Get a relationship by ID.

        Args:
            relationship_id: Relationship UUID

        Returns:
            Relationship: Found relationship

        Raises:
            RelationshipNotFoundError: If relationship doesn't exist
        """
        relationship = (
            self.db.query(Relationship)
            .filter(Relationship.id == relationship_id)
            .first()
        )

        if not relationship:
            raise RelationshipNotFoundError(str(relationship_id))

        return relationship

    def get_relationships(
        self,
        limit: int = 100,
        offset: int = 0,
        entity_id: Optional[UUID] = None,
        source_entity_id: Optional[UUID] = None,
        target_entity_id: Optional[UUID] = None,
        relationship_type: Optional[str] = None,
        min_confidence: Optional[float] = None,
    ) -> tuple[List[Relationship], int]:
        """
        Get relationships with filters.

        Args:
            limit: Maximum number of results
            offset: Number of results to skip
            entity_id: Filter by entity (source or target)
            source_entity_id: Filter by source entity
            target_entity_id: Filter by target entity
            relationship_type: Filter by type
            min_confidence: Minimum confidence score

        Returns:
            tuple: (relationships list, total count)
        """
        query = self.db.query(Relationship)

        # Apply filters
        if entity_id:
            query = query.filter(
                or_(
                    Relationship.source_entity_id == entity_id,
                    Relationship.target_entity_id == entity_id,
                )
            )

        if source_entity_id:
            query = query.filter(Relationship.source_entity_id == source_entity_id)

        if target_entity_id:
            query = query.filter(Relationship.target_entity_id == target_entity_id)

        if relationship_type:
            query = query.filter(Relationship.type == relationship_type)

        if min_confidence is not None:
            query = query.filter(Relationship.confidence >= min_confidence)

        # Get total count
        total = query.count()

        # Apply pagination
        relationships = query.offset(offset).limit(limit).all()

        return relationships, total

    def update_relationship(
        self,
        relationship_id: UUID,
        relationship_type: Optional[str] = None,
        confidence: Optional[float] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Relationship:
        """
        Update a relationship.

        Args:
            relationship_id: Relationship UUID
            relationship_type: New type (optional)
            confidence: New confidence score (optional)
            metadata: New metadata (optional)

        Returns:
            Relationship: Updated relationship

        Raises:
            RelationshipNotFoundError: If relationship doesn't exist
            DatabaseError: If database operation fails
        """
        try:
            relationship = self.get_relationship(relationship_id)

            # Update fields
            if relationship_type is not None:
                relationship.type = relationship_type

            if confidence is not None:
                relationship.confidence = confidence

            if metadata is not None:
                relationship.metadata = metadata

            relationship.last_observed = datetime.utcnow()

            self.db.commit()
            self.db.refresh(relationship)

            logger.info(f"Updated relationship: {relationship_id}")

            # Sync to Neo4j
            if self.neo4j_client:
                self._sync_to_neo4j(relationship)

            return relationship

        except RelationshipNotFoundError:
            raise
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to update relationship: {e}")
            raise DatabaseError("update_relationship", str(e))

    def delete_relationship(self, relationship_id: UUID) -> bool:
        """
        Delete a relationship.

        Args:
            relationship_id: Relationship UUID

        Returns:
            bool: True if deleted successfully

        Raises:
            RelationshipNotFoundError: If relationship doesn't exist
            DatabaseError: If database operation fails
        """
        try:
            relationship = self.get_relationship(relationship_id)

            # Delete from Neo4j first
            if self.neo4j_client:
                self._delete_from_neo4j(relationship)

            # Delete from database
            self.db.delete(relationship)
            self.db.commit()

            logger.info(f"Deleted relationship: {relationship_id}")

            return True

        except RelationshipNotFoundError:
            raise
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to delete relationship: {e}")
            raise DatabaseError("delete_relationship", str(e))

    def get_entity_relationships(
        self, entity_id: UUID, direction: str = "both"
    ) -> List[Relationship]:
        """
        Get all relationships for an entity.

        Args:
            entity_id: Entity UUID
            direction: Relationship direction ("in", "out", "both")

        Returns:
            List[Relationship]: List of relationships
        """
        query = self.db.query(Relationship)

        if direction == "in":
            query = query.filter(Relationship.target_entity_id == entity_id)
        elif direction == "out":
            query = query.filter(Relationship.source_entity_id == entity_id)
        else:  # both
            query = query.filter(
                or_(
                    Relationship.source_entity_id == entity_id,
                    Relationship.target_entity_id == entity_id,
                )
            )

        return query.all()

    def _sync_to_neo4j(self, relationship: Relationship) -> None:
        """
        Sync relationship to Neo4j graph database.

        Args:
            relationship: Relationship to sync
        """
        if not self.neo4j_client:
            return

        try:
            # Get source and target entities
            source_entity = (
                self.db.query(Entity)
                .filter(Entity.id == relationship.source_entity_id)
                .first()
            )
            target_entity = (
                self.db.query(Entity)
                .filter(Entity.id == relationship.target_entity_id)
                .first()
            )

            if not source_entity or not target_entity:
                logger.warning(
                    f"Cannot sync relationship {relationship.id}: entities not found"
                )
                return

            # Create relationship in Neo4j
            self.neo4j_client.create_relationship(
                start_node_label="Entity",
                start_node_properties={
                    "id": str(source_entity.id),
                    "value": source_entity.value,
                },
                relationship_type=relationship.type.upper().replace("-", "_"),
                end_node_label="Entity",
                end_node_properties={
                    "id": str(target_entity.id),
                    "value": target_entity.value,
                },
                relationship_properties={
                    "confidence": relationship.confidence,
                    "created_at": relationship.created_at.isoformat()
                    if relationship.created_at
                    else None,
                },
            )

            logger.info(f"Synced relationship {relationship.id} to Neo4j")

        except Exception as e:
            logger.error(f"Failed to sync relationship to Neo4j: {e}")
            # Don't raise exception - Neo4j sync is not critical

    def _delete_from_neo4j(self, relationship: Relationship) -> None:
        """
        Delete relationship from Neo4j graph database.

        Args:
            relationship: Relationship to delete
        """
        if not self.neo4j_client:
            return

        try:
            # Delete relationship from Neo4j
            query = """
            MATCH (source:Entity {id: $source_id})-[r]->(target:Entity {id: $target_id})
            WHERE type(r) = $rel_type
            DELETE r
            """

            self.neo4j_client.run_query(
                query,
                {
                    "source_id": str(relationship.source_entity_id),
                    "target_id": str(relationship.target_entity_id),
                    "rel_type": relationship.type.upper().replace("-", "_"),
                },
            )

            logger.info(f"Deleted relationship {relationship.id} from Neo4j")

        except Exception as e:
            logger.error(f"Failed to delete relationship from Neo4j: {e}")
            # Don't raise exception - Neo4j sync is not critical
