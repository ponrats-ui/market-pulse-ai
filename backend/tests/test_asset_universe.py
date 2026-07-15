from app.services.asset_universe import search_assets


def test_search_assets_finds_nvda() -> None:
    payload = search_assets("nvda")
    symbols = {asset["symbol"] for asset in payload["assets"]}
    assert "NVDA" in symbols


def test_search_assets_finds_thai_stock_keyword() -> None:
    payload = search_assets("bank")
    symbols = {asset["symbol"] for asset in payload["assets"]}
    assert "KBANK.BK" in symbols


def test_search_assets_finds_clean_thai_name() -> None:
    payload = search_assets("กสิกร")
    symbols = {asset["symbol"] for asset in payload["assets"]}
    assert "KBANK.BK" in symbols


def test_search_assets_finds_etf_by_name() -> None:
    payload = search_assets("total stock")
    symbols = {asset["symbol"] for asset in payload["assets"]}
    assert "VTI" in symbols


def test_search_assets_finds_bond_etf_reit_and_thai_gold_keyword() -> None:
    assert "TLT" in {asset["symbol"] for asset in search_assets("treasury bond")["assets"]}
    assert "VNQ" in {asset["symbol"] for asset in search_assets("real estate")["assets"]}
    assert "GC=F" in {asset["symbol"] for asset in search_assets("ทอง")["assets"]}


def test_search_assets_maps_common_set_ticker_to_bk_symbol() -> None:
    assert "TTB.BK" in {asset["symbol"] for asset in search_assets("TTB")["assets"]}
    assert "AOT.BK" in {asset["symbol"] for asset in search_assets("AOT")["assets"]}


def test_search_assets_finds_verified_us_listed_symbols() -> None:
    payload = search_assets("RKLB")
    assert payload["assets"][0]["symbol"] == "RKLB"
    assert payload["assets"][0]["coverage_status"] == "partial"
    assert search_assets("SPGI")["assets"][0]["symbol"] == "SPGI"


def test_search_assets_supports_company_name_and_ranking() -> None:
    assert search_assets("Apple")["assets"][0]["symbol"] == "AAPL"
    assert search_assets("Rocket Lab")["assets"][0]["symbol"] == "RKLB"
    prefix_payload = search_assets("SP")
    prefix_symbols = [asset["symbol"] for asset in prefix_payload["assets"][:5]]
    assert "SPGI" in prefix_symbols
    assert "SPCX" in prefix_symbols


def test_search_assets_supports_thai_aliases_and_gold() -> None:
    assert search_assets("ทหารไทยธนชาต")["assets"][0]["symbol"] == "TTB.BK"
    assert search_assets("KBANK")["assets"][0]["symbol"] == "KBANK.BK"
    gold_symbols = {asset["symbol"] for asset in search_assets("ทอง")["assets"]}
    assert {"GLD", "GC=F"} & gold_symbols


def test_search_assets_does_not_return_unsupported_gibberish() -> None:
    payload = search_assets("ZZZNOTAREALMARKETPULSE")
    assert payload["assets"] == []
