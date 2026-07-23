from __future__ import annotations

from dataclasses import replace

from app.data_hub.master_asset_registry import MasterAsset
from app import main
from app.services import penny_opportunities as po


def asset(symbol: str = "TTB.BK", country: str = "Thailand", exchange: str = "SET", currency: str = "THB") -> MasterAsset:
    return MasterAsset(
        canonical_symbol=symbol,
        display_symbol=symbol.replace(".BK", ""),
        company_name=f"{symbol} Company",
        thai_name="",
        aliases=[],
        asset_class="equity",
        asset_type="stock",
        exchange=exchange,
        market=exchange,
        country=country,
        currency=currency,
        sector="Financial Services",
        industry="Banking",
        provider_symbols={"yfinance": symbol},
        enabled=True,
        searchable=True,
        coverage_source="test",
        coverage_timestamp=None,
        live_data_capability={"quote": "available", "history": "available"},
    )


def quote(symbol: str = "TTB.BK", price: float = 2.5, volume: float = 3_000_000, **extra):
    payload = {
        "symbol": symbol,
        "name": symbol,
        "asset_type": "stock",
        "currency": "THB" if symbol.endswith(".BK") else "USD",
        "price": price,
        "previous_close": price * 0.98,
        "change": price * 0.02,
        "change_percent": 2.0,
        "volume": volume,
        "market_cap": 4_000_000_000,
        "debt_to_equity": 40,
        "return_on_equity": 0.12,
        "return_on_assets": 0.05,
        "revenue_growth": 0.18,
        "earnings_growth": 0.12,
        "trailing_pe": 12,
        "price_to_book": 1.1,
        "source": "test_provider",
        "timestamp": "2026-07-23T00:00:00+00:00",
    }
    payload.update(extra)
    return payload


def history(days: int = 30, start: float = 2.0, volume: float = 3_000_000):
    return {
        "symbol": "TTB.BK",
        "range": "3mo",
        "interval": "1d",
        "points": [
            {"time": f"2026-07-{index + 1:02d}", "close": start + index * 0.03, "volume": volume}
            for index in range(days)
        ],
        "source": "test_provider",
        "data_timestamp": "2026-07-23T00:00:00+00:00",
    }


def no_news(symbol: str, limit: int):
    return {"symbol": symbol, "items": [], "source": "test_news", "unavailable_reason": "No verified catalyst data available"}


def test_thai_price_classification() -> None:
    classified = po.classify_price(5.0, po.POLICIES["TH"])
    assert classified["status"] == "PASS"
    assert classified["classification"] == "penny_stock"


def test_us_penny_classification() -> None:
    classified = po.classify_price(4.99, po.POLICIES["US"])
    assert classified["classification"] == "penny_stock"


def test_us_low_priced_small_cap_is_not_labeled_penny() -> None:
    classified = po.classify_price(7.5, po.POLICIES["US"])
    assert classified["classification"] == "low_priced_small_cap"


def test_price_alone_cannot_create_high_score() -> None:
    result = po.evaluate_candidate(
        asset(),
        po.POLICIES["TH"],
        lambda symbol: quote(symbol, volume=None, market_cap=None, debt_to_equity=None, return_on_equity=None, return_on_assets=None, revenue_growth=None, earnings_growth=None, trailing_pe=None),
        lambda symbol, range, interval: {"points": [], "source": "test_provider"},
        no_news,
    )
    assert result["penny_opportunity_score"] < 60
    assert result["eligible_for_top5"] is False


def test_illiquid_stock_is_hard_disqualified() -> None:
    result = po.evaluate_candidate(asset(), po.POLICIES["TH"], lambda symbol: quote(symbol, volume=10), lambda *_: history(volume=10), no_news)
    assert result["hard_disqualified"] is True
    assert any(risk["code"] == "insufficient_liquidity" for risk in result["risks"])


def test_missing_data_remains_unknown() -> None:
    result = po.evaluate_candidate(asset(), po.POLICIES["TH"], lambda symbol: quote(symbol, volume=None), lambda *_: {"points": [{"time": "t1", "close": 2.5}], "source": "test"}, no_news)
    assert result["factor_availability"]["liquidity"] == "UNKNOWN"


def test_missing_fundamentals_reduce_confidence() -> None:
    full = po.evaluate_candidate(asset(), po.POLICIES["TH"], lambda symbol: quote(symbol), lambda *_: history(), no_news)
    missing = po.evaluate_candidate(asset(), po.POLICIES["TH"], lambda symbol: quote(symbol, debt_to_equity=None, return_on_equity=None, return_on_assets=None, revenue_growth=None, earnings_growth=None, trailing_pe=None), lambda *_: history(), no_news)
    assert missing["data_confidence"] < full["data_confidence"]


