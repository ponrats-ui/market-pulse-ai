from __future__ import annotations

import os
import xml.etree.ElementTree as ET
from typing import Any, Dict
from urllib.parse import quote_plus
from urllib.request import Request, urlopen

from app.providers.news.base import NewsProvider, provider_payload, unavailable_news


class RSSNewsProvider(NewsProvider):
    name = "rss"

    def __init__(self, feed_url: str | None = None) -> None:
        self.feed_url = feed_url or os.getenv("NEWS_RSS_URL", "")
        self.configured = bool(self.feed_url)

    def fetch(self, query: str, limit: int = 10) -> Dict[str, Any]:
        if not self.feed_url:
            return unavailable_news(self.name, "NEWS_RSS_URL is not configured.")
        url = self.feed_url.format(query=quote_plus(query))
        try:
            request = Request(url, headers={"User-Agent": "MarketPulseAI/0.3"})
            with urlopen(request, timeout=8) as response:
                raw = response.read()
            root = ET.fromstring(raw)
            items = []
            for item in root.findall(".//item")[:limit]:
                title = _text(item, "title")
                link = _text(item, "link")
                published_at = _text(item, "pubDate")
                if title:
                    items.append({"title": title, "url": link, "published_at": published_at, "source": self.name})
            return provider_payload(self.name, items)
        except Exception as exc:
            return unavailable_news(self.name, f"RSS provider failed: {exc}")


def _text(item: ET.Element, tag: str) -> str:
    value = item.findtext(tag)
    return value.strip() if value else ""
