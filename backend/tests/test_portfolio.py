from app.services.portfolio import evaluate_portfolio


def test_evaluate_portfolio_uses_live_quote_shape() -> None:
    def quote(symbol):
        return {"symbol": symbol, "price": 120, "currency": "USD", "source": "test", "timestamp": "2026-01-01T00:00:00Z"}

    payload = evaluate_portfolio([{"symbol": "AAPL", "quantity": 2, "averageCost": 100}], quote)
    assert payload["total_value"] == 240
    assert payload["total_gain_loss"] == 40
    assert payload["items"][0]["gain_loss_percent"] == 20
