"""
Entity service for ReconVault intelligence system.

This module provides business logic and CRUD operations
for entity management in the intelligence system.
"""

import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy import and_, asc, desc, or_
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Entity, EntityType, Target
from app.models.audit import AuditAction, AuditLog, AuditSeverity
from app.schemas.entity import (EntityBulkRequest, EntityBulkResponse,
                                EntityCreate, EntityListResponse,
                                EntityResponse, EntitySearchRequest,
                                EntitySearchResponse, EntityStats,
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

    def create_entity(
        self, entity_data: EntityCreate, user_id: Optional[int] = None
    ) -> EntityResponse:
        """
        Create a new entity.

        Args:
            entity_data: Entity creation data
            user_id: ID of user creating the entity

        Returns:
            EntityResponse: Created entity data
        """
        try:
            # Verify target exists if target_id is provided
            if entity_data.target_id:
                target = (
                    self.db.query(Target)
                    .filter(
                        and_(
                            Target.id == entity_data.target_id, Target.is_active == True
                        )
                    )
                    .first()
                )
                if not target:
                    raise ValueError(
                        f"Target {entity_data.target_id} not found or inactive"
                    )

            # Convert tags list to comma-separated string
            tags_str = ",".join(entity_data.tags) if entity_data.tags else None

            # Create entity
            db_entity = Entity(
                type=entity_data.type,
                name=entity_data.name,
                value=entity_data.value,
                risk_score=entity_data.risk_score,
                confidence=entity_data.confidence,
                source=entity_data.source,
                target_id=entity_data.target_id,
                description=entity_data.description,
                metadata=entity_data.metadata,
                tags=tags_str,
                first_seen=entity_data.first_seen,
                last_seen=entity_data.last_seen,
            )

            self.db.add(db_entity)
            self.db.commit()
            self.db.refresh(db_entity)

            # Log audit event
            self._log_audit_event(
                AuditAction.ENTITY_CREATE,
                user_id,
                f"Created entity: {entity_data.value}",
                entity_id=db_entity.id,
                target_id=entity_data.target_id,
                risk_score=entity_data.risk_score,
            )

            logger.info(f"Created entity {db_entity.id}: {entity_data.value}")
            return EntityResponse.from_orm(db_entity)

        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to create entity: {e}")
            raise

    def get_entity(self, entity_id: int) -> Optional[EntityResponse]:
        """
        Get entity by ID.

        Args:
            entity_id: Entity database ID

        Returns:
            Optional[EntityResponse]: Entity data or None if not found
        """
        try:
            db_entity = self.db.query(Entity).filter(Entity.id == entity_id).first()
            if db_entity:
                return EntityResponse.from_orm(db_entity)
            return None
        except Exception as e:
            logger.error(f"Failed to get entity {entity_id}: {e}")
            return None

    def get_entities(
        self,
        skip: int = 0,
        limit: int = 100,
        active_only: bool = True,
        target_id: Optional[int] = None,
    ) -> EntityListResponse:
        """
        Get list of entities with pagination.

        Args:
            skip: Number of entities to skip
            limit: Maximum number of entities to return
            active_only: Whether to return only active entities
            target_id: Filter by target ID

        Returns:
            EntityListResponse: Paginated list of entities
        """
        try:
            query = self.db.query(Entity)

            if active_only:
                query = query.filter(Entity.is_active == True)

            if target_id:
                query = query.filter(Entity.target_id == target_id)

            total = query.count()
            entities = (
                query.order_by(desc(Entity.risk_score)).offset(skip).limit(limit).all()
            )

            return EntityListResponse(
                entities=[EntityResponse.from_orm(entity) for entity in entities],
                total=total,
                page=(skip // limit) + 1,
                per_page=limit,
                pages=(total + limit - 1) // limit,
            )

        except Exception as e:
            logger.error(f"Failed to get entities: {e}")
            raise

    def update_entity(
        self, entity_id: int, entity_data: EntityUpdate, user_id: Optional[int] = None
    ) -> Optional[EntityResponse]:
        """
        Update an existing entity.

        Args:
            entity_id: Entity database ID
            entity_data: Entity update data
            user_id: ID of user updating the entity

        Returns:
            Optional[EntityResponse]: Updated entity data or None if not found
        """
        try:
            db_entity = self.db.query(Entity).filter(Entity.id == entity_id).first()
            if not db_entity:
                return None

            # Verify target exists if target_id is being updated
            if entity_data.target_id is not None:
                target = (
                    self.db.query(Target)
                    .filter(
                        and_(
                            Target.id == entity_data.target_id, Target.is_active == True
                        )
                    )
                    .first()
                )
                if not target:
                    raise ValueError(
                        f"Target {entity_data.target_id} not found or inactive"
                    )

            # Update fields
            update_data = entity_data.dict(exclude_unset=True)

            # Handle tags conversion
            if "tags" in update_data and update_data["tags"] is not None:
                update_data["tags"] = ",".join(update_data["tags"])

            for field, value in update_data.items():
                setattr(db_entity, field, value)

            self.db.commit()
            self.db.refresh(db_entity)

            # Log audit event
            self._log_audit_event(
                AuditAction.ENTITY_UPDATE,
                user_id,
                f"Updated entity: {db_entity.value}",
                entity_id=db_entity.id,
                target_id=db_entity.target_id,
                risk_score=db_entity.risk_score,
            )

            logger.info(f"Updated entity {entity_id}")
            return EntityResponse.from_orm(db_entity)

        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to update entity {entity_id}: {e}")
            raise

    def delete_entity(self, entity_id: int, user_id: Optional[int] = None) -> bool:
        """
        Delete an entity (soft delete by setting is_active to False).

        Args:
            entity_id: Entity database ID
            user_id: ID of user deleting the entity

        Returns:
            bool: True if deletion successful
        """
        try:
            db_entity = self.db.query(Entity).filter(Entity.id == entity_id).first()
            if not db_entity:
                return False

            # Soft delete
            db_entity.is_active = False
            self.db.commit()

            # Log audit event
            self._log_audit_event(
                AuditAction.ENTITY_DELETE,
                user_id,
                f"Deleted entity: {db_entity.value}",
                entity_id=db_entity.id,
                target_id=db_entity.target_id,
                risk_score=db_entity.risk_score,
            )

            logger.info(f"Deleted entity {entity_id}")
            return True

        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to delete entity {entity_id}: {e}")
            return False

    def search_entities(
        self, search_request: EntitySearchRequest
    ) -> EntitySearchResponse:
        """
        Search entities based on criteria.

        Args:
            search_request: Search criteria

        Returns:
            EntitySearchResponse: Search results
        """
        try:
            query = self.db.query(Entity)

            # Apply filters
            if search_request.query:
                search_term = f"%{search_request.query}%"
                query = query.filter(
                    or_(
                        Entity.value.ilike(search_term),
                        Entity.name.ilike(search_term),
                        Entity.description.ilike(search_term),
                        Entity.tags.ilike(search_term),
                    )
                )

            if search_request.type:
                query = query.filter(Entity.type == search_request.type)

            if search_request.source:
                search_term = f"%{search_request.source}%"
                query = query.filter(Entity.source.ilike(search_term))

            if search_request.target_id:
                query = query.filter(Entity.target_id == search_request.target_id)

            if search_request.risk_level:
                # Convert risk level to score range
                risk_ranges = {
                    "critical": (0.8, 1.0),
                    "high": (0.6, 0.8),
                    "medium": (0.4, 0.6),
                    "low": (0.2, 0.4),
                    "minimal": (0.0, 0.2),
                }
                if search_request.risk_level in risk_ranges:
                    min_score, max_score = risk_ranges[search_request.risk_level]
                    query = query.filter(
                        and_(
                            Entity.risk_score >= min_score,
                            Entity.risk_score < max_score,
                        )
                    )

            if search_request.verified is not None:
                query = query.filter(Entity.is_verified == search_request.verified)

            if search_request.tags:
                for tag in search_request.tags:
                    search_term = f"%{tag}%"
                    query = query.filter(Entity.tags.ilike(search_term))

            if search_request.created_after:
                query = query.filter(Entity.created_at >= search_request.created_after)

            if search_request.created_before:
                query = query.filter(Entity.created_at <= search_request.created_before)

            # Only active entities by default
            query = query.filter(Entity.is_active == True)

            total = query.count()
            entities = (
                query.order_by(desc(Entity.risk_score))
                .offset(search_request.offset)
                .limit(search_request.limit)
                .all()
            )

            return EntitySearchResponse(
                entities=[EntityResponse.from_orm(entity) for entity in entities],
                total=total,
                query=search_request.query,
                filters=search_request.dict(exclude_unset=True),
            )

        except Exception as e:
            logger.error(f"Failed to search entities: {e}")
            raise

    def verify_entity(
        self, entity_id: int, verified: bool = True, user_id: Optional[int] = None
    ) -> bool:
        """
        Verify or unverify an entity.

        Args:
            entity_id: Entity database ID
            verified: Verification status
            user_id: ID of user performing verification

        Returns:
            bool: True if operation successful
        """
        try:
            db_entity = self.db.query(Entity).filter(Entity.id == entity_id).first()
            if not db_entity:
                return False

            db_entity.is_verified = verified
            self.db.commit()

            # Log audit event
            action = (
                AuditAction.ENTITY_VERIFY if verified else AuditAction.ENTITY_UPDATE
            )
            self._log_audit_event(
                action,
                user_id,
                f"{'Verified' if verified else 'Unverified'} entity: {db_entity.value}",
                entity_id=db_entity.id,
                target_id=db_entity.target_id,
                risk_score=db_entity.risk_score,
            )

            logger.info(
                f"{'Verified' if verified else 'Unverified'} entity {entity_id}"
            )
            return True

        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to verify entity {entity_id}: {e}")
            return False

    def add_tags(
        self, entity_id: int, tags: List[str], user_id: Optional[int] = None
    ) -> bool:
        """
        Add tags to an entity.

        Args:
            entity_id: Entity database ID
            tags: Tags to add
            user_id: ID of user performing the operation

        Returns:
            bool: True if operation successful
        """
        try:
            db_entity = self.db.query(Entity).filter(Entity.id == entity_id).first()
            if not db_entity:
                return False

            # Add tags
            for tag in tags:
                db_entity.add_tag(tag)

            self.db.commit()

            # Log audit event
            self._log_audit_event(
                AuditAction.ENTITY_UPDATE,
                user_id,
                f"Added tags to entity: {tags}",
                entity_id=db_entity.id,
                target_id=db_entity.target_id,
                risk_score=db_entity.risk_score,
            )

            logger.info(f"Added tags {tags} to entity {entity_id}")
            return True

        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to add tags to entity {entity_id}: {e}")
            return False

    def remove_tags(
        self, entity_id: int, tags: List[str], user_id: Optional[int] = None
    ) -> bool:
        """
        Remove tags from an entity.

        Args:
            entity_id: Entity database ID
            tags: Tags to remove
            user_id: ID of user performing the operation

        Returns:
            bool: True if operation successful
        """
        try:
            db_entity = self.db.query(Entity).filter(Entity.id == entity_id).first()
            if not db_entity:
                return False

            # Remove tags
            for tag in tags:
                db_entity.remove_tag(tag)

            self.db.commit()

            # Log audit event
            self._log_audit_event(
                AuditAction.ENTITY_UPDATE,
                user_id,
                f"Removed tags from entity: {tags}",
                entity_id=db_entity.id,
                target_id=db_entity.target_id,
                risk_score=db_entity.risk_score,
            )

            logger.info(f"Removed tags {tags} from entity {entity_id}")
            return True

        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to remove tags from entity {entity_id}: {e}")
            return False

    def get_entity_statistics(self) -> EntityStats:
        """
        Get entity statistics.

        Returns:
            EntityStats: Entity statistics
        """
        try:
            # Get counts
            total_entities = self.db.query(Entity).count()
            active_entities = (
                self.db.query(Entity).filter(Entity.is_active == True).count()
            )
            verified_entities = (
                self.db.query(Entity)
                .filter(and_(Entity.is_verified == True, Entity.is_active == True))
                .count()
            )
            entities_with_target = (
                self.db.query(Entity)
                .filter(and_(Entity.target_id.isnot(None), Entity.is_active == True))
                .count()
            )

            # Get type distribution
            type_counts = {}
            for entity_type in EntityType:
                count = (
                    self.db.query(Entity)
                    .filter(and_(Entity.type == entity_type, Entity.is_active == True))
                    .count()
                )
                type_counts[entity_type] = count

            # Get source distribution
            source_counts = {}
            sources = (
                self.db.query(Entity.source)
                .filter(Entity.is_active == True)
                .distinct()
                .all()
            )
            for source in sources:
                source_name = source[0]
                count = (
                    self.db.query(Entity)
                    .filter(
                        and_(Entity.source == source_name, Entity.is_active == True)
                    )
                    .count()
                )
                source_counts[source_name] = count

            # Get risk level distribution
            risk_counts = {
                "critical": self.db.query(Entity)
                .filter(and_(Entity.risk_score >= 0.8, Entity.is_active == True))
                .count(),
                "high": self.db.query(Entity)
                .filter(
                    and_(
                        Entity.risk_score >= 0.6,
                        Entity.risk_score < 0.8,
                        Entity.is_active == True,
                    )
                )
                .count(),
                "medium": self.db.query(Entity)
                .filter(
                    and_(
                        Entity.risk_score >= 0.4,
                        Entity.risk_score < 0.6,
                        Entity.is_active == True,
                    )
                )
                .count(),
                "low": self.db.query(Entity)
                .filter(
                    and_(
                        Entity.risk_score >= 0.2,
                        Entity.risk_score < 0.4,
                        Entity.is_active == True,
                    )
                )
                .count(),
                "minimal": self.db.query(Entity)
                .filter(and_(Entity.risk_score < 0.2, Entity.is_active == True))
                .count(),
            }

            # Calculate average risk score
            avg_risk = (
                self.db.query(Entity.risk_score).filter(Entity.is_active == True).all()
            )
            average_risk_score = (
                sum([score[0] for score in avg_risk]) / len(avg_risk)
                if avg_risk
                else 0.0
            )

            return EntityStats(
                total_entities=total_entities,
                active_entities=active_entities,
                verified_entities=verified_entities,
                entities_by_type=type_counts,
                entities_by_source=source_counts,
                entities_by_risk_level=risk_counts,
                average_risk_score=average_risk_score,
                entities_with_target=entities_with_target,
            )

        except Exception as e:
            logger.error(f"Failed to get entity statistics: {e}")
            raise

    def bulk_create_entities(
        self, bulk_request: EntityBulkRequest, user_id: Optional[int] = None
    ) -> EntityBulkResponse:
        """
        Create multiple entities in bulk.

        Args:
            bulk_request: Bulk entity creation request
            user_id: ID of user performing the operation

        Returns:
            EntityBulkResponse: Results of bulk operation
        """
        try:
            created = []
            skipped = []
            failed = []

            for i, entity_data in enumerate(bulk_request.entities):
                try:
                    # Verify target if specified
                    if entity_data.target_id:
                        target = (
                            self.db.query(Target)
                            .filter(
                                and_(
                                    Target.id == entity_data.target_id,
                                    Target.is_active == True,
                                )
                            )
                            .first()
                        )
                        if not target:
                            failed.append(
                                {
                                    "index": i,
                                    "reason": f"Target {entity_data.target_id} not found",
                                    "value": entity_data.value,
                                }
                            )
                            continue

                    # Check for duplicates
                    existing = (
                        self.db.query(Entity)
                        .filter(
                            and_(
                                Entity.value == entity_data.value,
                                Entity.type == entity_data.type,
                                Entity.source == entity_data.source,
                                Entity.is_active == True,
                            )
                        )
                        .first()
                    )
                    if existing and bulk_request.skip_duplicates:
                        skipped.append(
                            {
                                "index": i,
                                "reason": "duplicate",
                                "value": entity_data.value,
                            }
                        )
                        continue

                    # Convert tags list to comma-separated string
                    tags_str = ",".join(entity_data.tags) if entity_data.tags else None

                    # Create entity
                    db_entity = Entity(
                        type=entity_data.type,
                        name=entity_data.name,
                        value=entity_data.value,
                        risk_score=entity_data.risk_score,
                        confidence=entity_data.confidence,
                        source=entity_data.source,
                        target_id=entity_data.target_id or bulk_request.link_to_target,
                        description=entity_data.description,
                        metadata=entity_data.metadata,
                        tags=tags_str,
                        first_seen=entity_data.first_seen,
                        last_seen=entity_data.last_seen,
                    )

                    self.db.add(db_entity)
                    self.db.commit()
                    self.db.refresh(db_entity)

                    created.append(EntityResponse.from_orm(db_entity))

                except Exception as e:
                    self.db.rollback()
                    failed.append(
                        {"index": i, "reason": str(e), "value": entity_data.value}
                    )

            # Log audit event
            self._log_audit_event(
                AuditAction.ENTITY_CREATE,
                user_id,
                f"Bulk created {len(created)} entities, skipped {len(skipped)}, failed {len(failed)}",
            )

            logger.info(f"Bulk created {len(created)} entities")
            return EntityBulkResponse(created=created, skipped=skipped, failed=failed)

        except Exception as e:
            logger.error(f"Failed to bulk create entities: {e}")
            raise

    def calculate_risk_score(self, entity_data: Dict[str, Any]) -> float:
        """
        Calculate risk score for an entity based on its properties.

        Args:
            entity_data: Entity properties

        Returns:
            float: Calculated risk score
        """
        # Base risk calculation logic
        base_score = 0.0

        # Type-based risk
        high_risk_types = ["threat_actor", "malware", "vulnerability"]
        medium_risk_types = ["ip_address", "domain", "indicator"]

        if entity_data.get("type") in high_risk_types:
            base_score += 0.7
        elif entity_data.get("type") in medium_risk_types:
            base_score += 0.4
        else:
            base_score += 0.2

        # Source-based risk
        if entity_data.get("source") == "threat_intel":
            base_score += 0.3
        elif entity_data.get("source") == "osint":
            base_score += 0.1

        # Confidence adjustment
        confidence = entity_data.get("confidence", 1.0)
        base_score = base_score * confidence

        return min(base_score, 1.0)

    def _log_audit_event(
        self,
        action: AuditAction,
        user_id: Optional[int],
        description: str,
        entity_id: Optional[int] = None,
        target_id: Optional[int] = None,
        risk_score: float = 0.0,
    ) -> None:
        """
        Log an audit event.

        Args:
            action: Audit action type
            user_id: User ID
            description: Event description
            entity_id: Related entity ID
            target_id: Related target ID
            risk_score: Risk score for the event
        """
        try:
            audit_log = AuditLog.create_log(
                action=action,
                user_id=user_id,
                description=description,
                entity_id=entity_id,
                target_id=target_id,
                severity=AuditSeverity.INFO,
                risk_score=risk_score,
            )

            self.db.add(audit_log)
            self.db.commit()

        except Exception as e:
            logger.error(f"Failed to log audit event: {e}")


def get_entity_service(db: Session = None) -> EntityService:
    """
    Get entity service instance.

    Args:
        db: Database session (optional)

    Returns:
        EntityService: Entity service instance
    """
    if db is None:
        db = next(get_db())
    return EntityService(db)
