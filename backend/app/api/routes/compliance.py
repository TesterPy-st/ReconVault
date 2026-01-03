"""
Compliance API Routes

Endpoints for monitoring ethics compliance, violations, and audit trails.
"""

import logging
from datetime import datetime, timedelta
from typing import Any, Dict, Optional

from fastapi import APIRouter, Body, Depends, HTTPException, Query
from sqlalchemy import desc, func
from sqlalchemy.orm import Session

from app.database import get_db
from app.ethics.osint_compliance import OSINTCompliance
from app.models.intelligence import ComplianceAuditTrail, ComplianceViolation

# Configure logging
logger = logging.getLogger("reconvault.api.compliance")

router = APIRouter()
compliance_checker = OSINTCompliance()


@router.get("/status")
async def get_compliance_status(db: Session = Depends(get_db)):
    """
    Get current compliance status and summary metrics.
    """
    try:
        total_violations = db.query(ComplianceViolation).count()
        unresolved_violations = db.query(ComplianceViolation).filter(ComplianceViolation.resolved.is_(False)).count()
        critical_violations = (
            db.query(ComplianceViolation)
            .filter(ComplianceViolation.resolved.is_(False), ComplianceViolation.severity == "critical")
            .count()
        )

        status_val = "green"
        if critical_violations > 0:
            status_val = "red"
        elif unresolved_violations > 0:
            status_val = "warning"

        # Calculate compliance score (0-100)
        # Baseline 100, deduct for unresolved violations
        compliance_score = 100.0
        if total_violations > 0:
            deduction = (unresolved_violations * 2) + (critical_violations * 10)
            compliance_score = max(0, 100 - deduction)

        last_violation = db.query(ComplianceViolation).order_by(desc(ComplianceViolation.created_at)).first()

        return {
            "status": status_val,
            "total_violations": total_violations,
            "unresolved_violations": unresolved_violations,
            "critical_violations": critical_violations,
            "compliance_score": compliance_score,
            "last_violation": last_violation.created_at.isoformat() if last_violation else None,
            "violations": [
                v.to_dict()
                for v in db.query(ComplianceViolation).order_by(desc(ComplianceViolation.created_at)).limit(5).all()
            ],
        }
    except Exception as e:
        logger.error(f"Failed to get compliance status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/violations")
