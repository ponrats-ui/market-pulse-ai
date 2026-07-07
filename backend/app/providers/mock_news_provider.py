from __future__ import annotations

from typing import Any, Dict

from app.providers.news_base import NewsProvider


class MockNewsProvider(NewsProvider):
    name = "mock-news"

    def get_news_impact(self, symbol: str) -> Dict[str, Any]:
        return {
            "symbol": symbol,
            "source": self.name,
            "provider_roadmap": ["Finnhub", "NewsAPI", "Alpha Vantage News", "GDELT", "RSS feeds"],
            "items": [
                {
                    "headline": f"{symbol} remains sensitive to macro and liquidity headlines",
                    "source": "Market Pulse Mock",
                    "asset_impact": symbol,
                    "impact_level": "medium",
                    "sentiment": "neutral",
                    "ai_explanation": "Headlines may affect short-term volatility, but lasting impact depends on confirmation from price, volume, and fundamentals.",
                    "risk_warning": "News placeholders are not live news and should not be used as trading signals.",
                }
            ],
            "disclaimer": "This is not financial advice.",
        }
