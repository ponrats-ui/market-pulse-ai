from app.services.analysis import build_ai_analysis, build_risk


def test_analysis_preserves_data_hub_metadata_on_available_quote() -> None:
    quote = {
        "symbol": "TTB.BK",
        "price": 2.64,
        "change_percent": -0.75,
        "source": "test",
        "timestamp": "2026-01-01T00:00:00Z",
        "data_hub": {"canonical_symbol": "TTB.BK", "data_type": "quote"},
    }
    payload = build_ai_analysis("TTB.BK", quote, {"points": [{"close": 2.5}, {"close": 2.6}, {"close": 2.64}]})
    assert payload["data_hub"]["canonical_symbol"] == "TTB.BK"
    assert payload["algorithm_version"]


def test_risk_preserves_data_hub_metadata() -> None:
    quote = {
        "symbol": "TTB.BK",
        "asset_type": "thai_stock",
        "change_percent": -0.75,
        "source": "test",
        "data_hub": {"canonical_symbol": "TTB.BK", "data_type": "quote"},
    }
    payload = build_risk("TTB.BK", quote, {"points": [{"close": 2.5}, {"close": 2.6}, {"close": 2.64}]})
    assert payload["data_hub"]["canonical_symbol"] == "TTB.BK"
    assert payload["asset_type"] == "thai_stock"
