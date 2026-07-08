from app.main import news_impact


def test_news_impact_returns_provider_ready_payload():
    payload = news_impact("BTC-USD")
    assert payload["symbol"] == "BTC-USD"
    assert payload["items"] == []
    assert payload["source"] == "Unavailable"
    assert payload["provider_configured"] is False
    assert payload["message"] == "No news provider configured."
