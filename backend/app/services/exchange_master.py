from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List

PROJECT_DIR = Path(__file__).resolve().parents[3]
EXCHANGE_MASTER_PATH = PROJECT_DIR / "configs" / "exchange_master.json"


@lru_cache(maxsize=1)
def load_exchange_master() -> Dict[str, Any]:
    with EXCHANGE_MASTER_PATH.open("r", encoding="utf-8") as file:
        payload = json.load(file)
    assets = [_normalize_asset(asset) for asset in payload.get("assets", [])]
    return {**payload, "assets": assets}


def exchange_master_assets() -> List[Dict[str, Any]]:
    return load_exchange_master().get("assets", [])


def exchange_master_metadata() -> Dict[str, Any]:
    payload = load_exchange_master()
    return {
        "version": payload.get("version"),
        "source": payload.get("source"),
        "provider_ready": payload.get("provider_ready", False),
        "supported_exchanges": payload.get("supported_exchanges", []),
        "count": len(payload.get("assets", [])),
        "limitations": payload.get("limitations", []),
    }


def _normalize_asset(asset: Dict[str, Any]) -> Dict[str, Any]:
    aliases = asset.get("aliases", [])
    if isinstance(aliases, str):
        aliases = [aliases]
    return {
        "symbol": str(asset.get("symbol", "")).strip(),
        "label": str(asset.get("label", "")).strip(),
        "thai_name": str(asset.get("thai_name", "")).strip(),
        "asset_type": str(asset.get("asset_type", "unknown")).strip(),
        "market": str(asset.get("market") or asset.get("exchange") or "Unknown").strip(),
        "exchange": str(asset.get("exchange") or asset.get("market") or "Unknown").strip(),
        "sector": str(asset.get("sector", "")).strip(),
        "industry": str(asset.get("industry", "")).strip(),
        "country": str(asset.get("country", "")).strip(),
        "currency": str(asset.get("currency", "")).strip(),
        "keywords": " ".join(str(alias) for alias in aliases),
        "alias": " ".join(str(alias) for alias in aliases),
        "logo_url": str(asset.get("logo_url", "")).strip(),
    }
