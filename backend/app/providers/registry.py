from __future__ import annotations

from app.providers.base import MarketDataProvider
from app.providers.yfinance_provider import YFinanceProvider

_PROVIDER = YFinanceProvider()


def get_provider(name: str = "yfinance") -> MarketDataProvider:
    if name != "yfinance":
        raise ValueError(f"Unsupported provider: {name}")
    return _PROVIDER
