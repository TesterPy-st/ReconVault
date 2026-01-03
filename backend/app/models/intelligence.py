"""
Intelligence findings model for ReconVault intelligence system.

This module defines the Intelligence SQLAlchemy model for storing
intelligence findings and analysis results.
"""

import enum
from typing import Optional

from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class IntelligenceType(str, enum.Enum):
    """Enumeration of intelligence finding types"""

    OSINT = "osint"
    THREAT_INTEL = "threat_intel"
    VULNERABILITY = "vulnerability"
    MALWARE_ANALYSIS = "malware_analysis"
    SOCIAL_ENGINEERING = "social_engineering"
    TECHNICAL_ANALYSIS = "technical_analysis"
    GEOGRAPHIC = "geographic"
    TEMPORAL = "temporal"
    BEHAVIORAL = "behavioral"
    ATTRIBUTION = "attribution"
    CAMPAIGN = "campaign"
    INDICATOR = "indicator"
    ENRICHMENT = "enrichment"


class IntelligencePriority(str, enum.Enum):
    """Enumeration of intelligence priority levels"""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class IntelligenceStatus(str, enum.Enum):
    """Enumeration of intelligence processing status"""

    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    REVIEWED = "reviewed"
    VERIFIED = "verified"


class Intelligence(Base):
    """
    Intelligence model representing findings and analysis results.

    Attributes:
        id (int): Primary key
        type (IntelligenceType): Type of intelligence finding
        priority (IntelligencePriority): Priority level
        title (str): Title of the intelligence finding
        description (str): Detailed description
        content (str): Intelligence content/analysis
        source (str): Source of intelligence
        confidence (float): Confidence score (0.0 to 1.0)
        target_id (int): Foreign key to associated target
        entity_id (int): Foreign key to associated entity
        priority_score (float): Calculated priority score
        status (IntelligenceStatus): Current processing status
        tags (str): Comma-separated tags
        metadata (str): JSON string for flexible metadata
        ioc_indicators (str): JSON string for IoC indicators
        recommendations (str): Action recommendations
        analyst_notes (str): Analyst notes and comments
        verified_by (str): Who verified this intelligence
        verified_at (datetime): When intelligence was verified
        created_at (datetime): Creation timestamp
        updated_at (datetime): Last update timestamp
        published_at (datetime): When intelligence was published
        is_active (bool): Whether intelligence is currently active
        is_public (bool): Whether intelligence is publicly accessible
    """

    __tablename__ = "intelligence"

    # Primary key
    id = Column(Integer, primary_key=True, index=True)

    # Intelligence identification
    type = Column(String(50), nullable=False, index=True)
    priority = Column(String(20), default=IntelligencePriority.MEDIUM, nullable=False, index=True)
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)
    content = Column(Text, nullable=False)

    # Source and confidence
    source = Column(String(100), nullable=False, index=True)
    confidence = Column(Float, default=1.0, nullable=False, index=True)

    # Relationships
    target_id = Column(Integer, ForeignKey("targets.id"), nullable=True, index=True)
    entity_id = Column(Integer, ForeignKey("entities.id"), nullable=True, index=True)

    # Assessment and status
    priority_score = Column(Float, default=0.0, nullable=False, index=True)
    status = Column(String(20), default=IntelligenceStatus.PENDING, nullable=False, index=True)

    # Categorization
    tags = Column(String(1000), nullable=True)  # Comma-separated tags
    metadata = Column(Text, nullable=True)  # JSON string for flexible metadata
    ioc_indicators = Column(Text, nullable=True)  # JSON string for IoC data

    # Recommendations and notes
    recommendations = Column(Text, nullable=True)
    analyst_notes = Column(Text, nullable=True)

    # Verification
    verified_by = Column(String(100), nullable=True)
    verified_at = Column(DateTime(timezone=True), nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
    published_at = Column(DateTime(timezone=True), nullable=True)

    # Status flags
    is_active = Column(Boolean, default=True, nullable=False)
    is_public = Column(Boolean, default=False, nullable=False)

    # Relationships
    target = relationship("Target")
    entity = relationship("Entity")

    def __repr__(self) -> str:
        """String representation of Intelligence instance"""
        return f"<Intelligence(id={self.id}, type='{self.type}', title='{self.title}', priority='{self.priority}')>"

    @property
    def risk_level(self) -> str:
        """
        Get human-readable risk level based on priority and confidence.

        Returns:
            str: Risk level category
        """
        effective_score = self.priority_score * self.confidence

        if effective_score >= 0.9:
            return "critical"
        elif effective_score >= 0.7:
            return "high"
        elif effective_score >= 0.5:
            return "medium"
        elif effective_score >= 0.3:
            return "low"
        else:
            return "minimal"

    @property
    def age_days(self) -> int:
        """
        Calculate age of intelligence in days.

        Returns:
            int: Age in days
        """
        from datetime import datetime, timezone

        return (datetime.now(timezone.utc) - self.created_at).days

    def calculate_priority_score(self) -> float:
        """
        Calculate priority score based on type, confidence, and other factors.

        Returns:
            float: Calculated priority score
        """
        base_score = self.confidence

        # Adjust based on type
        type_multipliers = {
            IntelligenceType.THREAT_INTEL: 1.5,
            IntelligenceType.MALWARE_ANALYSIS: 1.4,
            IntelligenceType.VULNERABILITY: 1.3,
            IntelligenceType.OSINT: 1.0,
            IntelligenceType.ATTRIBUTION: 1.2,
            IntelligenceType.CAMPAIGN: 1.3,
        }

        multiplier = type_multipliers.get(self.type, 1.0)
        adjusted_score = base_score * multiplier

        # Priority boost
        priority_boosts = {
            IntelligencePriority.CRITICAL: 1.5,
            IntelligencePriority.HIGH: 1.2,
            IntelligencePriority.MEDIUM: 1.0,
            IntelligencePriority.LOW: 0.8,
            IntelligencePriority.INFO: 0.6,
        }

        priority_multiplier = priority_boosts.get(self.priority, 1.0)
        final_score = adjusted_score * priority_multiplier

        return min(final_score, 1.0)  # Cap at 1.0

    def to_dict(self) -> dict:
        """
        Convert Intelligence instance to dictionary.

        Returns:
            dict: Dictionary representation of intelligence
        """
        return {
            "id": self.id,
            "type": self.type,
            "priority": self.priority,
            "title": self.title,
            "description": self.description,
            "content": self.content,
            "source": self.source,
            "confidence": self.confidence,
            "target_id": self.target_id,
            "entity_id": self.entity_id,
            "priority_score": self.priority_score,
            "status": self.status,
            "risk_level": self.risk_level,
            "age_days": self.age_days,
            "tags": self.tags,
            "metadata": self.metadata,
            "ioc_indicators": self.ioc_indicators,
            "recommendations": self.recommendations,
            "analyst_notes": self.analyst_notes,
            "verified_by": self.verified_by,
            "verified_at": self.verified_at.isoformat() if self.verified_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "published_at": self.published_at.isoformat() if self.published_at else None,
            "is_active": self.is_active,
            "is_public": self.is_public,
        }

    def add_tag(self, tag: str) -> None:
        """
        Add a tag to the intelligence.

        Args:
            tag (str): Tag to add
        """
        if not self.tags:
            self.tags = tag
        elif tag not in self.tags.split(","):
            self.tags = f"{self.tags},{tag}"

    def remove_tag(self, tag: str) -> None:
        """
        Remove a tag from the intelligence.

        Args:
            tag (str): Tag to remove
        """
        if self.tags and tag in self.tags:
            tags_list = [t.strip() for t in self.tags.split(",")]
            tags_list.remove(tag)
            self.tags = ",".join(tags_list)

    def get_tags(self) -> list:
        """
        Get list of tags for the intelligence.

        Returns:
            list: List of tags
        """
        if not self.tags:
            return []
        return [tag.strip() for tag in self.tags.split(",")]

    def verify(self, analyst: str) -> None:
        """
        Mark intelligence as verified.

        Args:
            analyst (str): Name of analyst verifying
        """
        from datetime import datetime, timezone

        self.verified_by = analyst
        self.verified_at = datetime.now(timezone.utc)
        self.status = IntelligenceStatus.VERIFIED
        self.updated_at = datetime.now(timezone.utc)


# Indexes for performance optimization
Intelligence.__table__.append_column(Column("idx_intelligence_type_priority", String(70), index=True))

Intelligence.__table__.append_column(Column("idx_intelligence_status", String(20), index=True))

Intelligence.__table__.append_column(Column("idx_intelligence_source", String(100), index=True))


class Anomaly(Base):
    """
    Anomaly model representing detected anomalies in OSINT data.

    Attributes:
        id (str): Primary key (UUID)
        entity_id (int): Foreign key to associated entity
        relationship_id (int): Foreign key to associated relationship (optional)
        anomaly_type (str): Type of anomaly (behavioral, relationship, infrastructure, etc.)
        anomaly_score (float): Anomaly score (0.0 to 1.0)
        confidence (float): Confidence in anomaly detection (0.0 to 1.0)
        severity (str): Severity level (low, medium, high, critical)
        explanation (str): JSON string with feature contributions (SHAP values)
        detection_method (str): Method used for detection (isolation_forest, lstm, rule_based)
        indicators (str): Comma-separated indicators
        description (str): Human-readable description
        recommendations (str): JSON string with recommended actions
        reviewed (bool): Whether anomaly has been reviewed by analyst
        review_notes (str): Analyst review notes
        reviewed_by (str): Analyst who reviewed
        reviewed_at (datetime): When anomaly was reviewed
        created_at (datetime): When anomaly was detected
        updated_at (datetime): Last update timestamp
        is_active (bool): Whether anomaly is currently active
    """

    __tablename__ = "anomalies"

    # Primary key
    id = Column(String(36), primary_key=True, index=True)

    # Foreign keys
    entity_id = Column(Integer, ForeignKey("entities.id"), nullable=True, index=True)
    relationship_id = Column(Integer, nullable=True, index=True)  # Optional relationship FK

    # Anomaly classification
    anomaly_type = Column(String(50), nullable=False, index=True)
    anomaly_score = Column(Float, nullable=False, index=True)
    confidence = Column(Float, default=0.0, nullable=False)
    severity = Column(String(20), nullable=False, index=True)

    # Detection details
    explanation = Column(Text, nullable=True)  # JSON string
    detection_method = Column(String(50), nullable=True)
    indicators = Column(String(500), nullable=True)  # Comma-separated
    description = Column(Text, nullable=True)
    recommendations = Column(Text, nullable=True)  # JSON string

    # Review status
    reviewed = Column(Boolean, default=False, nullable=False, index=True)
    review_notes = Column(Text, nullable=True)
    reviewed_by = Column(String(100), nullable=True)
    reviewed_at = Column(DateTime(timezone=True), nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # Status
    is_active = Column(Boolean, default=True, nullable=False)

    # Relationships
    entity = relationship("Entity")

    def __repr__(self) -> str:
        """String representation of Anomaly instance"""
        return f"<Anomaly(id={self.id}, type='{self.anomaly_type}', severity='{self.severity}', score={self.anomaly_score})>"

    def to_dict(self) -> dict:
        """
        Convert Anomaly instance to dictionary.

        Returns:
            dict: Dictionary representation of anomaly
        """
        import json

        # Parse JSON fields
        explanation_dict = {}
        if self.explanation:
            try:
                explanation_dict = json.loads(self.explanation)
            except json.JSONDecodeError:
                pass

        recommendations_list = []
        if self.recommendations:
            try:
                recommendations_list = json.loads(self.recommendations)
            except json.JSONDecodeError:
                pass

        return {
            "id": self.id,
            "entity_id": self.entity_id,
            "relationship_id": self.relationship_id,
            "anomaly_type": self.anomaly_type,
            "anomaly_score": self.anomaly_score,
            "confidence": self.confidence,
            "severity": self.severity,
            "explanation": explanation_dict,
            "detection_method": self.detection_method,
            "indicators": self.indicators.split(",") if self.indicators else [],
            "description": self.description,
            "recommendations": recommendations_list,
            "reviewed": self.reviewed,
            "review_notes": self.review_notes,
            "reviewed_by": self.reviewed_by,
            "reviewed_at": self.reviewed_at.isoformat() if self.reviewed_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "is_active": self.is_active,
        }

    def mark_reviewed(self, analyst: str, notes: Optional[str] = None) -> None:
        """
        Mark anomaly as reviewed.

        Args:
            analyst (str): Name of analyst
            notes (str): Optional review notes
        """
        from datetime import datetime, timezone

        self.reviewed = True
        self.reviewed_by = analyst
        self.reviewed_at = datetime.now(timezone.utc)
        if notes:
            self.review_notes = notes
        self.updated_at = datetime.now(timezone.utc)


class ComplianceViolation(Base):
    """
    Compliance violation model for tracking OSINT policy breaches.

    Attributes:
        id (str): Primary key (UUID)
        collection_id (str): Associated collection task ID
        entity_id (int): Foreign key to associated entity (optional)
        violation_type (str): Type of violation (rate_limit, robots_txt, policy, data_sensitivity)
        severity (str): Severity level (low, medium, high, critical)
        message (str): Human-readable violation message
        source (str): Source of violation (collector name, API)
        metadata (str): JSON string for flexible metadata
        resolved (bool): Whether violation has been resolved
        resolved_at (datetime): When violation was resolved
        resolution_notes (str): Notes on violation resolution
        created_at (datetime): Creation timestamp
    """

    __tablename__ = "compliance_violations"

    # Primary key
    id = Column(String(36), primary_key=True, index=True)

    # Identification
    collection_id = Column(String(36), index=True, nullable=True)
    entity_id = Column(Integer, ForeignKey("entities.id"), nullable=True, index=True)

    # Violation details
    violation_type = Column(String(50), nullable=False, index=True)
    severity = Column(String(20), nullable=False, index=True)
    message = Column(Text, nullable=False)
    source = Column(String(100), nullable=False, index=True)

    # Resolution and Metadata
    metadata = Column(Text, nullable=True)  # JSON string
    resolved = Column(Boolean, default=False, nullable=False, index=True)
    resolved_at = Column(DateTime(timezone=True), nullable=True)
    resolution_notes = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    entity = relationship("Entity")

    def __repr__(self) -> str:
        """String representation of ComplianceViolation instance"""
        return f"<ComplianceViolation(id={self.id}, type='{self.violation_type}', severity='{self.severity}', resolved={self.resolved})>"

    def to_dict(self) -> dict:
        """
        Convert ComplianceViolation instance to dictionary.

        Returns:
            dict: Dictionary representation of violation
        """
        import json

        metadata_dict = {}
        if self.metadata:
            try:
                metadata_dict = json.loads(self.metadata)
            except json.JSONDecodeError:
                pass

        return {
            "id": self.id,
            "collection_id": self.collection_id,
            "entity_id": self.entity_id,
            "violation_type": self.violation_type,
            "severity": self.severity,
            "message": self.message,
            "source": self.source,
            "metadata": metadata_dict,
            "resolved": self.resolved,
            "resolved_at": self.resolved_at.isoformat() if self.resolved_at else None,
            "resolution_notes": self.resolution_notes,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class ComplianceAuditTrail(Base):
    """
    Compliance audit trail model for tracking data handling actions.

    Attributes:
        id (str): Primary key (UUID)
        entity_id (int): Foreign key to associated entity (optional)
        action (str): Action performed (collected, accessed, exported, deleted)
        actor (str): System or user ID who performed action
        timestamp (datetime): When action occurred
        source (str): Collector name or API endpoint
        status (str): Outcome of action (success, warning, blocked)
        details (str): JSON string for additional details
        ip_address (str): IP address of actor
        user_agent (str): User agent of actor
    """

    __tablename__ = "compliance_audit_trail"

    # Primary key
    id = Column(String(36), primary_key=True, index=True)

    # Relationships
    entity_id = Column(Integer, ForeignKey("entities.id"), nullable=True, index=True)

    # Action details
    action = Column(String(50), nullable=False, index=True)
    actor = Column(String(100), nullable=False, index=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    source = Column(String(100), nullable=False, index=True)
    status = Column(String(20), nullable=False, index=True)

    # Additional info
    details = Column(Text, nullable=True)  # JSON string
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)

    # Relationships
    entity = relationship("Entity")

    def __repr__(self) -> str:
        """String representation of ComplianceAuditTrail instance"""
        return f"<ComplianceAuditTrail(id={self.id}, action='{self.action}', actor='{self.actor}', status='{self.status}')>"

    def to_dict(self) -> dict:
        """
        Convert ComplianceAuditTrail instance to dictionary.

        Returns:
            dict: Dictionary representation of audit trail entry
        """
        import json

        details_dict = {}
        if self.details:
            try:
                details_dict = json.loads(self.details)
            except json.JSONDecodeError:
                pass

        return {
            "id": self.id,
            "entity_id": self.entity_id,
            "action": self.action,
            "actor": self.actor,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "source": self.source,
            "status": self.status,
            "details": details_dict,
            "ip_address": self.ip_address,
            "user_agent": self.user_agent,
        }
