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
