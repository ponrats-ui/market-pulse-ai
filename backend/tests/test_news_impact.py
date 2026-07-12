from app.main import news, news_impact
from app.services.cache import cache


def test_news_impact_returns_provider_ready_payload(monkeypatch):
    cache.clear()
    monkeypatch.setenv("ENABLE_YAHOO_FINANCE_NEWS", "false")
    payload = news_impact("BTC-USD")
    assert payload["symbol"] == "BTC-USD"
    assert payload["items"] == []
    assert payload["source"] == "news_aggregator"
    assert payload["provider_configured"] is False
    assert payload["message"] == "No configured news provider returned articles."
    assert payload["provider_status"]
    assert payload["confidence"] == "low"


def test_news_endpoint_returns_transparent_unavailable_payload(monkeypatch):
    cache.clear()
    monkeypatch.setenv("ENABLE_YAHOO_FINANCE_NEWS", "false")
    payload = news("NVDA", 5)
    assert payload["symbol"] == "NVDA"
    assert payload["items"] == []
    assert payload["provider_configured"] is False
    assert payload["unavailable_reason"] == "No configured news provider returned articles."


def test_news_endpoint_uses_data_hub_canonical_symbol(monkeypatch):
    cache.clear()
    monkeypatch.setenv("ENABLE_YAHOO_FINANCE_NEWS", "false")
    payload = news("TTB", 5)
    assert payload["symbol"] == "TTB.BK"
    assert payload["items"] == []
    assert payload["data_hub"]["canonical_symbol"] == "TTB.BK"


def test_news_endpoint_rejects_unsupported_symbol_without_fabrication(monkeypatch):
    cache.clear()
    monkeypatch.setenv("ENABLE_YAHOO_FINANCE_NEWS", "false")
    payload = news("RKLB", 5)
    assert payload["symbol"] == "RKLB"
    assert payload["items"] == []
    assert payload["source"] == "Unavailable"
    assert payload["data_hub"]["data_type"] == "news"
    assert payload["data_hub"]["canonical_symbol"] is None
