from app.data_hub.master_asset_registry import master_asset_registry_metadata, validate_master_asset_registry
from app.services.asset_universe import search_assets, sector_browser


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


def test_search_assets_finds_required_thai_registry_symbols() -> None:
    required = [
        "KKP",
        "BBL",
        "KTB",
        "SCB",
        "KBANK",
        "BAY",
        "TISCO",
        "TTB",
        "AOT",
        "CPALL",
        "CPF",
        "ADVANC",
        "TRUE",
        "PTT",
        "PTTEP",
        "SCC",
        "SCGP",
        "BDMS",
        "BH",
        "CRC",
        "BJC",
        "MINT",
        "CENTEL",
        "GPSC",
        "GULF",
        "EA",
        "BGRIM",
        "OR",
        "HMPRO",
        "GLOBAL",
        "COM7",
        "TU",
        "OSP",
        "TOP",
        "BCP",
        "DELTA",
        "HANA",
        "KCE",
        "CHG",
        "BCH",
        "AAV",
        "BA",
        "BTS",
        "IVL",
        "PTTGC",
        "CBG",
    ]
    for ticker in required:
        assert search_assets(ticker)["assets"][0]["symbol"] == f"{ticker}.BK"


def test_search_assets_finds_thai_bank_by_thai_name() -> None:
    assert search_assets("ธนาคารกรุงเทพ")["assets"][0]["symbol"] == "BBL.BK"
    assert search_assets("กรุงเทพ")["assets"][0]["symbol"] == "BBL.BK"
    assert search_assets("เกียรตินาคินภัทร")["assets"][0]["symbol"] == "KKP.BK"
    assert search_assets("กรุงไทย")["assets"][0]["symbol"] == "KTB.BK"
    assert search_assets("ไทยพาณิชย์")["assets"][0]["symbol"] == "SCB.BK"
    assert search_assets("กสิกรไทย")["assets"][0]["symbol"] == "KBANK.BK"
    assert search_assets("ทหารไทยธนชาต")["assets"][0]["symbol"] == "TTB.BK"
    assert search_assets("ปตท")["assets"][0]["symbol"] == "PTT.BK"
    assert search_assets("ปตท.สผ.")["assets"][0]["symbol"] == "PTTEP.BK"
    assert search_assets("ซีพีออลล์")["assets"][0]["symbol"] == "CPALL.BK"
    assert search_assets("แอดวานซ์")["assets"][0]["symbol"] == "ADVANC.BK"
    assert search_assets("ท่าอากาศยานไทย")["assets"][0]["symbol"] == "AOT.BK"
    assert search_assets("กรุงเทพดุสิตเวชการ")["assets"][0]["symbol"] == "BDMS.BK"
    assert search_assets("โรงพยาบาลบำรุงราษฎร์")["assets"][0]["symbol"] == "BH.BK"
    assert search_assets("ปูนซิเมนต์ไทย")["assets"][0]["symbol"] == "SCC.BK"


def test_thai_registry_search_result_exposes_master_fields() -> None:
    asset = search_assets("KKP")["assets"][0]
    assert asset["symbol"] == "KKP.BK"
    assert asset["company_name_en"]
    assert asset["company_name_th"]
    assert asset["short_name_en"]
    assert asset["short_name_th"]
    assert asset["security_type"] == "stock"
    assert asset["quote_capability"] in {"partial", "available", True}
    assert "fundamentals_capability" in asset
    assert "news_capability" in asset


def test_thai_registry_validation_and_counts_are_available() -> None:
    metadata = master_asset_registry_metadata()
    validation = validate_master_asset_registry()
    assert validation["valid"] is True
    assert validation["duplicates"] == []
    assert validation["duplicate_provider_symbols"] == []
    assert validation["invalid_thai_mapping"] == []
    assert metadata["sources"][2]["record_count"] == 1827


def test_sector_browser_uses_full_thai_registry_counts() -> None:
    payload = sector_browser()
    thai_count = sum(1 for sector in payload["sectors"] for asset in sector["assets"] if asset.get("country") == "Thailand")
    assert payload["exchange_master"]["sources"][2]["record_count"] == 1827
    assert thai_count >= 1827


def test_search_assets_does_not_return_unsupported_gibberish() -> None:
    payload = search_assets("ZZZNOTAREALMARKETPULSE")
    assert payload["assets"] == []
