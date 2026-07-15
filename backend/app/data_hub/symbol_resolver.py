from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Dict

from app.data_hub.master_asset_registry import MasterAsset, list_registry_assets


@dataclass(frozen=True)
class ResolutionResult:
    ok: bool
    query: str
    canonical_symbol: str | None = None
    display_symbol: str | None = None
    provider_symbols: Dict[str, str] | None = None
    asset: Dict[str, Any] | None = None
    reason: str | None = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def resolve_symbol(query: str, provider: str = "yfinance") -> ResolutionResult:
    term = str(query or "").strip()
    if not term:
        return ResolutionResult(False, query, reason="empty_query")
    normalized = _normalize(term)
    for asset in list_registry_assets(enabled_only=True, searchable_only=True):
        if _matches(asset, normalized):
            provider_symbol = asset.provider_symbols.get(provider)
            if not provider_symbol:
                return ResolutionResult(False, query, reason=f"provider_symbol_unavailable:{provider}")
            return ResolutionResult(
                True,
                query,
                canonical_symbol=asset.canonical_symbol,
                display_symbol=asset.display_symbol,
                provider_symbols=asset.provider_symbols,
                asset=asset.to_dict(),
            )
    return ResolutionResult(False, query, reason="unsupported_under_current_universe")


def provider_symbol(query: str, provider: str = "yfinance") -> str | None:
    resolved = resolve_symbol(query, provider)
    if not resolved.ok or not resolved.provider_symbols:
        return None
    return resolved.provider_symbols.get(provider)


def _matches(asset: MasterAsset, normalized: str) -> bool:
    candidates = [asset.canonical_symbol, asset.display_symbol, asset.company_name, asset.thai_name, *asset.aliases]
    return any(_normalize(candidate) == normalized for candidate in candidates if candidate)


def _normalize(value: str) -> str:
    return str(value).strip().casefold().replace(" ", "")
