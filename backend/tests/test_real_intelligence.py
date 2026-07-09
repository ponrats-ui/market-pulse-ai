from app.services.news import news_impact_for_symbol
from app.services.cache import cache


def test_news_impact_classifies_provider_articles(monkeypatch):
    cache.clear()
    class Provider:
        def fetch(self, query, limit):
            return {
                "provider": "test_news",
                "provider_configured": True,
                "items": [{"title": "NVDA earnings beats expectations", "url": "https://example.test", "published_at": "now", "source": "test"}],
                "timestamp": "2026-01-01T00:00:00Z",
                "cache_age_seconds": 0,
                "confidence": "medium",
                "unavailable_reason": None,
                "fallback_attempts": [{"provider": "test_news", "configured": True, "reason": None}],
            }

    monkeypatch.setattr("app.services.news.get_news_aggregator", lambda: Provider())
    payload = news_impact_for_symbol("NVDA", 5)
    assert payload["provider_configured"] is True
    assert payload["items"][0]["category"] == "Earnings"
    assert payload["items"][0]["sentiment"] == "Bullish"
    assert payload["items"][0]["affected_assets"] == ["NVDA"]
