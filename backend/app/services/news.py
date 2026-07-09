from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List

from app.providers.news import get_news_aggregator
from app.services.cache import INTELLIGENCE_TTL_SECONDS, cache, cache_key

NEWS_CATEGORIES = {
    "earnings": "Earnings",
    "guidance": "Guidance",
    "merger": "M&A",
    "acquisition": "M&A",
    "dividend": "Dividend",
    "product": "Product Launch",
    "launch": "Product Launch",
    "ai": "AI",
    "semiconductor": "Semiconductor",
    "chip": "Semiconductor",
    "energy": "Energy",
    "oil": "Energy",
    "defense": "Defense",
    "healthcare": "Healthcare",
    "government": "Government",
    "inflation": "Macroeconomics",
    "fomc": "Central Bank",
    "fed": "Central Bank",
    "supply": "Supply Chain",
    "regulation": "Regulation",
    "war": "Geopolitics",
    "sanction": "Geopolitics",
}

BULLISH_WORDS = {"beats", "raises", "growth", "surges", "approval", "deal", "record"}
BEARISH_WORDS = {"misses", "cuts", "falls", "lawsuit", "probe", "sanction", "warning", "recall"}


def news_for_symbol(symbol: str, limit: int = 10) -> Dict[str, Any]:
    key = cache_key("intelligence", "news", symbol, str(limit))
    cached, age = cache.get_with_age(key)
    if cached is not None:
        return _with_cache_age(cached, age)
    payload = get_news_aggregator().fetch(symbol, limit)
    items = [_classify_article(symbol, item) for item in payload.get("items", [])]
    response = {
        "symbol": symbol,
        "items": items,
        "source": payload.get("provider", "Unavailable"),
        "provider": payload.get("provider", "Unavailable"),
        "provider_configured": payload.get("provider_configured", False),
        "provider_status": payload.get("fallback_attempts", []),
        "timestamp": payload.get("timestamp") or _now(),
        "cache_age_seconds": 0,
        "confidence": payload.get("confidence", "low"),
        "unavailable_reason": payload.get("unavailable_reason"),
        "message": None if items else payload.get("unavailable_reason", "No news provider returned articles."),
        "message_th": None if items else "ยังไม่มีผู้ให้บริการข่าวที่พร้อมใช้งาน",
        "disclaimer": "This is not financial advice.",
    }
    return cache.set(key, response, INTELLIGENCE_TTL_SECONDS)


def news_impact_for_symbol(symbol: str, limit: int = 10) -> Dict[str, Any]:
    payload = news_for_symbol(symbol, limit)
    impact_items = [
        {
            "headline": item["title"],
            "source": item.get("source", payload["source"]),
            "category": item["category"],
            "asset_impact": item["immediate_impact"],
            "immediate_impact": item["immediate_impact"],
            "short_term_impact": item["short_term_impact"],
            "long_term_impact": item["long_term_impact"],
            "impact_level": item["importance"],
            "sentiment": item["direction"],
            "affected_assets": item["affected_assets"],
            "affected_sector": item["affected_sector"],
            "confidence": item["confidence"],
            "evidence": item["evidence"],
            "ai_explanation": item["evidence"],
            "risk_warning": "News impact is directional context only and can change quickly.",
        }
        for item in payload.get("items", [])
    ]
    return {**payload, "items": impact_items}


def _classify_article(symbol: str, item: Dict[str, Any]) -> Dict[str, Any]:
    title = str(item.get("title", ""))
    text = title.lower()
    category = next((label for key, label in NEWS_CATEGORIES.items() if key in text), "Unavailable")
    direction = _direction(text)
    importance = "High" if category in {"Earnings", "Guidance", "M&A", "Central Bank", "Geopolitics", "Regulation"} else "Medium"
    confidence = "medium" if category != "Unavailable" else "low"
    evidence = f"Classified from provider headline: {title}" if title else "Provider did not return a headline."
    return {
        **item,
        "category": category,
        "affected_assets": [symbol] if symbol else [],
        "affected_sector": _sector_for_category(category),
        "importance": importance,
        "confidence": confidence,
        "direction": direction,
        "immediate_impact": direction,
        "short_term_impact": direction if confidence == "medium" else "Neutral",
        "long_term_impact": "Neutral",
        "evidence": evidence,
    }


def _direction(text: str) -> str:
    if any(word in text for word in BULLISH_WORDS):
        return "Bullish"
    if any(word in text for word in BEARISH_WORDS):
        return "Bearish"
    return "Neutral"


def _sector_for_category(category: str) -> str:
    return {
        "AI": "Technology",
        "Semiconductor": "Semiconductors",
        "Energy": "Energy",
        "Defense": "Defense",
        "Healthcare": "Healthcare",
        "Central Bank": "Macro",
        "Macroeconomics": "Macro",
        "Geopolitics": "Macro",
    }.get(category, "Unavailable")


def _with_cache_age(payload: Dict[str, Any], age: int | None) -> Dict[str, Any]:
    return {**payload, "cache_age_seconds": age or 0}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()
