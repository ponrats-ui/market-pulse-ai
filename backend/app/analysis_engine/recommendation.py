from __future__ import annotations

from typing import Any, Dict, List

COMMITTEE_MEMBERS = (
    "Value Investor",
    "Growth Investor",
    "Technical Analyst",
    "Macro Economist",
    "Quant Analyst",
    "Risk Manager",
    "Behavioral Finance Analyst",
)


def build_committee_opinions(evidence: Dict[str, Any], factor_scores: Dict[str, float], weighted_score: float) -> List[Dict[str, str]]:
    unavailable = evidence.get("unavailable_data", [])
    return [
        _opinion("Value Investor", factor_scores.get("valuation", 50), "Valuation data is useful only when provider fundamentals are available.", unavailable),
        _opinion("Growth Investor", factor_scores.get("growth", 50), "Growth view leans on returned price trend until deeper fundamentals are available.", unavailable),
        _opinion("Technical Analyst", factor_scores.get("technical", 50), "Technical view is based on trend and volatility evidence, not a standalone signal.", unavailable),
        _opinion("Macro Economist", factor_scores.get("macro", 50), "Macro score is neutral until configured macro feeds are available.", unavailable),
        _opinion("Quant Analyst", weighted_score, "Weighted score combines all configured factors for reproducibility.", unavailable),
        _opinion("Risk Manager", factor_scores.get("risk", 50), "Risk control should dominate when volatility or missing data is elevated.", unavailable),
        _opinion("Behavioral Finance Analyst", factor_scores.get("sentiment", 50), "Behavioral view stays neutral until sentiment and positioning providers are configured.", unavailable),
    ]


def build_final_recommendation(weighted_score: float, confidence: Dict[str, Any], regime: str) -> Dict[str, Any]:
    if confidence.get("label") == "low":
        stance = "Insufficient confidence"
        action = "Wait for more complete data before forming a stronger view."
    elif weighted_score >= 65:
        stance = "Constructive but cautious"
        action = "น่าติดตาม แต่ควรกำหนดแผนรับมือก่อนลงทุนและหลีกเลี่ยงการไล่ราคา."
    elif weighted_score <= 40:
        stance = "Defensive"
        action = "รอจังหวะหรือหลีกเลี่ยงการเพิ่มความเสี่ยงจนกว่าหลักฐานจะดีขึ้น."
    else:
        stance = "Neutral"
        action = "รอจังหวะและติดตามข้อมูลเพิ่มเติมก่อนเพิ่มน้ำหนัก."
    return {
        "stance": stance,
        "cautious_action": action,
        "chairman_summary": f"Chairman AI aggregates committee views under the {regime} regime with {confidence.get('label')} confidence.",
        "consensus": "Committee consensus is conservative when evidence is incomplete.",
        "conflict": "Growth or momentum views can conflict with risk-manager views during volatile regimes.",
        "minority_opinion": "Minority opinions are preserved when factor scores diverge materially.",
        "disclaimer": "This is not financial advice. No assured outcome or direct buy/sell instruction is provided.",
    }


def _opinion(member: str, score: float, rationale: str, unavailable: List[str]) -> Dict[str, str]:
    if score >= 65:
        view = "constructive"
    elif score <= 40:
        view = "cautious"
    else:
        view = "neutral"
    if unavailable:
        rationale = f"{rationale} Missing data: {', '.join(unavailable)}."
    return {"member": member, "view": view, "rationale": rationale}
