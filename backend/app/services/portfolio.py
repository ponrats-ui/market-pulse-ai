from __future__ import annotations

from typing import Any, Callable, Dict, List


def evaluate_portfolio(holdings: List[Dict[str, Any]], quote_fn: Callable[[str], Dict[str, Any]]) -> Dict[str, Any]:
    cash_balance = _portfolio_cash(holdings)
    transactions = _portfolio_transactions(holdings)
    realized_pl = _realized_pl(transactions)
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
            "daily_change_percent": _number(quote.get("change_percent")),
            "sector": quote.get("sector"),
            "asset_type": quote.get("asset_type"),
            "source": quote.get("source"),
            "timestamp": quote.get("timestamp"),
            "error": quote.get("error"),
        })
    for row in rows:
        value = row.get("market_value")
        row["allocation_percent"] = (value / total_value) * 100 if isinstance(value, (int, float)) and total_value else None
    return {
        "items": rows,
        "cash_balance": cash_balance,
        "total_value": total_value if total_value else None,
        "total_equity": (total_value + cash_balance) if total_value or cash_balance else None,
        "total_cost": total_cost if total_cost else None,
        "total_gain_loss": total_value - total_cost if total_value and total_cost else None,
        "total_gain_loss_percent": ((total_value - total_cost) / total_cost) * 100 if total_value and total_cost else None,
        "realized_gain_loss": realized_pl,
        "daily_return_percent": _weighted_daily_return(rows),
        "portfolio_return_percent": ((total_value - total_cost + realized_pl) / total_cost) * 100 if total_value and total_cost else None,
        "risk_score": _portfolio_risk_score(rows),
        "diversification_score": _diversification_score(rows),
        "sector_allocation": _sector_allocation(rows),
        "sharpe_ratio": None,
        "max_drawdown_percent": None,
        "performance_points": [],
        "transaction_history": transactions,
        "transaction_count": len(transactions),
        "analytics_status": "partial",
        "analytics_unavailable_reason": "Sharpe ratio, drawdown, and performance chart require persisted portfolio value history.",
        "currency_conversion": "Unavailable until FX conversion provider is configured.",
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


def _portfolio_cash(holdings: List[Dict[str, Any]]) -> float:
    for holding in holdings:
        value = _number(holding.get("cashBalance") or holding.get("cash_balance"))
        if value is not None:
            return value
    return 0.0


def _portfolio_transactions(holdings: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    for holding in holdings:
        transactions = holding.get("transactions")
        if isinstance(transactions, list):
            return [item for item in transactions if isinstance(item, dict)]
    return []


def _realized_pl(transactions: List[Dict[str, Any]]) -> float:
    positions: Dict[str, Dict[str, float]] = {}
    realized = 0.0
    for transaction in transactions:
        symbol = str(transaction.get("symbol", "")).strip().upper()
        side = str(transaction.get("side", "")).strip().lower()
        quantity = _number(transaction.get("quantity"))
        price = _number(transaction.get("price"))
        if not symbol or quantity is None or price is None or quantity <= 0:
            continue
        position = positions.setdefault(symbol, {"quantity": 0.0, "cost": 0.0})
        if side == "buy":
            position["quantity"] += quantity
            position["cost"] += quantity * price
        elif side == "sell" and position["quantity"] > 0:
            average_cost = position["cost"] / position["quantity"] if position["quantity"] else 0
            sold = min(quantity, position["quantity"])
            realized += (price - average_cost) * sold
            position["quantity"] -= sold
            position["cost"] -= average_cost * sold
    return realized


def _weighted_daily_return(rows: List[Dict[str, Any]]) -> float | None:
    total_value = sum(row["market_value"] for row in rows if isinstance(row.get("market_value"), (int, float)))
    if not total_value:
        return None
    weighted = 0.0
    for row in rows:
        value = row.get("market_value")
        change = row.get("daily_change_percent")
        if isinstance(value, (int, float)) and isinstance(change, (int, float)):
            weighted += (value / total_value) * change
    return weighted


def _portfolio_risk_score(rows: List[Dict[str, Any]]) -> int | None:
    if not rows:
        return None
    concentration = max((row.get("allocation_percent") or 0 for row in rows), default=0)
    score = 3
    if concentration >= 50:
        score += 3
    elif concentration >= 30:
        score += 2
    if len(rows) <= 2:
        score += 2
    return max(1, min(10, score))


def _diversification_score(rows: List[Dict[str, Any]]) -> int | None:
    if not rows:
        return None
    concentration = max((row.get("allocation_percent") or 0 for row in rows), default=100)
    score = 100 - int(concentration)
    if len(rows) >= 5:
        score += 10
    return max(0, min(100, score))


def _sector_allocation(rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    allocation: Dict[str, float] = {}
    for row in rows:
        sector = str(row.get("sector") or row.get("asset_type") or "Unavailable")
        percent = row.get("allocation_percent")
        if isinstance(percent, (int, float)):
            allocation[sector] = allocation.get(sector, 0.0) + percent
    return [{"sector": sector, "allocation_percent": percent} for sector, percent in sorted(allocation.items())]
