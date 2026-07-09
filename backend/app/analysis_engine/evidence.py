from __future__ import annotations

from typing import Any, Dict, List


def build_evidence(symbol: str, quote: Dict[str, Any] | None = None, history: Dict[str, Any] | None = None) -> Dict[str, Any]:
    quote = quote or {}
    history = history or {}
    points = history.get("points", [])
    closes = [point.get("close") for point in points if isinstance(point.get("close"), (int, float)) and point.get("close")]
    unavailable = []
    if quote.get("price") is None:
        unavailable.append("latest_price")
    if quote.get("change_percent") is None:
        unavailable.append("daily_change")
    if len(closes) < 3:
        unavailable.append("historical_price_series")
    if quote.get("market_cap") is None:
        unavailable.append("market_cap")
    if quote.get("trailing_pe") is None:
        unavailable.append("trailing_pe")

    daily_change = quote.get("change_percent")
    history_performance = _performance(closes)
    average_move = _average_absolute_move(closes)
    facts = [
        f"Symbol under review: {symbol}.",
        f"Latest price: {quote.get('price') if quote.get('price') is not None else 'unavailable'}.",
        f"Daily change: {round(daily_change, 2) if isinstance(daily_change, (int, float)) else 'unavailable'}%.",
        f"Provider source: {quote.get('source', 'unknown')}.",
    ]
    if history_performance is not None:
        facts.append(f"Historical performance over returned series: {round(history_performance, 2)}%.")
    if average_move is not None:
        facts.append(f"Average absolute close-to-close move: {round(average_move, 2)}%.")

    return {
        "symbol": symbol,
        "raw_data": {"quote": quote, "history": history},
        "factor_inputs": {
            "daily_change_percent": daily_change,
            "history_performance_percent": history_performance,
            "average_absolute_move_percent": average_move,
            "market_cap": quote.get("market_cap"),
            "trailing_pe": quote.get("trailing_pe"),
            "volume": quote.get("volume"),
            "asset_type": quote.get("asset_type"),
        },
        "facts": facts,
        "unavailable_data": unavailable,
        "assumptions": [
            "Provider data may be delayed, revised, or incomplete.",
            "The engine does not infer unavailable fundamentals.",
            "Recommendation language is conservative and not a buy/sell instruction.",
        ],
    }


def _performance(closes: List[float]) -> float | None:
    if len(closes) < 2 or not closes[0]:
        return None
    return ((closes[-1] - closes[0]) / closes[0]) * 100


def _average_absolute_move(closes: List[float]) -> float | None:
    if len(closes) < 3:
        return None
    moves = [abs((current - previous) / previous) * 100 for previous, current in zip(closes, closes[1:]) if previous]
    return sum(moves) / len(moves) if moves else None
