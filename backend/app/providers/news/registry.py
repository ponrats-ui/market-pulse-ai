from __future__ import annotations

from typing import Any, Dict, List

from app.providers.news.api_providers import AlphaVantageNewsProvider, FinnhubNewsProvider, NewsAPIProvider
from app.providers.news.base import NewsProvider, unavailable_news, utc_now
from app.providers.news.rss_provider import RSSNewsProvider
from app.providers.news.yahoo_finance_news import YahooFinanceNewsProvider


class NewsAggregator:
    def __init__(self, providers: List[NewsProvider] | None = None) -> None:
        self.providers = providers or [
            YahooFinanceNewsProvider(),
            RSSNewsProvider(),
            FinnhubNewsProvider(),
            AlphaVantageNewsProvider(),
            NewsAPIProvider(),
        ]

    def fetch(self, query: str, limit: int = 10) -> Dict[str, Any]:
        attempts = []
        for provider in self.providers:
            if not getattr(provider, "configured", False):
                attempts.append({"provider": provider.name, "configured": False, "reason": "Provider is not configured."})
                continue
            payload = provider.fetch(query, limit)
            attempts.append({"provider": payload.get("provider"), "configured": payload.get("provider_configured"), "reason": payload.get("unavailable_reason")})
            if payload.get("provider_configured") and payload.get("items"):
                return {**payload, "fallback_attempts": attempts}
        return {
            **unavailable_news("news_aggregator", "No configured news provider returned articles."),
            "fallback_attempts": attempts,
            "timestamp": utc_now(),
        }


def get_news_aggregator() -> NewsAggregator:
    return NewsAggregator()
