from __future__ import annotations

from typing import Any, Dict

RESTRICTED_WORDS = ("guaranteed", "certain", "must buy", "sure profit")


def get_asset_type(symbol: str) -> str:
    if symbol.endswith("-USD"):
        return "crypto"
    if symbol.endswith("=F"):
        return "commodity"
    if symbol.endswith("=X") or symbol in {"DX-Y.NYB", "^TNX"}:
        return "macro"
    if symbol.startswith("^"):
        return "index"
    return "stock"


def build_ai_analysis(symbol: str, snapshot: Dict[str, Any] | None = None) -> Dict[str, Any]:
    price = (snapshot or {}).get("price")
    change_percent = (snapshot or {}).get("changePercent")
    trend = "sideways to constructive" if change_percent is None or change_percent >= 0 else "short-term pressure"
    risk_score = _risk_score(symbol, change_percent)
    volatility = "high" if risk_score >= 7 else "medium" if risk_score >= 4 else "low to medium"
    analysis = {
        "symbol": symbol,
        "trend": trend,
        "facts": [
            f"Latest available price is {price if price is not None else 'not available from provider'}.",
            f"Recent daily change is {round(change_percent, 2) if change_percent is not None else 'not available'}%.",
            "Data should be verified against a primary market source before making decisions.",
        ],
        "interpretation": [
            "The setup is น่าติดตาม, but confirmation from price action and volume is still important.",
            "A patient approach may favor รอจังหวะ rather than chasing a move after volatility expands.",
        ],
        "bullishFactors": [
            "Momentum may improve if price holds above recent support zones.",
            "Risk appetite and liquidity conditions can support continuation when macro conditions are favorable.",
        ],
        "bearishFactors": [
            "Breakdown below recent support would weaken the view.",
            "Unexpected macro, earnings, regulatory, or liquidity shocks can change the setup quickly.",
        ],
        "risks": [
            "เสี่ยงสูง for leveraged or concentrated positions.",
            "Volatility can invalidate short-term technical signals.",
            "Provider data can be delayed, missing, or revised.",
        ],
        "riskScore": risk_score,
        "volatilityLevel": volatility,
        "supportResistance": {
            "support": "Placeholder: derive from recent swing lows or moving averages.",
            "resistance": "Placeholder: derive from recent swing highs or volume nodes.",
        },
        "invalidation": "The view weakens if price loses key support with rising volume or if fundamentals deteriorate.",
        "cautiousActionPlan": [
            "ควรกำหนดแผนรับมือก่อนลงทุน, including position size and stop conditions.",
            "เหมาะกับผู้รับความเสี่ยงได้ only after confirming liquidity, volatility, and personal time horizon.",
            "Scale decisions gradually and avoid assuming any outcome is fixed.",
        ],
        "disclaimer": "This is not financial advice. No direct buy/sell instruction is provided.",
    }
    _validate_language(analysis)
    return analysis


def build_risk(symbol: str, snapshot: Dict[str, Any] | None = None) -> Dict[str, Any]:
    asset_type = get_asset_type(symbol)
    change_percent = (snapshot or {}).get("changePercent")
    score = _risk_score(symbol, change_percent)
    return {
        "symbol": symbol,
        "assetType": asset_type,
        "riskScore": score,
        "level": "High" if score >= 7 else "Medium" if score >= 4 else "Lower",
        "facts": ["Risk score is a heuristic and not a forecast.", "Volatility, liquidity, and macro sensitivity are considered qualitatively."],
        "interpretation": "Higher scores suggest wider price swings and a need for tighter risk controls.",
        "risks": ["Gap risk", "Liquidity risk", "Macro sensitivity", "Headline risk"],
        "cautiousActionPlan": ["Use smaller position sizing when volatility is elevated.", "Define invalidation before entry.", "Avoid leverage unless risk capacity is clear."],
        "disclaimer": "This is not financial advice.",
    }


def _risk_score(symbol: str, change_percent: float | None) -> int:
    asset_type = get_asset_type(symbol)
    base = {"crypto": 8, "commodity": 6, "macro": 5, "index": 4, "stock": 6}.get(asset_type, 5)
    if change_percent is not None and abs(change_percent) > 3:
        base += 1
    return max(1, min(10, base))


def _validate_language(payload: Dict[str, Any]) -> None:
    text = str(payload).lower()
    for word in RESTRICTED_WORDS:
        if word in text:
            raise ValueError(f"Restricted analysis wording detected: {word}")
