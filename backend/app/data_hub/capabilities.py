from __future__ import annotations

from typing import Any, Dict

from app.data_hub.master_asset_registry import master_asset_registry_metadata
from app.data_hub.symbol_resolver import resolve_symbol


def capabilities_for_symbol(symbol: str) -> Dict[str, Any]:
    resolved = resolve_symbol(symbol)
    if not resolved.ok or not resolved.asset:
        return {
            "symbol": symbol,
            "resolved": False,
            "reason": resolved.reason,
            "capabilities": {},
            "metadata": master_asset_registry_metadata(),
        }
    asset = resolved.asset
    raw = asset.get("data_capabilities") or asset.get("live_data_capability") or {}
    asset_type = asset.get("asset_type")
    capabilities = {
        "quote": _status(raw.get("quote")),
        "history": _status(raw.get("history")),
        "technicals": "available" if raw.get("history") else "unavailable",
        "fundamentals": _fundamental_status(asset_type, raw.get("fundamentals")),
        "news": _status(raw.get("news")),
        "calendar": raw.get("calendar", "provider_not_configured"),
        "risk": "available" if raw.get("quote") else "partial",
        "comparison": "available" if raw.get("quote") and raw.get("history") else "partial",
        "portfolio": "available" if raw.get("quote") else "partial",
    }
    return {
        "symbol": resolved.canonical_symbol,
        "resolved": True,
        "asset_class": asset.get("asset_class"),
        "asset_type": asset_type,
        "capabilities": capabilities,
        "metadata": master_asset_registry_metadata(),
    }


def _status(value: Any) -> str:
    if value is True:
        return "available"
    if value is False or value is None:
        return "unavailable"
    return str(value)


def _fundamental_status(asset_type: str | None, value: Any) -> str:
    if asset_type in {"crypto", "commodity", "index", "fx", "macro"}:
        return "not_applicable"
    return _status(value)
