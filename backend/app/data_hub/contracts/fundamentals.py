from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict


@dataclass(frozen=True)
class NormalizedFundamentals:
    symbol: str
    income_statement: Dict[str, Any]
    balance_sheet: Dict[str, Any]
    cash_flow: Dict[str, Any]
    ratios: Dict[str, Any]
    provider: str
    field_availability: Dict[str, str] = field(default_factory=dict)
    timestamp: str | None = None
