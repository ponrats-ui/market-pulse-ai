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


def test_search_assets_finds_utf8_thai_name() -> None:
    payload = search_assets("กสิกร")
    symbols = {asset["symbol"] for asset in payload["assets"]}
    assert "KBANK.BK" in symbols


def test_search_assets_finds_bond_etf_reit_and_thai_gold_keyword() -> None:
    assert "TLT" in {asset["symbol"] for asset in search_assets("treasury bond")["assets"]}
    assert "VNQ" in {asset["symbol"] for asset in search_assets("real estate")["assets"]}
    assert "GC=F" in {asset["symbol"] for asset in search_assets("ทอง")["assets"]}
