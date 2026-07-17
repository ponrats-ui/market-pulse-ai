from app.data_hub.provider_health import clear_provider_health, provider_health_snapshot, record_provider_result
from app.providers.calendar.registry import get_calendar_provider
from app.providers.news.registry import NewsAggregator
from app.providers.news.base import NewsProvider, provider_payload, unavailable_news
from app.providers.sentiment.registry import get_fear_greed_provider
from app.services.financials import build_financial_statement_analysis


class UnconfiguredNewsProvider(NewsProvider):
    name = "missing_news"
    configured = False

    def fetch(self, query: str, limit: int = 10):
        return unavailable_news(self.name, "missing")


class EmptyNewsProvider(NewsProvider):
    name = "empty_news"
    configured = True

    def fetch(self, query: str, limit: int = 10):
        return unavailable_news(self.name, "No articles")


class SuccessNewsProvider(NewsProvider):
    name = "success_news"
    configured = True

    def fetch(self, query: str, limit: int = 10):
        return provider_payload(self.name, [{"title": f"{query} real article", "url": "https://example.test/article", "published_at": "2026-01-01", "source": self.name}])


def test_news_aggregator_falls_back_to_success_provider() -> None:
    payload = NewsAggregator([UnconfiguredNewsProvider(), EmptyNewsProvider(), SuccessNewsProvider()]).fetch("NVDA", 5)
    assert payload["provider"] == "success_news"
    assert payload["items"][0]["url"].startswith("https://")
    assert [attempt["provider"] for attempt in payload["fallback_attempts"]] == ["missing_news", "empty_news", "success_news"]


def test_financials_include_field_level_provenance() -> None:
    payload = build_financial_statement_analysis(
        "NVDA",
        {
            "source": "test_provider",
            "revenue": 100,
            "netIncome": 20,
            "field_provenance": {
                "revenue": {"provider": "test_provider", "source": "income_statement", "available": True},
                "netIncome": {"provider": "test_provider", "source": "income_statement", "available": True},
            },
        },
        {"asset_type": "global_stock"},
    )
    assert payload["status"] == "partial"
    assert payload["facts"]["revenue"] == 100
    assert payload["field_provenance"]["revenue"]["provider"] == "test_provider"
    assert payload["field_provenance"]["gross_profit"]["available"] is False


def test_no_fake_calendar_without_provider_key(monkeypatch) -> None:
    monkeypatch.delenv("TRADING_ECONOMICS_KEY", raising=False)
    payload = get_calendar_provider().fetch_high_impact()
    assert payload["items"] == []
    assert payload["provider_configured"] is False
    assert payload["unavailable_reason"]


def test_no_fake_sentiment_without_provider_enabled(monkeypatch) -> None:
    monkeypatch.delenv("ENABLE_ALTERNATIVE_ME_FEAR_GREED", raising=False)
    payload = get_fear_greed_provider().fetch("BTC-USD")
    assert payload["score"] is None
    assert payload["provider_configured"] is False
    assert payload["unavailable_reason"]


def test_provider_health_reporting_statuses() -> None:
    clear_provider_health()
    record_provider_result("finnhub", configured=False, success=False, reason="FINNHUB_API_KEY is not configured.")
    record_provider_result("yfinance", configured=True, success=True, response_time_ms=12.4)
    record_provider_result("alpha_vantage", configured=True, success=False, reason="rate limit exceeded")
    snapshot = provider_health_snapshot()
    assert snapshot["providers"]["finnhub"]["status"] == "unavailable"
    assert snapshot["providers"]["yfinance"]["status"] == "healthy"
    assert snapshot["providers"]["alpha_vantage"]["status"] == "rate_limited"
