from __future__ import annotations

import os
from typing import Any, Dict

from app.providers.news.base import NewsProvider, unavailable_news


class NewsAPIProvider(NewsProvider):
    name = "newsapi"
    configured = bool(os.getenv("NEWSAPI_KEY"))

    def fetch(self, query: str, limit: int = 10) -> Dict[str, Any]:
        if not os.getenv("NEWSAPI_KEY"):
            return unavailable_news(self.name, "NEWSAPI_KEY is not configured.")
        return unavailable_news(self.name, "NewsAPI transport is not enabled in this build.")


class FinnhubNewsProvider(NewsProvider):
    name = "finnhub"
    configured = bool(os.getenv("FINNHUB_API_KEY"))

    def fetch(self, query: str, limit: int = 10) -> Dict[str, Any]:
        if not os.getenv("FINNHUB_API_KEY"):
            return unavailable_news(self.name, "FINNHUB_API_KEY is not configured.")
        return unavailable_news(self.name, "Finnhub news transport is not enabled in this build.")


class AlphaVantageNewsProvider(NewsProvider):
    name = "alpha_vantage_news"
    configured = bool(os.getenv("ALPHAVANTAGE_API_KEY"))

    def fetch(self, query: str, limit: int = 10) -> Dict[str, Any]:
        if not os.getenv("ALPHAVANTAGE_API_KEY"):
            return unavailable_news(self.name, "ALPHAVANTAGE_API_KEY is not configured.")
        return unavailable_news(self.name, "Alpha Vantage news transport is not enabled in this build.")
