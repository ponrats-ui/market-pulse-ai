from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Literal

AssetClass = Literal["corporate_equity", "preferred_equity", "reit", "business_trust", "etf", "mutual_fund", "closed_end_fund", "crypto", "precious_metal", "commodity", "currency", "index", "unknown"]
IntelligenceProfileType = Literal["corporate_financial", "financial_institution", "insurance", "reit_financial", "fund_intelligence", "on_chain", "macro", "commodity_supply_demand", "unsupported", "unknown"]
PrimaryEvidenceDomain = Literal["financial_intelligence", "fund_intelligence", "on_chain", "macro", "commodity_supply_demand", "market_context", "unsupported", "unknown"]


@dataclass(frozen=True)
class AssetClassificationEvidence:
    field: str
    value: Any
    source: str
    interpretation: str


@dataclass(frozen=True)
class AssetClassificationConfidence:
    score: int
    level: Literal["high", "medium", "low", "unknown"]
    reasons: List[str] = field(default_factory=list)


@dataclass(frozen=True)
class AssetClassification:
    symbol: str
    exchange: str | None
    market: str | None
    asset_class: AssetClass
    asset_subtype: str
    sector: str | None
    industry: str | None
    selected_intelligence_profile: IntelligenceProfileType
    primary_evidence_domain: PrimaryEvidenceDomain
    classification_source: str
    classification_confidence: AssetClassificationConfidence
    classification_limitations: List[str]
    fallback_status: Literal["selected", "not_applicable", "unsupported", "unknown"]
    evidence: List[AssetClassificationEvidence] = field(default_factory=list)


@dataclass(frozen=True)
class AssetIntelligenceProfile:
    profile_type: IntelligenceProfileType
    display_name: str
    primary_evidence_domain: PrimaryEvidenceDomain
    primary_evidence_weight_target: float | None
    primary_evidence_weight_range: tuple[float, float] | None
    secondary_evidence_domains: List[str]
    supported_scoring_domains: List[str]
    not_applicable_domains: List[str]
    financial_model: str
    minimum_evidence_requirements: List[str]
    freshness_requirements: List[str]
    confidence_requirements: Dict[str, Any]
    completeness_requirements: Dict[str, Any]
    risk_model: str
    version: str
    limitations: List[str]
    non_claims: List[str]


@dataclass(frozen=True)
class FinancialMetricDefinition:
    metric_id: str
    display_name: str
    formula: str
    required_fields: List[str]
    domain: str
    role: Literal["positive", "risk", "eligibility", "confidence", "completeness", "context"]
    limitations: List[str]


@dataclass(frozen=True)
class FinancialMetricValue:
    metric_id: str
    value: float | None
    status: Literal["measured", "partial", "unavailable", "not_applicable"]
    formula: str
    inputs: Dict[str, Any]
    missing_inputs: List[str]
    interpretation: str


@dataclass(frozen=True)
class FinancialSubscore:
    domain: str
    score: int | None
    status: Literal["measured", "partial", "unavailable", "not_applicable"]
    role: str
    weight: float
    metrics: List[FinancialMetricValue]
    explanation_en: str
    explanation_th: str
    limitations: List[str]


@dataclass(frozen=True)
class FinancialRiskSignal:
    code: str
    severity: Literal["low", "medium", "high", "critical"]
    status: Literal["confirmed", "possible", "unknown"]
    evidence: List[str]
    explanation_en: str
    explanation_th: str


@dataclass(frozen=True)
class FinancialIntelligenceVersionSet:
    methodology_version: str
    formula_version: str
    scoring_version: str
    policy_version: str
    profile_version: str


@dataclass(frozen=True)
class FinancialValidationResult:
    valid: bool
    errors: List[str]
    warnings: List[str] = field(default_factory=list)


@dataclass(frozen=True)
class FinancialIntelligenceReport:
    symbol: str
    status: Literal["measured", "partial", "unavailable", "not_applicable", "unsupported"]
    applicable: bool
    classification: AssetClassification
    profile: AssetIntelligenceProfile
    model_id: str
    financial_intelligence_score: int | None
    score_status: Literal["measured", "partial", "unavailable", "not_applicable"]
    confidence: int
    completeness: int
    primary_evidence_domain: PrimaryEvidenceDomain
    primary_evidence_weight: float | None
    domain_subscores: List[FinancialSubscore]
    risk_signals: List[FinancialRiskSignal]
    facts: Dict[str, Any]
    evidence_metadata: List[Dict[str, Any]]
    missing_evidence: List[str]
    limitations: List[str]
    explanation: Dict[str, Any]
    formula_version: str
    versions: FinancialIntelligenceVersionSet
    cache_metadata: Dict[str, Any]
    disclaimer: str = "This is not financial advice."

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
