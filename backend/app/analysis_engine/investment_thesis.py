from __future__ import annotations

from typing import Any, Dict


def build_investment_thesis(symbol: str, evidence: Dict[str, Any], factor_scores: Dict[str, float], probabilities: Dict[str, Any]) -> Dict[str, Any]:
    unavailable = evidence.get("unavailable_data", [])
    facts = evidence.get("facts", [])
    return {
        "symbol": symbol,
        "thesis": "Evidence is mixed until more complete provider data is available." if unavailable else "The thesis is based on provider-returned trend, liquidity, valuation, quality, and risk evidence.",
        "bull_case": _case_text("bull", factor_scores, probabilities),
        "bear_case": _case_text("bear", factor_scores, probabilities),
        "catalysts": ["Provider-confirmed trend improvement", "Improving liquidity", "Macro regime support"],
        "risks": ["Data gaps", "Volatility shock", "Macro reversal", "Liquidity deterioration"],
        "valuation": "Unavailable" if "trailing_pe" in unavailable else "Valuation score is included when trailing PE is returned by provider.",
        "key_metrics": facts,
        "what_to_monitor_next": ["Price trend", "Volatility", "Volume/liquidity", "Macro/news regime", "Provider data completeness"],
    }


def _case_text(case_type: str, factor_scores: Dict[str, float], probabilities: Dict[str, Any]) -> str:
    if case_type == "bull":
        return f"Bull case depends on momentum and quality evidence improving; estimated bullish probability is {probabilities['bullish_probability']}%."
    return f"Bear case depends on risk, volatility, or missing evidence deteriorating; estimated bearish probability is {probabilities['bearish_probability']}%."
