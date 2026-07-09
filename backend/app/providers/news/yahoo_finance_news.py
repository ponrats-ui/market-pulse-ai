from __future__ import annotations

import os

from app.providers.news.rss_provider import RSSNewsProvider


class YahooFinanceNewsProvider(RSSNewsProvider):
    name = "yahoo_finance_news"

    def __init__(self) -> None:
        enabled = os.getenv("ENABLE_YAHOO_FINANCE_NEWS", "").strip().lower() in {"1", "true", "yes"}
        super().__init__("https://feeds.finance.yahoo.com/rss/2.0/headline?s={query}&region=US&lang=en-US" if enabled else "")
