"""
Audit logging model for ReconVault intelligence system.

This module defines the AuditLog SQLAlchemy model for tracking
all system activities and changes for compliance and security.
"""

from sqlalchemy import Column, Integer, String, DateTime, Float, Text, ForeignKey, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base
import enum
from typing import Optional, Dict, Any


class AuditAction(str, enum.Enum):
    """Enumeration of audit action types"""
    # Authentication actions
    LOGIN = "login"
    LOGOUT = "logout"
    LOGIN_FAILED = "login_failed"
    PASSWORD_CHANGE = "password_change"
    PASSWORD_RESET = "password_reset"
    
    # User management actions
    USER_CREATE = "user_create"
    USER_UPDATE = "user_update"
    USER_DELETE = "user_delete"
    USER_ACTIVATE = "user_activate"
    USER_DEACTIVATE = "user_deactivate"
    USER_SUSPEND = "user_suspend"
    USER_VERIFY = "user_verify"
    
    # Target actions
    TARGET_CREATE = "target_create"
    TARGET_READ = "target_read"
    TARGET_UPDATE = "target_update"
    TARGET_DELETE = "target_delete"
    TARGET_EXPORT = "target_export"
    
    # Entity actions
    ENTITY_CREATE = "entity_create"
    ENTITY_READ = "entity_read"
    ENTITY_UPDATE = "entity_update"
    ENTITY_DELETE = "entity_delete"
    ENTITY_VERIFY = "entity_verify"
    
    # Relationship actions
    RELATIONSHIP_CREATE = "relationship_create"
    RELATIONSHIP_READ = "relationship_read"
    RELATIONSHIP_UPDATE = "relationship_update"
    RELATIONSHIP_DELETE = "relationship_delete"
    
    # Intelligence actions
    INTELLIGENCE_CREATE = "intelligence_create"
    INTELLIGENCE_READ = "intelligence_read"
    INTELLIGENCE_UPDATE = "intelligence_update"
    INTELLIGENCE_DELETE = "intelligence_delete"
    INTELLIGENCE_VERIFY = "intelligence_verify"
    INTELLIGENCE_PUBLISH = "intelligence_publish"
    
    # Graph actions
    GRAPH_SEARCH = "graph_search"
    GRAPH_EXPORT = "graph_export"
    GRAPH_ANALYSIS = "graph_analysis"
    GRAPH_IMPORT = "graph_import"
    
    # System actions
    SYSTEM_CONFIG = "system_config"
    SYSTEM_BACKUP = "system_backup"
    SYSTEM_RESTORE = "system_restore"
    SYSTEM_MAINTENANCE = "system_maintenance"
    SYSTEM_ERROR = "system_error"
    
    # API actions
    API_ACCESS = "api_access"
    API_RATE_LIMIT = "api_rate_limit"
    API_ERROR = "api_error"
    
    # Security actions
    SECURITY_ALERT = "security_alert"
    SECURITY_BREACH = "security_breach"
    PERMISSION_DENIED = "permission_denied"
    UNAUTHORIZED_ACCESS = "unauthorized_access"


