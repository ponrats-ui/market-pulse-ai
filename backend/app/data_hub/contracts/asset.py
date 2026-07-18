from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass(frozen=True)
class NormalizedAsset:
    canonical_symbol: str
    display_symbol: str
    provider_symbols: Dict[str, str]
    company_name: str
    asset_class: str
    exchange: str
    country: str
    currency: str
    aliases: List[str] = field(default_factory=list)
