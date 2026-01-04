"""
Reports API Routes

Endpoints for generating and managing intelligence reports.
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Body, Depends, HTTPException, Query
from fastapi.responses import FileResponse, Response
from sqlalchemy.orm import Session
from enum import Enum

from app.database import get_db
from app.models.intelligence import Entity, Relationship, Target
from app.services.report_service import ReportService

# Configure logging
logger = logging.getLogger("reconvault.api.reports")

router = APIRouter()
report_service = ReportService()


class ReportFormat(str, Enum):
    """Supported report formats."""
    JSON = "json"
    CSV = "csv"
    HTML = "html"
    PDF = "pdf"
    GRAPHML = "graphml"
    GEXF = "gexf"


class ReportTemplate(str, Enum):
    """Available report templates."""
    EXECUTIVE_SUMMARY = "executive_summary"
    DETAILED_ANALYSIS = "detailed_analysis"
    RISK_ASSESSMENT = "risk_assessment"
    COMPLIANCE_REPORT = "compliance_report"
    CUSTOM = "custom"


@router.post("/generate")
async def generate_report(
    format: ReportFormat = Query(..., description="Output format"),
    template: ReportTemplate = Query(ReportTemplate.DETAILED_ANALYSIS, description="Report template"),
    target_id: Optional[int] = Query(None, description="Filter by target ID"),
    include_entities: bool = Query(True, description="Include entities"),
    include_relationships: bool = Query(True, description="Include relationships"),
    include_risk_analysis: bool = Query(True, description="Include risk analysis"),
    filters: Dict[str, Any] = Body(default={}, description="Custom filters"),
    db: Session = Depends(get_db)
):
    """
    Generate a new intelligence report.

    Args:
        format: Output format (json, csv, html, pdf, graphml, gexf)
        template: Report template to use
        target_id: Optional target ID to filter
        include_entities: Whether to include entity data
        include_relationships: Whether to include relationship data
        include_risk_analysis: Whether to include risk analysis
        filters: Additional custom filters
        db: Database session

    Returns:
        Report data or file download
    """
    try:
        logger.info(f"Generating {format.value} report with template {template.value}")

        # Build query filters
        query_filters = {}
        if target_id:
            query_filters["target_id"] = target_id
        query_filters.update(filters)

        # Generate report based on format
        if format == ReportFormat.JSON:
            report_data = await report_service.generate_json_report(
                db=db,
                filters=query_filters,
                template=template.value,
                include_entities=include_entities,
                include_relationships=include_relationships,
                include_risk_analysis=include_risk_analysis
            )
            return {
                "status": "success",
                "format": format.value,
                "template": template.value,
                "generated_at": datetime.utcnow().isoformat(),
                "data": report_data
            }

        elif format in [ReportFormat.CSV, ReportFormat.GRAPHML, ReportFormat.GEXF]:
            # Generate file
            file_path = await report_service.generate_file_report(
                db=db,
                format=format.value,
                filters=query_filters,
                template=template.value
            )
            return FileResponse(
                path=file_path,
                filename=f"reconvault_report_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.{format.value}",
                media_type=f"application/{format.value}"
            )

        elif format in [ReportFormat.HTML, ReportFormat.PDF]:
            # Generate HTML or PDF report
            report_data = await report_service.generate_formatted_report(
                db=db,
                format=format.value,
                filters=query_filters,
                template=template.value
            )
            if format == ReportFormat.HTML:
                return Response(
                    content=report_data,
                    media_type="text/html",
                    headers={
                        "Content-Disposition": f"attachment; filename=reconvault_report_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.html"
                    }
                )
            else:  # PDF
                return Response(
                    content=report_data,
                    media_type="application/pdf",
                    headers={
                        "Content-Disposition": f"attachment; filename=reconvault_report_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.pdf"
                    }
                )

    except Exception as e:
        logger.error(f"Failed to generate report: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate report: {str(e)}"
        )


@router.get("/")
async def list_reports(
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """
    List all generated reports.

    Args:
        limit: Maximum number of reports to return
        offset: Number of reports to skip
        db: Database session

    Returns:
        List of reports
    """
    try:
        # This would typically query a reports table
        # For now, return empty list as reports are generated on-demand
        return {
            "total": 0,
            "limit": limit,
            "offset": offset,
            "reports": []
        }
    except Exception as e:
        logger.error(f"Failed to list reports: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list reports: {str(e)}"
        )


@router.get("/{report_id}/status")
async def get_report_status(
    report_id: str,
    db: Session = Depends(get_db)
):
    """
    Get status of a generated report.

    Args:
        report_id: Report identifier
        db: Database session

    Returns:
        Report status
    """
    try:
        # For on-demand generation, report is always ready
        return {
            "report_id": report_id,
            "status": "ready",
            "generated_at": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Failed to get report status: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get report status: {str(e)}"
        )


@router.get("/templates")
async def list_templates():
    """
    List available report templates.

    Returns:
        List of templates with descriptions
    """
    return {
        "templates": [
            {
                "id": ReportTemplate.EXECUTIVE_SUMMARY,
                "name": "Executive Summary",
                "description": "High-level overview for executives",
                "sections": ["summary", "key_findings", "recommendations"]
            },
            {
                "id": ReportTemplate.DETAILED_ANALYSIS,
                "name": "Detailed Analysis",
                "description": "Comprehensive technical analysis",
                "sections": ["overview", "entities", "relationships", "risk_analysis", "findings"]
            },
            {
                "id": ReportTemplate.RISK_ASSESSMENT,
                "name": "Risk Assessment",
                "description": "Focused risk scoring and analysis",
                "sections": ["risk_summary", "entity_risks", "threat_vectors", "mitigation"]
            },
            {
                "id": ReportTemplate.COMPLIANCE_REPORT,
                "name": "Compliance Report",
                "description": "Ethics and compliance monitoring",
                "sections": ["compliance_status", "violations", "audit_trail", "recommendations"]
            },
            {
                "id": ReportTemplate.CUSTOM,
                "name": "Custom Report",
                "description": "Build your own report",
                "sections": []
            }
        ]
    }


@router.get("/formats")
async def list_formats():
    """
    List supported export formats.

    Returns:
        List of formats with descriptions
    """
    return {
        "formats": [
            {
                "id": ReportFormat.JSON,
                "name": "JSON",
                "description": "Structured JSON format",
                "mime_type": "application/json",
                "supports": ["entities", "relationships", "risk_data", "metadata"]
            },
            {
                "id": ReportFormat.CSV,
                "name": "CSV",
                "description": "Comma-separated values",
                "mime_type": "text/csv",
                "supports": ["entities", "relationships"]
            },
            {
                "id": ReportFormat.HTML,
                "name": "HTML",
                "description": "Formatted HTML document",
                "mime_type": "text/html",
                "supports": ["entities", "relationships", "charts", "styling"]
            },
            {
                "id": ReportFormat.PDF,
                "name": "PDF",
                "description": "Portable Document Format",
                "mime_type": "application/pdf",
                "supports": ["entities", "relationships", "charts", "styling"]
            },
            {
                "id": ReportFormat.GRAPHML,
                "name": "GraphML",
                "description": "Graph Markup Language for graph tools",
                "mime_type": "application/graphml+xml",
                "supports": ["graph_structure", "attributes"]
            },
            {
                "id": ReportFormat.GEXF,
                "name": "GEXF",
                "description": "Gephi XML Format",
                "mime_type": "application/gexf+xml",
                "supports": ["graph_structure", "attributes", "dynamics"]
            }
        ]
    }


@router.post("/preview")
async def preview_report(
    template: ReportTemplate = Query(..., description="Report template"),
    filters: Dict[str, Any] = Body(default={}),
    db: Session = Depends(get_db)
):
    """
    Preview a report without generating it fully.

    Args:
        template: Report template to preview
        filters: Filter criteria
        db: Database session

    Returns:
        Preview data
    """
    try:
        preview_data = await report_service.preview_report(
            db=db,
            filters=filters,
            template=template.value
        )
        return {
            "template": template.value,
            "preview": preview_data
        }
    except Exception as e:
        logger.error(f"Failed to preview report: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to preview report: {str(e)}"
        )


@router.delete("/{report_id}")
async def delete_report(
    report_id: str,
    db: Session = Depends(get_db)
):
    """
    Delete a generated report.

    Args:
        report_id: Report identifier
        db: Database session

    Returns:
        Deletion status
    """
    try:
        # For on-demand generation, this would delete cached reports
        return {
            "status": "success",
            "message": f"Report {report_id} deleted successfully"
        }
    except Exception as e:
        logger.error(f"Failed to delete report: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete report: {str(e)}"
        )
