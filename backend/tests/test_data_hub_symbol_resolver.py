from app.data_hub.symbol_resolver import resolve_symbol


def test_resolver_maps_common_set_aliases_to_canonical_symbols() -> None:
    assert resolve_symbol("TTB").canonical_symbol == "TTB.BK"
    assert resolve_symbol("ttb.bk").canonical_symbol == "TTB.BK"
    assert resolve_symbol("KBANK").canonical_symbol == "KBANK.BK"
    assert resolve_symbol("AOT").canonical_symbol == "AOT.BK"


def test_resolver_maps_thai_aliases() -> None:
    assert resolve_symbol("กสิกร").canonical_symbol == "KBANK.BK"
    assert resolve_symbol("ทหารไทยธนชาต").canonical_symbol == "TTB.BK"


def test_resolver_rejects_unsupported_symbol() -> None:
    result = resolve_symbol("RKLB")
    assert result.ok is False
    assert result.reason == "unsupported_under_current_universe"