def test_missing_catalyst_does_not_create_fake_catalyst() -> None:
    result = po.evaluate_candidate(asset(), po.POLICIES["TH"], lambda symbol: quote(symbol), lambda *_: history(), no_news)
    assert result["catalysts"] == []
    assert "verified_catalyst_data" in result["missing_data"]


def test_confirmed_critical_risk_disqualifies_candidate() -> None:
    result = po.evaluate_candidate(asset(), po.POLICIES["TH"], lambda symbol: {**quote(symbol), "price": None, "error": "No latest price"}, lambda *_: history(), no_news)
    assert result["hard_disqualified"] is True
    assert result["eligible_for_top5"] is False


def test_related_liquidity_risks_do_not_double_count_unbounded() -> None:
    result = po.evaluate_candidate(asset(), po.POLICIES["TH"], lambda symbol: quote(symbol, volume=0), lambda *_: history(volume=0), no_news)
    assert [risk["code"] for risk in result["risks"]].count("insufficient_liquidity") == 1


def test_risk_penalty_reduces_final_score() -> None:
    good = po.evaluate_candidate(asset(), po.POLICIES["TH"], lambda symbol: quote(symbol), lambda *_: history(), no_news)
    risky = po.evaluate_candidate(asset(), po.POLICIES["TH"], lambda symbol: quote(symbol), lambda *_: history(start=3.0, volume=3_000_000), no_news)
    assert risky["risk_penalty"] >= good["risk_penalty"]
    assert risky["penny_opportunity_score"] <= 100


def test_final_score_remains_within_zero_to_one_hundred() -> None:
    result = po.evaluate_candidate(asset(), po.POLICIES["TH"], lambda symbol: quote(symbol, change_percent=30), lambda *_: history(), no_news)
    assert 0 <= result["penny_opportunity_score"] <= 100


def test_confidence_is_separate_from_score() -> None:
    result = po.evaluate_candidate(asset(), po.POLICIES["TH"], lambda symbol: quote(symbol), lambda *_: history(), no_news)
    assert result["data_confidence"] != result["penny_opportunity_score"]


def test_low_completeness_blocks_top5_eligibility() -> None:
    result = po.evaluate_candidate(
        asset(),
        po.POLICIES["TH"],
        lambda symbol: quote(symbol, market_cap=None, volume=None, debt_to_equity=None, return_on_equity=None, return_on_assets=None, revenue_growth=None, earnings_growth=None),
        lambda *_: {"points": [], "source": "test"},
        no_news,
    )
    assert result["data_completeness"] < po.POLICIES["TH"].minimum_data_completeness
    assert result["eligible_for_top5"] is False


def test_fewer_than_five_qualified_returns_fewer_results(monkeypatch) -> None:
    monkeypatch.setattr(po, "list_registry_assets", lambda enabled_only=True, searchable_only=True: [asset("TTB.BK")])
    payload = po.build_penny_opportunities(lambda symbol: quote(symbol), lambda *_: history(), no_news, market="TH", limit=5)
    assert payload["qualification"]["ranked_count"] <= 1
    assert len(payload["items"]) <= 1


def test_ranking_is_deterministic(monkeypatch) -> None:
    assets = [asset("TTB.BK"), asset("TRUE.BK")]
    monkeypatch.setattr(po, "list_registry_assets", lambda enabled_only=True, searchable_only=True: assets)
    first = po.build_penny_opportunities(lambda symbol: quote(symbol), lambda *_: history(), no_news, market="TH")
    second = po.build_penny_opportunities(lambda symbol: quote(symbol), lambda *_: history(), no_news, market="TH")
    assert [item["symbol"] for item in first["items"]] == [item["symbol"] for item in second["items"]]


def test_tie_breaking_is_deterministic(monkeypatch) -> None:
    assets = [asset("TRUE.BK"), asset("TTB.BK")]
    monkeypatch.setattr(po, "list_registry_assets", lambda enabled_only=True, searchable_only=True: assets)
    payload = po.build_penny_opportunities(lambda symbol: quote(symbol), lambda *_: history(), no_news, market="TH")
    assert [item["symbol"] for item in payload["items"]] == sorted(item["symbol"] for item in payload["items"])


