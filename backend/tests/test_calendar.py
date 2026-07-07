from app.main import calendar


def test_calendar_returns_placeholder_events():
    payload = calendar()
    assert len(payload["events"]) >= 6
    assert payload["events"][0]["note_th"]
