from __future__ import annotations

from dataclasses import replace

from app.services import penny_opportunities as po

from tests.test_penny_opportunities import asset, history, no_news, quote


def _validation_errors(definition) -> list[str]:
    return po.validate_algorithm_definition(definition, po.PENNY_FACTOR_WEIGHTS).errors


def test_trust_policy_loads_successfully() -> None:
    validation = po.validate_penny_algorithm_definition()

    assert validation["valid"] is True
    assert validation["errors"] == []
    assert po.PENNY_ALGORITHM_DEFINITION.trust.trust_policy_version == po.TRUST_POLICY_VERSION


def test_penny_algorithm_endpoint_exposes_trust_metadata() -> None:
    payload = po.get_penny_algorithm_definition()

    assert payload["status"] == "ok"
    assert payload["trust"]["evidence_based"] is True
    assert payload["trust"]["methodology_inspectable"] is True
    assert payload["trust"]["commercial_influence_on_ranking"] is False
    assert payload["trust"]["engagement_influence_on_ranking"] is False
    assert payload["trust"]["popularity_influence_on_ranking"] is False
    assert payload["trust"]["user_decision_required"] is True


def test_missing_trust_disclosure_blocks_activation() -> None:
    broken = replace(po.PENNY_ALGORITHM_DEFINITION, trust=None)

    assert "missing_trust_disclosure" in _validation_errors(broken)


def test_missing_decision_boundary_blocks_activation() -> None:
    trust = po.PENNY_ALGORITHM_DEFINITION.trust
    broken = replace(
        po.PENNY_ALGORITHM_DEFINITION,
        trust=replace(trust, decision_boundary=replace(trust.decision_boundary, statement_en="")),
    )

    assert "missing_decision_boundary" in _validation_errors(broken)


def test_missing_uncertainty_policy_blocks_activation() -> None:
    trust = po.PENNY_ALGORITHM_DEFINITION.trust
    broken = replace(
        po.PENNY_ALGORITHM_DEFINITION,
        trust=replace(trust, uncertainty=replace(trust.uncertainty, disclosed_conditions=[])),
    )

    assert "missing_uncertainty_policy" in _validation_errors(broken)


def test_missing_commercial_independence_declaration_blocks_activation() -> None:
    trust = po.PENNY_ALGORITHM_DEFINITION.trust
    broken = replace(
        po.PENNY_ALGORITHM_DEFINITION,
        trust=replace(
            trust,
            conflict_of_interest=replace(trust.conflict_of_interest, current_commercial_relationships=""),
        ),
    )

    assert "missing_commercial_independence_declaration" in _validation_errors(broken)


def test_missing_ranking_integrity_declaration_blocks_activation() -> None:
    trust = po.PENNY_ALGORITHM_DEFINITION.trust
    broken = replace(
        po.PENNY_ALGORITHM_DEFINITION,
        trust=replace(trust, ranking_integrity=replace(trust.ranking_integrity, prohibited_influences=[])),
    )

    assert "missing_ranking_integrity_declaration" in _validation_errors(broken)


def test_commercial_engagement_and_popularity_cannot_affect_ranking() -> None:
    trust = po.PENNY_ALGORITHM_DEFINITION.trust
    neutrality = trust.neutrality
    broken = replace(
        po.PENNY_ALGORITHM_DEFINITION,
        trust=replace(
            trust,
            neutrality=replace(
                neutrality,
                sponsored_or_commercial_factors_exist=True,
                user_engagement_affects_scoring=True,
                asset_popularity_affects_scoring=True,
                editorial_opinion_affects_scoring=True,
            ),
        ),
    )

    errors = _validation_errors(broken)
    assert "commercial_influence_declared_active" in errors
    assert "engagement_influence_declared_active" in errors
    assert "popularity_influence_declared_active" in errors
    assert "editorial_influence_declared_active" in errors


def test_required_neutrality_exclusions_are_declared() -> None:
    exclusions = {item.lower() for item in po.PENNY_ALGORITHM_DEFINITION.trust.neutrality.ranking_exclusions}

    for required in {
        "advertising",
        "sponsorship",
        "affiliate relationships",
        "broker relationships",
        "asset issuer payments",
        "user click-through rate",
        "page popularity",
        "watchlist popularity",
        "social engagement",
        "developer preference",
        "founder preference",
        "provider promotional placement",
    }:
        assert required in exclusions


def test_declared_ranking_inputs_match_actual_policy() -> None:
    trust = po.PENNY_ALGORITHM_DEFINITION.trust

    assert trust.ranking_integrity.declared_ranking_inputs == po.PENNY_ENGINE_DEFINITION.tie_breaker_policy
    assert trust.ranking_integrity.declared_ranking_inputs == po.PENNY_ALGORITHM_DEFINITION.ranking["policy"]


