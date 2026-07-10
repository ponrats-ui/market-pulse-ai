from __future__ import annotations

from typing import Any, Callable, Dict, List

from app.services.analysis import build_risk


def build_comparison(symbols: List[str], quote_fn: Callable[[str], Dict[str, Any]], history_fn: Callable[[str, str, str], Dict[str, Any]]) -> Dict[str, Any]:
    selected = [symbol.strip() for symbol in symbols if symbol.strip()][:5]
    items: List[Dict[str, Any]] = []
    histories: Dict[str, Dict[str, Any]] = {}
    for symbol in selected:
        quote = quote_fn(symbol)
        history = history_fn(symbol, "1y", "1d")
        histories[symbol] = history
        risk = build_risk(symbol, quote, history)
        metrics = _history_metrics(history)
        correlation = _correlation_to_first(symbol, selected, histories)
        items.append({
            "symbol": symbol,
            "name": quote.get("name", symbol),
            "asset_type": quote.get("asset_type", "unknown"),
            "price": quote.get("price"),
            "change_percent": quote.get("change_percent"),
            "performance_1d_percent": quote.get("change_percent"),
            "performance_1mo_percent": metrics.get("performance_percent"),
            "performance_1w_percent": metrics.get("performance_1w_percent"),
            "performance_ytd_percent": metrics.get("performance_ytd_percent"),
            "realized_volatility_percent": metrics.get("realized_volatility_percent"),
            "max_drawdown_percent": metrics.get("max_drawdown_percent"),
            "trend": metrics.get("trend"),
            "market_cap": quote.get("market_cap"),
            "pe": quote.get("trailing_pe"),
            "pb": quote.get("price_to_book"),
            "ps": quote.get("price_to_sales"),
            "eps_growth": quote.get("earnings_growth"),
            "revenue_growth": quote.get("revenue_growth"),
            "debt": quote.get("debt_to_equity"),
            "roe": quote.get("return_on_equity"),
            "roa": quote.get("return_on_assets"),
            "roic": quote.get("return_on_invested_capital"),
            "beta": quote.get("beta"),
            "dividend_yield": quote.get("dividend_yield"),
            "sector": quote.get("sector"),
            "correlation_to_first": correlation,
            "relative_strength": metrics.get("relative_strength"),
            "ai_opinion": _ai_opinion(symbol, metrics, risk),
            "investment_thesis": _investment_thesis(symbol, metrics, risk, quote),
            "recommendation": _recommendation(metrics, risk),
            "currency": quote.get("currency"),
            "volatility_estimate": risk.get("volatility_level", "unknown"),
            "risk_score": risk.get("risk_score"),
            "source": quote.get("source", "unknown"),
            "timestamp": quote.get("timestamp"),
            "error": quote.get("error"),
        })
    return {
        "symbols": selected,
        "items": items,
        "performance_points": _performance_points(selected, histories),
        "correlation_matrix": _correlation_matrix(selected, histories),
        "radar_chart": _radar_chart(items),
        "summary": _summary(items),
        "disclaimer": "This is not financial advice.",
    }


def _performance_points(symbols: List[str], histories: Dict[str, Dict[str, Any]]) -> List[Dict[str, Any]]:
    normalized: Dict[str, List[Dict[str, Any]]] = {}
    max_len = 0
    for symbol in symbols:
        points = histories.get(symbol, {}).get("points", [])
        closes = [point for point in points if isinstance(point.get("close"), (int, float)) and point.get("close")]
        if not closes:
            normalized[symbol] = []
            continue
        base = closes[0]["close"]
        series = [{"time": point.get("time"), symbol: ((point.get("close") - base) / base) * 100} for point in closes]
        normalized[symbol] = series
        max_len = max(max_len, len(series))
    rows: List[Dict[str, Any]] = []
    for index in range(max_len):
        row: Dict[str, Any] = {}
        for symbol in symbols:
            series = normalized.get(symbol, [])
            if index < len(series):
                row["time"] = row.get("time") or series[index].get("time")
                row[symbol] = series[index].get(symbol)
        if row:
            rows.append(row)
    return rows


