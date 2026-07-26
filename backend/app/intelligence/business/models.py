from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Literal

BusinessStatus = Literal["measured", "partial", "unavailable", "not_applicable", "unsupported"]
EvidenceStatus = Literal["available", "partial", "unavailable", "inferred"]


@dataclass(frozen=True)
class BusinessEvidenceItem:
    evidence_id: str
    domain: str
    evidence_type: str
    provider: str
    status: EvidenceStatus
    verification_status: Literal["provider_reported", "inferred", "unverified"]
    value: Any
    interpretation: str
    limitations: List[str] = field(default_factory=list)


@dataclass(frozen=True)
class BusinessDomainAssessment:
    domain: str
    score: int | None
    status: Literal["measured", "partial", "unavailable", "not_applicable"]
    role: Literal["quality", "risk", "context", "governance", "capital_allocation"]
    evidence: List[BusinessEvidenceItem]
    missing_evidence: List[str]
    explanation_en: str
    limitations: List[str] = field(default_factory=list)


@dataclass(frozen=True)
class BusinessRiskSignal:
    code: str
    severity: Literal["low", "medium", "high", "critical"]
    status: Literal["confirmed", "possible", "unknown"]
    evidence: List[str]
    explanation_en: str


@dataclass(frozen=True)
class BusinessIntelligenceVersionSet:
    methodology_version: str
    scoring_version: str
    policy_version: str
    evidence_version: str


@dataclass(frozen=True)
class BusinessIntelligenceReport:
    symbol: str
    status: BusinessStatus
    applicable: bool
    asset_class: str
    profile: str
    business_intelligence_score: int | None
    business_quality_score: int | None
    business_risk: str
    business_confidence: int
    business_completeness: int
    domain_assessments: List[BusinessDomainAssessment]
    business_evidence: List[BusinessEvidenceItem]
    missing_business_evidence: List[str]
    risk_signals: List[BusinessRiskSignal]
    limitations: List[str]
    evidence_based_narrative: Dict[str, Any]
    financial_intelligence_reference: Dict[str, Any]
    versions: BusinessIntelligenceVersionSet
    cache_metadata: Dict[str, Any]
    disclaimer: str = "This is not financial advice."

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
