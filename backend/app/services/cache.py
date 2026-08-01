from __future__ import annotations

import time
import os
from dataclasses import dataclass
from threading import Lock, RLock
from typing import Any, Callable, Dict, Hashable, Tuple

QUOTE_TTL_SECONDS = int(os.getenv("DATA_HUB_QUOTE_TTL_SECONDS", "60"))
HISTORICAL_TTL_SECONDS = int(os.getenv("DATA_HUB_HISTORY_TTL_SECONDS", "300"))
WATCHLIST_TTL_SECONDS = int(os.getenv("DATA_HUB_ASSET_MASTER_TTL_SECONDS", "300"))
INTELLIGENCE_TTL_SECONDS = int(os.getenv("DATA_HUB_NEWS_TTL_SECONDS", "900"))
FUNDAMENTALS_TTL_SECONDS = int(os.getenv("DATA_HUB_FUNDAMENTALS_TTL_SECONDS", "3600"))
MAX_CACHE_ENTRIES = max(50, int(os.getenv("DATA_HUB_MAX_CACHE_ENTRIES", "300")))


@dataclass
class CacheEntry:
    value: Any
    created_at: float
    expires_at: float


class TTLCache:
    def __init__(self) -> None:
        self._items: Dict[Tuple[Hashable, ...], CacheEntry] = {}
        self._lock = RLock()
        self._key_locks: Dict[Tuple[Hashable, ...], Lock] = {}

    def get(self, key: Tuple[Hashable, ...]) -> Any | None:
        with self._lock:
            entry = self._items.get(key)
            if entry is None:
                return None
            if entry.expires_at <= time.time():
                self._items.pop(key, None)
                return None
            return entry.value

    def get_with_age(self, key: Tuple[Hashable, ...]) -> tuple[Any | None, int | None]:
        with self._lock:
            entry = self._items.get(key)
            if entry is None:
                return None, None
            now = time.time()
            if entry.expires_at <= now:
                self._items.pop(key, None)
                return None, None
            return entry.value, max(0, int(now - entry.created_at))

    def set(self, key: Tuple[Hashable, ...], value: Any, ttl_seconds: int) -> Any:
        with self._lock:
            now = time.time()
            self._purge_expired_at(now)
            self._evict_if_needed()
            self._items[key] = CacheEntry(value=value, created_at=now, expires_at=now + ttl_seconds)
            return value

    def get_or_set(self, key: Tuple[Hashable, ...], factory: Callable[[], Any], ttl_seconds: int) -> Any:
        cached = self.get(key)
        if cached is not None:
            return cached
        with self._lock:
            key_lock = self._key_locks.setdefault(key, Lock())
        with key_lock:
            cached = self.get(key)
            if cached is not None:
                return cached
            return self.set(key, factory(), ttl_seconds)

    def clear(self) -> None:
        with self._lock:
            self._items.clear()
            self._key_locks.clear()

    def size(self) -> int:
        with self._lock:
            self._purge_expired()
            return len(self._items)

    def _purge_expired(self) -> None:
        self._purge_expired_at(time.time())

    def _purge_expired_at(self, now: float) -> None:
        expired_keys: list[Tuple[Hashable, ...]] = []
        expired = [key for key, entry in self._items.items() if entry.expires_at <= now]
        for key in expired:
            self._items.pop(key, None)
            expired_keys.append(key)
        for key in expired_keys:
            self._key_locks.pop(key, None)

    def _evict_if_needed(self) -> None:
        while len(self._items) >= MAX_CACHE_ENTRIES:
            oldest_key = min(self._items, key=lambda key: self._items[key].created_at)
            self._items.pop(oldest_key, None)
            self._key_locks.pop(oldest_key, None)


cache = TTLCache()


def cache_key(provider: str, endpoint_type: str, symbol: str = "", range: str = "", interval: str = "") -> Tuple[str, str, str, str, str]:
    return (provider, endpoint_type, symbol, range, interval)
