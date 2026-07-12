from app.data_hub.exchange_master import exchange_master_metadata, get_asset, validate_exchange_master


def test_exchange_master_validates_and_maps_provider_symbol() -> None:
    validation = validate_exchange_master()
    assert validation["valid"] is True
    assert validation["duplicates"] == []
    assert validation["record_count"] > 0
    asset = get_asset("TTB.BK")
    assert asset is not None
    assert asset.provider_symbols["yfinance"] == "TTB.BK"
    assert asset.enabled is True


def test_exchange_master_metadata_reports_partial_coverage() -> None:
    metadata = exchange_master_metadata()
    assert metadata["version"]
    assert metadata["record_count"] > 0
    assert metadata["coverage_status"] in {"partial", "verified_ingestion_partial"}
