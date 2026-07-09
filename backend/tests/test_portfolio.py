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
