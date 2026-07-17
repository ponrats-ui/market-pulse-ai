from __future__ import annotations

from typing import Any, Dict

from app.providers.calendar import get_calendar_provider
from app.services.cache import INTELLIGENCE_TTL_SECONDS, cache, cache_key


def economic_calendar() -> Dict[str, Any]:
    key = cache_key("intelligence", "calendar", "high_impact")
    cached, age = cache.get_with_age(key)
    if cached is not None:
        return {**cached, "cache_age_seconds": age or 0}
    payload = get_calendar_provider().fetch_high_impact()
    response = {
        **payload,
        "message": payload.get("unavailable_reason", "Economic calendar provider is not configured."),
        "message_th": "ยังไม่ได้ตั้งค่าผู้ให้บริการปฏิทินเศรษฐกิจ",
    }
    return cache.set(key, response, INTELLIGENCE_TTL_SECONDS)
