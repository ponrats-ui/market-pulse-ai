from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass(frozen=True)
class NormalizedNewsItem:
    headline: str
    original_url: str | None
    source: str
    published_at: str | None
    related_symbols: List[str]
    provider: str
    summary: str | None = None
    impact_metadata: Dict[str, Any] = field(default_factory=dict)