def _summary(items: List[Dict[str, Any]]) -> Dict[str, str]:
    if not items:
        return {"th": "ยังไม่มีสินทรัพย์สำหรับเปรียบเทียบ", "en": "No assets were selected for comparison."}
    leader = max(items, key=lambda item: item.get("performance_1mo_percent") if isinstance(item.get("performance_1mo_percent"), (int, float)) else -999)
    riskiest = max(items, key=lambda item: item.get("risk_score") if isinstance(item.get("risk_score"), (int, float)) else 0)
    return {
        "th": f"{leader.get('symbol')} แข็งแรงกว่าในชุดนี้จากผลตอบแทนย้อนหลังที่ผู้ให้บริการส่งกลับ ขณะที่ {riskiest.get('symbol')} มีคะแนนความเสี่ยงสูงกว่า ควรประเมินขนาดสถานะและความผันผวนก่อนตัดสินใจ",
        "en": f"{leader.get('symbol')} currently looks stronger based on provider-returned historical performance, while {riskiest.get('symbol')} carries the higher risk score. Position size and volatility should be reviewed before any decision.",
    }


def _history_metrics(history: Dict[str, Any]) -> Dict[str, Any]:
    points = history.get("points", [])
    closes_with_time = [(point.get("time"), float(point["close"])) for point in points if isinstance(point.get("close"), (int, float)) and point.get("close")]
    closes = [close for _, close in closes_with_time]
    if len(closes) < 2:
        return {"performance_percent": None, "performance_1w_percent": None, "performance_ytd_percent": None, "realized_volatility_percent": None, "max_drawdown_percent": None, "trend": "unavailable"}
    performance = ((closes[-1] - closes[0]) / closes[0]) * 100
    performance_1w = _window_performance(closes, 5)
    performance_ytd = _ytd_performance(closes_with_time)
    returns = [((closes[index] - closes[index - 1]) / closes[index - 1]) * 100 for index in range(1, len(closes)) if closes[index - 1]]
    mean_return = sum(returns) / len(returns) if returns else 0
    variance = sum((value - mean_return) ** 2 for value in returns) / len(returns) if returns else 0
    realized_volatility = variance ** 0.5
    peak = closes[0]
    max_drawdown = 0.0
    for close in closes:
        peak = max(peak, close)
        drawdown = ((close - peak) / peak) * 100 if peak else 0
        max_drawdown = min(max_drawdown, drawdown)
    trend = "uptrend" if performance > 2 else "downtrend" if performance < -2 else "sideways"
    return {
        "performance_percent": performance,
        "relative_strength": performance,
        "performance_1w_percent": performance_1w,
        "performance_ytd_percent": performance_ytd,
        "realized_volatility_percent": realized_volatility,
        "max_drawdown_percent": max_drawdown,
        "trend": trend,
    }


def _correlation_to_first(symbol: str, symbols: List[str], histories: Dict[str, Dict[str, Any]]) -> float | None:
    if not symbols or symbol == symbols[0]:
        return 1.0 if symbol == symbols[0] else None
    first_returns = _returns(histories.get(symbols[0], {}).get("points", []))
    current_returns = _returns(histories.get(symbol, {}).get("points", []))
    length = min(len(first_returns), len(current_returns))
    if length < 3:
        return None
    return _correlation(first_returns[-length:], current_returns[-length:])


def _correlation_matrix(symbols: List[str], histories: Dict[str, Dict[str, Any]]) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    for left in symbols:
        row: Dict[str, Any] = {"symbol": left}
        left_returns = _returns(histories.get(left, {}).get("points", []))
        for right in symbols:
            if left == right:
                row[right] = 1.0
                continue
            right_returns = _returns(histories.get(right, {}).get("points", []))
            length = min(len(left_returns), len(right_returns))
            row[right] = _correlation(left_returns[-length:], right_returns[-length:]) if length >= 3 else None
        rows.append(row)
    return rows


