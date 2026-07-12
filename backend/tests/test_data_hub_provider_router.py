from app.data_hub import provider_router


def test_provider_router_primary_success(monkeypatch) -> None:
    class Provider:
        name = "yfinance"

        def get_quote(self, symbol):
            return {"symbol": symbol, "price": 10, "source": self.name}

    monkeypatch.setattr(provider_router, "get_provider", lambda name: Provider())
    payload = provider_router.get_quote("TTB")
    assert payload["symbol"] == "TTB.BK"
    assert payload["provider_symbol"] == "TTB.BK"
    assert payload["data_hub"]["provider"] == "yfinance"


def test_provider_router_fallback_to_unavailable(monkeypatch) -> None:
    class Provider:
        name = "yfinance"

        def get_quote(self, symbol):
            return {"symbol": symbol, "error": "provider failed"}

    monkeypatch.setattr(provider_router, "get_provider", lambda name: Provider())
    payload = provider_router.get_quote("TTB")
    assert payload["source"] == "Unavailable"
    assert payload["data_hub"]["provider_failures"]


def test_provider_router_rejects_unsupported_without_fabricating() -> None:
    payload = provider_router.get_quote("RKLB")
    assert payload["source"] == "Unavailable"
    assert payload["error"] == "unsupported_under_current_universe"
    assert "price" not in payload
