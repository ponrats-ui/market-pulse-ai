from app.main import watchlist


def test_watchlist_has_expected_categories() -> None:
    payload = watchlist()
    categories = payload["categories"]
    ids = {category["id"] for category in categories}
    assert "crypto" in ids
    assert "thai_stocks" in ids
    assert "global_stocks" in ids
    assert "fx_macro" in ids


def test_watchlist_contains_btc() -> None:
    payload = watchlist()
    symbols = {asset["symbol"] for category in payload["categories"] for asset in category["assets"]}
    assert "BTC-USD" in symbols
