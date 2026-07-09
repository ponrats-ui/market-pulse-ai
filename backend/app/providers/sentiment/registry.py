from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict


class FearGreedProvider:
    name = "fear_greed"

    def fetch(self, symbol: str) -> Dict[str, Any]:
        return {
            "symbol": symbol,
            "score": None,
            "label": "Unavailable",
            "provider": self.name,
            "source": "Unavailable",
            "provider_configured": False,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "cache_age_seconds": 0,
            "confidence": "low",
            "unavailable_reason": "Fear & Greed provider is not configured.",
            "note": "Fear & Greed data unavailable.",
            "note_th": "ยังไม่มีข้อมูล Fear & Greed",
        }


def get_fear_greed_provider() -> FearGreedProvider:
    return FearGreedProvider()
