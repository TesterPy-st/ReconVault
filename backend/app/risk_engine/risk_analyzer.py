"""
Risk Analyzer

Core risk assessment engine that combines ML models, exposure analysis,
and pattern detection for comprehensive risk scoring.
"""

import json
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from loguru import logger
from sqlalchemy.orm import Session

from app.models.entity import Entity
from app.models.relationship import Relationship
from app.risk_engine.exposure_models import ExposureAnalyzer
from app.risk_engine.ml_models import RiskMLModel


class RiskAnalyzer:
    """
    Main risk analysis engine combining ML models and rule-based analysis.
    """
    
    def __init__(self, db: Optional[Session] = None):
        """
        Initialize risk analyzer.
        
        Args:
            db: Optional database session
        """
        self.db = db
        self.ml_model = RiskMLModel()
        self.exposure_analyzer = ExposureAnalyzer()
        
        # Try to load pre-trained model
        self.ml_model.load_model()
    
    def calculate_entity_risk(self, entity: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate comprehensive risk score for an entity.
        
        Args:
            entity: Entity dictionary
            
        Returns:
            Risk assessment results
        """
        logger.debug(f"Calculating risk for entity {entity.get('id')}")
        
        # 1. Calculate exposure level
        exposure_score = self.calculate_exposure_level(entity)
        
        # 2. Calculate threat level
        threat_score = self._calculate_threat_level(entity)
        
        # 3. Calculate behavioral indicators
        behavioral_score = self._calculate_behavioral_indicators(entity)
        
        # 4. Calculate base risk using weighted formula
        base_risk = (
            exposure_score * 0.4 +
            threat_score * 0.3 +
            behavioral_score * 0.3
        )
        
        # 5. Get ML prediction if model is trained
        ml_prediction = None
        if self.ml_model.model_trained:
            ml_prediction = self.ml_model.predict_risk(entity)
            # Blend ML prediction with rule-based score
            ml_score = ml_prediction["risk_class"] * 25 + 12.5  # Map class to score
            base_risk = base_risk * 0.7 + ml_score * 0.3
        
        # 6. Calculate data quality
        data_quality = self._calculate_data_quality(entity)
        
        # 7. Calculate confidence
        confidence = 0.7 + (data_quality * 0.3)
        
        # 8. Final risk score
        final_risk_score = min(base_risk, 100)
        
        # 9. Determine risk level
        risk_level = self._score_to_level(final_risk_score)
        
        return {
            "entity_id": entity.get("id"),
            "risk_score": round(final_risk_score, 2),
            "risk_level": risk_level,
            "confidence": round(confidence, 3),
            "components": {
                "exposure": round(exposure_score, 2),
                "threat_level": round(threat_score, 2),
                "behavioral_indicators": round(behavioral_score, 2)
            },
            "data_quality": round(data_quality, 3),
            "ml_prediction": ml_prediction,
            "calculated_at": datetime.utcnow().isoformat()
        }
    
    def calculate_relationship_risk(self, relationship: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate risk score for a relationship.
        
        Args:
            relationship: Relationship dictionary
            
        Returns:
            Risk assessment results
        """
        logger.debug(f"Calculating risk for relationship {relationship.get('id')}")
        
        risk_score = 0.0
        risk_factors = []
        
        rel_type = relationship.get("type", "").lower()
        confidence = relationship.get("confidence", 1.0)
        weight = relationship.get("weight", 1.0)
        
        # High-risk relationship types
        high_risk_types = [
            "vulnerable_to", "threatens", "targets", "attributed_to",
            "indicator_of", "compromised_by", "exploits"
        ]
        
        if rel_type in high_risk_types:
            risk_score += 40
            risk_factors.append({
                "factor": "high_risk_relationship_type",
                "description": f"Relationship type '{rel_type}' indicates high risk",
                "score": 40
            })
        
        # Medium-risk types
        medium_risk_types = [
            "communicates_with", "connected_to", "uses", "depends_on"
        ]
        
        if rel_type in medium_risk_types:
            risk_score += 20
            risk_factors.append({
                "factor": "medium_risk_relationship_type",
                "description": f"Relationship type '{rel_type}' indicates medium risk",
                "score": 20
            })
        
        # Metadata analysis
        metadata = relationship.get("metadata", {})
        if isinstance(metadata, str):
            try:
                metadata = json.loads(metadata)
            except:
                metadata = {}
        
        # Dark web related
        if metadata.get("dark_web_related"):
            risk_score += 25
            risk_factors.append({
                "factor": "dark_web_connection",
                "description": "Relationship involves dark web activity",
                "score": 25
            })
        
        # Malware related
        if metadata.get("malware_related"):
            risk_score += 30
            risk_factors.append({
                "factor": "malware_connection",
                "description": "Relationship involves malware",
                "score": 30
            })
        
        # Unverified relationship
        if not relationship.get("verified", False):
            risk_score += 5
        
        # Weight and confidence adjustments
        risk_score = risk_score * weight * confidence
        
        # Cap at 100
        risk_score = min(risk_score, 100)
        
        risk_level = self._score_to_level(risk_score)
        
        return {
            "relationship_id": relationship.get("id"),
            "risk_score": round(risk_score, 2),
            "risk_level": risk_level,
            "confidence": round(confidence, 3),
            "risk_factors": risk_factors,
            "calculated_at": datetime.utcnow().isoformat()
        }
    
    def calculate_exposure_level(self, entity: Dict[str, Any]) -> float:
        """
        Calculate exposure level for entity (0-100).
        
        Args:
            entity: Entity dictionary
            
        Returns:
            Exposure score
        """
        return self.exposure_analyzer.calculate_total_exposure(entity)
    
    def detect_risk_patterns(
        self,
        entities: List[Dict[str, Any]],
        relationships: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Detect risk patterns across entities and relationships.
        
        Args:
            entities: List of entity dictionaries
            relationships: List of relationship dictionaries
            
        Returns:
            List of detected patterns
        """
        logger.info(f"Detecting risk patterns in {len(entities)} entities and {len(relationships)} relationships")
        
        patterns = []
        
        # Pattern 1: Breach cluster
        breach_entities = [
            e for e in entities
            if e.get("metadata", {}).get("breaches_found", 0) > 0
        ]
        if len(breach_entities) >= 3:
            patterns.append({
                "pattern_type": "breach_cluster",
                "severity": "high",
                "description": f"Cluster of {len(breach_entities)} entities found in data breaches",
                "affected_entities": [e.get("id") for e in breach_entities[:10]],
                "risk_score": min(len(breach_entities) * 5, 80)
            })
        
        # Pattern 2: Dark web exposure
        darkweb_entities = [
            e for e in entities
            if e.get("metadata", {}).get("dark_web_mentions")
        ]
        if len(darkweb_entities) >= 2:
            patterns.append({
                "pattern_type": "dark_web_exposure",
                "severity": "critical",
                "description": f"{len(darkweb_entities)} entities found on dark web",
                "affected_entities": [e.get("id") for e in darkweb_entities],
                "risk_score": 90
            })
        
        # Pattern 3: High connectivity (potential pivot point)
        for entity in entities:
            rel_count = entity.get("relationship_count", 0)
            if rel_count > 15:
                patterns.append({
                    "pattern_type": "high_connectivity",
                    "severity": "medium",
                    "description": f"Entity has {rel_count} connections (potential pivot point)",
                    "affected_entities": [entity.get("id")],
                    "risk_score": min(30 + rel_count, 70)
                })
        
        # Pattern 4: Malware infrastructure
        malware_rels = [
            r for r in relationships
            if "malware" in r.get("type", "").lower() or
            r.get("metadata", {}).get("malware_related")
        ]
        if len(malware_rels) >= 2:
            affected = set()
            for rel in malware_rels:
                affected.add(rel.get("source_entity_id"))
                affected.add(rel.get("target_entity_id"))
            
            patterns.append({
                "pattern_type": "malware_infrastructure",
                "severity": "critical",
                "description": f"Detected malware infrastructure with {len(malware_rels)} connections",
                "affected_entities": list(affected),
                "risk_score": 85
            })
        
        # Pattern 5: Vulnerability chain
        vuln_entities = [
            e for e in entities
            if e.get("type") == "vulnerability" or
            len(e.get("metadata", {}).get("vulnerabilities", [])) > 0
        ]
        if len(vuln_entities) >= 3:
            patterns.append({
                "pattern_type": "vulnerability_chain",
                "severity": "high",
                "description": f"Chain of {len(vuln_entities)} vulnerable entities detected",
                "affected_entities": [e.get("id") for e in vuln_entities],
                "risk_score": 75
            })
        
        # Pattern 6: Anomaly cluster
        anomaly_entities = [
            e for e in entities
            if e.get("metadata", {}).get("is_anomaly")
        ]
        if len(anomaly_entities) >= 4:
            patterns.append({
                "pattern_type": "anomaly_cluster",
                "severity": "medium",
                "description": f"Cluster of {len(anomaly_entities)} anomalous entities",
                "affected_entities": [e.get("id") for e in anomaly_entities[:10]],
                "risk_score": 60
            })
        
        logger.info(f"Detected {len(patterns)} risk patterns")
        return patterns
    
    def generate_risk_report(self, target_id: int) -> Dict[str, Any]:
        """
        Generate comprehensive risk report for a target.
        
        Args:
            target_id: Target ID
            
        Returns:
            Comprehensive risk report
        """
        if not self.db:
            logger.error("Database session required for risk report generation")
            return {"error": "Database session not available"}
        
        logger.info(f"Generating risk report for target {target_id}")
        
        try:
            # Get all entities for target
            entities = self.db.query(Entity).filter(
                Entity.target_id == target_id,
                Entity.is_active == True
            ).all()
            
            if not entities:
                return {
                    "target_id": target_id,
                    "status": "no_data",
                    "message": "No entities found for target"
                }
            
            # Convert to dictionaries
            entity_dicts = [self._entity_to_dict(e) for e in entities]
            
            # Calculate risk for each entity
            entity_risks = []
            for entity in entity_dicts:
                risk = self.calculate_entity_risk(entity)
                entity_risks.append(risk)
            
            # Get relationships
            entity_ids = [e.id for e in entities]
            relationships = self.db.query(Relationship).filter(
                (Relationship.source_entity_id.in_(entity_ids)) |
                (Relationship.target_entity_id.in_(entity_ids))
            ).all()
            
            relationship_dicts = [self._relationship_to_dict(r) for r in relationships]
            
            # Calculate relationship risks
            relationship_risks = []
            for rel in relationship_dicts:
                risk = self.calculate_relationship_risk(rel)
                relationship_risks.append(risk)
            
            # Detect patterns
            patterns = self.detect_risk_patterns(entity_dicts, relationship_dicts)
            
            # Calculate aggregate statistics
            risk_scores = [r["risk_score"] for r in entity_risks]
            avg_risk = sum(risk_scores) / len(risk_scores) if risk_scores else 0
            max_risk = max(risk_scores) if risk_scores else 0
            
            # Risk distribution
            critical_count = sum(1 for r in entity_risks if r["risk_level"] == "critical")
            high_count = sum(1 for r in entity_risks if r["risk_level"] == "high")
            medium_count = sum(1 for r in entity_risks if r["risk_level"] == "medium")
            low_count = sum(1 for r in entity_risks if r["risk_level"] == "low")
            
            # Top risks
            top_risks = sorted(entity_risks, key=lambda x: x["risk_score"], reverse=True)[:10]
            
            # Overall risk level
            overall_risk_level = self._score_to_level(max_risk)
            
            # Recommendations
            recommendations = self._generate_recommendations(
                entity_risks, relationship_risks, patterns
            )
            
            report = {
                "target_id": target_id,
                "generated_at": datetime.utcnow().isoformat(),
                "summary": {
                    "total_entities": len(entities),
                    "total_relationships": len(relationships),
                    "average_risk_score": round(avg_risk, 2),
                    "maximum_risk_score": round(max_risk, 2),
                    "overall_risk_level": overall_risk_level,
                    "risk_distribution": {
                        "critical": critical_count,
                        "high": high_count,
                        "medium": medium_count,
                        "low": low_count
                    }
                },
                "top_risks": top_risks,
                "patterns_detected": patterns,
                "recommendations": recommendations,
                "entity_count_by_type": self._count_entities_by_type(entity_dicts),
                "exposure_summary": self._calculate_exposure_summary(entity_dicts)
            }
            
            logger.info(f"Risk report generated for target {target_id}: {overall_risk_level} risk")
            return report
            
        except Exception as e:
            logger.error(f"Error generating risk report: {e}", exc_info=True)
            return {
                "target_id": target_id,
                "status": "error",
                "message": str(e)
            }
    
    def _calculate_threat_level(self, entity: Dict[str, Any]) -> float:
        """Calculate threat level component (0-100)."""
        threat_score = 0.0
        metadata = entity.get("metadata", {})
        
        if isinstance(metadata, str):
            try:
                metadata = json.loads(metadata)
            except:
                metadata = {}
        
        # Malware detected
        if metadata.get("malware_detected"):
            threat_score += 40
        
        # Phishing indicator
        if metadata.get("phishing_indicator"):
            threat_score += 35
        
        # Threat actor related
        if entity.get("type") == "threat_actor":
            threat_score += 50
        
        # High-risk country
        high_risk_countries = ["RU", "CN", "KP", "IR"]
        if metadata.get("country") in high_risk_countries:
            threat_score += 15
        
        # Suspicious TLD
        value = entity.get("value", "").lower()
        if any(value.endswith(tld) for tld in [".xyz", ".top", ".zip", ".tk"]):
            threat_score += 10
        
        return min(threat_score, 100)
    
    def _calculate_behavioral_indicators(self, entity: Dict[str, Any]) -> float:
        """Calculate behavioral indicators component (0-100)."""
        behavioral_score = 0.0
        metadata = entity.get("metadata", {})
        
        if isinstance(metadata, str):
            try:
                metadata = json.loads(metadata)
            except:
                metadata = {}
        
        # Anomaly detection
        if metadata.get("is_anomaly"):
            behavioral_score += 25
        
        # High activity (frequent collection)
        collection_count = metadata.get("collection_count", 1)
        if collection_count > 10:
            behavioral_score += 15
        
        # Rapid changes
        if metadata.get("rapid_changes_detected"):
            behavioral_score += 20
        
        # Suspicious patterns
        if metadata.get("suspicious_patterns"):
            behavioral_score += 20
        
        # Multiple sources correlation
        sources = metadata.get("sources", [])
        if isinstance(sources, list) and len(sources) > 5:
            behavioral_score += 10
        
        return min(behavioral_score, 100)
    
    def _calculate_data_quality(self, entity: Dict[str, Any]) -> float:
        """Calculate data quality score (0-1)."""
        quality = 0.5  # Base quality
        
        # Has confidence score
        if entity.get("confidence"):
            quality += 0.1
        
        # Is verified
        if entity.get("is_verified"):
            quality += 0.2
        
        # Has metadata
        metadata = entity.get("metadata", {})
        if metadata:
            quality += 0.1
        
        # Has multiple sources
        if isinstance(metadata, dict):
            sources = metadata.get("sources", [])
            if isinstance(sources, list) and len(sources) > 1:
                quality += 0.1
        
        return min(quality, 1.0)
    
    def _score_to_level(self, score: float) -> str:
        """Convert risk score to level."""
        if score >= 76:
            return "critical"
        elif score >= 51:
            return "high"
        elif score >= 26:
            return "medium"
        else:
            return "low"
    
    def _entity_to_dict(self, entity: Entity) -> Dict[str, Any]:
        """Convert Entity model to dictionary."""
        metadata = entity.metadata
        if isinstance(metadata, str):
            try:
                metadata = json.loads(metadata)
            except:
                metadata = {}
        
        return {
            "id": entity.id,
            "type": entity.type,
            "value": entity.value,
            "risk_score": entity.risk_score,
            "confidence": entity.confidence,
            "relationship_count": entity.relationship_count,
            "is_verified": entity.is_verified,
            "metadata": metadata
        }
    
    def _relationship_to_dict(self, relationship: Relationship) -> Dict[str, Any]:
        """Convert Relationship model to dictionary."""
        metadata = relationship.metadata
        if isinstance(metadata, str):
            try:
                metadata = json.loads(metadata)
            except:
                metadata = {}
        
        return {
            "id": relationship.id,
            "source_entity_id": relationship.source_entity_id,
            "target_entity_id": relationship.target_entity_id,
            "type": relationship.type,
            "confidence": relationship.confidence,
            "weight": relationship.weight,
            "verified": relationship.verified,
            "metadata": metadata
        }
    
    def _generate_recommendations(
        self,
        entity_risks: List[Dict[str, Any]],
        relationship_risks: List[Dict[str, Any]],
        patterns: List[Dict[str, Any]]
    ) -> List[str]:
        """Generate actionable recommendations."""
        recommendations = []
        
        # Check for critical entities
        critical_entities = [r for r in entity_risks if r["risk_level"] == "critical"]
        if critical_entities:
            recommendations.append(
                f"URGENT: {len(critical_entities)} critical risk entities detected. Immediate investigation required."
            )
        
        # Check for patterns
        if patterns:
            critical_patterns = [p for p in patterns if p.get("severity") == "critical"]
            if critical_patterns:
                recommendations.append(
                    f"Critical risk patterns detected: {', '.join(p['pattern_type'] for p in critical_patterns)}"
                )
        
        # Check for dark web exposure
        if any(p.get("pattern_type") == "dark_web_exposure" for p in patterns):
            recommendations.append(
                "Dark web exposure detected. Consider password resets and credential monitoring."
            )
        
        # Check for vulnerabilities
        if any(p.get("pattern_type") == "vulnerability_chain" for p in patterns):
            recommendations.append(
                "Vulnerability chain detected. Prioritize patching and security updates."
            )
        
        # Check for data breaches
        if any(p.get("pattern_type") == "breach_cluster" for p in patterns):
            recommendations.append(
                "Multiple entities in data breaches. Implement breach response procedures."
            )
        
        # General recommendations
        high_risk_count = len([r for r in entity_risks if r["risk_level"] in ["high", "critical"]])
        if high_risk_count > 10:
            recommendations.append(
                "High volume of risky entities. Consider comprehensive security audit."
            )
        
        if not recommendations:
            recommendations.append("Overall risk levels acceptable. Continue routine monitoring.")
        
        return recommendations
    
    def _count_entities_by_type(self, entities: List[Dict[str, Any]]) -> Dict[str, int]:
        """Count entities by type."""
        counts = {}
        for entity in entities:
            entity_type = entity.get("type", "unknown")
            counts[entity_type] = counts.get(entity_type, 0) + 1
        return counts
    
    def _calculate_exposure_summary(self, entities: List[Dict[str, Any]]) -> Dict[str, float]:
        """Calculate average exposure across all categories."""
        if not entities:
            return {}
        
        data_exp = []
        network_exp = []
        identity_exp = []
        infra_exp = []
        
        for entity in entities:
            comprehensive = self.exposure_analyzer.get_comprehensive_exposure(entity)
            data_exp.append(comprehensive["data_exposure"]["exposure_score"])
            network_exp.append(comprehensive["network_exposure"]["exposure_score"])
            identity_exp.append(comprehensive["identity_exposure"]["exposure_score"])
            infra_exp.append(comprehensive["infrastructure_exposure"]["exposure_score"])
        
        return {
            "average_data_exposure": round(sum(data_exp) / len(data_exp), 2),
            "average_network_exposure": round(sum(network_exp) / len(network_exp), 2),
            "average_identity_exposure": round(sum(identity_exp) / len(identity_exp), 2),
            "average_infrastructure_exposure": round(sum(infra_exp) / len(infra_exp), 2)
        }
