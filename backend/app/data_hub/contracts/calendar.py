from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass(frozen=True)
class NormalizedCalendarEvent:
    date: str
    name: str
    region: str
    impact_level: str
    related_symbols: List[str]
    provider: str
    metadata: Dict[str, str] = field(default_factory=dict)