def _radar_chart(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    return [
        {
            "symbol": item["symbol"],
            "momentum": _scale(item.get("performance_1mo_percent"), -20, 20),
            "volatility_control": 100 - _scale(item.get("realized_volatility_percent"), 0, 8),
            "valuation": 100 - _scale(item.get("pe"), 0, 80),
            "profitability": _scale(item.get("roe"), -0.2, 0.5),
            "risk_control": 100 - ((item.get("risk_score") or 10) * 10),
        }
        for item in items
    ]


def _scale(value: Any, low: float, high: float) -> float | None:
    if not isinstance(value, (int, float)) or high == low:
        return None
    return max(0, min(100, ((float(value) - low) / (high - low)) * 100))


def _returns(points: List[Dict[str, Any]]) -> List[float]:
    closes = [float(point["close"]) for point in points if isinstance(point.get("close"), (int, float)) and point.get("close")]
    return [((current - previous) / previous) * 100 for previous, current in zip(closes, closes[1:]) if previous]


def _correlation(left: List[float], right: List[float]) -> float | None:
    if len(left) != len(right) or len(left) < 3:
        return None
    left_mean = sum(left) / len(left)
    right_mean = sum(right) / len(right)
    numerator = sum((a - left_mean) * (b - right_mean) for a, b in zip(left, right))
    left_var = sum((a - left_mean) ** 2 for a in left)
    right_var = sum((b - right_mean) ** 2 for b in right)
    if not left_var or not right_var:
        return None
    return numerator / ((left_var * right_var) ** 0.5)


def _ai_opinion(symbol: str, metrics: Dict[str, Any], risk: Dict[str, Any]) -> str:
    trend = metrics.get("trend", "unavailable")
    score = risk.get("risk_score")
    if score is None:
        return f"{symbol}: evidence is incomplete; wait for more data."
    return f"{symbol}: {trend} with risk score {score}/10; review position size before acting."


def _investment_thesis(symbol: str, metrics: Dict[str, Any], risk: Dict[str, Any], quote: Dict[str, Any]) -> Dict[str, Any]:
    evidence = [
        f"One-month performance from provider history: {metrics.get('performance_percent') if metrics.get('performance_percent') is not None else 'Unavailable'}.",
        f"Risk score from risk engine: {risk.get('risk_score') if risk.get('risk_score') is not None else 'Unavailable'}.",
        f"Quote source: {quote.get('source', 'unknown')}.",
    ]
    return {
        "summary": _ai_opinion(symbol, metrics, risk),
        "evidence": evidence,
        "confidence": "medium" if metrics.get("performance_percent") is not None and risk.get("risk_score") is not None else "low",
        "limitations": ["Comparison uses available provider data only; missing fundamentals remain unavailable."],
    }


def _recommendation(metrics: Dict[str, Any], risk: Dict[str, Any]) -> str:
    score = risk.get("risk_score")
    performance = metrics.get("performance_percent")
    if score is None or performance is None:
        return "Data unavailable"
    if score >= 7:
        return "รอจังหวะและควบคุมความเสี่ยง"
    if performance > 5 and score <= 5:
        return "น่าติดตาม แต่ไม่ใช่คำแนะนำซื้อขาย"
    return "ติดตามต่อและประเมินหลักฐานเพิ่ม"


def _window_performance(closes: List[float], sessions: int) -> float | None:
    if len(closes) <= sessions:
        return None
    base = closes[-sessions - 1]
    return ((closes[-1] - base) / base) * 100 if base else None


def _ytd_performance(closes_with_time: List[tuple[Any, float]]) -> float | None:
    if not closes_with_time:
        return None
    latest_time = str(closes_with_time[-1][0] or "")
    current_year = latest_time[:4]
    if not current_year:
        return None
    ytd_points = [close for timestamp, close in closes_with_time if str(timestamp or "").startswith(current_year)]
    if len(ytd_points) < 2 or not ytd_points[0]:
        return None
    return ((ytd_points[-1] - ytd_points[0]) / ytd_points[0]) * 100
