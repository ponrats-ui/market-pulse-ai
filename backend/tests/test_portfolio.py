from app.services.portfolio import evaluate_portfolio


def test_evaluate_portfolio_uses_live_quote_shape() -> None:
    def quote(symbol):
        return {"symbol": symbol, "price": 120, "change_percent": 1.5, "currency": "USD", "source": "test", "timestamp": "2026-01-01T00:00:00Z"}

    payload = evaluate_portfolio([{"cashBalance": 50}, {"symbol": "AAPL", "quantity": 2, "averageCost": 100}], quote)
    assert payload["total_value"] == 240
    assert payload["total_equity"] == 290
    assert payload["total_gain_loss"] == 40
    assert payload["items"][0]["gain_loss_percent"] == 20
    assert payload["daily_return_percent"] == 1.5
    assert payload["risk_score"] is not None
    assert payload["diversification_score"] is not None


def test_evaluate_portfolio_tracks_realized_pl_from_transactions() -> None:
    def quote(symbol):
        return {"symbol": symbol, "price": 130, "change_percent": 0, "currency": "USD", "source": "test", "timestamp": "2026-01-01T00:00:00Z"}

    payload = evaluate_portfolio([
        {"transactions": [
            {"symbol": "AAPL", "side": "buy", "quantity": 2, "price": 100},
            {"symbol": "AAPL", "side": "sell", "quantity": 1, "price": 125},
        ]},
        {"symbol": "AAPL", "quantity": 1, "averageCost": 100},
    ], quote)
    assert payload["realized_gain_loss"] == 25
    assert payload["transaction_count"] == 2


def test_evaluate_portfolio_builds_single_position_from_repeated_buys_and_sell() -> None:
    def quote(symbol):
        return {"symbol": symbol, "price": 140, "change_percent": 0, "currency": "USD", "source": "test", "timestamp": "2026-01-01T00:00:00Z"}

    payload = evaluate_portfolio([
        {"cashBalance": 1000, "transactions": [
            {"symbol": "AAPL", "side": "buy", "quantity": 2, "price": 100},
            {"symbol": "AAPL", "side": "buy", "quantity": 2, "price": 120},
            {"symbol": "AAPL", "side": "sell", "quantity": 1, "price": 130},
        ]},
    ], quote)

    assert len(payload["items"]) == 1
    assert payload["items"][0]["symbol"] == "AAPL"
    assert payload["items"][0]["quantity"] == 3
    assert payload["items"][0]["average_cost"] == 110
    assert payload["cash_balance"] == 690
    assert payload["realized_gain_loss"] == 20
    assert payload["items"][0]["market_value"] == 420


def test_evaluate_portfolio_canonicalizes_aliases_and_rejects_unsupported() -> None:
    def quote(symbol):
        return {"symbol": symbol, "price": 2, "change_percent": 0, "currency": "THB", "source": "test", "timestamp": "2026-01-01T00:00:00Z"}

    payload = evaluate_portfolio([
        {"symbol": "TTB", "quantity": 10, "averageCost": 1},
        {"symbol": "TTB.BK", "quantity": 5, "averageCost": 2},
        {"symbol": "RKLB", "quantity": 1, "averageCost": 1},
    ], quote)
    assert len(payload["items"]) == 1
    assert payload["items"][0]["symbol"] == "TTB.BK"
    assert payload["items"][0]["quantity"] == 15
    assert payload["items"][0]["average_cost"] == 1.3333333333333333
    assert payload["unsupported_symbols"] == [{"symbol": "RKLB", "reason": "unsupported_under_current_universe"}]


def test_portfolio_partial_sell_and_sell_all() -> None:
    def quote(symbol):
        return {"symbol": symbol, "price": 150, "change_percent": 2, "currency": "USD", "source": "test", "timestamp": "2026-01-01T00:00:00Z"}

    payload = evaluate_portfolio([
        {"cashBalance": 1000, "transactions": [
            {"symbol": "AAPL", "side": "buy", "quantity": 4, "price": 100},
            {"symbol": "AAPL", "side": "sell", "quantity": 1, "price": 120},
            {"symbol": "AAPL", "side": "sell", "quantity": 3, "price": 130},
        ]},
    ], quote)
    assert payload["items"] == []
    assert payload["realized_gain_loss"] == 110
    assert payload["cash_balance"] == 1110
    assert payload["transaction_count"] == 3


def test_portfolio_rejects_insufficient_cash_and_shares() -> None:
    def quote(symbol):
        return {"symbol": symbol, "price": 100, "change_percent": 0, "currency": "USD", "source": "test", "timestamp": "2026-01-01T00:00:00Z"}

    payload = evaluate_portfolio([
        {"cashBalance": 100, "transactions": [
            {"symbol": "AAPL", "side": "buy", "quantity": 2, "price": 100},
            {"symbol": "AAPL", "side": "buy", "quantity": 1, "price": 50},
            {"symbol": "AAPL", "side": "sell", "quantity": 2, "price": 60},
        ]},
    ], quote)
    assert [error["reason"] for error in payload["transaction_errors"]] == ["insufficient_cash", "insufficient_shares"]
    assert payload["items"][0]["quantity"] == 1
    assert payload["cash_balance"] == 50


def test_portfolio_allocations_coach_and_scenarios() -> None:
    def quote(symbol):
        return {
            "symbol": symbol,
            "price": 100,
            "change_percent": 5 if symbol == "BTC-USD" else 1,
            "currency": "USD",
            "sector": "Technology" if symbol == "NVDA" else "Crypto",
            "country": "US",
            "asset_type": "crypto" if symbol == "BTC-USD" else "global_stock",
            "source": "test",
            "timestamp": "2026-01-01T00:00:00Z",
        }

    payload = evaluate_portfolio([
        {"cashBalance": 1000},
        {"symbol": "NVDA", "quantity": 8, "averageCost": 80},
        {"symbol": "BTC-USD", "quantity": 1, "averageCost": 90},
    ], quote)
    assert payload["asset_allocation"]
    assert payload["sector_allocation"]
    assert payload["country_allocation"]
    assert payload["currency_allocation"]
    assert payload["cash_ratio_percent"] is not None
    assert payload["portfolio_coach"]["observations"]
    assert len(payload["scenarios"]) == 5


def test_portfolio_reset_and_stale_quote_handling() -> None:
    def quote(symbol):
        return {"symbol": symbol, "price": None, "change_percent": None, "currency": "USD", "source": "test", "timestamp": "2026-01-01T00:00:00Z", "error": "market closed or stale"}

    payload = evaluate_portfolio([
        {"cashBalance": 500, "transactions": [
            {"symbol": "AAPL", "side": "buy", "quantity": 1, "price": 100},
            {"reset": True},
            {"symbol": "AAPL", "side": "buy", "quantity": 1, "price": 100},
        ]},
    ], quote)
    assert payload["cash_balance"] == 400
    assert payload["items"][0]["stale"] is True
    assert payload["stale_quotes"] == [{"symbol": "AAPL", "reason": "market closed or stale"}]
    assert payload["analytics_status"] == "partial"
