from __future__ import annotations

from app.data_hub.provider_symbol_mapper import map_thai_yfinance_symbol
from app.providers import yfinance_provider
from app.providers.yfinance_provider import YFinanceProvider


def test_thai_common_share_symbols_map_to_yfinance_provider_symbols() -> None:
    for raw, canonical, provider in [
        ("AOT", "AOT", "AOT.BK"),
        ("AOT.BK", "AOT", "AOT.BK"),
        ("ptt", "PTT", "PTT.BK"),
        ("PTT.BK", "PTT", "PTT.BK"),
        ("88TH", "88TH", "88TH.BK"),
    ]:
        mapping = map_thai_yfinance_symbol(raw)
        assert mapping.supported is True
        assert mapping.board == "common"
        assert mapping.canonical_symbol == canonical
        assert mapping.provider_symbol == provider


def test_thai_foreign_board_symbols_are_excluded_before_provider_calls() -> None:
    for raw in ["AOT-F", "AOT-F.BK", "ACAP-F.BK"]:
        mapping = map_thai_yfinance_symbol(raw)
        assert mapping.supported is False
        assert mapping.board == "foreign_board"
        assert mapping.provider_symbol is None
        assert mapping.exclusion_reason == "foreign_board_excluded"


def test_malformed_or_duplicate_thai_symbols_are_rejected() -> None:
    assert map_thai_yfinance_symbol("AOT.BK.BK").exclusion_reason == "duplicate_exchange_suffix"
    assert map_thai_yfinance_symbol("AOT-P.BK").exclusion_reason == "special_board_excluded"
    assert map_thai_yfinance_symbol("AOT USD").exclusion_reason == "malformed_symbol"


def test_yfinance_scan_quotes_filters_foreign_board_symbols_before_download(monkeypatch) -> None:
    calls = []

    def fake_download(**kwargs):
        tickers = kwargs.get("tickers", "")
        calls.append(tickers)
        assert "-F" not in tickers
        return None

    monkeypatch.setattr(yfinance_provider.yf, "download", fake_download)
    YFinanceProvider().get_scan_quotes(["AOT-F.BK", "PTT.BK", "ACAP-F.BK"], chunk_size=10)

    assert calls == ["PTT.BK"]
