"""
Audit API routes for ReconVault.

This module provides REST API endpoints for audit logging
and compliance monitoring.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_, or_
from typing import List, Optional
import logging
from datetime import datetime, timezone

from app.database import get_db
from app.models.audit import AuditLog, AuditAction, AuditSeverity, AuditStatus
from app.models.user import User
from pydantic import BaseModel

# Configure logging
logger = logging.getLogger("reconvault.api.audit")

# Create router
router = APIRouter()


class AuditLogResponse(BaseModel):
    """Schema for audit log responses"""
    id: int
    action: str
    severity: str
    status: str
    user_id: Optional[int]
    target_id: Optional[int]
    entity_id: Optional[int]
    resource_type: Optional[str]
    resource_id: Optional[str]
    description: str
    ip_address: Optional[str]
    timestamp: datetime
    risk_score: float
    risk_level: str
    
    class Config:
        orm_mode = True


class AuditStats(BaseModel):
    """Schema for audit statistics"""
    total_logs: int
    logs_by_action: dict
    logs_by_severity: dict
    logs_by_status: dict
    recent_activity: int
    security_events: int
    failed_events: int


@router.get("/logs", response_model=List[AuditLogResponse])
async def get_audit_logs(
    skip: int = Query(0, ge=0, description="Number of logs to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of logs to return"),
    action: Optional[str] = Query(None, description="Filter by action type"),
    severity: Optional[str] = Query(None, description="Filter by severity"),
    status: Optional[str] = Query(None, description="Filter by status"),
    user_id: Optional[int] = Query(None, description="Filter by user ID"),
    target_id: Optional[int] = Query(None, description="Filter by target ID"),
    start_date: Optional[datetime] = Query(None, description="Filter by start date"),
    end_date: Optional[datetime] = Query(None, description="Filter by end date"),
    db: Session = Depends(get_db)
):
    """
    Get audit logs with filtering and pagination.
    
    Args:
        skip: Number of logs to skip
        limit: Maximum number of logs to return
        action: Filter by action type
        severity: Filter by severity
        status: Filter by status
        user_id: Filter by user ID
        target_id: Filter by target ID
        start_date: Filter by start date
        end_date: Filter by end date
        db: Database session
    
    Returns:
        List[AuditLogResponse]: List of audit logs
    """
    try:
        query = db.query(AuditLog)
        
        # Apply filters
        if action:
            query = query.filter(AuditLog.action == action)
        
        if severity:
            query = query.filter(AuditLog.severity == severity)
        
        if status:
            query = query.filter(AuditLog.status == status)
        
        if user_id:
            query = query.filter(AuditLog.user_id == user_id)
        
        if target_id:
            query = query.filter(AuditLog.target_id == target_id)
        
        if start_date:
            query = query.filter(AuditLog.timestamp >= start_date)
        
        if end_date:
            query = query.filter(AuditLog.timestamp <= end_date)
        
        # Order by timestamp descending
        query = query.order_by(desc(AuditLog.timestamp))
        
        # Apply pagination
        logs = query.offset(skip).limit(limit).all()
        
        # Convert to response format
        result = []
        for log in logs:
            result.append(AuditLogResponse(
                id=log.id,
                action=log.action,
                severity=log.severity,
                status=log.status,
                user_id=log.user_id,
                target_id=log.target_id,
                entity_id=log.entity_id,
                resource_type=log.resource_type,
                resource_id=log.resource_id,
                description=log.description,
                ip_address=log.ip_address,
                timestamp=log.timestamp,
                risk_score=log.risk_score,
                risk_level=log.risk_level
            ))
        
        return result
        
    except Exception as e:
        logger.error(f"Failed to get audit logs: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get audit logs: {str(e)}"
        )


@router.get("/logs/statistics", response_model=AuditStats)
async def get_audit_statistics(db: Session = Depends(get_db)):
    """
    Get audit log statistics.
    
    Args:
        db: Database session
    
    Returns:
        AuditStats: Audit statistics
    """
    try:
        # Get total logs count
        total_logs = db.query(AuditLog).count()
        
        # Get logs by action
        action_counts = {}
        actions = db.query(AuditLog.action).distinct().all()
        for action_tuple in actions:
            action = action_tuple[0]
            count = db.query(AuditLog).filter(AuditLog.action == action).count()
            action_counts[action] = count
        
        # Get logs by severity
        severity_counts = {}
        severities = db.query(AuditLog.severity).distinct().all()
        for severity_tuple in severities:
            severity = severity_tuple[0]
            count = db.query(AuditLog).filter(AuditLog.severity == severity).count()
            severity_counts[severity] = count
        
        # Get logs by status
        status_counts = {}
        statuses = db.query(AuditLog.status).distinct().all()
        for status_tuple in statuses:
            status = status_tuple[0]
            count = db.query(AuditLog).filter(AuditLog.status == status).count()
            status_counts[status] = count
        
        # Get recent activity (last 24 hours)
        yesterday = datetime.now(timezone.utc)
        yesterday = yesterday.replace(day=yesterday.day - 1)
        recent_activity = db.query(AuditLog).filter(
            AuditLog.timestamp >= yesterday
        ).count()
        
        # Get security events (high/critical severity)
        security_events = db.query(AuditLog).filter(
            AuditLog.severity.in_([AuditSeverity.HIGH, AuditSeverity.CRITICAL])
        ).count()
        
        # Get failed events
        failed_events = db.query(AuditLog).filter(
            AuditLog.status == AuditStatus.FAILED
        ).count()
        
        return AuditStats(
            total_logs=total_logs,
            logs_by_action=action_counts,
            logs_by_severity=severity_counts,
            logs_by_status=status_counts,
            recent_activity=recent_activity,
            security_events=security_events,
            failed_events=failed_events
        )
        
    except Exception as e:
        logger.error(f"Failed to get audit statistics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get audit statistics: {str(e)}"
        )


@router.get("/logs/security", response_model=List[AuditLogResponse])
async def get_security_events(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """
    Get security-related audit events.
    
    Args:
        skip: Number of logs to skip
        limit: Maximum number of logs to return
        db: Database session
    
    Returns:
        List[AuditLogResponse]: Security events
    """
    try:
        # Get security events (high/critical severity or specific security actions)
        security_actions = [
            AuditAction.LOGIN_FAILED,
            AuditAction.UNAUTHORIZED_ACCESS,
            AuditAction.PERMISSION_DENIED,
            AuditAction.SECURITY_ALERT,
            AuditAction.SECURITY_BREACH
        ]
        
        query = db.query(AuditLog).filter(
            or_(
                AuditLog.severity.in_([AuditSeverity.HIGH, AuditSeverity.CRITICAL]),
                AuditLog.action.in_(security_actions),
                AuditLog.risk_score >= 0.7
            )
        ).order_by(desc(AuditLog.timestamp))
        
        logs = query.offset(skip).limit(limit).all()
        
        # Convert to response format
        result = []
        for log in logs:
            result.append(AuditLogResponse(
                id=log.id,
                action=log.action,
                severity=log.severity,
                status=log.status,
                user_id=log.user_id,
                target_id=log.target_id,
                entity_id=log.entity_id,
                resource_type=log.resource_type,
                resource_id=log.resource_id,
                description=log.description,
                ip_address=log.ip_address,
                timestamp=log.timestamp,
                risk_score=log.risk_score,
                risk_level=log.risk_level
            ))
        
        return result
        
    except Exception as e:
        logger.error(f"Failed to get security events: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get security events: {str(e)}"
        )


@router.get("/logs/user/{user_id}", response_model=List[AuditLogResponse])
async def get_user_audit_logs(
    user_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """
    Get audit logs for a specific user.
    
    Args:
        user_id: User ID
        skip: Number of logs to skip
        limit: Maximum number of logs to return
        db: Database session
    
    Returns:
        List[AuditLogResponse]: User audit logs
    """
    try:
        logs = db.query(AuditLog).filter(
            AuditLog.user_id == user_id
        ).order_by(desc(AuditLog.timestamp)).offset(skip).limit(limit).all()
        
        # Convert to response format
        result = []
        for log in logs:
            result.append(AuditLogResponse(
                id=log.id,
                action=log.action,
                severity=log.severity,
                status=log.status,
                user_id=log.user_id,
                target_id=log.target_id,
                entity_id=log.entity_id,
                resource_type=log.resource_type,
                resource_id=log.resource_id,
                description=log.description,
                ip_address=log.ip_address,
                timestamp=log.timestamp,
                risk_score=log.risk_score,
                risk_level=log.risk_level
            ))
        
        return result
        
    except Exception as e:
        logger.error(f"Failed to get user audit logs: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get user audit logs: {str(e)}"
        )


@router.get("/logs/target/{target_id}", response_model=List[AuditLogResponse])
async def get_target_audit_logs(
    target_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """
    Get audit logs for a specific target.
    
    Args:
        target_id: Target ID
        skip: Number of logs to skip
        limit: Maximum number of logs to return
        db: Database session
    
    Returns:
        List[AuditLogResponse]: Target audit logs
    """
    try:
        logs = db.query(AuditLog).filter(
            AuditLog.target_id == target_id
        ).order_by(desc(AuditLog.timestamp)).offset(skip).limit(limit).all()
        
        # Convert to response format
        result = []
        for log in logs:
            result.append(AuditLogResponse(
                id=log.id,
                action=log.action,
                severity=log.severity,
                status=log.status,
                user_id=log.user_id,
                target_id=log.target_id,
                entity_id=log.entity_id,
                resource_type=log.resource_type,
                resource_id=log.resource_id,
                description=log.description,
                ip_address=log.ip_address,
                timestamp=log.timestamp,
                risk_score=log.risk_score,
                risk_level=log.risk_level
            ))
        
        return result
        
    except Exception as e:
        logger.error(f"Failed to get target audit logs: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get target audit logs: {str(e)}"
        )


@router.post("/logs/export", response_model=dict)
async def export_audit_logs(
    start_date: Optional[datetime] = Query(None, description="Export from date"),
    end_date: Optional[datetime] = Query(None, description="Export to date"),
    action: Optional[str] = Query(None, description="Filter by action"),
    severity: Optional[str] = Query(None, description="Filter by severity"),
    format: str = Query("json", description="Export format"),
    db: Session = Depends(get_db)
):
    """
    Export audit logs.
    
    Args:
        start_date: Export from date
        end_date: Export to date
        action: Filter by action
        severity: Filter by severity
        format: Export format
        db: Database session
    
    Returns:
        dict: Export result
    """
    try:
        query = db.query(AuditLog)
        
        # Apply filters
        if start_date:
            query = query.filter(AuditLog.timestamp >= start_date)
        
        if end_date:
            query = query.filter(AuditLog.timestamp <= end_date)
        
        if action:
            query = query.filter(AuditLog.action == action)
        
        if severity:
            query = query.filter(AuditLog.severity == severity)
        
        logs = query.order_by(desc(AuditLog.timestamp)).all()
        
        # Generate export data
        export_data = {
            "export_id": f"audit_export_{datetime.now().timestamp()}",
            "format": format,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "total_records": len(logs),
            "filters": {
                "start_date": start_date.isoformat() if start_date else None,
                "end_date": end_date.isoformat() if end_date else None,
                "action": action,
                "severity": severity
            },
            "data": [log.to_dict() for log in logs]
        }
        
        # In a real implementation, this would save to file and return download URL
        download_url = f"/api/audit/export/download/{export_data['export_id']}"
        
        return {
            "export_id": export_data["export_id"],
            "status": "completed",
            "download_url": download_url,
            "total_records": len(logs),
            "expires_at": (datetime.now(timezone.utc)).isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to export audit logs: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to export audit logs: {str(e)}"
        )


@router.get("/logs/activity-summary", response_model=dict)
async def get_activity_summary(
    days: int = Query(30, ge=1, le=365, description="Number of days to analyze"),
    db: Session = Depends(get_db)
):
    """
    Get activity summary for the last N days.
    
    Args:
        days: Number of days to analyze
        db: Database session
    
    Returns:
        dict: Activity summary
    """
    try:
        from datetime import timedelta
        
        start_date = datetime.now(timezone.utc) - timedelta(days=days)
        
        # Get logs in the time period
        logs = db.query(AuditLog).filter(
            AuditLog.timestamp >= start_date
        ).all()
        
        # Analyze activity
        daily_activity = {}
        top_actions = {}
        top_users = {}
        risk_distribution = {"critical": 0, "high": 0, "medium": 0, "low": 0, "minimal": 0}
        
        for log in logs:
            # Daily activity
            day_key = log.timestamp.date().isoformat()
            daily_activity[day_key] = daily_activity.get(day_key, 0) + 1
            
            # Top actions
            top_actions[log.action] = top_actions.get(log.action, 0) + 1
            
            # Top users
            if log.user_id:
                top_users[str(log.user_id)] = top_users.get(str(log.user_id), 0) + 1
            
            # Risk distribution
            risk_distribution[log.risk_level] += 1
        
        # Sort top items
        top_actions = dict(sorted(top_actions.items(), key=lambda x: x[1], reverse=True)[:10])
        top_users = dict(sorted(top_users.items(), key=lambda x: x[1], reverse=True)[:10])
        
        return {
            "period_days": days,
            "total_events": len(logs),
            "daily_activity": daily_activity,
            "top_actions": top_actions,
            "top_users": top_users,
            "risk_distribution": risk_distribution,
            "generated_at": datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to get activity summary: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get activity summary: {str(e)}"
        )