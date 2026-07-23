from __future__ import annotations

from dataclasses import asdict
from typing import Any, Dict

from app.opportunities.models import AlgorithmDefinition, AlgorithmValidationResult


def algorithm_to_dict(definition: AlgorithmDefinition) -> Dict[str, Any]:
    return asdict(definition)


def validate_algorithm_definition(definition: AlgorithmDefinition, active_factor_weights: Dict[str, float]) -> AlgorithmValidationResult:
    errors: list[str] = []
    identity = definition.identity
    required_identity = {
        "engine_id": identity.engine_id,
        "algorithm_id": identity.algorithm_id,
        "methodology_version": identity.methodology_version,
        "score_version": identity.score_version,
        "policy_version": identity.policy_version,
        "config_version": identity.config_version,
        "display_name_th": identity.display_name_th,
        "display_name_en": identity.display_name_en,
    }
    for field, value in required_identity.items():
        if not value:
            errors.append(f"missing_identity_{field}")
    if not definition.objective.th or not definition.objective.en:
        errors.append("missing_objective")
    if not definition.hypothesis.th or not definition.hypothesis.en:
        errors.append("missing_hypothesis")
    if not definition.limitations:
        errors.append("missing_limitations")
    if not definition.non_claims:
        errors.append("missing_non_claims")
    if not definition.change_history:
        errors.append("missing_change_history")

    documented_weights = {factor.factor_id: factor.weight for factor in definition.factors}
    if set(documented_weights) != set(active_factor_weights):
        errors.append("active_factor_set_mismatch")
    for factor in definition.factors:
        if not factor.display_name_th:
            errors.append(f"missing_factor_th_label:{factor.factor_id}")
        if not factor.display_name_en:
            errors.append(f"missing_factor_en_label:{factor.factor_id}")
        if not factor.rationale_th or not factor.rationale_en:
            errors.append(f"missing_factor_rationale:{factor.factor_id}")
        active_weight = active_factor_weights.get(factor.factor_id)
        if active_weight is None or round(active_weight, 6) != round(factor.weight, 6):
            errors.append(f"factor_weight_mismatch:{factor.factor_id}")
    if not definition.score_formula:
        errors.append("missing_score_formula")
    if not definition.confidence:
        errors.append("missing_confidence_methodology")
    if not definition.completeness:
        errors.append("missing_completeness_methodology")
    if not definition.ranking:
        errors.append("missing_ranking_methodology")
    errors.extend(_validate_trust_disclosure(definition, active_factor_weights))
    return AlgorithmValidationResult(valid=not errors, errors=errors)


def _validate_trust_disclosure(definition: AlgorithmDefinition, active_factor_weights: Dict[str, float]) -> list[str]:
    errors: list[str] = []
    trust = getattr(definition, "trust", None)
    if trust is None:
        return ["missing_trust_disclosure"]
    if not trust.trust_policy_version:
        errors.append("missing_trust_policy_version")
    if not trust.principles:
        errors.append("missing_trust_principles")
    if not trust.compact_disclosure.th or not trust.compact_disclosure.en:
        errors.append("missing_compact_trust_disclosure")
    if not trust.founder_trust_statement.th or not trust.founder_trust_statement.en:
        errors.append("missing_founder_trust_statement")

    if not trust.decision_boundary.statement_th or not trust.decision_boundary.statement_en:
        errors.append("missing_decision_boundary")
    if not trust.decision_boundary.prohibited_phrases:
        errors.append("missing_prohibited_phrases")
    if not trust.uncertainty.disclosed_conditions or not trust.uncertainty.statement_th or not trust.uncertainty.statement_en:
        errors.append("missing_uncertainty_policy")

    neutrality = trust.neutrality
    if neutrality.sponsored_or_commercial_factors_exist:
        errors.append("commercial_influence_declared_active")
    if neutrality.user_engagement_affects_scoring:
        errors.append("engagement_influence_declared_active")
    if neutrality.asset_popularity_affects_scoring:
        errors.append("popularity_influence_declared_active")
    if neutrality.editorial_opinion_affects_scoring:
        errors.append("editorial_influence_declared_active")
    required_exclusions = {
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
        "Founder preference",
        "provider promotional placement",
    }
    declared_exclusions = {item.lower() for item in neutrality.ranking_exclusions}
    for required in required_exclusions:
        if required.lower() not in declared_exclusions:
            errors.append(f"missing_neutrality_exclusion:{required}")

    coi = trust.conflict_of_interest
    if coi.sponsored_content_score_impact_allowed:
        errors.append("sponsored_content_can_affect_score")
    if coi.commercial_relationship_rank_impact_allowed:
        errors.append("commercial_relationship_can_affect_rank")
    if coi.paid_placement_in_rankings_allowed:
        errors.append("paid_placement_allowed_in_rankings")
    if not coi.current_commercial_relationships:
        errors.append("missing_commercial_independence_declaration")

    ranking = trust.ranking_integrity
    if not ranking.prohibited_influences:
        errors.append("missing_ranking_integrity_declaration")
    if ranking.manual_override_supported:
        required_manual_fields = {"visible", "timestamped", "authorized actor", "reason", "original algorithmic rank"}
        manual_text = " ".join(ranking.manual_override_rules).lower()
        for required in required_manual_fields:
            if required not in manual_text:
                errors.append(f"missing_manual_override_rule:{required}")
    if ranking.declared_ranking_inputs != definition.ranking.get("policy"):
        errors.append("declared_ranking_inputs_mismatch")
    expected_ranking_inputs = [
        "penny_opportunity_score DESC",
        "data_confidence DESC",
        "data_completeness DESC",
        "liquidity_score DESC",
        "risk_penalty ASC",
        "symbol ASC",
    ]
    if ranking.declared_ranking_inputs != expected_ranking_inputs:
        errors.append("actual_ranking_inputs_mismatch")

    if not trust.score_interpretation or not trust.score_interpretation.get("does_not_represent"):
        errors.append("missing_score_interpretation")
    if not trust.confidence_interpretation or not trust.confidence_interpretation.get("does_not_represent"):
        errors.append("missing_confidence_interpretation")
    if not trust.completeness_interpretation or not trust.completeness_interpretation.get("does_not_represent"):
        errors.append("missing_completeness_interpretation")
    if "probability of profit" in str(trust.score_interpretation.get("represents", "")).lower():
        errors.append("score_labeled_as_profit_probability")
    if "probability of profit" in str(trust.confidence_interpretation.get("represents", "")).lower():
        errors.append("confidence_labeled_as_profit_probability")
    if "investment quality" in str(trust.completeness_interpretation.get("represents", "")).lower():
        errors.append("completeness_labeled_as_investment_quality")

    evidence = trust.evidence_integrity
    required_evidence_fields = {
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
    }
    for required in required_evidence_fields:
        if required not in evidence.required_metadata:
            errors.append(f"missing_evidence_metadata:{required}")
    for status in ["available", "partial", "unavailable", "stale", "failed", "unsupported"]:
        if status not in evidence.allowed_availability_statuses:
            errors.append(f"missing_evidence_availability_status:{status}")
    for status in ["verified", "provider_reported", "inferred", "unverified", "conflicting"]:
        if status not in evidence.allowed_verification_statuses:
            errors.append(f"missing_evidence_verification_status:{status}")

    documented_weights = {factor.factor_id: factor.weight for factor in definition.factors}
    if documented_weights != active_factor_weights:
        errors.append("trust_active_factor_weight_mismatch")
    return errors
