from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict


class CompanyEventsProvider:
    name = "company_events_unconfigured"

    def fetch(self, symbol: str) -> Dict[str, Any]:
        return {
            "symbol": symbol,
            "events": [],
            "provider": self.name,
            "source": "Unavailable",
            "provider_configured": False,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "cache_age_seconds": 0,
            "confidence": "low",
            "unavailable_reason": "Company events provider is not configured.",
            "supported_events": ["Earnings", "Dividend", "Split", "Guidance", "Buyback", "Insider", "M&A", "SEC Filing"],
        }


def get_company_events_provider() -> CompanyEventsProvider:
    return CompanyEventsProvider()
