from app import main


def test_compare_returns_items_and_performance(monkeypatch):
    def quote(symbol):
        return {"symbol": symbol, "name": symbol, "asset_type": "crypto", "price": 100, "change_percent": 2, "currency": "USD", "source": "test", "timestamp": "2026-01-01T00:00:00Z", "dividend_yield": None, "market_cap": 1000, "trailing_pe": 20, "sector": "Test"}

    def history(symbol, range, interval):
        return {"symbol": symbol, "points": [{"time": "t1", "close": 100}, {"time": "t2", "close": 110}], "source": "test"}

    monkeypatch.setattr(main, "get_cached_quote", quote)
    monkeypatch.setattr(main, "get_cached_history", history)
    payload = main.compare("BTC-USD,ETH-USD")
    assert payload["symbols"] == ["BTC-USD", "ETH-USD"]
    assert len(payload["items"]) == 2
    assert payload["performance_points"][1]["BTC-USD"] == 10
    assert payload["items"][0]["performance_1mo_percent"] == 10
    assert payload["items"][0]["trend"] == "uptrend"
    assert payload["items"][0]["correlation_to_first"] == 1.0
    assert "recommendation" in payload["items"][0]
    assert "ai_opinion" in payload["items"][0]
