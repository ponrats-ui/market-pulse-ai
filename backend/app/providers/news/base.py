from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Any, Dict, List


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class NewsProvider(ABC):
    name: str
    configured: bool = False

    @abstractmethod
    def fetch(self, query: str, limit: int = 10) -> Dict[str, Any]:
        raise NotImplementedError


def unavailable_news(provider: str, reason: str) -> Dict[str, Any]:
    return {
        "provider": provider,
        "provider_configured": False,
        "items": [],
        "timestamp": utc_now(),
        "cache_age_seconds": 0,
        "confidence": "low",
        "unavailable_reason": reason,
    }


def provider_payload(provider: str, items: List[Dict[str, Any]], confidence: str = "medium") -> Dict[str, Any]:
    return {
        "provider": provider,
        "provider_configured": True,
        "items": items,
        "timestamp": utc_now(),
        "cache_age_seconds": 0,
        "confidence": confidence if items else "low",
        "unavailable_reason": None if items else "Provider returned no articles.",
    }
