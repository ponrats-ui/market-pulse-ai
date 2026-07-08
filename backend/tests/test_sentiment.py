from app.main import sentiment


def test_sentiment_returns_unavailable_without_provider():
    payload = sentiment("BTC-USD")
    assert payload["symbol"] == "BTC-USD"
    assert payload["score"] is None
    assert payload["source"] == "Unavailable"
    assert payload["provider_configured"] is False
