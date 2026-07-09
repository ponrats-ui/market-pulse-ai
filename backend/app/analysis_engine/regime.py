from __future__ import annotations

from typing import Any, Dict


def detect_market_regime(evidence: Dict[str, Any]) -> str:
    inputs = evidence.get("factor_inputs", {})
    daily_change = inputs.get("daily_change_percent")
    performance = inputs.get("history_performance_percent")
    average_move = inputs.get("average_absolute_move_percent")

    if isinstance(average_move, (int, float)) and average_move >= 3:
        return "High Volatility"
    if isinstance(average_move, (int, float)) and average_move <= 0.6 and isinstance(performance, (int, float)) and abs(performance) < 3:
        return "Low Volatility"
    if isinstance(performance, (int, float)) and performance >= 8 and (not isinstance(daily_change, (int, float)) or daily_change >= -2):
        return "Bull Market"
    if isinstance(performance, (int, float)) and performance <= -8:
        return "Bear Market"
    if isinstance(daily_change, (int, float)) and daily_change >= 1.5:
        return "Risk-On"
    if isinstance(daily_change, (int, float)) and daily_change <= -1.5:
        return "Risk-Off"
    return "Sideways"
