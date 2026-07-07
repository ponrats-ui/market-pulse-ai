from __future__ import annotations

from typing import Any, Callable, Dict, List

from app.services.analysis import build_risk


def build_comparison(symbols: List[str], quote_fn: Callable[[str], Dict[str, Any]], history_fn: Callable[[str, str, str], Dict[str, Any]]) -> Dict[str, Any]:
    selected = [symbol.strip() for symbol in symbols if symbol.strip()][:6]
    items: List[Dict[str, Any]] = []
    histories: Dict[str, Dict[str, Any]] = {}
    for symbol in selected:
        quote = quote_fn(symbol)
        history = history_fn(symbol, "1mo", "1d")
        histories[symbol] = history
        risk = build_risk(symbol, quote, history)
        items.append({
            "symbol": symbol,
            "name": quote.get("name", symbol),
            "asset_type": quote.get("asset_type", "unknown"),
            "price": quote.get("price"),
            "change_percent": quote.get("change_percent"),
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
    leader = max(items, key=lambda item: item.get("change_percent") if isinstance(item.get("change_percent"), (int, float)) else -999)
    riskiest = max(items, key=lambda item: item.get("risk_score") if isinstance(item.get("risk_score"), (int, float)) else 0)
    return {
        "th": f"{leader.get('symbol')} แสดงแรงเปรียบเทียบระยะสั้นดีกว่าในชุดนี้ ขณะที่ {riskiest.get('symbol')} มีคะแนนความเสี่ยงสูงกว่า ควรประเมินขนาดสถานะและความผันผวนก่อนตัดสินใจ",
        "en": f"{leader.get('symbol')} has the stronger short-term relative move in this set, while {riskiest.get('symbol')} carries the higher risk score. Position size and volatility should be reviewed before any decision.",
    }
