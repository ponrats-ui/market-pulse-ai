from __future__ import annotations

from typing import Any, Dict


def engineer_features(evidence: Dict[str, Any]) -> Dict[str, Any]:
    inputs = evidence.get("factor_inputs", {})
    daily_change = inputs.get("daily_change_percent")
    average_move = inputs.get("average_absolute_move_percent")
    market_cap = inputs.get("market_cap")
    return {
        "market_volatility": _bucket(average_move, low=0.8, high=2.5),
        "liquidity": "available" if inputs.get("volume") else "unavailable",
        "news_density": "unavailable",
        "confidence_inputs_missing": len(evidence.get("unavailable_data", [])),
        "size_bucket": _size_bucket(market_cap),
        "short_term_pressure": isinstance(daily_change, (int, float)) and daily_change < -1.5,
    }


def _bucket(value: Any, low: float, high: float) -> str:
    if not isinstance(value, (int, float)):
        return "unavailable"
    if value >= high:
        return "high"
    if value <= low:
        return "low"
    return "medium"


def _size_bucket(value: Any) -> str:
    if not isinstance(value, (int, float)):
        return "unavailable"
    if value >= 200_000_000_000:
        return "mega_cap"
    if value >= 10_000_000_000:
        return "large_cap"
    if value >= 2_000_000_000:
        return "mid_cap"
    return "small_cap"