async def list_violations(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    resolved: Optional[bool] = None,
    severity: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """
    List all compliance violations with filtering and pagination.
    """
    try:
        query = db.query(ComplianceViolation)
        if resolved is not None:
            query = query.filter(ComplianceViolation.resolved == resolved)
        if severity:
            query = query.filter(ComplianceViolation.severity == severity)

        total = query.count()
        violations = query.order_by(desc(ComplianceViolation.created_at)).offset(skip).limit(limit).all()

        return {"total": total, "violations": [v.to_dict() for v in violations]}
    except Exception as e:
        logger.error(f"Failed to list violations: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/violations/{collection_id}")
async def get_collection_violations(collection_id: str, db: Session = Depends(get_db)):
    """
    Get violations associated with a specific collection.
    """
    try:
        violations = db.query(ComplianceViolation).filter(ComplianceViolation.collection_id == collection_id).all()
        return [v.to_dict() for v in violations]
    except Exception as e:
        logger.error(f"Failed to get collection violations: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/check")
async def check_compliance(target: str = Body(..., embed=True), action_type: str = Body("collection", embed=True)):
    """
    Check if a proposed action is compliant with current policies.
    """
    try:
        verdict = await compliance_checker.get_ethical_verdict(target, action_type)
        return verdict
    except Exception as e:
        logger.error(f"Failed to check compliance: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/audit-trail")
async def get_audit_trail(
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    """
    Get compliance audit trail with date filtering and pagination.
    """
    try:
        query = db.query(ComplianceAuditTrail)
        if start_date:
            query = query.filter(ComplianceAuditTrail.timestamp >= start_date)
        if end_date:
            query = query.filter(ComplianceAuditTrail.timestamp <= end_date)

        total = query.count()
        trail = query.order_by(desc(ComplianceAuditTrail.timestamp)).offset(skip).limit(limit).all()

        return {"total": total, "trail": [t.to_dict() for t in trail]}
    except Exception as e:
        logger.error(f"Failed to get audit trail: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/audit-trail/{entity_id}")
async def get_entity_audit_trail(entity_id: int, db: Session = Depends(get_db)):
    """
    Get audit trail for a specific entity.
    """
    try:
        trail = (
            db.query(ComplianceAuditTrail)
            .filter(ComplianceAuditTrail.entity_id == entity_id)
            .order_by(desc(ComplianceAuditTrail.timestamp))
            .all()
        )
        return [t.to_dict() for t in trail]
    except Exception as e:
        logger.error(f"Failed to get entity audit trail: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/report")
async def generate_compliance_report(days: int = Query(30, ge=1, le=365), db: Session = Depends(get_db)):
    """
    Generate a summary compliance report for the specified period.
    """
    try:
        start_date = datetime.utcnow() - timedelta(days=days)

        violations = db.query(ComplianceViolation).filter(ComplianceViolation.created_at >= start_date).all()
        audit_count = db.query(ComplianceAuditTrail).filter(ComplianceAuditTrail.timestamp >= start_date).count()

        severity_counts = {}
        type_counts = {}
        for v in violations:
            severity_counts[v.severity] = severity_counts.get(v.severity, 0) + 1
            type_counts[v.violation_type] = type_counts.get(v.violation_type, 0) + 1

        return {
            "report_period_days": days,
            "generated_at": datetime.utcnow().isoformat(),
            "total_violations": len(violations),
            "total_audit_events": audit_count,
            "severity_breakdown": severity_counts,
            "type_breakdown": type_counts,
            "compliance_status": "PASS" if len(violations) < 10 else "REVIEW_REQUIRED",
        }
    except Exception as e:
        logger.error(f"Failed to generate report: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/policy")
async def get_policies():
    """
    Retrieve current ethics and compliance policies.
    """
    return {
        "rate_limits": compliance_checker.default_rate_limits,
        "blocked_domains": compliance_checker.blocked_domains,
        "user_agents_count": len(compliance_checker.user_agents),
        "pii_detection": ["ssn", "credit_card", "phone", "password", "api_key"],
    }


@router.post("/policy")
async def update_policies(policy_update: Dict[str, Any] = Body(...)):
    """
    Update compliance policies (Admin only).
    """
    # Note: In a real app, check for admin role here
    if "rate_limits" in policy_update:
        compliance_checker.default_rate_limits.update(policy_update["rate_limits"])
    if "blocked_domains" in policy_update:
        compliance_checker.blocked_domains = policy_update["blocked_domains"]

    return {"status": "success", "message": "Policy updated", "current_policy": policy_update}


@router.get("/stats")
async def get_compliance_stats(db: Session = Depends(get_db)):
    """
    Get compliance statistics and metrics.
    """
    try:
        # General counts
        total_violations = db.query(ComplianceViolation).count()
        unresolved = db.query(ComplianceViolation).filter(ComplianceViolation.resolved.is_(False)).count()

        # Severity breakdown
        severity_stats = (
            db.query(ComplianceViolation.severity, func.count(ComplianceViolation.id))
            .group_by(ComplianceViolation.severity)
            .all()
        )

        # Type breakdown
        type_stats = (
            db.query(ComplianceViolation.violation_type, func.count(ComplianceViolation.id))
            .group_by(ComplianceViolation.violation_type)
            .all()
        )

        # Trend (last 7 days)
        seven_days_ago = datetime.utcnow() - timedelta(days=7)
        trend = (
            db.query(
                func.date(ComplianceViolation.created_at).label("date"),
                func.count(ComplianceViolation.id).label("count"),
            )
            .filter(ComplianceViolation.created_at >= seven_days_ago)
            .group_by("date")
            .all()
        )

        return {
            "total_violations": total_violations,
            "unresolved_violations": unresolved,
            "severity_breakdown": dict(severity_stats),
            "type_breakdown": dict(type_stats),
            "trend": [{"date": str(t[0]), "count": t[1]} for t in trend],
            "compliance_score": 92.5,  # Placeholder for complex calculation
        }
    except Exception as e:
        logger.error(f"Failed to get stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/violations/{violation_id}")
async def resolve_violation(violation_id: str, notes: Dict[str, str] = Body(None), db: Session = Depends(get_db)):
    """
    Resolve a specific compliance violation.
    """
    try:
        violation = db.query(ComplianceViolation).filter(ComplianceViolation.id == violation_id).first()
        if not violation:
            raise HTTPException(status_code=404, detail="Violation not found")

        violation.resolved = True
        violation.resolved_at = datetime.utcnow()
        if notes and "notes" in notes:
            violation.resolution_notes = notes["notes"]

        db.commit()
        return {"status": "success", "message": f"Violation {violation_id} resolved"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to resolve violation: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
