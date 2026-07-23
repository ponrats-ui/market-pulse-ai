from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Literal

OpportunityEngineStatus = Literal["running", "ok", "partial", "failed", "unavailable"]


@dataclass(frozen=True)
class OpportunityEngineDefinition:
    engine_id: str
    category: str
    display_name: str
    methodology_version: str
    score_version: str
    policy_version: str
    config_version: str
    supported_markets: List[str]
    schedule_frequency_minutes: int
    maximum_results: int
    shortlist_limit: int
    minimum_score: float
    minimum_confidence: float
    minimum_completeness: float
    freshness_policy: Dict[str, Any]
    factor_weights: Dict[str, float]
    risk_policy: Dict[str, Any]
    tie_breaker_policy: List[str]
    enabled: bool = True


@dataclass(frozen=True)
class OpportunityProviderStatus:
    provider: str
    stage: str
    status: str
    reason: str | None = None
    timestamp: str | None = None
    symbol: str | None = None


@dataclass(frozen=True)
class OpportunityScanMetrics:
    universe_size: int = 0
    prefiltered_count: int = 0
    eligible_count: int = 0
    qualified_count: int = 0
    excluded_count: int = 0
    failed_candidate_count: int = 0
    ranked_count: int = 0
    result_count: int = 0
    scan_duration_ms: int = 0


@dataclass(frozen=True)
class OpportunitySnapshot:
    snapshot_id: str | None
    engine_id: str
    category: str
    status: OpportunityEngineStatus
    scan_started_at: str | None
    scan_completed_at: str | None
    generated_at: str
    last_successful_scan_at: str | None
    next_scan_at: str | None
    frequency_minutes: int
    methodology_version: str
    score_version: str
    policy_version: str
    config_version: str
    metrics: OpportunityScanMetrics
    items: List[Dict[str, Any]] = field(default_factory=list)
    provider_status: List[Dict[str, Any]] = field(default_factory=list)
    limitations: List[str] = field(default_factory=list)
    failure_metadata: Dict[str, Any] | None = None
    is_stale: bool = False


@dataclass(frozen=True)
class OpportunityEngineRuntime:
    definition: OpportunityEngineDefinition
    scan_once: Callable[..., Dict[str, Any]]
    get_snapshot: Callable[..., Dict[str, Any]]
    start_scheduler: Callable[..., bool]
    stop_scheduler: Callable[[], None]


@dataclass(frozen=True)
class AlgorithmIdentity:
    engine_id: str
    algorithm_id: str
    category: str
    display_name_th: str
    display_name_en: str
    short_description_th: str
    short_description_en: str
    methodology_name: str
    methodology_version: str
    score_version: str
    policy_version: str
    config_version: str
    release_date: str
    last_updated_at: str
    status: str
    supported_markets: List[str]
    schedule_frequency_minutes: int
    maximum_results: int


@dataclass(frozen=True)
class AlgorithmTextBlock:
    th: str
    en: str


@dataclass(frozen=True)
class AlgorithmFactorDefinition:
    factor_id: str
    display_name_th: str
    display_name_en: str
    purpose_th: str
    purpose_en: str
    rationale_th: str
    rationale_en: str
    weight: float
    maximum_contribution: float
    input_fields: List[str]
    evidence_requirements: List[str]
    provider_dependencies: List[str]
    freshness_expectation: str
    missing_data_behavior: str
    partial_data_behavior: str
    score_interpretation: str
    limitations: List[str]
    factor_version: str


@dataclass(frozen=True)
class AlgorithmRiskDefinition:
    code: str
    family: str
    severity: str
    rationale_th: str
    rationale_en: str
    disqualifying: bool


@dataclass(frozen=True)
class AlgorithmChangeRecord:
    version: str
    date: str
    summary: str
    impact: str


@dataclass(frozen=True)
class AlgorithmDefinition:
    identity: AlgorithmIdentity
    objective: AlgorithmTextBlock
    hypothesis: AlgorithmTextBlock
    universe: Dict[str, Any]
    eligibility: Dict[str, Any]
    factors: List[AlgorithmFactorDefinition]
    risks: List[AlgorithmRiskDefinition]
    score_formula: Dict[str, Any]
    confidence: Dict[str, Any]
    completeness: Dict[str, Any]
    ranking: Dict[str, Any]
    data_dependencies: List[Dict[str, Any]]
    limitations: List[AlgorithmTextBlock]
    non_claims: List[AlgorithmTextBlock]
    change_history: List[AlgorithmChangeRecord]


@dataclass(frozen=True)
class AlgorithmValidationResult:
    valid: bool
    errors: List[str]
    warnings: List[str] = field(default_factory=list)
