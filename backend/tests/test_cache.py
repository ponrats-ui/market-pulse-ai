import time

from app.services import cache as cache_module
from app.services.cache import TTLCache, cache_key


def test_cache_returns_value_before_ttl() -> None:
    cache = TTLCache()
    key = cache_key("yfinance", "quote", "BTC-USD")
    cache.set(key, {"price": 1}, ttl_seconds=5)
    assert cache.get(key) == {"price": 1}
    value, age = cache.get_with_age(key)
    assert value == {"price": 1}
    assert age is not None and age >= 0


def test_cache_expires_value() -> None:
    cache = TTLCache()
    key = cache_key("yfinance", "history", "BTC-USD", "1mo", "1d")
    cache.set(key, [1, 2, 3], ttl_seconds=0)
    time.sleep(0.01)
    assert cache.get(key) is None


def test_cache_evicts_oldest_entries_when_bounded(monkeypatch) -> None:
    monkeypatch.setattr(cache_module, "MAX_CACHE_ENTRIES", 3)
    cache = TTLCache()

    for index in range(4):
        cache.set(cache_key("yfinance", "quote", f"SYM{index}"), {"price": index}, ttl_seconds=60)

    assert cache.size() == 3
    assert cache.get(cache_key("yfinance", "quote", "SYM0")) is None
    assert cache.get(cache_key("yfinance", "quote", "SYM3")) == {"price": 3}
