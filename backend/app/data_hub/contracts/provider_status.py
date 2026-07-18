from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ProviderStatus:
    provider: str
    data_type: str
    status: str
    reason: str | None = None
