from datetime import datetime, timedelta, timezone

from app import main
from app.providers.yfinance_provider import YFinanceProvider
from app.services.cache import cache


def _history(symbol: str, points: int = 7, close_start: float = 100.0):
    now = datetime.now(timezone.utc)
    return {
        "symbol": symbol,
        "source": "test_provider",
        "points": [
            {"time": (now - timedelta(days=points - index)).isoformat(), "close": close_start + index}
            for index in range(points)
        ],
    }


def test_batch_sparkline_success(monkeypatch):
    cache.clear()
    monkeypatch.setattr(main, "get_cached_history", lambda symbol, range, interval: _history(symbol))

    payload = main.asset_sparklines("AAPL,NVDA")

    assert payload["symbols"] == ["AAPL", "NVDA"]
    assert len(payload["items"]) == 2
    assert payload["items"][0]["points"][0]["close"] == 100.0
    assert payload["items"][0]["points"][-1]["close"] == 106.0
    assert payload["items"][0]["change_percent"] is not None
    assert payload["items"][0]["provider"] == "test_provider"
    assert payload["items"][0]["unavailable_reason"] is None


def test_batch_sparkline_deduplicates_symbols(monkeypatch):
    cache.clear()
    calls: list[str] = []

    def fake_history(symbol, range, interval):
        calls.append(symbol)
        return _history(symbol)

    monkeypatch.setattr(main, "get_cached_history", fake_history)
    payload = main.asset_sparklines("AAPL,aapl,NVDA,AAPL")

    assert payload["symbols"] == ["AAPL", "NVDA"]
    assert calls == ["AAPL", "NVDA"]


def test_sparkline_partial_history_is_transparent(monkeypatch):
    cache.clear()
    monkeypatch.setattr(main, "get_cached_history", lambda symbol, range, interval: _history(symbol, points=3))

    item = main.asset_sparklines("OKLO")["items"][0]

    assert len(item["points"]) == 3
    assert "Fewer than five" in item["unavailable_reason"]


def test_sparkline_missing_history_does_not_fabricate_points(monkeypatch):
    cache.clear()
    monkeypatch.setattr(main, "get_cached_history", lambda symbol, range, interval: {"symbol": symbol, "points": [], "source": "test", "error": "provider unavailable"})

    item = main.asset_sparklines("MISSING")["items"][0]

    assert item["points"] == []
    assert item["start_price"] is None
    assert item["end_price"] is None
    assert item["change_percent"] is None
    assert item["unavailable_reason"] == "provider unavailable"


def test_sparkline_stale_metadata(monkeypatch):
    cache.clear()
    old = datetime.now(timezone.utc) - timedelta(days=8)
    monkeypatch.setattr(main, "get_cached_history", lambda symbol, selected_range, interval: {"symbol": symbol, "source": "test", "points": [{"time": old.isoformat(), "close": 100 + i} for i in range(7)]})

    item = main.asset_sparklines("AAPL")["items"][0]

    assert item["stale"] is True


def test_yfinance_logo_metadata_normalization(monkeypatch):
    provider = YFinanceProvider()

    class FakeTicker:
        info = {"shortName": "Apple", "logo_url": "https://logo.clearbit.com/apple.com", "regularMarketPrice": 10, "regularMarketPreviousClose": 9, "currency": "USD"}
        fast_info = {}

        def history(self, period, interval, auto_adjust):
            import pandas as pd
            return pd.DataFrame([{"Open": 9, "High": 11, "Low": 8, "Close": 10, "Volume": 1000}], index=pd.to_datetime(["2026-01-01"]))

    monkeypatch.setattr("app.providers.yfinance_provider.yf.Ticker", lambda symbol: FakeTicker())
    quote = provider.get_quote("AAPL")

    assert quote["logo_url"] == "https://logo.clearbit.com/apple.com"
    assert quote["icon_url"] == quote["logo_url"]
    assert quote["provider_logo_url"] == quote["logo_url"]
    assert quote["logo_provider"] == "yfinance"
    assert quote["logo_available"] is True
