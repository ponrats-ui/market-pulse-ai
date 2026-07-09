from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict


class MacroProvider:
    name = "macro_unconfigured"

    def fetch(self) -> Dict[str, Any]:
        return {
            "items": [],
            "provider": self.name,
            "source": "Unavailable",
            "provider_configured": False,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "cache_age_seconds": 0,
            "confidence": "low",
            "unavailable_reason": "FRED or macro provider credentials are not configured.",
            "supported_indicators": ["US Rates", "Inflation", "Unemployment", "Yield Curve", "Dollar Index", "Oil", "Gold", "VIX"],
        }


def get_macro_provider() -> MacroProvider:
    return MacroProvider()
