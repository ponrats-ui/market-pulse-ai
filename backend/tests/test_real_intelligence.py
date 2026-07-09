from app.services.news import news_impact_for_symbol
from app.services.cache import cache
from app.main import analysis, macro, sentiment
from app.providers.news.api_providers import AlphaVantageNewsProvider, FinnhubNewsProvider, NewsAPIProvider


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
    assert payload["items"][0]["affected_assets"] == ["NVDA", "AMD", "TSM", "QQQ", "SOXX"]
    assert payload["items"][0]["cross_asset_effects"]


def test_keyed_news_providers_return_unavailable_without_keys(monkeypatch):
    monkeypatch.delenv("NEWSAPI_KEY", raising=False)
    monkeypatch.delenv("FINNHUB_API_KEY", raising=False)
    monkeypatch.delenv("ALPHA_VANTAGE_API_KEY", raising=False)
    assert NewsAPIProvider().fetch("NVDA")["provider_configured"] is False
    assert FinnhubNewsProvider().fetch("NVDA")["provider_configured"] is False
    assert AlphaVantageNewsProvider().fetch("NVDA")["provider_configured"] is False


def test_macro_endpoint_returns_unavailable_metadata_without_fred_key(monkeypatch):
    cache.clear()
    monkeypatch.delenv("FRED_API_KEY", raising=False)
    payload = macro()
    assert payload["provider"] == "fred"
    assert payload["provider_configured"] is False
    assert payload["items"] == []
    assert payload["unavailable_reason"]


def test_sentiment_endpoint_returns_unavailable_metadata_without_fear_greed_provider(monkeypatch):
    cache.clear()
    monkeypatch.delenv("ENABLE_ALTERNATIVE_ME_FEAR_GREED", raising=False)
    payload = sentiment("BTC-USD")
    assert payload["provider_configured"] is False
    assert payload["score"] is None
    assert payload["unavailable_reason"]


def test_analysis_includes_real_intelligence_provider_status(monkeypatch):
    cache.clear()
    monkeypatch.setenv("ENABLE_YAHOO_FINANCE_NEWS", "false")
    monkeypatch.delenv("FRED_API_KEY", raising=False)
    monkeypatch.setattr("app.main.get_cached_quote", lambda symbol: {"symbol": symbol, "price": 100, "change_percent": 1, "source": "test", "timestamp": "now", "asset_type": "global_stock"})
    monkeypatch.setattr("app.main.get_cached_history", lambda symbol, range, interval: {"points": [{"time": "t1", "close": 100}, {"time": "t2", "close": 101}], "source": "test"})
    payload = analysis("NVDA")
    assert payload["real_intelligence"]["news"]["provider_configured"] is False
    assert payload["real_intelligence"]["calendar"]["provider_configured"] is False
    assert payload["real_intelligence"]["sentiment"]["provider_configured"] is False
    assert payload["real_intelligence"]["macro"]["provider_configured"] is False
    assert payload["real_intelligence"]["company_events"]["provider_configured"] is False
