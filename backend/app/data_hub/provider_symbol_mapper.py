from __future__ import annotations

import re
from dataclasses import dataclass


_COMMON_THAI_SYMBOL_RE = re.compile(r"^[A-Z0-9]{1,16}$")
_THAI_FOREIGN_BOARD_SUFFIX = "-F"
_THAI_EXCHANGE_SUFFIX = ".BK"


@dataclass(frozen=True)
class ProviderSymbolMapping:
    input_symbol: str
    normalized_input: str
    canonical_symbol: str | None
    provider_symbol: str | None
    market: str
    provider: str
    board: str
    supported: bool
    exclusion_reason: str | None = None


def map_thai_yfinance_symbol(symbol: str) -> ProviderSymbolMapping:
    """Normalize Thai equity symbols for Yahoo Finance without leaking board variants."""
    raw = str(symbol or "").strip()
    normalized = raw.upper()
    provider = "yfinance"
    market = "TH"

    if not normalized:
        return ProviderSymbolMapping(raw, normalized, None, None, market, provider, "unknown", False, "empty_symbol")
    if normalized.count(_THAI_EXCHANGE_SUFFIX) > 1:
        return ProviderSymbolMapping(raw, normalized, None, None, market, provider, "unknown", False, "duplicate_exchange_suffix")
    if normalized.endswith(_THAI_EXCHANGE_SUFFIX):
        base = normalized[: -len(_THAI_EXCHANGE_SUFFIX)]
    else:
        base = normalized
    if not base:
        return ProviderSymbolMapping(raw, normalized, None, None, market, provider, "unknown", False, "empty_symbol")
    if base.endswith(_THAI_FOREIGN_BOARD_SUFFIX):
        canonical = base[: -len(_THAI_FOREIGN_BOARD_SUFFIX)]
        return ProviderSymbolMapping(raw, normalized, canonical or None, None, market, provider, "foreign_board", False, "foreign_board_excluded")
    if "-" in base:
        return ProviderSymbolMapping(raw, normalized, None, None, market, provider, "special_board", False, "special_board_excluded")
    if not _COMMON_THAI_SYMBOL_RE.fullmatch(base):
        return ProviderSymbolMapping(raw, normalized, None, None, market, provider, "unknown", False, "malformed_symbol")
    return ProviderSymbolMapping(raw, normalized, base, f"{base}{_THAI_EXCHANGE_SUFFIX}", market, provider, "common", True)


def map_provider_symbol(symbol: str, market: str, provider: str) -> ProviderSymbolMapping:
    selected_market = str(market or "").strip().upper()
    selected_provider = str(provider or "").strip().lower()
    if selected_market == "TH" and selected_provider == "yfinance":
        return map_thai_yfinance_symbol(symbol)
    normalized = str(symbol or "").strip().upper()
    return ProviderSymbolMapping(str(symbol or ""), normalized, normalized or None, normalized or None, selected_market, selected_provider, "default", bool(normalized))
