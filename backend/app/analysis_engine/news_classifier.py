from __future__ import annotations

from typing import Any, Dict, List

NEWS_TYPES = ("Earnings", "Guidance", "Acquisition", "Merger", "Government", "Supply Chain", "AI", "Energy", "Defense", "Banking", "Healthcare")


def classify_news(items: List[Dict[str, Any]] | None = None) -> List[Dict[str, Any]]:
    classified = []
    for item in items or []:
        category = item.get("category") if item.get("category") in NEWS_TYPES else "Unavailable"
        classified.append({
            "category": category,
            "impact": item.get("impact", "Unavailable"),
            "affected_companies": item.get("affected_companies", []),
            "affected_sectors": item.get("affected_sectors", []),
            "confidence": item.get("confidence", "low"),
        })
    return classified