def test_one_provider_failure_does_not_crash_all_results(monkeypatch) -> None:
    assets = [asset("TRUE.BK"), asset("TTB.BK")]
    monkeypatch.setattr(po, "list_registry_assets", lambda enabled_only=True, searchable_only=True: assets)

    def quote_fn(symbol: str):
        if symbol == "TRUE.BK":
            raise RuntimeError("provider boom")
        return quote(symbol)

    payload = po.build_penny_opportunities(quote_fn, lambda *_: history(), no_news, market="TH")
    assert payload["qualification"]["excluded_count"] >= 1
    assert all(item["symbol"] != "TRUE.BK" for item in payload["items"])


def test_unsupported_market_is_handled_honestly() -> None:
    payload = po.build_penny_opportunities(lambda symbol: quote(symbol), lambda *_: history(), no_news, market="JP")
    assert payload["status"] == "unavailable"
    assert payload["markets"] == []


def test_stale_or_short_history_is_identified() -> None:
    result = po.evaluate_candidate(asset(), po.POLICIES["TH"], lambda symbol: quote(symbol), lambda *_: history(days=3), no_news)
    assert any(risk["code"] == "insufficient_trading_history" for risk in result["risks"])


def test_api_response_schema_is_valid(monkeypatch) -> None:
    monkeypatch.setattr(po, "list_registry_assets", lambda enabled_only=True, searchable_only=True: [asset("TTB.BK")])
    payload = po.build_penny_opportunities(lambda symbol: quote(symbol), lambda *_: history(), no_news)
    assert payload["category"] == "penny_opportunity"
    assert payload["methodology_version"] == po.METHODOLOGY_VERSION
    assert "warning" in payload
    assert "qualification" in payload
    assert "items" in payload


def test_limit_parameter_is_bounded(monkeypatch) -> None:
    assets = [asset("TTB.BK"), asset("TRUE.BK")]
    monkeypatch.setattr(po, "list_registry_assets", lambda enabled_only=True, searchable_only=True: assets)
    payload = po.build_penny_opportunities(lambda symbol: quote(symbol), lambda *_: history(), no_news, limit=100)
    assert len(payload["items"]) <= 20


def test_no_candidate_with_hard_disqualification_appears_in_top5(monkeypatch) -> None:
    monkeypatch.setattr(po, "list_registry_assets", lambda enabled_only=True, searchable_only=True: [asset("TTB.BK")])
    payload = po.build_penny_opportunities(lambda symbol: quote(symbol, price=None, error="missing price"), lambda *_: history(), no_news, market="TH")
    assert payload["items"] == []


def test_memory_sensitive_shortlist_does_not_fetch_history_for_invalid_price(monkeypatch) -> None:
    monkeypatch.setattr(po, "list_registry_assets", lambda enabled_only=True, searchable_only=True: [asset("TTB.BK")])
    calls = {"history": 0}

    def history_fn(*_):
        calls["history"] += 1
        return history()

    po.build_penny_opportunities(lambda symbol: quote(symbol, price=20), history_fn, no_news, market="TH")
    assert calls["history"] == 0


def test_no_mock_values_appear_in_result(monkeypatch) -> None:
    monkeypatch.setattr(po, "list_registry_assets", lambda enabled_only=True, searchable_only=True: [asset("TTB.BK")])
    payload = po.build_penny_opportunities(lambda symbol: quote(symbol), lambda *_: history(), no_news, market="TH")
    assert "mock" not in str(payload).lower()


def test_api_endpoint_uses_penny_scanner(monkeypatch) -> None:
    captured = {}

    def fake_scanner(quote_fn, history_fn, news_fn=None, market=None, limit=5):
        captured["market"] = market
        captured["limit"] = limit
        captured["quote_callable"] = callable(quote_fn)
        captured["history_callable"] = callable(history_fn)
        captured["news_callable"] = callable(news_fn)
        return {
            "status": "ok",
            "category": "penny_opportunity",
            "methodology_version": po.METHODOLOGY_VERSION,
            "configuration_version": po.CONFIGURATION_VERSION,
            "generated_at": "2026-01-01T00:00:00Z",
            "markets": ["TH"],
            "warning": {"th": po.PENNY_WARNING_TH, "en": po.PENNY_WARNING_EN},
            "qualification": {"universe_size": 1, "eligible_count": 1, "ranked_count": 0, "excluded_count": 0, "unknown_count": 0},
            "items": [],
            "limitations": [],
            "provider_status": [],
            "disclaimer": "This is not financial advice.",
        }

    monkeypatch.setattr(main, "build_penny_opportunities", fake_scanner)
    payload = main.penny_opportunities(market="TH", limit=5, language="en")
    assert payload["category"] == "penny_opportunity"
    assert captured == {
        "market": "TH",
        "limit": 5,
        "quote_callable": True,
        "history_callable": True,
        "news_callable": True,
    }
