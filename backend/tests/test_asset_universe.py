from app.services.asset_universe import search_assets


def test_search_assets_finds_nvda() -> None:
    payload = search_assets("nvda")
    symbols = {asset["symbol"] for asset in payload["assets"]}
    assert "NVDA" in symbols


def test_search_assets_finds_thai_stock_keyword() -> None:
    payload = search_assets("bank")
    symbols = {asset["symbol"] for asset in payload["assets"]}
    assert "KBANK.BK" in symbols


def test_search_assets_finds_thai_name() -> None:
    payload = search_assets("กสิกร")
    symbols = {asset["symbol"] for asset in payload["assets"]}
    assert "KBANK.BK" in symbols


def test_search_assets_finds_etf_by_name() -> None:
    payload = search_assets("total stock")
    symbols = {asset["symbol"] for asset in payload["assets"]}
    assert "VTI" in symbols