def test_score_confidence_and_completeness_are_not_profit_claims() -> None:
    trust = po.PENNY_ALGORITHM_DEFINITION.trust

    assert "probability of profit" in trust.score_interpretation["does_not_represent"]
    assert "probability of profit" in trust.confidence_interpretation["does_not_represent"]
    assert "investment quality" in trust.completeness_interpretation["does_not_represent"]
    score_represents = " ".join(trust.score_interpretation["represents"]).lower()
    confidence_represents = " ".join(trust.confidence_interpretation["represents"]).lower()
    completeness_represents = " ".join(trust.completeness_interpretation["represents"]).lower()
    assert "probability of profit" not in score_represents
    assert "probability of profit" not in confidence_represents
    assert "investment quality" not in completeness_represents


def test_evidence_integrity_policy_requires_auditable_metadata() -> None:
    required = set(po.PENNY_ALGORITHM_DEFINITION.trust.evidence_integrity.required_metadata)

    assert {
        "evidence_id",
        "evidence_type",
        "provider",
        "source_timestamp",
        "retrieval_timestamp",
        "freshness_status",
        "availability_status",
        "verification_status",
        "supported_factor",
        "candidate_symbol",
        "transformation_summary",
        "data_limitations",
    }.issubset(required)


def test_inferred_evidence_is_allowed_but_not_verified() -> None:
    policy = po.PENNY_ALGORITHM_DEFINITION.trust.evidence_integrity

    assert "inferred" in policy.allowed_verification_statuses
    assert "verified" in policy.allowed_verification_statuses
    assert "must not be described as verified fact" in policy.inferred_evidence_rule


def test_candidate_exposes_uncertainty_and_evidence_integrity() -> None:
    result = po.evaluate_candidate(
        asset(),
        po.POLICIES["TH"],
        lambda symbol: quote(symbol, volume=None, market_cap=None, debt_to_equity=None, return_on_equity=None),
        lambda *_: {"points": [], "source": "test_provider", "error": "history unavailable"},
        no_news,
    )

    assert result["trust"]["trust_policy_version"] == po.TRUST_POLICY_VERSION
    assert "verified_catalyst_data" in result["uncertainty_disclosure"]["missing_evidence"]
    assert result["uncertainty_disclosure"]["provider_failures"]
    assert result["evidence_integrity"]
    assert all("evidence_id" in row for row in result["evidence_integrity"])


def test_suspected_or_unknown_risk_is_not_labeled_confirmed() -> None:
    result = po.evaluate_candidate(
        asset(),
        po.POLICIES["TH"],
        lambda symbol: quote(symbol, volume=None),
        lambda *_: {"points": [{"time": "t1", "close": 2.5}], "source": "test"},
        no_news,
    )

    unknown_risks = [risk for risk in result["risks"] if risk.get("status") == "unknown"]
    assert unknown_risks
    assert all(risk["status"] != "confirmed" for risk in unknown_risks)


def test_stale_evidence_and_provider_failure_remain_visible() -> None:
    payload = po._uncertainty_disclosure(
        [],
        [
            {"provider": "test", "stage": "history", "status": "ok", "freshness_status": "stale"},
            {"provider": "test", "stage": "quote", "status": "error", "reason": "timeout"},
        ],
        [],
    )

    assert payload["stale_evidence"]
    assert payload["provider_failures"]


def test_compact_trust_disclosure_is_bilingual() -> None:
    trust = po.PENNY_ALGORITHM_DEFINITION.trust

    assert trust.compact_disclosure.th
    assert trust.compact_disclosure.en
    assert trust.founder_trust_statement.th
    assert trust.founder_trust_statement.en
    assert trust.decision_boundary.statement_th
    assert trust.decision_boundary.statement_en


def test_non_directive_language_policy_is_declared() -> None:
    boundary = po.PENNY_ALGORITHM_DEFINITION.trust.decision_boundary
    text = " ".join([boundary.statement_en, *boundary.non_directive_actions]).lower()

    assert "decision remains yours" in text
    for phrase in boundary.prohibited_phrases:
        assert phrase.lower() not in text


def test_snapshot_contains_trust_metadata(monkeypatch) -> None:
    monkeypatch.setattr(po, "list_registry_assets", lambda enabled_only=True, searchable_only=True: [asset("TTB.BK")])

    payload = po.build_penny_opportunities(lambda symbol: quote(symbol), lambda *_: history(), no_news, market="TH")

    assert payload["trust"]["trust_policy_version"] == po.TRUST_POLICY_VERSION
    assert payload["trust"]["score_is_not_probability"] is True
    assert payload["configuration_version"] == po.CONFIGURATION_VERSION


def test_score_breakdown_records_trust_version() -> None:
    result = po.evaluate_candidate(asset(), po.POLICIES["TH"], lambda symbol: quote(symbol), lambda *_: history(), no_news)

    assert result["score_breakdown"]["display_precision"] == "whole_number"
    assert result["score_breakdown"]["trust_policy_version"] == po.TRUST_POLICY_VERSION


def test_why_not_response_contains_decision_boundary() -> None:
    payload = po.get_penny_why_not("NOTREAL")

    assert payload["trust"]["user_decision_required"] is True
    assert payload["trust"]["decision_boundary"]["en"]
