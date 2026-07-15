from app.data_hub.capabilities import capabilities_for_symbol


def test_capabilities_for_equity_and_crypto() -> None:
    equity = capabilities_for_symbol("TTB")
    assert equity["resolved"] is True
    assert equity["symbol"] == "TTB.BK"
    assert equity["capabilities"]["fundamentals"] == "partial"

    crypto = capabilities_for_symbol("BTC-USD")
    assert crypto["capabilities"]["fundamentals"] == "not_applicable"


def test_capabilities_for_unsupported_asset() -> None:
    payload = capabilities_for_symbol("ZZZNOTAREALMARKETPULSE")
    assert payload["resolved"] is False
    assert payload["reason"] == "unsupported_under_current_universe"
