from __future__ import annotations

from typing import Any, Dict, List

RESTRICTED_WORDS = ("guaranteed", "certain", "must buy", "sure profit")


def get_asset_type(symbol: str, quote: Dict[str, Any] | None = None) -> str:
    if quote and quote.get("asset_type"):
        return str(quote["asset_type"])
    if symbol.endswith("-USD"):
        return "crypto"
    if symbol.endswith("=F"):
        return "commodity"
    if symbol.endswith("=X"):
        return "fx"
    if symbol in {"DX-Y.NYB", "^TNX"}:
        return "macro"
    if symbol.startswith("^"):
        return "index"
    if symbol.endswith(".BK"):
        return "thai_stock"
    return "global_stock"


def build_ai_analysis(symbol: str, quote: Dict[str, Any] | None = None) -> Dict[str, Any]:
    quote = quote or {}
    price = quote.get("price")
    change_percent = quote.get("change_percent")
    trend = "sideways to constructive" if change_percent is None or change_percent >= 0 else "short-term pressure"
    risk_score = _risk_score(symbol, change_percent, quote)
    volatility = _volatility_level(risk_score, change_percent)
    analysis = {
        "symbol": symbol,
        "trend": trend,
        "facts": [
            f"Latest available price is {price if price is not None else 'not available from provider'}.",
            f"Recent daily change is {round(change_percent, 2) if change_percent is not None else 'not available'}%.",
            f"Data source is {quote.get('source', 'unknown')} with timestamp {quote.get('timestamp', 'not available')}.",
            "Data should be verified against a primary market source before making decisions.",
        ],
        "interpretation": [
            "The setup is น่าติดตาม, but confirmation from price action and volume is still important.",
            "A patient approach may favor รอจังหวะ rather than chasing a move after volatility expands.",
        ],
        "bullish_factors": [
            "Momentum may improve if price holds above recent support zones.",
            "Risk appetite and liquidity conditions can support continuation when macro conditions are favorable.",
        ],
        "bearish_factors": [
            "Breakdown below recent support would weaken the view.",
            "Unexpected macro, earnings, regulatory, or liquidity shocks can change the setup quickly.",
        ],
        "risks": [
            "เสี่ยงสูง for leveraged or concentrated positions.",
            "Volatility can invalidate short-term technical signals.",
            "Provider data can be delayed, missing, or revised.",
        ],
        "risk_score": risk_score,
        "volatility_level": volatility,
        "support_resistance": {
            "support": "Placeholder: derive from recent swing lows or moving averages.",
            "resistance": "Placeholder: derive from recent swing highs or volume nodes.",
        },
        "invalidation": "The view weakens if price loses key support with rising volume or if fundamentals deteriorate.",
        "cautious_action_plan": [
            "ควรกำหนดแผนรับมือก่อนลงทุน, including position size and stop conditions.",
            "เหมาะกับผู้รับความเสี่ยงได้ only after confirming liquidity, volatility, and personal time horizon.",
            "Scale decisions gradually and avoid assuming any outcome is fixed.",
        ],
        "disclaimer": "This is not financial advice. No direct buy/sell instruction is provided.",
    }
    _validate_language(analysis)
    return analysis


def build_risk(symbol: str, quote: Dict[str, Any] | None = None, history: Dict[str, Any] | None = None) -> Dict[str, Any]:
    quote = quote or {}
    history = history or {}
    change_percent = quote.get("change_percent")
    realized_hint = _history_volatility_hint(history.get("points", []))
    score = _risk_score(symbol, change_percent, quote)
    if realized_hint == "high":
        score = min(10, score + 1)
    level = _volatility_level(score, change_percent)
    return {
        "symbol": symbol,
        "asset_type": get_asset_type(symbol, quote),
        "risk_score": score,
        "volatility_level": level,
        "main_risks": ["Gap risk", "Liquidity risk", "Macro sensitivity", "Headline risk", "Provider data delay risk"],
        "risk_controls": [
            "Use smaller position sizing when volatility is elevated.",
            "Define invalidation before entry.",
            "Avoid leverage unless risk capacity is clear.",
            "Review exposure correlation before adding risk.",
        ],
        "facts": [
            "Risk score is a heuristic and not a forecast.",
            f"Latest quote source is {quote.get('source', 'unknown')}.",
            f"Historical volatility hint is {realized_hint}.",
        ],
        "interpretation": "Higher scores suggest wider price swings and a need for tighter risk controls.",
        "disclaimer": "This is not financial advice.",
    }


def _risk_score(symbol: str, change_percent: float | None, quote: Dict[str, Any] | None = None) -> int:
    asset_type = get_asset_type(symbol, quote)
    base = {"crypto": 8, "commodity": 6, "macro": 5, "fx": 5, "index": 4, "thai_stock": 6, "global_stock": 6}.get(asset_type, 5)
    if change_percent is not None and abs(change_percent) > 3:
        base += 1
    return max(1, min(10, base))


def _volatility_level(risk_score: int, change_percent: float | None = None) -> str:
    if risk_score >= 7 or (change_percent is not None and abs(change_percent) >= 4):
        return "high"
    if risk_score >= 4:
        return "medium"
    return "low to medium"


def _history_volatility_hint(points: List[Dict[str, Any]]) -> str:
    closes = [point.get("close") for point in points if isinstance(point.get("close"), (int, float))]
    if len(closes) < 3:
        return "unknown"
    moves = []
    for previous, current in zip(closes, closes[1:]):
        if previous:
            moves.append(abs((current - previous) / previous) * 100)
    if not moves:
        return "unknown"
    average_move = sum(moves) / len(moves)
    if average_move >= 3:
        return "high"
    if average_move >= 1:
        return "medium"
    return "low"


def _validate_language(payload: Dict[str, Any]) -> None:
    text = str(payload).lower()
    for word in RESTRICTED_WORDS:
        if word in text:
            raise ValueError(f"Restricted analysis wording detected: {word}")
