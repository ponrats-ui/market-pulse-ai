from dataclasses import replace

from app.data_hub.master_asset_registry import list_registry_assets, search_registry, validate_master_asset_registry


def test_master_registry_has_no_duplicate_canonical_symbols() -> None:
    validation = validate_master_asset_registry()
    assert validation["valid"] is True
    assert validation["duplicates"] == []


def test_searchable_partial_coverage_asset_remains_selectable() -> None:
    result = search_registry("RKLB")
    assert result["assets"][0]["canonical_symbol"] == "RKLB"
    assert result["assets"][0]["live_data_capability"]["fundamentals"] == "partial"


def test_duplicate_canonical_symbols_are_rejected() -> None:
    asset = list_registry_assets(enabled_only=False)[0]
    validation = validate_master_asset_registry([asset, replace(asset)])
    assert validation["valid"] is False
    assert asset.canonical_symbol in validation["duplicates"]
