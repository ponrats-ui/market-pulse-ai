from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any, Dict, Hashable, Tuple

QUOTE_TTL_SECONDS = 60
HISTORICAL_TTL_SECONDS = 300
WATCHLIST_TTL_SECONDS = 300
INTELLIGENCE_TTL_SECONDS = 900


@dataclass
class CacheEntry:
    value: Any
    created_at: float
    expires_at: float


class TTLCache:
    def __init__(self) -> None:
        self._items: Dict[Tuple[Hashable, ...], CacheEntry] = {}

    def get(self, key: Tuple[Hashable, ...]) -> Any | None:
        entry = self._items.get(key)
        if entry is None:
            return None
        if entry.expires_at <= time.time():
            self._items.pop(key, None)
            return None
        return entry.value

    def get_with_age(self, key: Tuple[Hashable, ...]) -> tuple[Any | None, int | None]:
        entry = self._items.get(key)
        if entry is None:
            return None, None
        now = time.time()
        if entry.expires_at <= now:
            self._items.pop(key, None)
            return None, None
        return entry.value, max(0, int(now - entry.created_at))

    def set(self, key: Tuple[Hashable, ...], value: Any, ttl_seconds: int) -> Any:
        now = time.time()
        self._items[key] = CacheEntry(value=value, created_at=now, expires_at=now + ttl_seconds)
        return value

    def clear(self) -> None:
        self._items.clear()

    def size(self) -> int:
        self._purge_expired()
        return len(self._items)

    def _purge_expired(self) -> None:
        now = time.time()
        expired = [key for key, entry in self._items.items() if entry.expires_at <= now]
        for key in expired:
            self._items.pop(key, None)


cache = TTLCache()


def cache_key(provider: str, endpoint_type: str, symbol: str = "", range: str = "", interval: str = "") -> Tuple[str, str, str, str, str]:
    return (provider, endpoint_type, symbol, range, interval)
