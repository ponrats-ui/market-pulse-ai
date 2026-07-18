import pandas as pd

from app.providers import yfinance_provider
from app.providers.yfinance_provider import VALID_RANGES, YFinanceProvider
from app import main


def test_professional_chart_timeframes_are_supported():
    expected = {"1d", "5d", "1mo", "3mo", "6mo", "ytd", "1y", "3y", "5y", "max"}
    assert expected.issubset(VALID_RANGES)


def test_technical_endpoint_preserves_selected_range(monkeypatch):
    calls = []

    def history(symbol, selected_range, interval):
        calls.append((symbol, selected_range, interval))
        return {
            "symbol": symbol,
            "range": selected_range,
            "interval": interval,
            "points": [
                {"time": f"2026-01-{index:02d}T00:00:00Z", "open": 100 + index, "high": 102 + index, "low": 99 + index, "close": 100 + index, "volume": 1000 + index}
                for index in range(1, 61)
            ],
            "source": "test",
        }

    monkeypatch.setattr(main, "get_cached_history", history)
    payload = main.technical("AAPL", "3y", "1d")

    assert payload["status"] == "ok"
    assert calls == [("AAPL", "3y", "1d")]


def test_yfinance_provider_requests_three_year_history_with_dates(monkeypatch):
    calls = []

    class FakeTicker:
        def __init__(self, symbol):
            self.symbol = symbol

        def history(self, **kwargs):
            calls.append(kwargs)
            index = pd.date_range("2024-01-01", periods=2, freq="D")
            return pd.DataFrame(
                {
                    "Open": [100, 101],
                    "High": [102, 103],
                    "Low": [99, 100],
                    "Close": [101, 102],
                    "Volume": [1000, 1200],
                },
                index=index,
            )

    monkeypatch.setattr(yfinance_provider.yf, "Ticker", FakeTicker)

    payload = YFinanceProvider().get_history("AAPL", "3y", "1d")

    assert payload["range"] == "3y"
    assert len(payload["points"]) == 2
    assert calls[0]["interval"] == "1d"
    assert calls[0]["auto_adjust"] is False
    assert "start" in calls[0]
    assert "end" in calls[0]
    assert "period" not in calls[0]


def test_history_response_includes_normalized_candle_contract(monkeypatch):
    class FakeTicker:
        def __init__(self, symbol):
            self.symbol = symbol

        def history(self, **kwargs):
            index = pd.date_range("2024-01-01", periods=2, freq="D")
            return pd.DataFrame(
                {
                    "Open": [100, 101],
                    "High": [103, 104],
                    "Low": [99, 100],
                    "Close": [102, 103],
                    "Adj Close": [101.5, 102.5],
                    "Volume": [1000, 1200],
                },
                index=index,
            )

    monkeypatch.setattr(yfinance_provider.yf, "Ticker", FakeTicker)

    payload = YFinanceProvider().get_history("AAPL", "1mo", "1d")

    assert payload["provider"] == "yfinance"
    assert payload["currency"] == "USD"
    assert payload["requested_at"]
    assert payload["data_timestamp"] == payload["candles"][-1]["timestamp"]
    assert payload["stale"] is False
    assert payload["unavailable_reason"] is None
    assert payload["points"] == payload["candles"]
    assert payload["candles"][0]["adjusted_close"] == 101.5


def test_history_contract_skips_duplicate_and_malformed_candles(monkeypatch):
    class FakeTicker:
        def __init__(self, symbol):
            self.symbol = symbol

        def history(self, **kwargs):
            index = pd.to_datetime(["2024-01-01", "2024-01-01", "2024-01-02", "2024-01-03"])
            return pd.DataFrame(
                {
                    "Open": [100, 100, 0, 105],
                    "High": [103, 103, 104, 104],
                    "Low": [99, 99, 98, 100],
                    "Close": [102, 102, 101, 103],
                    "Volume": [1000, 1000, 900, 1200],
                },
                index=index,
            )

    monkeypatch.setattr(yfinance_provider.yf, "Ticker", FakeTicker)

    payload = YFinanceProvider().get_history("AAPL", "1mo", "1d")

    assert len(payload["candles"]) == 1
    assert payload["candles"][0]["timestamp"]
    assert {item["reason"] for item in payload["skipped_candles"]} == {"duplicate_timestamp", "invalid_ohlc", "high_below_ohlc"}
