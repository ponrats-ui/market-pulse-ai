from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Any, Dict


class EconomicCalendarProvider(ABC):
    name: str

    @abstractmethod
    def fetch_high_impact(self) -> Dict[str, Any]:
        raise NotImplementedError


def unavailable_calendar(provider: str, reason: str) -> Dict[str, Any]:
    return {
        "events": [],
        "items": [],
        "provider": provider,
        "source": "Unavailable",
        "provider_configured": False,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "cache_age_seconds": 0,
        "confidence": "low",
        "unavailable_reason": reason,
    }
