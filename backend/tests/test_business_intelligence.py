from __future__ import annotations

from app import main
from app.data_hub.master_asset_registry import MasterAsset
from app.intelligence.business import build_business_intelligence_report, business_intelligence_methodology
from app.intelligence.financial import build_financial_intelligence_report


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


def corporate_financial_report(symbol: str = "AAPL", **overrides):
    payload = financial_payload(symbol=symbol, **overrides)
    return build_financial_intelligence_report(symbol, payload, {"asset_type": "stock", "source": "test_provider", "timestamp": payload["timestamp"]}, registry_asset(symbol))


def test_business_methodology_exposes_evidence_policy() -> None:
    payload = business_intelligence_methodology()
    assert payload["status"] == "ok"
    assert payload["methodology_version"] == "business-intelligence-v1"
    assert "competitive_advantage_evidence" in payload["domains"]
    assert "Founder-approved methodology migration" in payload["relationship_to_financial_intelligence"]["activation_policy"]


def test_corporate_business_report_keeps_business_score_separate() -> None:
    financial = corporate_financial_report()
    report = build_business_intelligence_report("AAPL", {"asset_type": "stock", "source": "test_provider", "timestamp": "2026-07-23T00:00:00+00:00"}, financial)
    assert report["applicable"] is True
    assert report["status"] in {"measured", "partial"}
    assert report["business_intelligence_score"] is not None
    assert report["business_confidence"] != report["business_intelligence_score"]
    assert report["business_completeness"] != report["business_intelligence_score"]
    assert report["financial_intelligence_reference"]["financial_intelligence_score"] == financial["financial_intelligence_score"]


def test_business_report_does_not_fabricate_competitive_advantage_or_governance() -> None:
    report = build_business_intelligence_report("AAPL", {"asset_type": "stock", "timestamp": "no-fabrication"}, corporate_financial_report(timestamp="no-fabrication"))
    domains = {domain["domain"]: domain for domain in report["domain_assessments"]}
    assert domains["competitive_advantage_evidence"]["status"] == "unavailable"
    assert domains["management_execution_evidence"]["status"] == "unavailable"
    assert domains["governance_evidence"]["status"] == "unavailable"
    assert "market share evidence" in report["missing_business_evidence"]
    assert all("No synthetic evidence" in " ".join(domain["limitations"]) for key, domain in domains.items() if key in {"competitive_advantage_evidence", "governance_evidence"})


def test_crypto_is_not_applicable_to_business_intelligence() -> None:
    financial = build_financial_intelligence_report("BTC-USD", {}, {"asset_type": "crypto"})
    report = build_business_intelligence_report("BTC-USD", {"asset_type": "crypto"}, financial)
    assert report["applicable"] is False
    assert report["status"] == "not_applicable"
    assert report["business_intelligence_score"] is None
    assert "alternative_fundamentals" in report["evidence_based_narrative"]


def test_missing_business_evidence_does_not_score_as_zero() -> None:
    financial = build_financial_intelligence_report("AAPL", {"source": "test_provider", "timestamp": "missing"}, {"asset_type": "stock"}, registry_asset("AAPL"))
    report = build_business_intelligence_report("AAPL", {"asset_type": "stock", "timestamp": "missing"}, financial)
    assert report["business_intelligence_score"] is not None
    assert report["business_completeness"] < 100
    unavailable = [domain for domain in report["domain_assessments"] if domain["status"] == "unavailable"]
    assert unavailable
    assert report["limitations"]


def test_business_report_cache_uses_version_metadata() -> None:
    financial = corporate_financial_report(timestamp="business-cache-test")
    quote = {"asset_type": "stock", "source": "test_provider", "timestamp": "business-cache-test"}
    first = build_business_intelligence_report("AAPL", quote, financial)
    second = build_business_intelligence_report("AAPL", quote, financial)
    assert first["cache_metadata"]["cache_hit"] is False
    assert second["cache_metadata"]["cache_hit"] is True
    assert first["versions"] == second["versions"]


def test_api_contract_returns_business_intelligence(monkeypatch) -> None:
    monkeypatch.setattr(main, "get_cached_fundamentals", lambda symbol: financial_payload(symbol=symbol))
    monkeypatch.setattr(main, "get_cached_quote", lambda symbol: {"symbol": symbol, "asset_type": "stock", "source": "test_provider", "timestamp": "2026-07-23T00:00:00+00:00"})
    payload = main.business_intelligence("AAPL")
    assert payload["symbol"] == "AAPL"
    assert payload["business_intelligence_score"] is not None
    assert payload["versions"]["methodology_version"] == "business-intelligence-v1"
    assert main.business_intelligence_methodology_endpoint()["status"] == "ok"
