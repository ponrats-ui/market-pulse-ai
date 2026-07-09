from __future__ import annotations

from typing import Any, Dict


def estimate_probabilities(weighted_score: float, confidence: Dict[str, Any]) -> Dict[str, Any]:
    confidence_score = float(confidence.get("score", 0.0))
    tempered_score = 50 + ((weighted_score - 50) * confidence_score)
    bullish = max(5.0, min(80.0, tempered_score * 0.75))
    bearish = max(5.0, min(80.0, (100 - tempered_score) * 0.65))
    neutral = max(10.0, 100.0 - bullish - bearish)
    total = bullish + neutral + bearish
    return {
        "bullish_probability": round((bullish / total) * 100, 2),
        "neutral_probability": round((neutral / total) * 100, 2),
        "bearish_probability": round((bearish / total) * 100, 2),
        "explanation": "Probabilities are confidence-adjusted estimates from weighted evidence, not exact price predictions.",
    }
