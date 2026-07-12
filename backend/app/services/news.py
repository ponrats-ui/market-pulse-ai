from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List

from app.data_hub.exchange_master import exchange_master_metadata
from app.data_hub.symbol_resolver import resolve_symbol
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
    resolved = resolve_symbol(symbol)
    canonical = resolved.canonical_symbol or symbol
    key = cache_key("intelligence", "news", canonical, str(limit))
    cached, age = cache.get_with_age(key)
    if cached is not None:
        return _with_cache_age(cached, age)
    payload = get_news_aggregator().fetch(canonical, limit) if resolved.ok else _unsupported_news_payload(symbol, resolved.reason)
    items = [_classify_article(canonical, item) for item in payload.get("items", [])]
    response = {
        "symbol": canonical,
        "items": items,
        "source": payload.get("provider", "Unavailable"),
        "provider": payload.get("provider", "Unavailable"),
        "provider_configured": payload.get("provider_configured", False),
        "provider_status": payload.get("fallback_attempts", []),
        "data_hub": _data_hub_metadata(canonical, resolved.ok, resolved.reason),
        "timestamp": payload.get("timestamp") or _now(),
        "cache_age_seconds": 0,
        "confidence": payload.get("confidence", "low"),
        "unavailable_reason": payload.get("unavailable_reason"),
        "message": None if items else payload.get("unavailable_reason", "No news provider returned articles."),
        "message_th": None if items else "ยังไม่มีผู้ให้บริการข่าวที่พร้อมใช้งานสำหรับสินทรัพย์นี้",
        "disclaimer": "This is not financial advice.",
    }
    return cache.set(key, response, INTELLIGENCE_TTL_SECONDS)


def news_impact_for_symbol(symbol: str, limit: int = 10) -> Dict[str, Any]:
    payload = news_for_symbol(symbol, limit)
    impact_items = [
        {
            "headline": item["title"],
            "source": item.get("source", payload["source"]),
            "url": item.get("url"),
            "published_at": item.get("published_at"),
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
            "reasoning": item["reasoning"],
            "cross_asset_effects": item["cross_asset_effects"],
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
    related_assets = _related_assets(symbol, text)
    return {
        **item,
        "summary": title if title else "Unavailable",
        "category": category,
        "affected_assets": related_assets,
        "affected_sector": _sector_for_category(category),
        "importance": importance,
        "impact_strength": importance,
        "expected_duration": _expected_duration(category),
        "confidence": confidence,
        "direction": direction,
        "immediate_impact": direction,
        "short_term_impact": direction if confidence == "medium" else "Neutral",
        "long_term_impact": "Neutral",
        "reasoning": evidence,
        "cross_asset_effects": _cross_asset_effects(related_assets, category),
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


def _related_assets(symbol: str, text: str) -> List[str]:
    assets = [symbol] if symbol else []
    if "nvidia" in text or "nvda" in text:
        assets.extend(["AMD", "TSM", "QQQ", "SOXX"])
    if "bitcoin" in text or "btc" in text:
        assets.extend(["ETH-USD", "SOL-USD"])
    if "oil" in text or "energy" in text:
        assets.extend(["CL=F", "BZ=F", "XLE"])
    if "gold" in text:
        assets.extend(["GC=F", "GLD", "SI=F"])
    return list(dict.fromkeys(assets))


def _expected_duration(category: str) -> str:
    return {
        "Earnings": "Short term to medium term",
        "Guidance": "Medium term",
        "M&A": "Medium term",
        "Central Bank": "Short term market-wide",
        "Geopolitics": "Uncertain duration",
        "Regulation": "Medium term to long term",
    }.get(category, "Short term")


def _cross_asset_effects(assets: List[str], category: str) -> List[Dict[str, str]]:
    return [{"asset": asset, "effect": f"Potential {category.lower()} related sensitivity"} for asset in assets[1:]]


def _with_cache_age(payload: Dict[str, Any], age: int | None) -> Dict[str, Any]:
    return {**payload, "cache_age_seconds": age or 0}


def _data_hub_metadata(symbol: str, supported: bool, reason: str | None) -> Dict[str, Any]:
    return {
        "canonical_symbol": symbol if supported else None,
        "data_type": "news",
        "provider": "news_aggregator" if supported else "Unavailable",
        "provider_failures": [] if supported else [{"provider": "news_aggregator", "reason": reason or "unsupported_asset"}],
        "universe_version": exchange_master_metadata().get("version"),
        "coverage_status": exchange_master_metadata().get("coverage_status", "partial"),
    }


def _unsupported_news_payload(symbol: str, reason: str | None) -> Dict[str, Any]:
    return {
        "symbol": symbol,
        "provider": "Unavailable",
        "provider_configured": False,
        "items": [],
        "timestamp": _now(),
        "confidence": "low",
        "unavailable_reason": reason or "unsupported_asset",
        "fallback_attempts": [{"provider": "news_aggregator", "configured": False, "reason": reason or "unsupported_asset"}],
    }


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()
