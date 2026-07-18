from __future__ import annotations

from typing import Any, Dict, List

from app.data_hub.exchange_master import exchange_master_metadata as data_hub_metadata
from app.data_hub.exchange_master import list_assets


def exchange_master_assets() -> List[Dict[str, Any]]:
    return [asset.to_search_asset() for asset in list_assets(enabled_only=True)]


def exchange_master_metadata() -> Dict[str, Any]:
    return data_hub_metadata()
