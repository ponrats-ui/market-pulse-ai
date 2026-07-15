from dataclasses import replace

from app.data_hub.master_asset_registry import (
    list_registry_assets,
    master_asset_registry_metadata,
    search_registry,
    validate_master_asset_registry,
)


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


def test_thai_master_registry_has_hundreds_of_verified_records() -> None:
    metadata = master_asset_registry_metadata()
    thai_source = next(source for source in metadata["sources"] if source["name"] == "verified_set_public_listing_csv")
    assert thai_source["record_count"] >= 1800
    thai_assets = [asset for asset in list_registry_assets() if asset.country == "Thailand" and asset.exchange in {"SET", "mai"}]
    assert len(thai_assets) >= 1800


def test_thai_registry_payload_contains_clean_names_and_provider_mapping() -> None:
    result = search_registry("KKP")
    asset = result["assets"][0]
    assert asset["canonical_symbol"] == "KKP.BK"
    assert asset["display_symbol"] == "KKP"
    assert asset["thai_name"] == "ธนาคารเกียรตินาคินภัทร จำกัด (มหาชน)"
    assert asset["provider_symbols"]["yfinance"] == "KKP.BK"
    assert asset["country"] == "Thailand"
    assert asset["coverage_source"].endswith("verified_set_public_listing_csv")


def test_invalid_thai_provider_mapping_is_rejected() -> None:
    asset = next(item for item in list_registry_assets() if item.canonical_symbol == "KKP.BK")
    broken = replace(asset, provider_symbols={"yfinance": "KKP"})
    validation = validate_master_asset_registry([broken])
    assert validation["valid"] is False
    assert "KKP.BK" in validation["invalid_thai_mapping"]
