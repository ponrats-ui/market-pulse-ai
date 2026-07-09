from __future__ import annotations

from typing import Any, Dict


def calculate_confidence(evidence: Dict[str, Any], weighted_scores: Dict[str, Any]) -> Dict[str, Any]:
    unavailable = evidence.get("unavailable_data", [])
    raw_data = evidence.get("raw_data", {})
    quote_present = bool(raw_data.get("quote"))
    history_points = len(raw_data.get("history", {}).get("points", []))
    available_count = max(0, 6 - len(unavailable))
    coverage = available_count / 6
    if quote_present and history_points >= 20:
        coverage = min(1.0, coverage + 0.15)
    dispersion = _score_dispersion(weighted_scores.get("contributions", {}))
    score = max(0.0, min(1.0, (coverage * 0.8) + ((1 - dispersion) * 0.2)))
    label = "high" if score >= 0.75 else "medium" if score >= 0.45 else "low"
    return {"score": round(score, 3), "label": label, "coverage": round(coverage, 3)}


def _score_dispersion(contributions: Dict[str, float]) -> float:
    values = list(contributions.values())
    if len(values) < 2:
        return 0.0
    mean = sum(values) / len(values)
    if mean == 0:
        return 0.0
    variance = sum((value - mean) ** 2 for value in values) / len(values)
    return min(1.0, (variance ** 0.5) / mean)
