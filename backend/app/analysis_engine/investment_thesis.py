from __future__ import annotations

from typing import Any, Dict


def build_investment_thesis(symbol: str, evidence: Dict[str, Any], factor_scores: Dict[str, float], probabilities: Dict[str, Any]) -> Dict[str, Any]:
    unavailable = evidence.get("unavailable_data", [])
    facts = evidence.get("facts", [])
    inputs = evidence.get("factor_inputs", {})
    trend = _trend(inputs.get("history_performance_percent"))
    valuation = _valuation_view(inputs.get("trailing_pe"), factor_scores.get("valuation", 50))
    risk_score = factor_scores.get("risk", 50)
    return {
        "symbol": symbol,
        "overview": _overview(symbol, trend, probabilities, unavailable),
        "thesis": _overview(symbol, trend, probabilities, unavailable),
        "bull_case": _bull_case(factor_scores, probabilities),
        "bear_case": _bear_case(factor_scores, probabilities, risk_score),
        "catalysts": _catalysts(factor_scores, unavailable),
        "key_risks": _key_risks(risk_score, unavailable),
        "risks": _key_risks(risk_score, unavailable),
        "valuation_view": valuation,
        "valuation": valuation,
        "key_metrics": facts,
        "what_to_monitor_next": _monitor_next(unavailable),
    }


def _overview(symbol: str, trend: str, probabilities: Dict[str, Any], unavailable: list[str]) -> str:
    if unavailable:
        return f"{symbol} has a {trend} evidence profile, but the thesis remains limited by missing provider data."
    return f"{symbol} has a {trend} evidence profile with bullish/neutral/bearish probabilities of {probabilities['bullish_probability']}%/{probabilities['neutral_probability']}%/{probabilities['bearish_probability']}%."


def _bull_case(scores: Dict[str, float], probabilities: Dict[str, Any]) -> str:
    strongest = _strongest_factor(scores)
    return f"Bull case depends on {strongest} staying supportive and bullish probability improving from {probabilities['bullish_probability']}%."


def _bear_case(scores: Dict[str, float], probabilities: Dict[str, Any], risk_score: float) -> str:
    weakest = _weakest_factor(scores)
    return f"Bear case is that {weakest} deteriorates or risk remains elevated; bearish probability is {probabilities['bearish_probability']}% and risk score is {round(risk_score, 1)}."


def _catalysts(scores: Dict[str, float], unavailable: list[str]) -> list[str]:
    catalysts = ["Provider-confirmed trend improvement", "Improving liquidity", "Lower realized volatility"]
    if scores.get("valuation", 50) >= 60:
        catalysts.append("Valuation support relative to returned fundamentals")
    if "news" not in " ".join(unavailable).lower():
        catalysts.append("Confirmed asset-specific news catalyst")
    return catalysts


def _key_risks(risk_score: float, unavailable: list[str]) -> list[str]:
    risks = ["Volatility shock", "Liquidity deterioration", "Macro or rate regime reversal"]
    if risk_score <= 45:
        risks.append("Risk controls may dominate upside signals")
    if unavailable:
        risks.append("Missing provider data limits confidence")
    return risks


def _monitor_next(unavailable: list[str]) -> list[str]:
    monitor = ["Price trend", "Volatility", "Volume/liquidity", "Risk score changes", "Probability conflict"]
    if unavailable:
        monitor.append("Provider data completeness")
    return monitor


def _trend(value: Any) -> str:
    if not isinstance(value, (int, float)):
        return "limited"
    if value > 3:
        return "constructive"
    if value < -3:
        return "defensive"
    return "balanced"


def _valuation_view(pe: Any, score: float) -> str:
    if pe is None:
        return "Valuation view is limited because provider PE or equivalent valuation data is unavailable."
    if score >= 60:
        return f"Valuation appears relatively supportive from provider PE {pe}, but peer comparison is still required."
    if score <= 40:
        return f"Valuation risk is elevated from provider PE {pe}; earnings sensitivity should be monitored."
    return f"Valuation is mixed from provider PE {pe}; compare against peers and the asset's own history."


def _strongest_factor(scores: Dict[str, float]) -> str:
    if not scores:
        return "evidence quality"
    return max(scores, key=lambda key: scores.get(key, 0)).replace("_", " ")


def _weakest_factor(scores: Dict[str, float]) -> str:
    if not scores:
        return "missing evidence"
    return min(scores, key=lambda key: scores.get(key, 0)).replace("_", " ")
