from app.main import sentiment


def test_sentiment_returns_score_and_label():
    payload = sentiment("BTC-USD")
    assert payload["symbol"] == "BTC-USD"
    assert 0 <= payload["score"] <= 100
    assert payload["source"] == "mock"
