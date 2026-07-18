from __future__ import annotations

from typing import Any, Dict

from app.analysis_engine.score_calculator import apply_regime_adjustments


def adapt_weights(base_weights: Dict[str, float], regime_adjustments: Dict[str, float], asset_class_model: Dict[str, Any], features: Dict[str, Any], confidence: Dict[str, Any] | None = None) -> Dict[str, float]:
    adjusted = apply_regime_adjustments(base_weights, regime_adjustments)
    adjusted = apply_regime_adjustments(adjusted, asset_class_model.get("factor_bias", {}))
    if features.get("market_volatility") == "high":
        adjusted = apply_regime_adjustments(adjusted, {"risk": 1.2, "volatility": 1.2, "liquidity": 1.1, "momentum": 0.9})
    if features.get("news_density") == "high":
        adjusted = apply_regime_adjustments(adjusted, {"news": 1.25, "macro": 1.1, "technical": 0.9})
    if features.get("liquidity") == "unavailable":
        adjusted = apply_regime_adjustments(adjusted, {"liquidity": 0.75, "risk": 1.1})
    if confidence and confidence.get("label") == "low":
        adjusted = apply_regime_adjustments(adjusted, {"risk": 1.2, "volatility": 1.15, "momentum": 0.85})
    return adjusted
