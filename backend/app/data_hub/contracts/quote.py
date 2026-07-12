from __future__ import annotations

from dataclasses import dataclass, field
from typing import List


@dataclass(frozen=True)
class NormalizedQuote:
    symbol: str
    price: float | None
    currency: str
    change: float | None
    change_percent: float | None
    volume: float | None
    market_cap: float | None
    timestamp: str | None
    provider: str
    cache_age_seconds: int | None = None
    confidence: str = "low"
    unavailable_fields: List[str] = field(default_factory=list)
