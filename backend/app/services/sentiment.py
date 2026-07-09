from __future__ import annotations

from typing import Any, Dict

from app.providers.sentiment import get_fear_greed_provider
from app.services.cache import INTELLIGENCE_TTL_SECONDS, cache, cache_key


def sentiment_for_symbol(symbol: str) -> Dict[str, Any]:
    key = cache_key("intelligence", "fear_greed", symbol)
    cached, age = cache.get_with_age(key)
    if cached is not None:
        return {**cached, "cache_age_seconds": age or 0}
    payload = get_fear_greed_provider().fetch(symbol)
    return cache.set(key, payload, INTELLIGENCE_TTL_SECONDS)
