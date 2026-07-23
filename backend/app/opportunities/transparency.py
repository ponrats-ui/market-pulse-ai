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
    return AlgorithmValidationResult(valid=not errors, errors=errors)
