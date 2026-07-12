from __future__ import annotations

from typing import Any, Dict


def estimate_probabilities(weighted_score: float, confidence: Dict[str, Any]) -> Dict[str, Any]:
    confidence_score = float(confidence.get("score", 0.0))
    tempered_score = 50 + ((weighted_score - 50) * confidence_score)
    bullish = max(5.0, min(80.0, tempered_score * 0.75))
    bearish = max(5.0, min(80.0, (100 - tempered_score) * 0.65))
    neutral = max(10.0, 100.0 - bullish - bearish)
    total = bullish + neutral + bearish
    bull_pct = round((bullish / total) * 100)
    bear_pct = round((bearish / total) * 100)
    neutral_pct = 100 - bull_pct - bear_pct
    return {
        "bullish_probability": bull_pct,
        "neutral_probability": neutral_pct,
        "bearish_probability": bear_pct,
        "explanation": "Probabilities are confidence-adjusted estimates from weighted evidence, not exact price predictions.",
        "signal_conflicts": _signal_conflicts(bull_pct, neutral_pct, bear_pct, confidence),
    }


def _signal_conflicts(bullish: int, neutral: int, bearish: int, confidence: Dict[str, Any]) -> list[str]:
    conflicts: list[str] = []
    if abs(bullish - bearish) <= 12:
        conflicts.append("Bullish and bearish probabilities are close, so the signal mix is conflicted.")
    if neutral >= max(bullish, bearish):
        conflicts.append("Neutral probability is dominant, suggesting patience over prediction.")
    if confidence.get("label") == "low":
        conflicts.append("Low confidence tempers directional probabilities.")
    return conflicts or ["No major probability conflict detected from current weighted evidence."]
