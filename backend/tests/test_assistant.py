from app import main


def test_assistant_thai_response_uses_context(monkeypatch):
    monkeypatch.setattr(main, "get_cached_quote", lambda symbol: {"symbol": symbol, "price": 100, "change_percent": 1.2, "source": "test", "timestamp": "now"})
    monkeypatch.setattr(main, "get_cached_history", lambda symbol, range, interval: {"points": [{"close": 100}, {"close": 101}]})
    payload = main.AssistantRequest(question="BTC เสี่ยงไหม", selected_symbol="BTC-USD", language="th")
    response = main.assistant_ask(payload)
    assert "ข้อเท็จจริง" in response["answer"]
    assert response["disclaimer"] == "This is not financial advice."
