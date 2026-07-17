from __future__ import annotations

from typing import Any, Dict


def build_quant_risk_report(evidence: Dict[str, Any], probabilities: Dict[str, Any], asset_class_model: Dict[str, Any]) -> Dict[str, Any]:
    unavailable = evidence.get("unavailable_data", [])
    bearish = probabilities.get("bearish_probability")
    high_risk = isinstance(bearish, (int, float)) and bearish >= 40
    return {
        "risk_model": asset_class_model.get("risk_model"),
        "scenario_analysis": [
            "Base case: evidence remains mixed and position sizing should remain conservative.",
            "Bull case: momentum improves with acceptable volatility and liquidity.",
            "Bear case: volatility expands or key data remains unavailable.",
        ],
        "stress_test": "Stress test requires complete historical volatility and correlation data." if unavailable else "Stress scenario emphasizes drawdown and liquidity deterioration.",
        "position_size_suggestion": "Small or observational allocation only when confidence is low." if high_risk or unavailable else "Position size should remain aligned with personal risk capacity.",
        "diversification_impact": "Correlation engine is not yet connected; diversification impact is unavailable.",
        "correlation": "Unavailable until cross-asset correlation provider is configured.",
        "liquidity_risk": "Elevated if provider volume or liquidity evidence is unavailable.",
        "macro_risk": "Regime-sensitive and should be reviewed before adding exposure.",
        "tail_risk": "Tail events can invalidate model probabilities quickly.",
        "recommended_action": "รอจังหวะและกำหนดแผนรับมือก่อนลงทุน." if high_risk or unavailable else "น่าติดตาม แต่ยังควรควบคุมขนาดสถานะ.",
        "recommended_action": _recommended_action(high_risk, unavailable),
    }


def _recommended_action(high_risk: bool, unavailable: list[str]) -> str:
    if high_risk or unavailable:
        return "รอจังหวะและกำหนดแผนรับมือก่อนลงทุน."
    return "น่าติดตาม แต่ยังควรควบคุมขนาดสถานะ."
