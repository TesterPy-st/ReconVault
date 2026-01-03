"""
Collection Result model for ReconVault intelligence system.

This module defines the CollectionResult SQLAlchemy model for storing
OSINT collection results.
"""

from sqlalchemy import Column, DateTime, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base
import uuid


class CollectionResult(Base):
    """
    CollectionResult model representing OSINT collection results.
    
    Attributes:
        id (UUID): Primary key
        task_id (UUID): Foreign key to collection task
        entity_id (UUID): Foreign key to discovered entity
        raw_data (dict): Raw collection data
        processed_at (datetime): Processing timestamp
        created_at (datetime): Creation timestamp
    """
    
    __tablename__ = "collection_results"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    
    # Foreign keys
    task_id = Column(UUID(as_uuid=True), ForeignKey("collection_tasks.id", ondelete="CASCADE"), nullable=False, index=True)
    entity_id = Column(UUID(as_uuid=True), ForeignKey("entities.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Result data
    raw_data = Column(JSON, nullable=False)
    
    # Timestamps
    processed_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    
    # Relationships
    task = relationship("CollectionTask", back_populates="results")
    entity = relationship("Entity")
    
    def __repr__(self) -> str:
        """String representation of CollectionResult instance"""
        return f"<CollectionResult(id={self.id}, task_id={self.task_id}, entity_id={self.entity_id})>"
    
    def to_dict(self) -> dict:
        """
        Convert CollectionResult instance to dictionary.
        
        Returns:
            dict: Dictionary representation of collection result
        """
        return {
            "id": str(self.id),
            "task_id": str(self.task_id),
            "entity_id": str(self.entity_id),
            "raw_data": self.raw_data,
            "processed_at": self.processed_at.isoformat() if self.processed_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
