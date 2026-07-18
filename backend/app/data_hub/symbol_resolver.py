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
    assets = sorted(list_registry_assets(enabled_only=True, searchable_only=True), key=_asset_rank_priority)
    matches = [(score, asset) for asset in assets if (score := _match_score(asset, normalized)) > 0]
    if matches:
        _, asset = max(matches, key=lambda item: (item[0], -_asset_rank_priority(item[1])[0], item[1].canonical_symbol))
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
    return _match_score(asset, normalized) > 0


def _match_score(asset: MasterAsset, normalized: str) -> int:
    if _normalize(asset.canonical_symbol) == normalized:
        return 100
    if _normalize(asset.display_symbol) == normalized:
        return 95
    if asset.thai_name and _normalize(asset.thai_name) == normalized:
        return 90
    if asset.company_name and _normalize(asset.company_name) == normalized:
        return 80
    if any(_normalize(alias) == normalized for alias in asset.aliases if alias):
        return 70
    return 0


def _normalize(value: str) -> str:
    return str(value).strip().casefold().replace(" ", "").replace("-", "").replace(".", "")


def _asset_rank_priority(asset: MasterAsset) -> tuple[int, str]:
    if asset.country == "Thailand":
        if asset.asset_type == "stock" and "-" not in asset.display_symbol:
            return (0, asset.canonical_symbol)
        if asset.asset_type in {"foreign_stock", "preferred_stock"}:
            return (4, asset.canonical_symbol)
        if asset.asset_class == "fund":
            return (2, asset.canonical_symbol)
    return (1, asset.canonical_symbol)
