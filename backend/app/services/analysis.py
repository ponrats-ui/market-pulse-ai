from __future__ import annotations

from typing import Any, Dict, List

from app.analysis_engine import build_adaptive_recommendation

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


def build_ai_analysis(symbol: str, quote: Dict[str, Any] | None = None, history: Dict[str, Any] | None = None, profile: str = "Balanced") -> Dict[str, Any]:
    quote = quote or {}
    adaptive = build_adaptive_recommendation(symbol, quote, history, profile)
    adaptive_aliases = _adaptive_aliases(adaptive)
    price = quote.get("price")
    change_percent = quote.get("change_percent")
    if price is None or change_percent is None:
        return {
            "symbol": symbol,
            "trend": "unavailable",
            "facts": ["There is currently insufficient market data to produce a reliable analysis."],
            "interpretation": ["ข้อมูลยังไม่เพียงพอสำหรับการวิเคราะห์ที่น่าเชื่อถือ"],
            "bullish_factors": [],
            "bearish_factors": [],
            "risks": ["Provider data is unavailable or incomplete."],
            "risk_score": None,
            "volatility_level": "unavailable",
            "support_resistance": {"support": "Unavailable", "resistance": "Unavailable"},
            "invalidation": "Unavailable until sufficient market data is available.",
            "cautious_action_plan": ["Wait for complete market data before forming a view."],
            "disclaimer": "This is not financial advice.",
            "data_hub": quote.get("data_hub"),
            "adaptive_engine": adaptive,
            **adaptive_aliases,
        }
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
            "The setup is worth monitoring, but confirmation from price action and volume is still important.",
            "A patient approach may favor waiting for a cleaner entry rather than chasing a move after volatility expands.",
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
            "Leveraged or concentrated positions can carry high risk.",
            "Volatility can invalidate short-term technical signals.",
            "Provider data can be delayed, missing, or revised.",
        ],
        "risk_score": risk_score,
        "volatility_level": volatility,
        "support_resistance": {
            "support": "Unavailable until technical swing levels are calculated from historical prices.",
            "resistance": "Unavailable until technical swing levels are calculated from historical prices.",
        },
        "invalidation": "The view weakens if price loses key support with rising volume or if fundamentals deteriorate.",
        "cautious_action_plan": [
            "Define a risk plan before committing capital, including position size and stop conditions.",
            "Confirm liquidity, volatility, and personal time horizon before taking exposure.",
            "Scale decisions gradually and avoid assuming any outcome is fixed.",
        ],
        "disclaimer": "This is not financial advice. No direct buy/sell instruction is provided.",
        "data_hub": quote.get("data_hub"),
        "adaptive_engine": adaptive,
        **adaptive_aliases,
    }
    _validate_language(analysis)
    return analysis


def build_risk(symbol: str, quote: Dict[str, Any] | None = None, history: Dict[str, Any] | None = None) -> Dict[str, Any]:
    quote = quote or {}
    history = history or {}
    change_percent = quote.get("change_percent")
    realized_hint = _history_volatility_hint(history.get("points", []))
    if change_percent is None or realized_hint == "unknown":
        return {
            "symbol": symbol,
            "asset_type": get_asset_type(symbol, quote),
            "risk_score": None,
            "volatility_level": "unavailable",
            "main_risks": ["Unable to estimate risk."],
            "risk_controls": ["Wait for complete quote and historical price data before estimating risk."],
            "facts": ["Risk analysis requires real price movement and historical volatility data."],
            "interpretation": "Unable to estimate risk.",
            "categories": _risk_categories(symbol, None, "unknown"),
            "disclaimer": "This is not financial advice.",
            "data_hub": quote.get("data_hub"),
        }
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
        "categories": _risk_categories(symbol, score, realized_hint),
        "disclaimer": "This is not financial advice.",
        "data_hub": quote.get("data_hub"),
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


def _risk_categories(symbol: str, score: int | None, volatility_hint: str) -> List[Dict[str, Any]]:
    asset_type = get_asset_type(symbol)
    base_score = score or 0
    definitions = [
        ("Volatility", base_score, volatility_hint, "Use position sizing and avoid leverage when volatility rises."),
        ("Liquidity", 5 if asset_type in {"crypto", "thai_stock"} else 3, "medium", "Check spread, volume, and order size before entering."),
        ("Gap Risk", 6 if asset_type in {"global_stock", "thai_stock", "crypto"} else 4, "medium", "Avoid oversized overnight exposure around events."),
        ("Interest Rate", 7 if symbol in {"TLT", "^TNX"} or asset_type in {"macro", "reit"} else 4, "medium", "Review rate-sensitive exposure and duration."),
        ("Macro", 6 if asset_type in {"index", "commodity", "fx", "macro"} else 4, "medium", "Track central bank, inflation, and growth releases."),
        ("Correlation", 5, "medium", "Compare with existing portfolio exposures before adding risk."),
        ("Currency", 6 if asset_type in {"thai_stock", "fx"} or symbol.endswith(".BK") else 3, "medium", "Consider base currency and FX movement."),
        ("Concentration", 5, "medium", "Set maximum allocation per asset and sector."),
        ("Tail Risk", 7 if asset_type == "crypto" else 5, "medium", "Plan for extreme moves and liquidity stress."),
        ("Headline Risk", 6 if asset_type in {"crypto", "global_stock", "thai_stock"} else 4, "medium", "Monitor news and avoid reacting to unverified headlines."),
    ]
    return [
        {
            "category": category,
            "score": _bounded_risk(value),
            "probability": _probability(value),
            "severity": _severity(value),
            "trend": _risk_trend(value, volatility_hint),
            "evidence": f"{category} risk uses asset class {asset_type} and volatility hint {hint}.",
            "mitigation": mitigation,
        }
        for category, value, hint, mitigation in definitions
    ]


def _bounded_risk(value: int) -> int:
    return max(1, min(10, int(value or 1)))


def _probability(value: int) -> str:
    return "high" if value >= 7 else "medium" if value >= 4 else "low"


def _severity(value: int) -> str:
    return "high" if value >= 7 else "medium" if value >= 4 else "low"


def _risk_trend(value: int, volatility_hint: str) -> str:
    if value >= 7 or volatility_hint == "high":
        return "rising"
    if value <= 3 and volatility_hint == "low":
        return "contained"
    return "stable"


def _validate_language(payload: Dict[str, Any]) -> None:
    text = str(payload).lower()
    for word in RESTRICTED_WORDS:
        if word in text:
            raise ValueError(f"Restricted analysis wording detected: {word}")


def _adaptive_aliases(adaptive: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "algorithm_version": adaptive["algorithm_version"],
        "profile": adaptive["profile"],
        "asset_class": adaptive["asset_class"],
        "market_regime": adaptive["market_regime"],
        "adaptive_weights": adaptive["adaptive_weights"],
        "evidence": adaptive["evidence"],
        "confidence": adaptive["confidence"],
        "probability": adaptive["probability"],
        "investment_thesis": adaptive["investment_thesis"],
        "risk_engine": adaptive["risk_engine"],
        "limitations": adaptive["limitations"],
        "timestamp": adaptive["timestamp"],
    }
