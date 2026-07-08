import time

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
