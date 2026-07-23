from __future__ import annotations

from app import main
from app.data_hub.master_asset_registry import MasterAsset
from app.intelligence.financial import build_financial_intelligence_report, classify_asset_for_intelligence, financial_intelligence_methodology, validate_primary_evidence_policy
from app.services import penny_opportunities as po


def registry_asset(symbol: str, asset_class: str = "equity", asset_type: str = "stock", sector: str = "Technology") -> MasterAsset:
    return MasterAsset(
        canonical_symbol=symbol,
        display_symbol=symbol,
        company_name=f"{symbol} Company",
        thai_name="",
        aliases=[],
        asset_class=asset_class,
        asset_type=asset_type,
        exchange="NASDAQ",
        market="US",
        country="United States",
        currency="USD",
        sector=sector,
        industry="Software",
        provider_symbols={"yfinance": symbol},
        enabled=True,
        searchable=True,
        coverage_source="test",
        coverage_timestamp=None,
        live_data_capability={"quote": "available", "history": "available"},
    )


def financial_payload(**overrides):
    payload = {
        "symbol": "AAPL",
        "source": "test_provider",
        "timestamp": "2026-07-23T00:00:00+00:00",
        "totalRevenue": 1000.0,
        "grossProfit": 430.0,
        "operatingIncome": 300.0,
        "netIncome": 240.0,
        "operatingCashFlow": 280.0,
        "freeCashFlow": 220.0,
        "totalAssets": 1400.0,
        "totalLiabilities": 700.0,
        "totalEquity": 700.0,
        "totalCash": 180.0,
        "totalDebt": 210.0,
        "currentAssets": 500.0,
        "currentLiabilities": 250.0,
        "revenueGrowth": 0.12,
        "earningsGrowth": 0.09,
        "trailingPE": 24.0,
        "priceToBook": 5.0,
    }
    payload.update(overrides)
    return payload


def test_classifies_corporate_equity(monkeypatch) -> None:
    monkeypatch.setattr("app.intelligence.financial.classification.get_registry_asset", lambda symbol: registry_asset(symbol))
    result = classify_asset_for_intelligence("AAPL", {"asset_type": "stock"})
    assert result.asset_class == "corporate_equity"
    assert result.selected_intelligence_profile == "corporate_financial"
    assert result.primary_evidence_domain == "financial_intelligence"


def test_classifies_financial_institution_boundary(monkeypatch) -> None:
    monkeypatch.setattr("app.intelligence.financial.classification.get_registry_asset", lambda symbol: registry_asset(symbol, sector="Financial Services"))
    result = classify_asset_for_intelligence("KBANK.BK", {"asset_type": "stock"})
    assert result.selected_intelligence_profile == "financial_institution"
    assert "Financial institution boundary selected" in " ".join(result.classification_limitations)


def test_etf_and_crypto_are_not_operating_company_models(monkeypatch) -> None:
    monkeypatch.setattr("app.intelligence.financial.classification.get_registry_asset", lambda symbol: registry_asset(symbol, "etf", "etf") if symbol == "SPY" else None)
    etf = classify_asset_for_intelligence("SPY", {"asset_type": "etf"})
    assert etf.selected_intelligence_profile == "fund_intelligence"
    assert etf.fallback_status == "not_applicable"
    crypto = classify_asset_for_intelligence("BTC-USD", {"asset_type": "crypto"})
    assert crypto.selected_intelligence_profile == "on_chain"
    assert crypto.primary_evidence_domain == "on_chain"


def test_primary_evidence_policy_requires_financial_to_be_largest() -> None:
    assert validate_primary_evidence_policy(po.PENNY_FACTOR_WEIGHTS)["valid"] is True
    assert validate_primary_evidence_policy({"financial": 0.40, "technical": 0.30})["valid"] is False
    assert validate_primary_evidence_policy({"financial": 0.55, "technical": 0.60})["valid"] is False


def test_financial_report_separates_score_confidence_and_completeness(monkeypatch) -> None:
    report = build_financial_intelligence_report("AAPL", financial_payload(), {"asset_type": "stock"}, registry_asset("AAPL"))
    assert report["status"] in {"measured", "partial"}
    assert report["financial_intelligence_score"] is not None
    assert report["confidence"] != report["financial_intelligence_score"]
    assert report["completeness"] != report["financial_intelligence_score"]
    assert report["primary_evidence_weight"] == 0.55


def test_missing_evidence_is_unavailable_not_zero(monkeypatch) -> None:
    report = build_financial_intelligence_report("AAPL", {"source": "test_provider", "timestamp": "missing"}, {"asset_type": "stock"}, registry_asset("AAPL"))
    assert report["financial_intelligence_score"] is None
    assert report["completeness"] == 0
    assert all(value is None for value in report["facts"].values())


def test_provider_failure_does_not_score_as_weakness(monkeypatch) -> None:
    report = build_financial_intelligence_report("AAPL", {"source": "test_provider", "error": "provider down"}, {"asset_type": "stock"}, registry_asset("AAPL"))
    assert report["financial_intelligence_score"] is None
    assert report["confidence"] == 0
    assert report["status"] == "unavailable"


def test_cache_key_uses_version_metadata(monkeypatch) -> None:
    first = build_financial_intelligence_report("AAPL", financial_payload(timestamp="cache-test"), {"asset_type": "stock"}, registry_asset("AAPL"))
    second = build_financial_intelligence_report("AAPL", financial_payload(timestamp="cache-test"), {"asset_type": "stock"}, registry_asset("AAPL"))
    assert first["cache_metadata"]["cache_hit"] is False
    assert second["cache_metadata"]["cache_hit"] is True
    assert first["versions"] == second["versions"]


def test_api_contract_returns_financial_intelligence(monkeypatch) -> None:
    monkeypatch.setattr(main, "get_cached_fundamentals", lambda symbol: financial_payload(symbol=symbol))
    monkeypatch.setattr(main, "get_cached_quote", lambda symbol: {"symbol": symbol, "asset_type": "stock", "timestamp": "2026-07-23T00:00:00+00:00"})
    payload = main.financial_intelligence("AAPL")
    assert payload["symbol"] == "AAPL"
    assert payload["versions"]["methodology_version"]
    assert main.financial_intelligence_methodology_endpoint()["status"] == "ok"


def test_methodology_exposes_financial_weight_policy() -> None:
    payload = financial_intelligence_methodology()
    assert payload["primary_evidence_policy"]["target_weight"] == 0.55
    assert payload["formula_version"]
