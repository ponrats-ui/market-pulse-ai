from __future__ import annotations

from typing import Any, Callable, Dict, List


def evaluate_portfolio(holdings: List[Dict[str, Any]], quote_fn: Callable[[str], Dict[str, Any]]) -> Dict[str, Any]:
    rows: List[Dict[str, Any]] = []
    total_value = 0.0
    total_cost = 0.0
    for holding in holdings:
        symbol = str(holding.get("symbol", "")).strip().upper()
        quantity = _number(holding.get("quantity"))
        average_cost = _number(holding.get("averageCost") or holding.get("average_cost"))
        if not symbol or quantity is None or average_cost is None or quantity <= 0:
            continue
        quote = quote_fn(symbol)
        price = _number(quote.get("price"))
        cost = quantity * average_cost
        value = quantity * price if price is not None else None
        if value is not None:
            total_value += value
        total_cost += cost
        rows.append({
            "symbol": symbol,
            "quantity": quantity,
            "average_cost": average_cost,
            "last_price": price,
            "currency": quote.get("currency"),
            "market_value": value,
            "cost_basis": cost,
            "gain_loss": value - cost if value is not None else None,
            "gain_loss_percent": ((value - cost) / cost) * 100 if value is not None and cost else None,
            "source": quote.get("source"),
            "timestamp": quote.get("timestamp"),
            "error": quote.get("error"),
        })
    for row in rows:
        value = row.get("market_value")
        row["allocation_percent"] = (value / total_value) * 100 if isinstance(value, (int, float)) and total_value else None
    return {
        "items": rows,
        "total_value": total_value if total_value else None,
        "total_cost": total_cost if total_cost else None,
        "total_gain_loss": total_value - total_cost if total_value and total_cost else None,
        "total_gain_loss_percent": ((total_value - total_cost) / total_cost) * 100 if total_value and total_cost else None,
        "source": "live_quotes",
        "disclaimer": "This is not financial advice.",
    }


def _number(value: Any) -> float | None:
    try:
        if value in (None, ""):
            return None
        return float(value)
    except (TypeError, ValueError):
        return None
