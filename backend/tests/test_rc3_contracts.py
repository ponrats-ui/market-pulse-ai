from app import main
from app.services.asset_universe import search_assets, sector_browser
from app.services.technical import build_technical_analysis


def test_clean_thai_asset_search_terms_work() -> None:
    assert "GC=F" in {asset["symbol"] for asset in search_assets("ทอง")["assets"]}
    assert "CL=F" in {asset["symbol"] for asset in search_assets("น้ำมัน")["assets"]}
    assert "KBANK.BK" in {asset["symbol"] for asset in search_assets("กสิกร")["assets"]}


def test_sector_browser_contract_contains_assets() -> None:
    payload = sector_browser()
    sectors = {sector["name"]: sector for sector in payload["sectors"]}
    assert "Semiconductor" in sectors
    assert {"NVDA", "AMD", "TSM", "SOXX"}.issubset({asset["symbol"] for asset in sectors["Semiconductor"]["assets"]})


def test_technical_analysis_returns_real_calculated_fields() -> None:
    points = [
        {"time": f"2026-01-{index:02d}T00:00:00Z", "open": 100 + index, "high": 102 + index, "low": 99 + index, "close": 100 + index, "volume": 1000 + index}
        for index in range(1, 61)
    ]
    payload = build_technical_analysis("NVDA", {"points": points, "source": "test"})
    assert payload["status"] == "ok"
    assert payload["indicators"]["EMA20"] is not None
    assert payload["indicators"]["RSI14"] is not None
    assert payload["indicators"]["MACD"]["line"] is not None
    assert payload["series"][-1]["bollinger_upper"] is not None


def test_rc3_routes_return_contracts(monkeypatch) -> None:
    def history(symbol, selected_range, interval):
        return {
            "symbol": symbol,
            "points": [
                {"time": f"2026-01-{index:02d}T00:00:00Z", "open": 100 + index, "high": 102 + index, "low": 99 + index, "close": 100 + index, "volume": 1000 + index}
                for index in range(1, 61)
            ],
            "source": "test",
        }

    monkeypatch.setattr(main, "get_cached_history", history)
    assert main.sectors()["sectors"]
    assert main.sector_assets("Semiconductor")["assets"]
    assert main.technical("NVDA")["status"] == "ok"
