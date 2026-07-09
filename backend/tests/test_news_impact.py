from app.main import news, news_impact


def test_news_impact_returns_provider_ready_payload():
    payload = news_impact("BTC-USD")
    assert payload["symbol"] == "BTC-USD"
    assert payload["items"] == []
    assert payload["source"] == "news_aggregator"
    assert payload["provider_configured"] is False
    assert payload["message"] == "No configured news provider returned articles."
    assert payload["provider_status"]
    assert payload["confidence"] == "low"


def test_news_endpoint_returns_transparent_unavailable_payload():
    payload = news("NVDA", 5)
    assert payload["symbol"] == "NVDA"
    assert payload["items"] == []
    assert payload["provider_configured"] is False
    assert payload["unavailable_reason"] == "No configured news provider returned articles."
