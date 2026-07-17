from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from typing import Any, Dict
from urllib.request import Request, urlopen


class FearGreedProvider:
    name = "fear_greed"

    def fetch(self, symbol: str) -> Dict[str, Any]:
        if os.getenv("ENABLE_ALTERNATIVE_ME_FEAR_GREED", "").strip().lower() in {"1", "true", "yes"}:
            return self._fetch_alternative_me(symbol)
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

    def _fetch_alternative_me(self, symbol: str) -> Dict[str, Any]:
        try:
            request = Request("https://api.alternative.me/fng/?limit=1&format=json", headers={"User-Agent": "MarketPulseAI/0.3"})
            with urlopen(request, timeout=8) as response:
                payload = json.loads(response.read().decode("utf-8"))
            item = (payload.get("data") or [{}])[0]
            score = int(item["value"]) if item.get("value") is not None else None
            label = item.get("value_classification") or "Unavailable"
            return {
                "symbol": symbol,
                "score": score,
                "label": label,
                "provider": "alternative_me",
                "source": "alternative.me",
                "provider_configured": True,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "cache_age_seconds": 0,
                "confidence": "medium" if score is not None else "low",
                "unavailable_reason": None if score is not None else "Alternative.me returned no score.",
                "note": "Crypto Fear & Greed index from Alternative.me.",
                "note_th": "ข้อมูล Fear & Greed จาก Alternative.me",
            }
        except Exception as exc:
            return {
                "symbol": symbol,
                "score": None,
                "label": "Unavailable",
                "provider": "alternative_me",
                "source": "Unavailable",
                "provider_configured": True,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "cache_age_seconds": 0,
                "confidence": "low",
                "unavailable_reason": f"Alternative.me Fear & Greed request failed: {exc}",
                "note": "Fear & Greed data unavailable.",
                "note_th": "ยังไม่มีข้อมูล Fear & Greed",
            }


def get_fear_greed_provider() -> FearGreedProvider:
    return FearGreedProvider()
