from __future__ import annotations

from typing import Any, Dict

from app.providers.company_events import get_company_events_provider
from app.providers.macro import get_macro_provider
from app.services.calendar import economic_calendar
from app.services.cache import INTELLIGENCE_TTL_SECONDS, cache, cache_key
from app.services.news import news_for_symbol
from app.services.sentiment import sentiment_for_symbol


def macro_indicators() -> Dict[str, Any]:
    key = cache_key("intelligence", "macro")
    cached, age = cache.get_with_age(key)
    if cached is not None:
        return {**cached, "cache_age_seconds": age or 0}
    payload = get_macro_provider().fetch()
    return cache.set(key, payload, INTELLIGENCE_TTL_SECONDS)


def company_events(symbol: str) -> Dict[str, Any]:
    key = cache_key("intelligence", "company_events", symbol)
    cached, age = cache.get_with_age(key)
    if cached is not None:
        return {**cached, "cache_age_seconds": age or 0}
    payload = get_company_events_provider().fetch(symbol)
    return cache.set(key, payload, INTELLIGENCE_TTL_SECONDS)


def intelligence_status(symbol: str) -> Dict[str, Any]:
    news = news_for_symbol(symbol, 5)
    calendar = economic_calendar()
    sentiment = sentiment_for_symbol(symbol)
    macro = macro_indicators()
    events = company_events(symbol)
    return {
        "news": _status(news),
        "calendar": _status(calendar),
        "sentiment": _status(sentiment),
        "macro": {
            "provider": macro.get("provider"),
            "provider_configured": macro.get("provider_configured"),
            "unavailable_reason": macro.get("unavailable_reason"),
            "timestamp": macro.get("timestamp"),
            "cache_age_seconds": macro.get("cache_age_seconds", 0),
            "confidence": macro.get("confidence", "low"),
        },
        "company_events": {
            "provider": events.get("provider"),
            "provider_configured": events.get("provider_configured"),
            "unavailable_reason": events.get("unavailable_reason"),
            "timestamp": events.get("timestamp"),
            "cache_age_seconds": events.get("cache_age_seconds", 0),
            "confidence": events.get("confidence", "low"),
        },
    }


def _status(payload: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "provider": payload.get("provider") or payload.get("source"),
        "provider_configured": payload.get("provider_configured"),
        "unavailable_reason": payload.get("unavailable_reason") or payload.get("message"),
        "timestamp": payload.get("timestamp"),
        "cache_age_seconds": payload.get("cache_age_seconds", 0),
        "confidence": payload.get("confidence", "low"),
    }
