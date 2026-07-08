from app.main import calendar


def test_calendar_returns_unavailable_when_provider_is_not_configured():
    payload = calendar()
    assert payload["events"] == []
    assert payload["source"] == "Unavailable"
    assert payload["provider_configured"] is False
