from __future__ import annotations

from typing import Any, Dict, List

EVENT_TYPES = (
    "War",
    "Ceasefire",
    "Tariffs",
    "Sanctions",
    "Trade Agreements",
    "Oil Disruptions",
    "Shipping Routes",
    "Semiconductor Restrictions",
    "Energy Policy",
    "AI Regulation",
    "Government Subsidies",
    "Military Conflict",
)


def classify_global_events(events: List[Dict[str, Any]] | None = None) -> List[Dict[str, Any]]:
    results = []
    for event in events or []:
        event_type = event.get("type") if event.get("type") in EVENT_TYPES else "Unavailable"
        results.append({
            "type": event_type,
            "affected_sectors": event.get("affected_sectors", []),
            "affected_countries": event.get("affected_countries", []),
            "affected_assets": event.get("affected_assets", []),
            "expected_duration": event.get("expected_duration", "Unavailable"),
            "confidence": event.get("confidence", "low"),
        })
    return results
