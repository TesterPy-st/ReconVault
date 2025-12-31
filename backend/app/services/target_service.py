"""
Target service for ReconVault intelligence system.

This module provides business logic and CRUD operations
for target management in the intelligence system.
"""

from typing import List, Optional, Dict, Any, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, asc
from datetime import datetime, timezone
import logging

from app.models import Target, TargetType, TargetStatus
from app.schemas.target import (
    TargetCreate, TargetUpdate, TargetResponse, TargetListResponse,
    TargetSearchRequest, TargetSearchResponse, TargetStats,
    TargetBulkRequest, TargetBulkResponse
)
from app.database import get_db
from app.models.audit import AuditLog, AuditAction, AuditSeverity

# Configure logging
logger = logging.getLogger("reconvault.services.target")


class TargetService:
    """
    Target service for business logic and CRUD operations.
    
    Handles all target-related operations including creation,
    retrieval, updating, deletion, and search functionality.
    """
    
    def __init__(self, db: Session):
        """Initialize target service with database session"""
        self.db = db
    
    def create_target(self, target_data: TargetCreate, user_id: Optional[int] = None) -> TargetResponse:
        """
        Create a new target.
        
        Args:
            target_data: Target creation data
            user_id: ID of user creating the target
        
        Returns:
            TargetResponse: Created target data
        """
        try:
            # Create target
            db_target = Target(
                type=target_data.type,
                value=target_data.value,
                status=target_data.status,
                risk_score=target_data.risk_score,
                description=target_data.description,
                metadata=target_data.metadata
            )
            
            self.db.add(db_target)
            self.db.commit()
            self.db.refresh(db_target)
            
            # Log audit event
            self._log_audit_event(
                AuditAction.TARGET_CREATE,
                user_id,
                f"Created target: {target_data.value}",
                target_id=db_target.id
            )
            
            logger.info(f"Created target {db_target.id}: {target_data.value}")
            return TargetResponse.from_orm(db_target)
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to create target: {e}")
            raise
    
    def get_target(self, target_id: int) -> Optional[TargetResponse]:
        """
        Get target by ID.
        
        Args:
            target_id: Target database ID
        
        Returns:
            Optional[TargetResponse]: Target data or None if not found
        """
        try:
            db_target = self.db.query(Target).filter(Target.id == target_id).first()
            if db_target:
                return TargetResponse.from_orm(db_target)
            return None
        except Exception as e:
            logger.error(f"Failed to get target {target_id}: {e}")
            return None
    
    def get_targets(
        self,
        skip: int = 0,
        limit: int = 100,
        active_only: bool = True
    ) -> TargetListResponse:
        """
        Get list of targets with pagination.
        
        Args:
            skip: Number of targets to skip
            limit: Maximum number of targets to return
            active_only: Whether to return only active targets
        
        Returns:
            TargetListResponse: Paginated list of targets
        """
        try:
            query = self.db.query(Target)
            
            if active_only:
                query = query.filter(Target.is_active == True)
            
            total = query.count()
            targets = query.order_by(desc(Target.created_at)).offset(skip).limit(limit).all()
            
            return TargetListResponse(
                targets=[TargetResponse.from_orm(target) for target in targets],
                total=total,
                page=(skip // limit) + 1,
                per_page=limit,
                pages=(total + limit - 1) // limit
            )
            
        except Exception as e:
            logger.error(f"Failed to get targets: {e}")
            raise
    
    def update_target(
        self,
        target_id: int,
        target_data: TargetUpdate,
        user_id: Optional[int] = None
    ) -> Optional[TargetResponse]:
        """
        Update an existing target.
        
        Args:
            target_id: Target database ID
            target_data: Target update data
            user_id: ID of user updating the target
        
        Returns:
            Optional[TargetResponse]: Updated target data or None if not found
        """
        try:
            db_target = self.db.query(Target).filter(Target.id == target_id).first()
            if not db_target:
                return None
            
            # Update fields
            update_data = target_data.dict(exclude_unset=True)
            for field, value in update_data.items():
                setattr(db_target, field, value)
            
            self.db.commit()
            self.db.refresh(db_target)
            
            # Log audit event
            self._log_audit_event(
                AuditAction.TARGET_UPDATE,
                user_id,
                f"Updated target: {db_target.value}",
                target_id=db_target.id
            )
            
            logger.info(f"Updated target {target_id}")
            return TargetResponse.from_orm(db_target)
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to update target {target_id}: {e}")
            raise
    
    def delete_target(self, target_id: int, user_id: Optional[int] = None) -> bool:
        """
        Delete a target (soft delete by setting is_active to False).
        
        Args:
            target_id: Target database ID
            user_id: ID of user deleting the target
        
        Returns:
            bool: True if deletion successful
        """
        try:
            db_target = self.db.query(Target).filter(Target.id == target_id).first()
            if not db_target:
                return False
            
            # Soft delete
            db_target.is_active = False
            self.db.commit()
            
            # Log audit event
            self._log_audit_event(
                AuditAction.TARGET_DELETE,
                user_id,
                f"Deleted target: {db_target.value}",
                target_id=db_target.id
            )
            
            logger.info(f"Deleted target {target_id}")
            return True
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to delete target {target_id}: {e}")
            return False
    
    def search_targets(self, search_request: TargetSearchRequest) -> TargetSearchResponse:
        """
        Search targets based on criteria.
        
        Args:
            search_request: Search criteria
        
        Returns:
            TargetSearchResponse: Search results
        """
        try:
            query = self.db.query(Target)
            
            # Apply filters
            if search_request.query:
                search_term = f"%{search_request.query}%"
                query = query.filter(
                    or_(
                        Target.value.ilike(search_term),
                        Target.description.ilike(search_term)
                    )
                )
            
            if search_request.type:
                query = query.filter(Target.type == search_request.type)
            
            if search_request.status:
                query = query.filter(Target.status == search_request.status)
            
            if search_request.risk_level:
                # Convert risk level to score range
                risk_ranges = {
                    "critical": (0.8, 1.0),
                    "high": (0.6, 0.8),
                    "medium": (0.4, 0.6),
                    "low": (0.2, 0.4),
                    "minimal": (0.0, 0.2)
                }
                if search_request.risk_level in risk_ranges:
                    min_score, max_score = risk_ranges[search_request.risk_level]
                    query = query.filter(
                        and_(
                            Target.risk_score >= min_score,
                            Target.risk_score < max_score
                        )
                    )
            
            if search_request.created_after:
                query = query.filter(Target.created_at >= search_request.created_after)
            
            if search_request.created_before:
                query = query.filter(Target.created_at <= search_request.created_before)
            
            # Only active targets by default
            query = query.filter(Target.is_active == True)
            
            total = query.count()
            targets = query.order_by(desc(Target.risk_score)).offset(search_request.offset).limit(search_request.limit).all()
            
            return TargetSearchResponse(
                targets=[TargetResponse.from_orm(target) for target in targets],
                total=total,
                query=search_request.query,
                filters=search_request.dict(exclude_unset=True)
            )
            
        except Exception as e:
            logger.error(f"Failed to search targets: {e}")
            raise
    
    def get_target_statistics(self) -> TargetStats:
        """
        Get target statistics.
        
        Returns:
            TargetStats: Target statistics
        """
        try:
            # Get counts
            total_targets = self.db.query(Target).count()
            active_targets = self.db.query(Target).filter(Target.is_active == True).count()
            
            # Get type distribution
            type_counts = {}
            for target_type in TargetType:
                count = self.db.query(Target).filter(
                    and_(Target.type == target_type, Target.is_active == True)
                ).count()
                type_counts[target_type] = count
            
            # Get status distribution
            status_counts = {}
            for status in TargetStatus:
                count = self.db.query(Target).filter(
                    and_(Target.status == status, Target.is_active == True)
                ).count()
                status_counts[status] = count
            
            # Get risk level distribution
            risk_counts = {
                "critical": self.db.query(Target).filter(
                    and_(Target.risk_score >= 0.8, Target.is_active == True)
                ).count(),
                "high": self.db.query(Target).filter(
                    and_(Target.risk_score >= 0.6, Target.risk_score < 0.8, Target.is_active == True)
                ).count(),
                "medium": self.db.query(Target).filter(
                    and_(Target.risk_score >= 0.4, Target.risk_score < 0.6, Target.is_active == True)
                ).count(),
                "low": self.db.query(Target).filter(
                    and_(Target.risk_score >= 0.2, Target.risk_score < 0.4, Target.is_active == True)
                ).count(),
                "minimal": self.db.query(Target).filter(
                    and_(Target.risk_score < 0.2, Target.is_active == True)
                ).count()
            }
            
            # Calculate average risk score
            avg_risk = self.db.query(Target.risk_score).filter(Target.is_active == True).all()
            average_risk_score = sum([score[0] for score in avg_risk]) / len(avg_risk) if avg_risk else 0.0
            
            return TargetStats(
                total_targets=total_targets,
                active_targets=active_targets,
                targets_by_type=type_counts,
                targets_by_status=status_counts,
                targets_by_risk_level=risk_counts,
                average_risk_score=average_risk_score
            )
            
        except Exception as e:
            logger.error(f"Failed to get target statistics: {e}")
            raise
    
    def bulk_create_targets(
        self,
        bulk_request: TargetBulkRequest,
        user_id: Optional[int] = None
    ) -> TargetBulkResponse:
        """
        Create multiple targets in bulk.
        
        Args:
            bulk_request: Bulk target creation request
            user_id: ID of user performing the operation
        
        Returns:
            TargetBulkResponse: Results of bulk operation
        """
        try:
            created = []
            skipped = []
            failed = []
            
            for i, target_data in enumerate(bulk_request.targets):
                try:
                    # Check for duplicates
                    if bulk_request.skip_duplicates:
                        existing = self.db.query(Target).filter(
                            and_(
                                Target.value == target_data.value,
                                Target.type == target_data.type,
                                Target.is_active == True
                            )
                        ).first()
                        if existing:
                            skipped.append({
                                "index": i,
                                "reason": "duplicate",
                                "value": target_data.value
                            })
                            continue
                    
                    # Create target
                    db_target = Target(
                        type=target_data.type,
                        value=target_data.value,
                        status=target_data.status,
                        risk_score=target_data.risk_score,
                        description=target_data.description,
                        metadata=target_data.metadata
                    )
                    
                    self.db.add(db_target)
                    self.db.commit()
                    self.db.refresh(db_target)
                    
                    created.append(TargetResponse.from_orm(db_target))
                    
                except Exception as e:
                    self.db.rollback()
                    failed.append({
                        "index": i,
                        "reason": str(e),
                        "value": target_data.value
                    })
            
            # Log audit event
            self._log_audit_event(
                AuditAction.TARGET_CREATE,
                user_id,
                f"Bulk created {len(created)} targets, skipped {len(skipped)}, failed {len(failed)}"
            )
            
            logger.info(f"Bulk created {len(created)} targets")
            return TargetBulkResponse(created=created, skipped=skipped, failed=failed)
            
        except Exception as e:
            logger.error(f"Failed to bulk create targets: {e}")
            raise
    
    def _log_audit_event(
        self,
        action: AuditAction,
        user_id: Optional[int],
        description: str,
        target_id: Optional[int] = None,
        risk_score: float = 0.0
    ) -> None:
        """
        Log an audit event.
        
        Args:
            action: Audit action type
            user_id: User ID
            description: Event description
            target_id: Related target ID
            risk_score: Risk score for the event
        """
        try:
            audit_log = AuditLog.create_log(
                action=action,
                user_id=user_id,
                description=description,
                target_id=target_id,
                severity=AuditSeverity.INFO,
                risk_score=risk_score
            )
            
            self.db.add(audit_log)
            self.db.commit()
            
        except Exception as e:
            logger.error(f"Failed to log audit event: {e}")


def get_target_service(db: Session = None) -> TargetService:
    """
    Get target service instance.
    
    Args:
        db: Database session (optional)
    
    Returns:
        TargetService: Target service instance
    """
    if db is None:
        db = next(get_db())
    return TargetService(db)