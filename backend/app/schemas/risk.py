"""
Risk Assessment Schemas

Pydantic models for risk assessment API requests and responses.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class RiskComponentsSchema(BaseModel):
    """Risk score components breakdown."""
    exposure: float = Field(..., ge=0, le=100)
    threat_level: float = Field(..., ge=0, le=100)
    behavioral_indicators: float = Field(..., ge=0, le=100)


class MLPredictionSchema(BaseModel):
    """ML model prediction results."""
    risk_class: int = Field(..., ge=0, le=3)
    risk_level: str
    confidence: float = Field(..., ge=0, le=1)
    probabilities: List[float]


class EntityRiskSchema(BaseModel):
    """Entity risk assessment results."""
    entity_id: int
    risk_score: float = Field(..., ge=0, le=100)
    risk_level: str
    confidence: float = Field(..., ge=0, le=1)
    components: RiskComponentsSchema
    data_quality: float = Field(..., ge=0, le=1)
    ml_prediction: Optional[MLPredictionSchema] = None
    calculated_at: str


class RiskFactorSchema(BaseModel):
    """Individual risk factor."""
    factor: str
    description: str
    score: float


class RelationshipRiskSchema(BaseModel):
    """Relationship risk assessment results."""
    relationship_id: int
    risk_score: float = Field(..., ge=0, le=100)
    risk_level: str
    confidence: float = Field(..., ge=0, le=1)
    risk_factors: List[RiskFactorSchema]
    calculated_at: str


class AnalyzeEntityRequest(BaseModel):
    """Request to analyze single entity risk."""
    entity_id: int = Field(..., description="Entity ID to analyze")


class AnalyzeBatchRequest(BaseModel):
    """Request to analyze multiple entities."""
    entity_ids: List[int] = Field(..., description="List of entity IDs to analyze")
    include_relationships: bool = Field(default=False, description="Include relationship risk analysis")


class RecalculateRequest(BaseModel):
    """Request to recalculate risks."""
    target_id: Optional[int] = Field(None, description="Target ID (null for all)")
    force: bool = Field(default=False, description="Force recalculation even if recent")


class RiskPatternSchema(BaseModel):
    """Detected risk pattern."""
    pattern_type: str
    severity: str
    description: str
    affected_entities: List[int]
    risk_score: float


class RiskDistributionSchema(BaseModel):
    """Risk level distribution."""
    critical: int
    high: int
    medium: int
    low: int


class RiskSummarySchema(BaseModel):
    """Risk summary statistics."""
    total_entities: int
    total_relationships: int
    average_risk_score: float
    maximum_risk_score: float
    overall_risk_level: str
    risk_distribution: RiskDistributionSchema


class ExposureSummarySchema(BaseModel):
    """Exposure summary across categories."""
    average_data_exposure: float
    average_network_exposure: float
    average_identity_exposure: float
    average_infrastructure_exposure: float


class RiskReportSchema(BaseModel):
    """Comprehensive risk report."""
    target_id: int
    generated_at: str
    summary: RiskSummarySchema
    top_risks: List[EntityRiskSchema]
    patterns_detected: List[RiskPatternSchema]
    recommendations: List[str]
    entity_count_by_type: Dict[str, int]
    exposure_summary: ExposureSummarySchema


class ExposureDetailsSchema(BaseModel):
    """Detailed exposure information."""
    exposure_score: float
    exposure_level: str


class DataExposureSchema(ExposureDetailsSchema):
    """Data exposure details."""
    breaches_found: int
    dark_web_mentions: bool
    pii_exposed: bool
    credentials_leaked: bool
    paste_mentions: int


class NetworkExposureSchema(ExposureDetailsSchema):
    """Network exposure details."""
    open_ports_count: int
    open_ports: List[int]
    publicly_accessible: bool
    firewall_detected: bool
    relationship_count: int


class IdentityExposureSchema(ExposureDetailsSchema):
    """Identity exposure details."""
    entity_type: str
    breaches_found: int
    exposed_pii_fields: List[str]
    identity_theft_detected: bool
    online_identities_count: int


class InfrastructureExposureSchema(ExposureDetailsSchema):
    """Infrastructure exposure details."""
    ssl_days_until_expiry: int
    has_ssl: bool
    vulnerabilities_count: int
    critical_vulnerabilities: int
    outdated_software: bool
    misconfigured: bool
    unpatched: bool


class ComprehensiveExposureSchema(BaseModel):
    """Comprehensive exposure analysis."""
    total_exposure: float
    data_exposure: DataExposureSchema
    network_exposure: NetworkExposureSchema
    identity_exposure: IdentityExposureSchema
    infrastructure_exposure: InfrastructureExposureSchema


class EntityMetricsSchema(BaseModel):
    """Entity risk metrics."""
    entity_id: int
    current_risk: EntityRiskSchema
    exposure_analysis: ComprehensiveExposureSchema
    historical_risk_scores: Optional[List[Dict[str, Any]]] = None


class PatternLibrarySchema(BaseModel):
    """Pattern library response."""
    patterns: List[Dict[str, str]]
    total_patterns: int


class AnalyzeResponse(BaseModel):
    """Response for single entity analysis."""
    success: bool
    risk_assessment: EntityRiskSchema
    exposure_analysis: Optional[ComprehensiveExposureSchema] = None


class AnalyzeBatchResponse(BaseModel):
    """Response for batch analysis."""
    success: bool
    results: List[EntityRiskSchema]
    relationship_risks: Optional[List[RelationshipRiskSchema]] = None
    patterns_detected: Optional[List[RiskPatternSchema]] = None
    summary: Optional[Dict[str, Any]] = None


class RecalculateResponse(BaseModel):
    """Response for recalculation request."""
    success: bool
    message: str
    entities_processed: int
    task_id: Optional[str] = None


class ErrorResponse(BaseModel):
    """Error response."""
    success: bool = False
    error: str
    details: Optional[str] = None
