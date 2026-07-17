from __future__ import annotations

from typing import Any, Dict, List

RECOMMENDATION_ACTIONS = ("Accumulate", "Buy", "Hold", "Wait", "Reduce", "Avoid", "Sell")


def build_committee_opinions(evidence: Dict[str, Any], factor_scores: Dict[str, float], weighted_score: float) -> List[Dict[str, Any]]:
    unavailable = evidence.get("unavailable_data", [])
    facts = evidence.get("facts", [])
    inputs = evidence.get("factor_inputs", {})
    return [
        _technical(factor_scores, inputs, facts, unavailable),
        _fundamental(factor_scores, inputs, facts, unavailable),
        _macro(factor_scores, inputs, facts, unavailable),
        _news(factor_scores, inputs, facts, unavailable),
        _risk(factor_scores, inputs, facts, unavailable),
    ]


def build_final_recommendation(weighted_score: float, confidence: Dict[str, Any], regime: str, committee: List[Dict[str, Any]] | None = None, probabilities: Dict[str, Any] | None = None) -> Dict[str, Any]:
    confidence_label = confidence.get("label", "low")
    action = _action(weighted_score, confidence_label)
    supporting = _supporting_reasons(committee or [])
    risks = _risk_reasons(committee or [])
    return {
        "recommendation": action,
        "stance": _stance(action),
        "confidence": confidence_label,
        "supporting_reasons": supporting,
        "risks": risks,
        "conditions_that_could_change": _change_conditions(committee or [], regime),
        "evidence": _committee_evidence(committee or []),
        "limitations": _committee_missing_data(committee or []),
        "cautious_action": _educational_action(action),
        "chairman_summary": f"Chief Investment AI combines committee evidence under the {regime} regime with {confidence_label} confidence.",
        "consensus": _consensus(committee or []),
        "conflict": _conflict(probabilities, committee or []),
        "minority_opinion": _minority(committee or []),
        "disclaimer": "This is not financial advice. No assured outcome or direct buy/sell instruction is provided.",
    }


def _technical(scores: Dict[str, float], inputs: Dict[str, Any], facts: List[str], missing: List[str]) -> Dict[str, Any]:
    score = scores.get("technical", 50)
    trend = _trend(inputs.get("history_performance_percent"))
    volatility = inputs.get("average_absolute_move_percent")
    return _member(
        "Technical Analyst",
        ["trend", "momentum", "volatility", "support/resistance", "technical risks"],
        [f for f in facts if any(key in f.lower() for key in ["price", "change", "history", "volume"])][:4],
        f"Trend is {trend}; momentum score is {round(score, 1)} and volatility input is {volatility if volatility is not None else 'unavailable'}.",
        _view(score),
        _confidence(score, missing),
        ["Support and resistance remain unavailable until swing-level extraction is configured."] if "support_resistance" in missing else [],
        ["A break in trend, volatility spike, or failed support test would change this view."],
        missing,
    )


def _fundamental(scores: Dict[str, float], inputs: Dict[str, Any], facts: List[str], missing: List[str]) -> Dict[str, Any]:
    score = (scores.get("valuation", 50) + scores.get("quality", 50) + scores.get("growth", 50)) / 3
    pe = inputs.get("trailing_pe")
    return _member(
        "Fundamental Analyst",
        ["quality", "growth", "profitability", "cash flow", "valuation"],
        [f for f in facts if any(key in f.lower() for key in ["pe", "market cap", "revenue", "earnings"])][:4],
        f"Fundamental evidence is {'usable' if pe is not None else 'limited'}; valuation/quality/growth composite is {round(score, 1)}.",
        _view(score),
        _confidence(score, missing),
        ["Revenue, cash flow, margins, or valuation fields are incomplete."] if missing else [],
        ["Material earnings deterioration, cash-flow weakness, or valuation expansion would change this view."],
        missing,
    )


def _macro(scores: Dict[str, float], inputs: Dict[str, Any], facts: List[str], missing: List[str]) -> Dict[str, Any]:
    score = scores.get("macro", 50)
    asset_type = inputs.get("asset_type", "unknown")
    return _member(
        "Macro Economist",
        ["interest rates", "inflation", "currency", "liquidity", "economic regime"],
        [f for f in facts if any(key in f.lower() for key in ["currency", "asset", "macro", "source"])][:4],
        f"Macro view is asset-class aware for {asset_type}; live macro feeds are weighted cautiously when unavailable.",
        _view(score),
        "low" if any("macro" in item.lower() for item in missing) else _confidence(score, missing),
        ["FRED or other macro provider data is unavailable."] if any("macro" in item.lower() for item in missing) else [],
        ["Rate, inflation, currency, or liquidity regime shifts would change this view."],
        missing,
    )


def _news(scores: Dict[str, float], inputs: Dict[str, Any], facts: List[str], missing: List[str]) -> Dict[str, Any]:
    score = scores.get("news", 50)
    return _member(
        "News Analyst",
        ["company events", "regulation", "earnings", "sector events", "news impact"],
        [f for f in facts if "news" in f.lower() or "source" in f.lower()][:4],
        "News impact is treated as unavailable unless provider-returned, asset-specific headlines are present.",
        _view(score),
        "low" if any("news" in item.lower() for item in missing) else _confidence(score, missing),
        ["Asset-specific news provider or classifier data is unavailable."] if any("news" in item.lower() for item in missing) else [],
        ["Confirmed earnings, regulation, sector shock, or company event would change this view."],
        missing,
    )


