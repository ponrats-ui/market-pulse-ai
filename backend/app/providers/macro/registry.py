from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from typing import Any, Dict
from urllib.parse import urlencode
from urllib.request import urlopen

FRED_SERIES = {
    "FEDFUNDS": "Federal Funds Rate",
    "CPIAUCSL": "Consumer Price Index",
    "UNRATE": "Unemployment Rate",
    "DGS10": "10-Year Treasury Rate",
    "DGS2": "2-Year Treasury Rate",
}


class MacroProvider:
    name = "fred"

    def fetch(self) -> Dict[str, Any]:
        api_key = os.getenv("FRED_API_KEY", "").strip()
        if api_key:
            return self._fetch_fred(api_key)
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

    def _fetch_fred(self, api_key: str) -> Dict[str, Any]:
        items = []
        errors = []
        for series_id, name in FRED_SERIES.items():
            try:
                params = urlencode({
                    "series_id": series_id,
                    "api_key": api_key,
                    "file_type": "json",
                    "sort_order": "desc",
                    "limit": 1,
                })
                with urlopen(f"https://api.stlouisfed.org/fred/series/observations?{params}", timeout=8) as response:
                    payload = json.loads(response.read().decode("utf-8"))
                observation = (payload.get("observations") or [{}])[0]
                value = observation.get("value")
                items.append({
                    "series_id": series_id,
                    "name": name,
                    "date": observation.get("date"),
                    "value": None if value in (None, ".") else float(value),
                    "source": "FRED",
                })
            except Exception as exc:
                errors.append(f"{series_id}: {exc}")
        return {
            "items": items,
            "provider": self.name,
            "source": "FRED" if items else "Unavailable",
            "provider_configured": True,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "cache_age_seconds": 0,
            "confidence": "medium" if items else "low",
            "unavailable_reason": None if items else f"FRED request failed: {'; '.join(errors)}",
            "supported_indicators": list(FRED_SERIES.values()),
            "provider_errors": errors,
        }


def get_macro_provider() -> MacroProvider:
    return MacroProvider()
