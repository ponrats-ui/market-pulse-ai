from app.main import health


def test_health_returns_ok() -> None:
    payload = health()
    assert payload["status"] == "ok"
    assert payload["service"] == "market-pulse-ai"
