from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict

from app.analysis_engine.adaptive_weights import adapt_weights
from app.analysis_engine.asset_class import get_asset_class_model
from app.analysis_engine.confidence import calculate_confidence
from app.analysis_engine.evidence import build_evidence
from app.analysis_engine.feature_engineering import engineer_features
from app.analysis_engine.investment_thesis import build_investment_thesis
from app.analysis_engine.learning import algorithm_registry
from app.analysis_engine.profile_loader import get_profile
from app.analysis_engine.probability import estimate_probabilities
from app.analysis_engine.recommendation import build_committee_opinions, build_final_recommendation
from app.analysis_engine.regime import detect_market_regime
from app.analysis_engine.risk_engine import build_quant_risk_report
from app.analysis_engine.score_calculator import apply_profile_weights, calculate_factor_scores


def build_adaptive_recommendation(symbol: str, quote: Dict[str, Any] | None = None, history: Dict[str, Any] | None = None, profile_name: str = "Balanced") -> Dict[str, Any]:
    profile = get_profile(profile_name)
    evidence = build_evidence(symbol, quote, history)
    features = engineer_features(evidence)
    asset_class_model = get_asset_class_model(evidence["factor_inputs"].get("asset_type"))
    regime = detect_market_regime(evidence)
    factor_scores = calculate_factor_scores(evidence)
    initial_weights = adapt_weights(profile["weights"], profile.get("regime_adjustments", {}).get(regime, {}), asset_class_model, features)
    initial_weighted_scores = apply_profile_weights(factor_scores, initial_weights)
    confidence = calculate_confidence(evidence, initial_weighted_scores)
    adjusted_weights = adapt_weights(profile["weights"], profile.get("regime_adjustments", {}).get(regime, {}), asset_class_model, features, confidence)
    weighted_scores = apply_profile_weights(factor_scores, adjusted_weights)
    confidence = calculate_confidence(evidence, weighted_scores)
    probabilities = estimate_probabilities(weighted_scores["weighted_score"], confidence)
    committee = build_committee_opinions(evidence, factor_scores, weighted_scores["weighted_score"])
    recommendation = build_final_recommendation(weighted_scores["weighted_score"], confidence, regime)
    thesis = build_investment_thesis(symbol, evidence, factor_scores, probabilities)
    quant_risk = build_quant_risk_report(evidence, probabilities, asset_class_model)
    return {
        "algorithm_version": profile["algorithm_version"],
        "profile": profile["name"],
        "market_regime": regime,
        "asset_class_model": asset_class_model,
        "features": features,
        "confidence": confidence,
        "evidence": {
            "facts": evidence["facts"],
            "unavailable_data": evidence["unavailable_data"],
            "assumptions": evidence["assumptions"],
        },
        "factor_scores": factor_scores,
        "weighted_scores": weighted_scores,
        "probability_engine": probabilities,
        "committee_opinions": committee,
        "investment_thesis": thesis,
        "risk_engine": quant_risk,
        "final_recommendation": recommendation,
        "learning": algorithm_registry(profile["algorithm_version"]),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