class AuditSeverity(str, enum.Enum):
    """Enumeration of audit severity levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class AuditStatus(str, enum.Enum):
    """Enumeration of audit status values"""
    SUCCESS = "success"
    FAILED = "failed"
    PENDING = "pending"
    REVIEWED = "reviewed"


class AuditLog(Base):
    """
    Audit log model for tracking all system activities.
    
    Attributes:
        id (int): Primary key
        action (AuditAction): Type of action performed
        severity (AuditSeverity): Severity level of the action
        status (AuditStatus): Status of the action
        user_id (int): Foreign key to user who performed action
        target_id (int): Foreign key to related target
        entity_id (int): Foreign key to related entity
        resource_type (str): Type of resource affected
        resource_id (str): ID of resource affected
        description (str): Description of the action
        details (str): JSON string for additional action details
        ip_address (str): IP address of user
        user_agent (str): User agent string
        session_id (str): Session identifier
        request_id (str): Request identifier for tracing
        timestamp (datetime): When action occurred
        risk_score (float): Risk assessment score
        metadata (str): JSON string for additional metadata
        created_at (datetime): Creation timestamp
    """
    
    __tablename__ = "audit_logs"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Action information
    action = Column(String(50), nullable=False, index=True)
    severity = Column(String(20), default=AuditSeverity.INFO, nullable=False, index=True)
    status = Column(String(20), default=AuditStatus.SUCCESS, nullable=False, index=True)
    
    # User and resource identification
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    target_id = Column(Integer, ForeignKey("targets.id"), nullable=True, index=True)
    entity_id = Column(Integer, ForeignKey("entities.id"), nullable=True, index=True)
    
    # Resource details
    resource_type = Column(String(50), nullable=True, index=True)
    resource_id = Column(String(100), nullable=True)
    
    # Action description and details
    description = Column(Text, nullable=False)
    details = Column(Text, nullable=True)  # JSON string for additional details
    
    # Connection and request information
    ip_address = Column(String(45), nullable=True, index=True)  # IPv6 compatible
    user_agent = Column(Text, nullable=True)
    session_id = Column(String(100), nullable=True, index=True)
    request_id = Column(String(100), nullable=True, index=True)
    
    # Timestamp
    timestamp = Column(
        DateTime(timezone=True), 
        server_default=func.now(), 
        nullable=False,
        index=True
    )
    
    # Risk assessment
    risk_score = Column(Float, default=0.0, nullable=False, index=True)
    metadata = Column(Text, nullable=True)  # JSON string for additional metadata
    
    # Created at (for indexing purposes)
    created_at = Column(
        DateTime(timezone=True), 
        server_default=func.now(), 
        nullable=False
    )
    
    # Relationships
    user = relationship("User", back_populates="audit_logs")
    target = relationship("Target", back_populates="audit_logs")
    entity = relationship("Entity")
    
    def __repr__(self) -> str:
        """String representation of AuditLog instance"""
        return f"<AuditLog(id={self.id}, action='{self.action}', user_id={self.user_id}, status='{self.status}')>"
    
    @property
    def risk_level(self) -> str:
        """
        Get human-readable risk level based on risk_score.
        
        Returns:
            str: Risk level category
        """
        if self.risk_score >= 0.9:
            return "critical"
        elif self.risk_score >= 0.7:
            return "high"
        elif self.risk_score >= 0.5:
            return "medium"
        elif self.risk_score >= 0.3:
            return "low"
        else:
            return "minimal"
    
    def to_dict(self) -> dict:
        """
        Convert AuditLog instance to dictionary.
        
        Returns:
            dict: Dictionary representation of audit log
        """
        return {
            "id": self.id,
            "action": self.action,
            "severity": self.severity,
            "status": self.status,
            "user_id": self.user_id,
            "target_id": self.target_id,
            "entity_id": self.entity_id,
            "resource_type": self.resource_type,
            "resource_id": self.resource_id,
            "description": self.description,
            "details": self.details,
            "ip_address": self.ip_address,
            "user_agent": self.user_agent,
            "session_id": self.session_id,
            "request_id": self.request_id,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "risk_score": self.risk_score,
            "risk_level": self.risk_level,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
    
    @classmethod
    def create_log(
        cls,
        action: AuditAction,
        user_id: Optional[int] = None,
        description: Optional[str] = None,
        severity: AuditSeverity = AuditSeverity.INFO,
        status: AuditStatus = AuditStatus.SUCCESS,
        target_id: Optional[int] = None,
        entity_id: Optional[int] = None,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        details: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        session_id: Optional[str] = None,
        request_id: Optional[str] = None,
        risk_score: float = 0.0,
        metadata: Optional[str] = None
    ) -> "AuditLog":
        """
        Create a new audit log entry.
        
        Args:
            action: Type of action performed
            user_id: ID of user performing action
            description: Description of the action
            severity: Severity level
            status: Action status
            target_id: Related target ID
            entity_id: Related entity ID
            resource_type: Type of resource affected
            resource_id: ID of resource affected
            details: Additional action details
            ip_address: User IP address
            user_agent: User agent string
            session_id: Session identifier
            request_id: Request identifier
            risk_score: Risk assessment score
            metadata: Additional metadata
        
        Returns:
            AuditLog: New audit log instance
        """
        return cls(
            action=action,
            severity=severity,
            status=status,
            user_id=user_id,
            target_id=target_id,
            entity_id=entity_id,
            resource_type=resource_type,
            resource_id=resource_id,
            description=description or action,
            details=details,
            ip_address=ip_address,
            user_agent=user_agent,
            session_id=session_id,
            request_id=request_id,
            risk_score=risk_score,
            metadata=metadata
        )
    
    def is_security_related(self) -> bool:
        """
        Check if this audit log is security-related.
        
        Returns:
            bool: True if security-related
        """
        security_actions = [
            AuditAction.LOGIN_FAILED,
            AuditAction.UNAUTHORIZED_ACCESS,
            AuditAction.PERMISSION_DENIED,
            AuditAction.SECURITY_ALERT,
            AuditAction.SECURITY_BREACH
        ]
        
        return (self.action in security_actions or 
                self.severity in [AuditSeverity.CRITICAL, AuditSeverity.HIGH] or
                self.risk_score >= 0.7)
    
    def requires_review(self) -> bool:
        """
        Check if this audit log requires review.
        
        Returns:
            bool: True if requires review
        """
        return (self.severity in [AuditSeverity.CRITICAL, AuditSeverity.HIGH] or
                self.status == AuditStatus.FAILED or
                self.is_security_related() or
                self.risk_score >= 0.6)


# Indexes for performance optimization
AuditLog.__table__.append_column(
    Column("idx_audit_action_timestamp", String(100), index=True)
)

AuditLog.__table__.append_column(
    Column("idx_audit_user_timestamp", String(100), index=True)
)

AuditLog.__table__.append_column(
    Column("idx_audit_severity_status", String(40), index=True)
)