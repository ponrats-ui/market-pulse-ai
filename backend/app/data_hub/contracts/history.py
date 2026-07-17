from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass(frozen=True)
class NormalizedHistory:
    symbol: str
    range: str
    interval: str
    points: List[Dict[str, Any]]
    provider: str
    unavailable_fields: List[str] = field(default_factory=list)
