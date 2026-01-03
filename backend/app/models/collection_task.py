"""
Collection Task model for ReconVault intelligence system.

This module defines the CollectionTask SQLAlchemy model for storing
OSINT collection task information.
"""

from sqlalchemy import Column, String, DateTime, Integer, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base
import uuid


class CollectionTask(Base):
    """
    CollectionTask model representing OSINT collection tasks.
    
    Attributes:
        id (UUID): Primary key
        target (str): Collection target
        collection_type (str): Type of collection
        status (str): Task status
        started_at (datetime): Task start timestamp
        completed_at (datetime): Task completion timestamp
        result_count (int): Number of results collected
        error_message (str): Error message if failed
        created_at (datetime): Creation timestamp
        updated_at (datetime): Last update timestamp
    """
    
    __tablename__ = "collection_tasks"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    
    # Task information
    target = Column(String(500), nullable=False, index=True)
    collection_type = Column(String(100), nullable=False, index=True)
    status = Column(String(50), nullable=False, default="pending", index=True)
    
    # Timestamps
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )
    
    # Results and error handling
    result_count = Column(Integer, default=0, nullable=False)
    error_message = Column(Text, nullable=True)
    
    # Relationships
    results = relationship(
        "CollectionResult",
        back_populates="task",
        cascade="all, delete-orphan"
    )
    
    def __repr__(self) -> str:
        """String representation of CollectionTask instance"""
        return f"<CollectionTask(id={self.id}, target='{self.target}', type='{self.collection_type}', status='{self.status}')>"
    
    def to_dict(self) -> dict:
        """
        Convert CollectionTask instance to dictionary.
        
        Returns:
            dict: Dictionary representation of collection task
        """
        return {
            "id": str(self.id),
            "target": self.target,
            "collection_type": self.collection_type,
            "status": self.status,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "result_count": self.result_count,
            "error_message": self.error_message,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
