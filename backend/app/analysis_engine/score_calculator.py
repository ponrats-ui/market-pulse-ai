from __future__ import annotations

from typing import Any, Dict

FACTOR_NAMES = (
    "technical",
    "fundamental",
    "macro",
    "news",
    "sentiment",
    "risk",
    "liquidity",
    "valuation",
    "quality",
    "growth",
    "momentum",
    "volatility",
)


def calculate_factor_scores(evidence: Dict[str, Any]) -> Dict[str, float]:
    inputs = evidence.get("factor_inputs", {})
    daily_change = inputs.get("daily_change_percent")
    history_performance = inputs.get("history_performance_percent")
    average_move = inputs.get("average_absolute_move_percent")
    market_cap = inputs.get("market_cap")
    trailing_pe = inputs.get("trailing_pe")
    volume = inputs.get("volume")

    momentum = _score_momentum(daily_change, history_performance)
    volatility_risk = _score_volatility(average_move, daily_change)
    valuation = _score_valuation(trailing_pe)
    liquidity = _score_liquidity(volume)
    quality = 55.0 if market_cap else 45.0

    return {
        "technical": momentum,
        "fundamental": _average([valuation, quality]),
        "macro": 50.0,
        "news": 50.0,
        "sentiment": 50.0,
        "risk": max(0.0, 100.0 - volatility_risk),
        "liquidity": liquidity,
        "valuation": valuation,
        "quality": quality,
        "growth": momentum if history_performance is not None else 50.0,
        "momentum": momentum,
        "volatility": max(0.0, 100.0 - volatility_risk),
    }


def apply_profile_weights(factor_scores: Dict[str, float], weights: Dict[str, float]) -> Dict[str, Any]:
    active_weights = {factor: float(weights.get(factor, 0)) for factor in FACTOR_NAMES}
    total_weight = sum(active_weights.values())
    if total_weight <= 0:
        raise ValueError("Profile weights must sum to more than zero")
    contributions = {
        factor: (factor_scores.get(factor, 50.0) * weight) / total_weight
        for factor, weight in active_weights.items()
        if weight > 0
    }
    return {
        "weighted_score": sum(contributions.values()),
        "contributions": contributions,
        "normalized_weights": {factor: weight / total_weight for factor, weight in active_weights.items() if weight > 0},
    }


def apply_regime_adjustments(weights: Dict[str, float], adjustments: Dict[str, float]) -> Dict[str, float]:
    adjusted = dict(weights)
    for factor, multiplier in adjustments.items():
        if factor in adjusted:
            adjusted[factor] = max(0.0, adjusted[factor] * float(multiplier))
    return adjusted


def _score_momentum(daily_change: Any, history_performance: Any) -> float:
    score = 50.0
    if isinstance(daily_change, (int, float)):
        score += max(-20.0, min(20.0, daily_change * 4))
    if isinstance(history_performance, (int, float)):
        score += max(-25.0, min(25.0, history_performance))
    return _clamp(score)


def _score_volatility(average_move: Any, daily_change: Any) -> float:
    risk = 35.0
    if isinstance(average_move, (int, float)):
        risk += min(45.0, average_move * 12)
    if isinstance(daily_change, (int, float)):
        risk += min(20.0, abs(daily_change) * 3)
    return _clamp(risk)


def _score_valuation(trailing_pe: Any) -> float:
    if not isinstance(trailing_pe, (int, float)) or trailing_pe <= 0:
        return 50.0
    if trailing_pe <= 15:
        return 70.0
    if trailing_pe <= 30:
        return 58.0
    if trailing_pe <= 50:
        return 45.0
    return 35.0


def _score_liquidity(volume: Any) -> float:
    if not isinstance(volume, (int, float)) or volume <= 0:
        return 45.0
    if volume >= 10_000_000:
        return 75.0
    if volume >= 1_000_000:
        return 65.0
    if volume >= 100_000:
        return 55.0
    return 45.0


def _average(values: list[float]) -> float:
    return sum(values) / len(values) if values else 50.0


def _clamp(value: float) -> float:
    return max(0.0, min(100.0, value))
