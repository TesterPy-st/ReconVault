"""
Entity service for ReconVault intelligence system.

This module provides business logic and CRUD operations
for entity management in the intelligence system.
"""

import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple
from uuid import UUID

from sqlalchemy import and_, desc, func, or_
from sqlalchemy.orm import Session

from app.exceptions import (DatabaseError, DuplicateEntityError,
                            EntityNotFoundError)
from app.exceptions import ValidationError as ReconVaultValidationError
from app.models.entity import Entity
from app.schemas.entity import (EntityBulkRequest, EntityBulkResponse,
                                EntityCreate, EntityListResponse,
                                EntityResponse, EntitySearchRequest,
                                EntitySearchResponse, EntityStats, EntityType,
                                EntityUpdate)

# Configure logging
logger = logging.getLogger("reconvault.services.entity")


class EntityService:
    """
    Entity service for business logic and CRUD operations.

    Handles all entity-related operations including creation,
    retrieval, updating, deletion, and search functionality.
    """

    def __init__(self, db: Session):
        """Initialize entity service with database session"""
        self.db = db

    def create_entity(self, entity_data: EntityCreate) -> Entity:
        """
        Create a new entity.

        Args:
            entity_data: Entity creation data

        Returns:
            Entity: Created entity

        Raises:
            DuplicateEntityError: If entity already exists
            DatabaseError: If database operation fails
        """
        try:
            # Check for duplicate
            existing = (
                self.db.query(Entity)
                .filter(
                    and_(
                        Entity.type == entity_data.type,
                        Entity.value == entity_data.value,
                    )
                )
                .first()
            )

            if existing:
                logger.info(
                    f"Entity already exists: {entity_data.type}={entity_data.value}"
                )
                return existing

            # Create entity
            db_entity = Entity(
                type=entity_data.type,
                value=entity_data.value,
                source=entity_data.source,
                confidence=entity_data.confidence
                if entity_data.confidence is not None
                else 1.0,
                meta=entity_data.metadata,
                discovered_at=datetime.now(timezone.utc),
            )

            self.db.add(db_entity)
            self.db.commit()
            self.db.refresh(db_entity)

            logger.info(f"Created entity {db_entity.id}: {entity_data.value}")
            return db_entity

        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to create entity: {e}")
            raise DatabaseError("create_entity", str(e))

    def get_entity(self, entity_id: UUID) -> Entity:
        """
        Get entity by ID.

        Args:
            entity_id: Entity UUID

        Returns:
            Entity: Found entity

        Raises:
            EntityNotFoundError: If entity not found
        """
        entity = self.db.query(Entity).filter(Entity.id == entity_id).first()
        if not entity:
            raise EntityNotFoundError(str(entity_id))
        return entity

    def get_entities(
        self,
        limit: int = 100,
        offset: int = 0,
        entity_type: Optional[str] = None,
        source: Optional[str] = None,
    ) -> Tuple[List[Entity], int]:
        """
        Get list of entities with pagination.

        Args:
            limit: Maximum number of entities to return
            offset: Number of entities to skip
            entity_type: Filter by entity type
            source: Filter by source

        Returns:
            Tuple[List[Entity], int]: (entities list, total count)
        """
        try:
            query = self.db.query(Entity)

            if entity_type:
                query = query.filter(Entity.type == entity_type)

            if source:
                query = query.filter(Entity.source == source)

            total = query.count()
            entities = (
                query.order_by(desc(Entity.created_at))
                .offset(offset)
                .limit(limit)
                .all()
            )

            return entities, total

        except Exception as e:
            logger.error(f"Failed to get entities: {e}")
            raise DatabaseError("get_entities", str(e))

    def update_entity(self, entity_id: UUID, entity_data: EntityUpdate) -> Entity:
        """
        Update an existing entity.

        Args:
            entity_id: Entity UUID
            entity_data: Entity update data

        Returns:
            Entity: Updated entity

        Raises:
            EntityNotFoundError: If entity not found
            DatabaseError: If database operation fails
        """
        try:
            entity = self.get_entity(entity_id)

            # Update fields
            update_data = entity_data.dict(exclude_unset=True)

            # Handle metadata field name mapping
            if "metadata" in update_data:
                update_data["meta"] = update_data.pop("metadata")

            # Handle tags conversion
            if "tags" in update_data and update_data["tags"] is not None:
                if isinstance(update_data["tags"], list):
                    update_data["tags"] = ",".join(update_data["tags"])

            for field, value in update_data.items():
                if hasattr(entity, field):
                    setattr(entity, field, value)

            self.db.commit()
            self.db.refresh(entity)

            logger.info(f"Updated entity {entity_id}")
            return entity

        except EntityNotFoundError:
            raise
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to update entity {entity_id}: {e}")
            raise DatabaseError("update_entity", str(e))

    def delete_entity(self, entity_id: UUID) -> bool:
        """
        Delete an entity (hard delete).

        Args:
            entity_id: Entity UUID

        Returns:
            bool: True if deletion successful

        Raises:
            EntityNotFoundError: If entity not found
            DatabaseError: If database operation fails
        """
        try:
            entity = self.get_entity(entity_id)

            self.db.delete(entity)
            self.db.commit()

            logger.info(f"Deleted entity {entity_id}")
            return True

        except EntityNotFoundError:
            raise
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to delete entity {entity_id}: {e}")
            raise DatabaseError("delete_entity", str(e))

    def search_entities(
        self,
        query: Optional[str] = None,
        entity_type: Optional[str] = None,
        source: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> Tuple[List[Entity], int]:
        """
        Search entities based on criteria.

        Args:
            query: Text search query
            entity_type: Filter by entity type
            source: Filter by source
            limit: Maximum results
            offset: Number of results to skip

        Returns:
            Tuple[List[Entity], int]: (matching entities, total count)
        """
        try:
            db_query = self.db.query(Entity)

            # Apply filters
            if query:
                search_term = f"%{query}%"
                db_query = db_query.filter(
                    or_(
                        Entity.value.ilike(search_term),
                        Entity.description.ilike(search_term),
                    )
                )

            if entity_type:
                db_query = db_query.filter(Entity.type == entity_type)

            if source:
                db_query = db_query.filter(Entity.source == source)

            total = db_query.count()
            entities = (
                db_query.order_by(desc(Entity.created_at))
                .offset(offset)
                .limit(limit)
                .all()
            )

            return entities, total

        except Exception as e:
            logger.error(f"Failed to search entities: {e}")
            raise DatabaseError("search_entities", str(e))

    def bulk_create_entities(
        self, entities_data: List[EntityCreate], skip_duplicates: bool = True
    ) -> Tuple[List[Entity], List[Dict[str, Any]], List[Dict[str, Any]]]:
        """
        Create multiple entities in bulk.

        Args:
            entities_data: List of entity creation data
            skip_duplicates: Whether to skip duplicates

        Returns:
            Tuple: (created entities, skipped entities, failed entities)
        """
        created = []
        skipped = []
        failed = []

        for entity_data in entities_data:
            try:
                # Check for duplicate
                existing = (
                    self.db.query(Entity)
                    .filter(
                        and_(
                            Entity.type == entity_data.type,
                            Entity.value == entity_data.value,
                        )
                    )
                    .first()
                )

                if existing:
                    if skip_duplicates:
                        skipped.append(
                            {
                                "type": entity_data.type,
                                "value": entity_data.value,
                                "reason": "duplicate",
                            }
                        )
                        continue
                    else:
                        created.append(existing)
                        continue

                entity = self.create_entity(entity_data)
                created.append(entity)

            except Exception as e:
                logger.error(f"Failed to create entity {entity_data.value}: {e}")
                failed.append(
                    {
                        "type": entity_data.type,
                        "value": entity_data.value,
                        "error": str(e),
                    }
                )

        return created, skipped, failed

    def get_entity_statistics(self) -> Dict[str, Any]:
        """
        Get entity statistics.

        Returns:
            Dict[str, Any]: Entity statistics
        """
        try:
            total_entities = self.db.query(Entity).count()

            # Get type distribution
            type_counts = {}
            for entity_type in EntityType:
                count = self.db.query(Entity).filter(Entity.type == entity_type).count()
                if count > 0:
                    type_counts[entity_type.value] = count

            # Get source distribution
            source_counts = {}
            sources = self.db.query(Entity.source).distinct().all()
            for (source,) in sources:
                count = self.db.query(Entity).filter(Entity.source == source).count()
                source_counts[source] = count

            # Calculate average confidence
            avg_confidence = self.db.query(func.avg(Entity.confidence)).scalar() or 0.0

            return {
                "total_entities": total_entities,
                "entities_by_type": type_counts,
                "entities_by_source": source_counts,
                "average_confidence": float(avg_confidence),
            }

        except Exception as e:
            logger.error(f"Failed to get entity statistics: {e}")
            raise DatabaseError("get_entity_statistics", str(e))


def get_entity_service(db: Session) -> EntityService:
    """
    Get entity service instance.

    Args:
        db: Database session

    Returns:
        EntityService: Entity service instance
    """
    return EntityService(db)
