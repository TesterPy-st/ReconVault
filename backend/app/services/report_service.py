"""
Report Service

Service for generating intelligence reports in various formats.
"""

import json
import csv
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional
from sqlalchemy.orm import Session

from app.models.intelligence import Entity, Relationship, Target
from app.intelligence_graph.graph_builder import GraphBuilder

# Configure logging
logger = logging.getLogger("reconvault.services.report_service")


class ReportService:
    """Service for generating intelligence reports."""

    def __init__(self):
        """Initialize report service."""
        self.graph_builder = GraphBuilder()

    async def generate_json_report(
        self,
        db: Session,
        filters: Dict[str, Any],
        template: str = "detailed_analysis",
        include_entities: bool = True,
        include_relationships: bool = True,
        include_risk_analysis: bool = True
    ) -> Dict[str, Any]:
        """
        Generate JSON report.

        Args:
            db: Database session
            filters: Query filters
            template: Report template name
            include_entities: Include entity data
            include_relationships: Include relationship data
            include_risk_analysis: Include risk analysis

        Returns:
            JSON report data
        """
        try:
            report = {
                "metadata": {
                    "generated_at": datetime.utcnow().isoformat(),
                    "template": template,
                    "format": "json"
                },
                "summary": await self._generate_summary(db, filters)
            }

            if include_entities:
                report["entities"] = await self._get_entities(db, filters)

            if include_relationships:
                report["relationships"] = await self._get_relationships(db, filters)

            if include_risk_analysis:
                report["risk_analysis"] = await self._get_risk_analysis(db, filters)

            return report

        except Exception as e:
            logger.error(f"Failed to generate JSON report: {str(e)}")
            raise

    async def generate_file_report(
        self,
        db: Session,
        format: str,
        filters: Dict[str, Any],
        template: str = "detailed_analysis"
    ) -> str:
        """
        Generate report file (CSV, GraphML, GEXF).

        Args:
            db: Database session
            format: Output format
            filters: Query filters
            template: Report template name

        Returns:
            File path
        """
        try:
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")

            if format == "csv":
                file_path = f"/tmp/reconvault_report_{timestamp}.csv"
                await self._generate_csv(db, filters, file_path)

            elif format == "graphml":
                file_path = f"/tmp/reconvault_report_{timestamp}.graphml"
                await self._generate_graphml(db, filters, file_path)

            elif format == "gexf":
                file_path = f"/tmp/reconvault_report_{timestamp}.gexf"
                await self._generate_gexf(db, filters, file_path)

            else:
                raise ValueError(f"Unsupported format: {format}")

            return file_path

        except Exception as e:
            logger.error(f"Failed to generate file report: {str(e)}")
            raise

    async def generate_formatted_report(
        self,
        db: Session,
        format: str,
        filters: Dict[str, Any],
        template: str = "detailed_analysis"
    ) -> str:
        """
        Generate formatted report (HTML, PDF).

        Args:
            db: Database session
            format: Output format
            filters: Query filters
            template: Report template name

        Returns:
            Formatted report content
        """
        try:
            # Generate HTML content
            html_content = await self._generate_html_report(db, filters, template)

            if format == "html":
                return html_content
            elif format == "pdf":
                # Would use weasyprint or similar for PDF generation
                # For now, return HTML content
                logger.warning("PDF generation not fully implemented, returning HTML")
                return html_content
            else:
                raise ValueError(f"Unsupported format: {format}")

        except Exception as e:
            logger.error(f"Failed to generate formatted report: {str(e)}")
            raise

    async def preview_report(
        self,
        db: Session,
        filters: Dict[str, Any],
        template: str
    ) -> Dict[str, Any]:
        """
        Preview report data.

        Args:
            db: Database session
            filters: Query filters
            template: Report template name

        Returns:
            Preview data
        """
        try:
            entities = await self._get_entities(db, filters, limit=5)
            relationships = await self._get_relationships(db, filters, limit=5)
            summary = await self._generate_summary(db, filters)

            return {
                "summary": summary,
                "sample_entities": entities,
                "sample_relationships": relationships
            }

        except Exception as e:
            logger.error(f"Failed to preview report: {str(e)}")
            raise

    async def _generate_summary(
        self,
        db: Session,
        filters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate report summary."""
        try:
            query = db.query(Entity)

            # Apply filters
            if "target_id" in filters:
                query = query.filter(Entity.target_id == filters["target_id"])

            total_entities = query.count()
            entity_types = db.query(Entity.type, db.func.count(Entity.type)) \
                .group_by(Entity.type).all()

            return {
                "total_entities": total_entities,
                "entity_types": {t: c for t, c in entity_types},
                "generated_at": datetime.utcnow().isoformat()
            }

        except Exception as e:
            logger.error(f"Failed to generate summary: {str(e)}")
            raise

    async def _get_entities(
        self,
        db: Session,
        filters: Dict[str, Any],
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Get entities for report."""
        try:
            query = db.query(Entity)

            # Apply filters
            if "target_id" in filters:
                query = query.filter(Entity.target_id == filters["target_id"])

            if limit:
                query = query.limit(limit)

            entities = query.all()

            return [
                {
                    "id": entity.id,
                    "name": entity.name,
                    "type": entity.type,
                    "properties": entity.properties or {},
                    "created_at": entity.created_at.isoformat() if entity.created_at else None
                }
                for entity in entities
            ]

        except Exception as e:
            logger.error(f"Failed to get entities: {str(e)}")
            raise

    async def _get_relationships(
        self,
        db: Session,
        filters: Dict[str, Any],
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Get relationships for report."""
        try:
            query = db.query(Relationship)

            # Apply filters
            if "target_id" in filters:
                query = query.filter(Relationship.target_id == filters["target_id"])

            if limit:
                query = query.limit(limit)

            relationships = query.all()

            return [
                {
                    "id": rel.id,
                    "source_id": rel.source_id,
                    "target_id": rel.target_id,
                    "type": rel.type,
                    "properties": rel.properties or {},
                    "created_at": rel.created_at.isoformat() if rel.created_at else None
                }
                for rel in relationships
            ]

        except Exception as e:
            logger.error(f"Failed to get relationships: {str(e)}")
            raise

    async def _get_risk_analysis(
        self,
        db: Session,
        filters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Get risk analysis for report."""
        try:
            # This would integrate with risk engine
            # For now, return placeholder
            return {
                "high_risk_entities": 0,
                "medium_risk_entities": 0,
                "low_risk_entities": 0,
                "average_risk_score": 0.0
            }

        except Exception as e:
            logger.error(f"Failed to get risk analysis: {str(e)}")
            raise

    async def _generate_csv(
        self,
        db: Session,
        filters: Dict[str, Any],
        file_path: str
    ):
        """Generate CSV report."""
        try:
            with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)

                # Write header
                writer.writerow(['ID', 'Name', 'Type', 'Properties', 'Created At'])

                # Write entities
                entities = await self._get_entities(db, filters)
                for entity in entities:
                    writer.writerow([
                        entity['id'],
                        entity['name'],
                        entity['type'],
                        json.dumps(entity['properties']),
                        entity['created_at']
                    ])

        except Exception as e:
            logger.error(f"Failed to generate CSV: {str(e)}")
            raise

    async def _generate_graphml(
        self,
        db: Session,
        filters: Dict[str, Any],
        file_path: str
    ):
        """Generate GraphML report."""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                # Write GraphML header
                f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
                f.write('<graphml xmlns="http://graphml.graphdrawing.org/xmlns"\n')
                f.write('    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"\n')
                f.write('    xsi:schemaLocation="http://graphml.graphdrawing.org/xmlns\n')
                f.write('     http://graphml.graphdrawing.org/xmlns/1.0/graphml.xsd">\n')

                # Write graph
                f.write('  <graph id="G" edgedefault="directed">\n')

                # Write nodes
                entities = await self._get_entities(db, filters)
                for entity in entities:
                    f.write(f'    <node id="{entity["id"]}">\n')
                    f.write(f'      <data key="name">{entity["name"]}</data>\n')
                    f.write(f'      <data key="type">{entity["type"]}</data>\n')
                    f.write('    </node>\n')

                # Write edges
                relationships = await self._get_relationships(db, filters)
                for rel in relationships:
                    f.write(f'    <edge id="{rel["id"]}" source="{rel["source_id"]}" target="{rel["target_id"]}">\n')
                    f.write(f'      <data key="type">{rel["type"]}</data>\n')
                    f.write('    </edge>\n')

                f.write('  </graph>\n')
                f.write('</graphml>')

        except Exception as e:
            logger.error(f"Failed to generate GraphML: {str(e)}")
            raise

    async def _generate_gexf(
        self,
        db: Session,
        filters: Dict[str, Any],
        file_path: str
    ):
        """Generate GEXF report."""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                # Write GEXF header
                f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
                f.write('<gexf xmlns="http://www.gexf.net/1.2draft" version="1.2">\n')
                f.write('  <graph mode="static" defaultedgetype="directed">\n')

                # Write attributes
                f.write('    <attributes class="node">\n')
                f.write('      <attribute id="0" title="name" type="string"/>\n')
                f.write('      <attribute id="1" title="type" type="string"/>\n')
                f.write('    </attributes>\n')

                # Write nodes
                f.write('    <nodes>\n')
                entities = await self._get_entities(db, filters)
                for entity in entities:
                    f.write(f'      <node id="{entity["id"]}">\n')
                    f.write(f'        <attvalues>\n')
                    f.write(f'          <attvalue for="0" value="{entity["name"]}"/>\n')
                    f.write(f'          <attvalue for="1" value="{entity["type"]}"/>\n')
                    f.write(f'        </attvalues>\n')
                    f.write('      </node>\n')
                f.write('    </nodes>\n')

                # Write edges
                f.write('    <edges>\n')
                relationships = await self._get_relationships(db, filters)
                for rel in relationships:
                    f.write(f'      <edge id="{rel["id"]}" source="{rel["source_id"]}" target="{rel["target_id"]}"/>\n')
                f.write('    </edges>\n')

                f.write('  </graph>\n')
                f.write('</gexf>')

        except Exception as e:
            logger.error(f"Failed to generate GEXF: {str(e)}")
            raise

    async def _generate_html_report(
        self,
        db: Session,
        filters: Dict[str, Any],
        template: str
    ) -> str:
        """Generate HTML report."""
        try:
            summary = await self._generate_summary(db, filters)
            entities = await self._get_entities(db, filters)
            relationships = await self._get_relationships(db, filters)

            html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ReconVault Intelligence Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; line-height: 1.6; }}
        .header {{ background: #1a1a2e; color: #4ade80; padding: 20px; border-radius: 8px; }}
        .section {{ margin: 20px 0; padding: 15px; background: #f5f5f5; border-radius: 8px; }}
        h1 {{ margin: 0; }}
        h2 {{ color: #1a1a2e; border-bottom: 2px solid #4ade80; padding-bottom: 10px; }}
        table {{ width: 100%; border-collapse: collapse; }}
        th, td {{ padding: 10px; text-align: left; border-bottom: 1px solid #ddd; }}
        th {{ background: #1a1a2e; color: white; }}
        tr:hover {{ background: #f0f0f0; }}
        .summary {{ display: flex; gap: 20px; flex-wrap: wrap; }}
        .stat {{ background: white; padding: 15px; border-radius: 8px; min-width: 150px; }}
        .stat-value {{ font-size: 24px; font-weight: bold; color: #4ade80; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>ReconVault Intelligence Report</h1>
        <p>Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}</p>
    </div>

    <div class="section">
        <h2>Summary</h2>
        <div class="summary">
            <div class="stat">
                <div class="stat-value">{summary['total_entities']}</div>
                <div>Total Entities</div>
            </div>
        </div>
    </div>

    <div class="section">
        <h2>Entities ({len(entities)})</h2>
        <table>
            <thead>
                <tr><th>ID</th><th>Name</th><th>Type</th><th>Created</th></tr>
            </thead>
            <tbody>
                {"".join([f'<tr><td>{e["id"]}</td><td>{e["name"]}</td><td>{e["type"]}</td><td>{e["created_at"] or "N/A"}</td></tr>' for e in entities[:100]])}
            </tbody>
        </table>
    </div>

    <div class="section">
        <h2>Relationships ({len(relationships)})</h2>
        <table>
            <thead>
                <tr><th>ID</th><th>Source</th><th>Target</th><th>Type</th></tr>
            </thead>
            <tbody>
                {"".join([f'<tr><td>{r["id"]}</td><td>{r["source_id"]}</td><td>{r["target_id"]}</td><td>{r["type"]}</td></tr>' for r in relationships[:100]])}
            </tbody>
        </table>
    </div>
</body>
</html>
"""
            return html

        except Exception as e:
            logger.error(f"Failed to generate HTML report: {str(e)}")
            raise
