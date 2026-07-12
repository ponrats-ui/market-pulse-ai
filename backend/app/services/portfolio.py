from __future__ import annotations

from typing import Any, Callable, Dict, List

from app.data_hub.symbol_resolver import resolve_symbol


def evaluate_portfolio(holdings: List[Dict[str, Any]], quote_fn: Callable[[str], Dict[str, Any]]) -> Dict[str, Any]:
    cash_balance = _portfolio_cash(holdings)
    transactions = _portfolio_transactions(holdings)
    unsupported: List[Dict[str, str]] = []
    transaction_errors: List[Dict[str, Any]] = []
    if transactions:
        cash_balance, position_inputs, realized_pl, unsupported, transaction_errors, transaction_history = _positions_from_transactions(cash_balance, transactions)
    else:
        position_inputs, unsupported = _positions_from_holdings(holdings)
        realized_pl = 0.0
        transaction_history = []

    rows: List[Dict[str, Any]] = []
    total_value = 0.0
    total_cost = 0.0
    stale_quotes: List[Dict[str, str]] = []
    for holding in position_inputs:
        symbol = str(holding.get("symbol", "")).strip().upper()
        quantity = _number(holding.get("quantity"))
        average_cost = _number(holding.get("averageCost") or holding.get("average_cost"))
        if not symbol or quantity is None or average_cost is None or quantity <= 0:
            continue
        quote = quote_fn(symbol)
        price = _number(quote.get("price"))
        cost = quantity * average_cost
        value = quantity * price if price is not None else None
        daily_change_percent = _number(quote.get("change_percent"))
        daily_pl = value * (daily_change_percent / 100) if value is not None and daily_change_percent is not None else None
        if value is not None:
            total_value += value
        total_cost += cost
        stale_reason = _stale_reason(quote)
        if stale_reason:
            stale_quotes.append({"symbol": symbol, "reason": stale_reason})
        rows.append({
            "symbol": symbol,
            "quantity": quantity,
            "average_cost": average_cost,
            "last_price": price,
            "currency": quote.get("currency"),
            "market_value": value,
            "cost_basis": cost,
            "gain_loss": value - cost if value is not None else None,
            "unrealized_gain_loss": value - cost if value is not None else None,
            "gain_loss_percent": ((value - cost) / cost) * 100 if value is not None and cost else None,
            "daily_change_percent": daily_change_percent,
            "daily_pl": daily_pl,
            "sector": quote.get("sector"),
            "country": quote.get("country"),
            "asset_type": quote.get("asset_type"),
            "source": quote.get("source"),
            "timestamp": quote.get("timestamp"),
            "stale": bool(stale_reason),
            "stale_reason": stale_reason,
            "error": quote.get("error"),
        })
    for row in rows:
        value = row.get("market_value")
        row["allocation_percent"] = (value / total_value) * 100 if isinstance(value, (int, float)) and total_value else None

    total_equity = total_value + cash_balance
    total_gain_loss = total_value - total_cost if total_value and total_cost else None
    analytics = _analytics(rows, cash_balance, total_equity, total_cost, total_gain_loss, realized_pl)
    return {
        "items": rows,
        "cash_balance": cash_balance,
        "initial_cash": _portfolio_cash(holdings),
        "total_value": total_value if total_value else None,
        "total_equity": total_equity if total_value or cash_balance else None,
        "total_portfolio_value": total_equity if total_value or cash_balance else None,
        "total_cost": total_cost if total_cost else None,
        "total_gain_loss": total_gain_loss,
        "total_unrealized_gain_loss": total_gain_loss,
        "total_gain_loss_percent": (total_gain_loss / total_cost) * 100 if total_gain_loss is not None and total_cost else None,
        "realized_gain_loss": realized_pl,
        "daily_pl": sum(row.get("daily_pl") or 0 for row in rows) if rows else None,
        "daily_return_percent": _weighted_daily_return(rows),
        "portfolio_return_percent": ((total_value - total_cost + realized_pl) / total_cost) * 100 if total_value and total_cost else None,
        "risk_score": _portfolio_risk_score(rows),
        "diversification_score": _diversification_score(rows),
        "concentration": _concentration(rows),
        "asset_allocation": _allocation(rows, "asset_type", "asset_type"),
        "sector_allocation": _allocation(rows, "sector", "sector"),
        "country_allocation": _allocation(rows, "country", "country"),
        "currency_allocation": _allocation(rows, "currency", "currency"),
        "cash_ratio_percent": (cash_balance / total_equity) * 100 if total_equity else None,
        "weekly_return_percent": None,
        "monthly_return_percent": None,
        "volatility_percent": analytics["volatility_percent"],
        "sharpe_ratio": analytics["sharpe_ratio"],
        "max_drawdown_percent": analytics["max_drawdown_percent"],
        "correlation": analytics["correlation"],
        "performance_points": [],
        "transaction_history": transaction_history,
        "transaction_count": len(transaction_history),
        "transaction_errors": transaction_errors,
        "unsupported_symbols": unsupported,
        "stale_quotes": stale_quotes,
        "analytics_status": analytics["status"],
        "analytics_unavailable_reason": analytics["unavailable_reason"],
        "portfolio_coach": _coach(rows, cash_balance, total_equity, stale_quotes),
        "scenarios": _scenarios(rows, cash_balance, total_equity),
        "persistence": {
            "mode": "local_simulated",
            "cloud_sync_ready": False,
            "reset_supported": True,
        },
        "currency_conversion": "Unavailable until FX conversion provider is configured.",
        "source": "live_quotes",
        "disclaimer": "This is educational portfolio analysis for simulated paper trading only. This is not financial advice.",
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
        value = _number(holding.get("cashBalance") or holding.get("cash_balance") or holding.get("initialCash") or holding.get("initial_cash"))
        if value is not None:
            return value
    return 0.0


def _portfolio_transactions(holdings: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    for holding in holdings:
        transactions = holding.get("transactions")
        if isinstance(transactions, list):
            return [item for item in transactions if isinstance(item, dict)]
    return []


def _positions_from_holdings(holdings: List[Dict[str, Any]]) -> tuple[List[Dict[str, Any]], List[Dict[str, str]]]:
    positions: Dict[str, Dict[str, float | str]] = {}
    unsupported: List[Dict[str, str]] = []
    for holding in holdings:
        raw_symbol = str(holding.get("symbol", "")).strip()
        resolved = resolve_symbol(raw_symbol)
        if raw_symbol and not resolved.ok:
            unsupported.append({"symbol": raw_symbol, "reason": resolved.reason or "unsupported"})
            continue
        symbol = resolved.canonical_symbol or raw_symbol.upper()
        quantity = _number(holding.get("quantity"))
        average_cost = _number(holding.get("averageCost") or holding.get("average_cost"))
        if not symbol or quantity is None or average_cost is None or quantity <= 0:
            continue
        position = positions.setdefault(symbol, {"symbol": symbol, "quantity": 0.0, "cost": 0.0})
        position["quantity"] = float(position["quantity"]) + quantity
        position["cost"] = float(position["cost"]) + (quantity * average_cost)
    return [
        {"symbol": symbol, "quantity": position["quantity"], "averageCost": float(position["cost"]) / float(position["quantity"])}
        for symbol, position in positions.items()
        if float(position["quantity"]) > 0
    ], unsupported


def _positions_from_transactions(initial_cash: float, transactions: List[Dict[str, Any]]) -> tuple[float, List[Dict[str, Any]], float, List[Dict[str, str]], List[Dict[str, Any]], List[Dict[str, Any]]]:
    positions: Dict[str, Dict[str, float | str]] = {}
    cash = initial_cash
    enforce_cash = initial_cash > 0
    realized = 0.0
    unsupported: List[Dict[str, str]] = []
    errors: List[Dict[str, Any]] = []
    history: List[Dict[str, Any]] = []
    for index, transaction in enumerate(transactions):
        if transaction.get("reset") is True:
            positions.clear()
            cash = initial_cash
            realized = 0.0
            history.append({"index": index, "side": "reset", "status": "accepted"})
            continue
        raw_symbol = str(transaction.get("symbol", "")).strip()
        resolved = resolve_symbol(raw_symbol)
        if raw_symbol and not resolved.ok:
            unsupported.append({"symbol": raw_symbol, "reason": resolved.reason or "unsupported"})
            errors.append({"index": index, "symbol": raw_symbol, "reason": resolved.reason or "unsupported"})
            continue
        symbol = resolved.canonical_symbol or raw_symbol.upper()
        side = str(transaction.get("side", "")).strip().lower()
        quantity = _number(transaction.get("quantity"))
        price = _number(transaction.get("price"))
        if not symbol or quantity is None or price is None or quantity <= 0 or price < 0:
            errors.append({"index": index, "symbol": raw_symbol, "reason": "invalid_transaction"})
            continue
        position = positions.setdefault(symbol, {"symbol": symbol, "quantity": 0.0, "cost": 0.0})
        notional = quantity * price
        if side == "buy":
            if enforce_cash and notional > cash:
                errors.append({"index": index, "symbol": symbol, "reason": "insufficient_cash", "required_cash": notional, "cash_balance": cash})
                continue
            position["quantity"] = float(position["quantity"]) + quantity
            position["cost"] = float(position["cost"]) + notional
            cash -= notional
            history.append({"index": index, "symbol": symbol, "side": side, "quantity": quantity, "price": price, "status": "accepted"})
        elif side == "sell":
            held = float(position["quantity"])
            if quantity > held:
                errors.append({"index": index, "symbol": symbol, "reason": "insufficient_shares", "requested": quantity, "available": held})
                continue
            average_cost = float(position["cost"]) / held if held else 0.0
            realized += (price - average_cost) * quantity
            position["quantity"] = held - quantity
            position["cost"] = float(position["cost"]) - average_cost * quantity
            cash += quantity * price
            history.append({"index": index, "symbol": symbol, "side": side, "quantity": quantity, "price": price, "status": "accepted", "realized_gain_loss": (price - average_cost) * quantity})
        else:
            errors.append({"index": index, "symbol": symbol, "reason": "unsupported_transaction_side"})
    rows = [
        {"symbol": symbol, "quantity": position["quantity"], "averageCost": float(position["cost"]) / float(position["quantity"])}
        for symbol, position in positions.items()
        if float(position["quantity"]) > 0
    ]
    return cash, rows, realized, unsupported, errors, history


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
    concentration = _concentration(rows)["largest_position_percent"] or 0
    score = 3
    if concentration >= 50:
        score += 3
    elif concentration >= 30:
        score += 2
    if len(rows) <= 2:
        score += 2
    if any((row.get("asset_type") == "crypto" or abs(row.get("daily_change_percent") or 0) >= 4) for row in rows):
        score += 1
    return max(1, min(10, score))


def _diversification_score(rows: List[Dict[str, Any]]) -> int | None:
    if not rows:
        return None
    concentration = _concentration(rows)["largest_position_percent"] or 100
    sectors = len({row.get("sector") or row.get("asset_type") for row in rows})
    score = 100 - int(concentration)
    score += min(20, sectors * 4)
    if len(rows) >= 5:
        score += 10
    return max(0, min(100, score))


def _concentration(rows: List[Dict[str, Any]]) -> Dict[str, Any]:
    if not rows:
        return {"largest_position_symbol": None, "largest_position_percent": None}
    largest = max(rows, key=lambda row: row.get("allocation_percent") or 0)
    return {"largest_position_symbol": largest.get("symbol"), "largest_position_percent": largest.get("allocation_percent")}


def _allocation(rows: List[Dict[str, Any]], field: str, output_key: str) -> List[Dict[str, Any]]:
    allocation: Dict[str, float] = {}
    for row in rows:
        key = str(row.get(field) or "Unavailable")
        percent = row.get("allocation_percent")
        if isinstance(percent, (int, float)):
            allocation[key] = allocation.get(key, 0.0) + percent
    return [{output_key: key, "allocation_percent": percent} for key, percent in sorted(allocation.items())]


def _analytics(rows: List[Dict[str, Any]], cash: float, total_equity: float, total_cost: float, total_gain_loss: float | None, realized: float) -> Dict[str, Any]:
    unavailable = []
    if not rows:
        unavailable.append("No open positions.")
    unavailable.extend([
        "Weekly and monthly returns require persisted daily portfolio snapshots.",
        "Max drawdown, volatility, Sharpe ratio, and correlation require portfolio value history.",
    ])
    return {
        "status": "partial" if rows else "unavailable",
        "unavailable_reason": " ".join(unavailable),
        "volatility_percent": None,
        "sharpe_ratio": None,
        "max_drawdown_percent": None,
        "correlation": {"status": "unavailable", "reason": "Correlation requires historical returns for each holding."},
    }


def _coach(rows: List[Dict[str, Any]], cash: float, total_equity: float, stale_quotes: List[Dict[str, str]]) -> Dict[str, Any]:
    observations: List[Dict[str, Any]] = []
    concentration = _concentration(rows)
    largest = concentration.get("largest_position_percent")
    if isinstance(largest, (int, float)) and largest >= 40:
        observations.append(_observation("excessive_concentration", "high" if largest >= 60 else "medium", [f"Largest position is {round(largest, 2)}% of portfolio."], "Review whether single-position exposure is within the simulated risk plan."))
    sectors = _allocation(rows, "sector", "sector")
    if sectors and max(item["allocation_percent"] for item in sectors) >= 55:
        observations.append(_observation("sector_imbalance", "medium", [f"Largest sector allocation is {round(max(item['allocation_percent'] for item in sectors), 2)}%."], "Consider whether sector exposure is intentional."))
    if len(rows) <= 2 and rows:
        observations.append(_observation("insufficient_diversification", "medium", [f"Only {len(rows)} open position(s)."], "Add more holdings only if supported by research and risk capacity."))
    if any((row.get("asset_type") == "crypto" or abs(row.get("daily_change_percent") or 0) >= 4) for row in rows):
        observations.append(_observation("high_volatility", "medium", ["At least one holding is crypto or moved more than 4% today."], "Review position size and downside plan."))
    cash_ratio = (cash / total_equity) * 100 if total_equity else None
    if isinstance(cash_ratio, (int, float)) and cash_ratio >= 40:
        observations.append(_observation("high_cash_position", "low", [f"Cash ratio is {round(cash_ratio, 2)}%."], "Confirm whether high cash is a deliberate waiting strategy."))
    currencies = _allocation(rows, "currency", "currency")
    if len(currencies) > 1:
        observations.append(_observation("currency_exposure", "low", [f"Portfolio has {len(currencies)} currencies."], "Review base-currency risk before adding exposure."))
    if stale_quotes:
        observations.append(_observation("stale_prices", "medium", [f"{len(stale_quotes)} quote(s) may be stale or unavailable."], "Refresh quotes and avoid acting on stale prices."))
    return {
        "observations": observations,
        "status": "available" if observations else "no_major_observation",
        "limitations": ["This is simulated educational coaching, not personalized regulated financial advice."],
        "confidence": "medium" if rows else "low",
    }


def _observation(kind: str, severity: str, evidence: List[str], action: str) -> Dict[str, Any]:
    return {
        "type": kind,
        "severity": severity,
        "evidence": evidence,
        "suggested_action": action,
        "limitations": ["Observation uses available simulated portfolio and quote data only."],
        "confidence": "medium" if severity in {"medium", "high"} else "low",
    }


def _scenarios(rows: List[Dict[str, Any]], cash: float, total_equity: float) -> List[Dict[str, Any]]:
    if not rows or not total_equity:
        return []
    return [
        _scenario("market_falls_10", rows, cash, total_equity, lambda row: -10),
        _scenario("technology_falls_15", rows, cash, total_equity, lambda row: -15 if "tech" in str(row.get("sector") or "").lower() or row.get("asset_type") in {"global_stock", "etf"} else 0),
        _scenario("usd_strengthens", rows, cash, total_equity, lambda row: 3 if row.get("currency") == "USD" else -3),
        _scenario("interest_rates_rise", rows, cash, total_equity, lambda row: -8 if row.get("asset_type") in {"bond_etf", "reit"} else -2),
        _scenario("btc_falls_20", rows, cash, total_equity, lambda row: -20 if row.get("symbol") == "BTC-USD" or row.get("asset_type") == "crypto" else 0),
    ]


def _scenario(name: str, rows: List[Dict[str, Any]], cash: float, total_equity: float, shock_fn: Callable[[Dict[str, Any]], float]) -> Dict[str, Any]:
    shocked_value = cash
    for row in rows:
        value = row.get("market_value")
        shock = shock_fn(row)
        if isinstance(value, (int, float)):
            shocked_value += value * (1 + shock / 100)
    impact = shocked_value - total_equity
    return {
        "scenario": name,
        "estimated_value": shocked_value,
        "estimated_pl": impact,
        "estimated_pl_percent": (impact / total_equity) * 100 if total_equity else None,
        "limitations": "Simple deterministic shock using current market values only; no Monte Carlo or prediction.",
    }


def _stale_reason(quote: Dict[str, Any]) -> str | None:
    if quote.get("error"):
        return str(quote["error"])
    if quote.get("stale") is True:
        return str(quote.get("stale_reason") or "Provider marked quote as stale.")
    if quote.get("price") is None:
        return "Current price is unavailable."
    return None
