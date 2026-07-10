from app import main
from app.services.analysis import build_risk
from app.services.asset_universe import search_assets, sector_browser
from app.services.portfolio import evaluate_portfolio
from app.services.subscription import subscription_features


def test_exchange_master_search_supports_clean_thai_and_metadata() -> None:
    payload = search_assets("ทอง")
    assert payload["source"] == "exchange_master_seed"
    assert payload["exchange_master"]["count"] > 20
    assert "GC=F" in {asset["symbol"] for asset in payload["assets"]}
    first = payload["assets"][0]
    assert "exchange" in first
    assert "country" in first
    assert "currency" in first


def test_sector_browser_uses_exchange_master_groups() -> None:
    payload = sector_browser()
    sectors = {item["name"]: item for item in payload["sectors"]}
    assert "Semiconductor" in sectors
    assert sectors["Semiconductor"]["count"] >= 3


def test_subscription_features_are_architecture_only() -> None:
    payload = subscription_features()
    assert payload["premium_price_monthly"] == 49
    assert payload["payment_enabled"] is False
    assert "price_alerts" in payload["tiers"]["premium"]["features"]


def test_risk_categories_include_trend() -> None:
    payload = build_risk("BTC-USD", {"symbol": "BTC-USD", "asset_type": "crypto", "change_percent": 5, "source": "test"}, {"points": [{"close": 100}, {"close": 110}, {"close": 90}]})
    assert payload["categories"]
    assert {"category", "probability", "severity", "trend", "evidence", "mitigation"}.issubset(payload["categories"][0])


def test_portfolio_contract_exposes_rc4_analytics_fields() -> None:
    def quote(symbol):
        return {"symbol": symbol, "price": 120, "change_percent": 1.5, "currency": "USD", "source": "test", "timestamp": "2026-01-01T00:00:00Z", "sector": "Technology", "asset_type": "stock"}

    payload = evaluate_portfolio([{"cashBalance": 50}, {"symbol": "AAPL", "quantity": 2, "averageCost": 100}], quote)
    assert payload["sector_allocation"][0]["sector"] == "Technology"
    assert payload["performance_points"] == []
    assert payload["sharpe_ratio"] is None
    assert payload["analytics_status"] == "partial"


def test_rc4_routes_expose_exchange_master_and_subscription() -> None:
    assert main.exchange_master()["source"] == "exchange_master_seed"
    assert main.subscription()["status"] == "architecture_only"
