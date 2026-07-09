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
            "sector": quote.get("sector"),
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
        "performance_1w_percent": performance_1w,
        "performance_ytd_percent": performance_ytd,
        "realized_volatility_percent": realized_volatility,
        "max_drawdown_percent": max_drawdown,
        "trend": trend,
    }


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