def _risk(scores: Dict[str, float], inputs: Dict[str, Any], facts: List[str], missing: List[str]) -> Dict[str, Any]:
    score = scores.get("risk", 50)
    volatility = inputs.get("average_absolute_move_percent")
    return _member(
        "Risk Manager",
        ["downside", "liquidity", "concentration", "event risk", "unknowns"],
        [f for f in facts if any(key in f.lower() for key in ["risk", "volatility", "volume", "change"])][:4],
        f"Risk view emphasizes downside and unknowns; volatility input is {volatility if volatility is not None else 'unavailable'}.",
        "cautious" if score <= 60 else "constructive",
        _confidence(score, missing),
        ["Liquidity, event risk, or volatility data is incomplete."] if missing else [],
        ["Position concentration, liquidity deterioration, or event risk would change the risk budget."],
        missing,
    )


def _member(member: str, responsibilities: List[str], facts: List[str], interpretation: str, opinion: str, confidence: str, evidence: List[str], change_conditions: List[str], missing: List[str]) -> Dict[str, Any]:
    return {
        "member": member,
        "responsibilities": responsibilities,
        "facts": facts or ["No complete provider fact is available for this committee role."],
        "interpretation": interpretation,
        "opinion": opinion,
        "view": opinion,
        "confidence": confidence,
        "evidence": evidence or facts[:3] or ["Evidence is limited and should be verified with provider data."],
        "missing_data": missing[:6],
        "conditions_that_would_change_opinion": change_conditions,
    }


def _action(score: float, confidence: str) -> str:
    if confidence == "low":
        return "Wait"
    if score >= 78:
        return "Buy"
    if score >= 66:
        return "Accumulate"
    if score >= 52:
        return "Hold"
    if score >= 42:
        return "Wait"
    if score >= 32:
        return "Reduce"
    return "Avoid"


def _stance(action: str) -> str:
    return {
        "Buy": "Constructive but risk-controlled",
        "Accumulate": "Constructive but cautious",
        "Hold": "Neutral to constructive",
        "Wait": "Neutral",
        "Reduce": "Defensive",
        "Avoid": "Defensive",
        "Sell": "Defensive",
    }[action]


def _educational_action(action: str) -> str:
    return {
        "Buy": "Only consider new exposure if it fits a documented plan, risk limit, and time horizon.",
        "Accumulate": "Consider gradual sizing only after confirming risk controls and avoiding price chasing.",
        "Hold": "Maintain observation and review whether the original thesis remains valid.",
        "Wait": "Wait for clearer evidence or a better risk/reward setup before acting.",
        "Reduce": "Consider reducing exposure if risk exceeds the plan or evidence deteriorates.",
        "Avoid": "Avoid new exposure until evidence improves and unknowns decline.",
        "Sell": "Consider exit only within a pre-defined risk plan; this is not an instruction.",
    }[action]


def _supporting_reasons(committee: List[Dict[str, Any]]) -> List[str]:
    return [f"{item['member']}: {item['interpretation']}" for item in committee if item.get("opinion") in {"constructive", "neutral"}][:5]


def _risk_reasons(committee: List[Dict[str, Any]]) -> List[str]:
    return [f"{item['member']}: {item['interpretation']}" for item in committee if item.get("member") == "Risk Manager" or item.get("opinion") == "cautious"][:5]


def _change_conditions(committee: List[Dict[str, Any]], regime: str) -> List[str]:
    conditions = [f"Market regime changes from {regime}."]
    for item in committee:
        conditions.extend(item.get("conditions_that_would_change_opinion", [])[:1])
    return list(dict.fromkeys(conditions))[:8]


def _committee_evidence(committee: List[Dict[str, Any]]) -> List[str]:
    evidence: List[str] = []
    for item in committee:
        evidence.extend(item.get("evidence", [])[:2])
    return list(dict.fromkeys(evidence))[:10]


def _committee_missing_data(committee: List[Dict[str, Any]]) -> List[str]:
    missing: List[str] = []
    for item in committee:
        missing.extend(item.get("missing_data", []))
    return list(dict.fromkeys(missing))[:10]


def _consensus(committee: List[Dict[str, Any]]) -> str:
    views = [item.get("opinion") for item in committee]
    if views.count("constructive") >= 3:
        return "Committee leans constructive, subject to risk controls."
    if views.count("cautious") >= 3:
        return "Committee leans cautious because risk or missing evidence is elevated."
    return "Committee is mixed; conclusion should stay probabilistic."


def _conflict(probabilities: Dict[str, Any] | None, committee: List[Dict[str, Any]]) -> str:
    if probabilities:
        bull = probabilities.get("bullish_probability", 0)
        bear = probabilities.get("bearish_probability", 0)
        if abs(float(bull) - float(bear)) < 12:
            return "Signals are conflicted; bullish and bearish probabilities are close."
    views = {item.get("opinion") for item in committee}
    if {"constructive", "cautious"}.issubset(views):
        return "Committee has both constructive and cautious views; position sizing matters."
    return "No major committee conflict was detected from available evidence."


def _minority(committee: List[Dict[str, Any]]) -> str:
    cautious = [item["member"] for item in committee if item.get("opinion") == "cautious"]
    constructive = [item["member"] for item in committee if item.get("opinion") == "constructive"]
    if cautious and constructive:
        return f"Minority caution from {', '.join(cautious[:2])} should be reviewed before acting."
    return "No strong minority view is available from current evidence."


def _trend(value: Any) -> str:
    if not isinstance(value, (int, float)):
        return "unavailable"
    if value > 3:
        return "up"
    if value < -3:
        return "down"
    return "sideways"


def _view(score: float) -> str:
    if score >= 62:
        return "constructive"
    if score <= 42:
        return "cautious"
    return "neutral"


def _confidence(score: float, missing: List[str]) -> str:
    if len(missing) >= 4:
        return "low"
    if score >= 65 or score <= 35:
        return "medium"
    return "medium" if len(missing) <= 2 else "low"
