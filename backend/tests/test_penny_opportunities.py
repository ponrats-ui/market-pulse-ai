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
    assert classified["classification"] == "thai_emerging_opportunity_universe"
    assert classified["tier"] == "classic_penny"


def test_thai_default_universe_includes_five_to_ten_thb() -> None:
    classified = po.classify_price(9.8, po.POLICIES["TH"])
    assert classified["status"] == "PASS"
    assert classified["tier"] == "thai_emerging"
    assert classified["maximum_share_price"] == 10.0


def test_thai_custom_threshold_filters_above_active_limit() -> None:
    policy = po._configured_policies(7.5)["TH"]
    classified = po.classify_price(9.8, policy)
    assert classified["status"] == "FAIL"
    assert classified["maximum_share_price"] == 7.5


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


def test_business_intelligence_is_consumed_as_score_factor() -> None:
    result = po.evaluate_candidate(replace(asset("QUALITY.BK"), sector="Technology", industry="Software"), po.POLICIES["TH"], lambda symbol: quote(symbol, price=8.4), lambda *_: history(), no_news)
    assert "business" in result["scores"]
    assert result["scores"]["business"] is not None
    assert result["business_intelligence"]["business_intelligence_score"] == result["scores"]["business"]
    assert any(row["factor_id"] == "business" for row in result["score_breakdown"]["factor_contributions"])


def test_value_trap_detection_adds_risk_penalty() -> None:
    result = po.evaluate_candidate(
        asset("WEAK.BK"),
        po.POLICIES["TH"],
        lambda symbol: quote(symbol, price=0.8, debt_to_equity=400, return_on_equity=-0.3, return_on_assets=-0.2, revenue_growth=-0.2, earnings_growth=-0.4),
        lambda *_: history(),
        no_news,
    )
    assert result["opportunity_setup"]["value_trap_detected"] is True
    assert any(risk["code"] == "value_trap_evidence" for risk in result["risks"])


def test_emerging_quality_detection_uses_evidence_not_price() -> None:
    result = po.evaluate_candidate(
        replace(asset("EMERGE.BK"), sector="Technology", industry="Software"),
        po.POLICIES["TH"],
        lambda symbol: quote(
            symbol,
            price=9.8,
            totalRevenue=1000.0,
            grossProfit=450.0,
            netIncome=180.0,
            freeCashFlow=200.0,
            totalDebt=120.0,
            totalEquity=500.0,
            debt_to_equity=0.24,
        ),
        lambda *_: history(),
        no_news,
    )
    assert result["price_tier"] == "thai_emerging"
    assert result["opportunity_setup"]["emerging_quality_detected"] is True
    assert "Price defines eligibility only" in result["opportunity_setup"]["interpretation"]


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
    assert result["confidence_explanation"]["score"] == result["data_confidence"]
    assert result["score_breakdown"]["raw_positive_score"] != result["data_confidence"]


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
    assert payload["universe"]["markets"]["TH"]["maximum_share_price"] == 10.0
    assert payload["qualification"]["active_thresholds"]["TH"] == 10.0


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

    def fake_snapshot(market=None, limit=5, thai_max_price=None):
        captured["market"] = market
        captured["limit"] = limit
        captured["thai_max_price"] = thai_max_price
        return {
            "status": "ok",
            "category": "penny_opportunity",
            "methodology_version": po.METHODOLOGY_VERSION,
            "score_version": po.SCORE_VERSION,
            "configuration_version": po.CONFIGURATION_VERSION,
            "scan": {"frequency_minutes": 60, "is_stale": False, "scan_duration_ms": 10},
            "generated_at": "2026-01-01T00:00:00Z",
            "markets": ["TH"],
            "warning": {"th": po.PENNY_WARNING_TH, "en": po.PENNY_WARNING_EN},
            "qualification": {"universe_size": 1, "classified_count": 1, "eligible_count": 1, "qualified_count": 1, "ranked_count": 0, "excluded_count": 0, "failed_candidate_count": 0, "unknown_count": 0},
            "items": [],
            "limitations": [],
            "provider_status": [],
            "disclaimer": "This is not financial advice.",
        }

    monkeypatch.setattr(main, "get_penny_opportunities_snapshot", fake_snapshot)
    payload = main.penny_opportunities(market="TH", limit=5, language="en")
    assert payload["category"] == "penny_opportunity"
    assert payload["scan"]["frequency_minutes"] == 60
    assert captured == {"market": "TH", "limit": 5, "thai_max_price": None}


def test_api_endpoint_with_custom_threshold_uses_snapshot(monkeypatch) -> None:
    captured = {}

    def fake_snapshot(market=None, limit=5, thai_max_price=None):
        captured["market"] = market
        captured["limit"] = limit
        captured["thai_max_price"] = thai_max_price
        return {"status": "ok", "items": [], "category": "penny_opportunity"}

    monkeypatch.setattr(main, "get_penny_opportunities_snapshot", fake_snapshot)
    payload = main.penny_opportunities(market="TH", limit=5, max_price=7.5)
    assert payload["status"] == "ok"
    assert captured == {"market": "TH", "limit": 5, "thai_max_price": 7.5}


def candidate_payload(symbol: str, score: int, confidence: int = 50, completeness: int = 50, liquidity: int = 50, risk_penalty: int = 0, hard: bool = False):
    return {
        "rank": None,
        "symbol": symbol,
        "provider_symbol": symbol,
        "name": symbol,
        "market": "TH" if symbol.endswith(".BK") else "US",
        "exchange": "SET" if symbol.endswith(".BK") else "NASDAQ",
        "currency": "THB" if symbol.endswith(".BK") else "USD",
        "classification": "penny_stock",
        "classification_status": "PASS",
        "price": 2,
        "price_timestamp": "2026-07-23T00:00:00+00:00",
        "penny_opportunity_score": score,
        "data_confidence": confidence,
        "data_completeness": completeness,
        "scores": {"financial": 50, "growth": 50, "technical": 50, "liquidity": liquidity, "catalyst": None, "market_context": 50},
        "risk_penalty": risk_penalty,
        "risk_level": "medium",
        "severe_risk_count": 0,
        "strengths": [],
        "risks": [],
        "missing_data": [],
        "catalysts": [],
        "explanation": {"th": symbol, "en": symbol},
        "provider_attribution": ["test_provider"],
        "provider_status": [],
        "hard_disqualified": hard,
        "eligible_for_top5": not hard,
    }


def test_top5_ordered_by_final_score_and_excludes_sixth(monkeypatch) -> None:
    symbols = ["AAA.BK", "BBB.BK", "CCC.BK", "DDD.BK", "EEE.BK", "FFF.BK"]
    scores = dict(zip(symbols, [91, 88, 87, 86, 85, 84]))
    monkeypatch.setattr(po, "list_registry_assets", lambda enabled_only=True, searchable_only=True: [asset(symbol) for symbol in symbols])
    monkeypatch.setattr(po, "evaluate_candidate", lambda asset_obj, *_: candidate_payload(asset_obj.canonical_symbol, scores[asset_obj.canonical_symbol]))
    payload = po.build_penny_opportunities(lambda symbol: quote(symbol), lambda *_: history(), no_news, market="TH", limit=5)
    assert [item["symbol"] for item in payload["items"]] == ["AAA.BK", "BBB.BK", "CCC.BK", "DDD.BK", "EEE.BK"]
    assert payload["items"][-1]["penny_opportunity_score"] == 85


def test_confidence_only_breaks_ties(monkeypatch) -> None:
    rows = [asset("HIGH.BK"), asset("LOW.BK")]
    monkeypatch.setattr(po, "list_registry_assets", lambda enabled_only=True, searchable_only=True: rows)
    payloads = {
        "HIGH.BK": candidate_payload("HIGH.BK", 80, confidence=10),
        "LOW.BK": candidate_payload("LOW.BK", 79, confidence=100),
    }
    monkeypatch.setattr(po, "evaluate_candidate", lambda asset_obj, *_: payloads[asset_obj.canonical_symbol])
    payload = po.build_penny_opportunities(lambda symbol: quote(symbol), lambda *_: history(), no_news, market="TH")
    assert [item["symbol"] for item in payload["items"][:2]] == ["HIGH.BK", "LOW.BK"]


def test_tie_breakers_are_deterministic(monkeypatch) -> None:
    symbols = ["BBB.BK", "AAA.BK", "CCC.BK"]
    monkeypatch.setattr(po, "list_registry_assets", lambda enabled_only=True, searchable_only=True: [asset(symbol) for symbol in symbols])
    payloads = {
        "BBB.BK": candidate_payload("BBB.BK", 80, confidence=80, completeness=70, liquidity=90, risk_penalty=5),
        "AAA.BK": candidate_payload("AAA.BK", 80, confidence=80, completeness=70, liquidity=90, risk_penalty=5),
        "CCC.BK": candidate_payload("CCC.BK", 80, confidence=80, completeness=75, liquidity=50, risk_penalty=5),
    }
    monkeypatch.setattr(po, "evaluate_candidate", lambda asset_obj, *_: payloads[asset_obj.canonical_symbol])
    payload = po.build_penny_opportunities(lambda symbol: quote(symbol), lambda *_: history(), no_news, market="TH")
    assert [item["symbol"] for item in payload["items"]] == ["CCC.BK", "AAA.BK", "BBB.BK"]


def test_complete_supported_universe_is_considered(monkeypatch) -> None:
    rows = [asset("AAA.BK"), asset("ZZZ.BK"), asset("AAPL", country="United States", exchange="NASDAQ", currency="USD")]
    seen = []
    monkeypatch.setattr(po, "list_registry_assets", lambda enabled_only=True, searchable_only=True: rows)

    def evaluator(asset_obj, *_):
        seen.append(asset_obj.canonical_symbol)
        return candidate_payload(asset_obj.canonical_symbol, 60)

    monkeypatch.setattr(po, "evaluate_candidate", evaluator)
    po.build_penny_opportunities(lambda symbol: quote(symbol), lambda *_: history(), no_news)
    assert set(seen) == {"AAA.BK", "AAPL", "ZZZ.BK"}


def test_hourly_scan_lock_prevents_overlap(monkeypatch) -> None:
    po.reset_penny_opportunity_snapshots_for_tests()
    acquired = po._scan_execution_lock.acquire(blocking=False)
    assert acquired is True
    try:
        payload = po.run_penny_scan_once(lambda symbol: quote(symbol), lambda *_: history(), no_news)
        assert payload["status"] in {"running", "unavailable"}
    finally:
        po._scan_execution_lock.release()


def test_failed_scan_preserves_latest_successful_snapshot(monkeypatch) -> None:
    po.reset_penny_opportunity_snapshots_for_tests()
    monkeypatch.setattr(po, "list_registry_assets", lambda enabled_only=True, searchable_only=True: [asset("AAA.BK")])
    success = po.run_penny_scan_once(lambda symbol: quote(symbol), lambda *_: history(), no_news, market="TH")
    assert success["items"]

    def broken_quote(symbol):
        raise RuntimeError("provider down")

    failed = po.run_penny_scan_once(broken_quote, lambda *_: history(), no_news, market="TH")
    assert failed["status"] == "partial"
    assert failed["items"][0]["symbol"] == success["items"][0]["symbol"]
    assert failed["scan"]["is_stale"] is True


def test_frontend_receives_scan_metadata(monkeypatch) -> None:
    po.reset_penny_opportunity_snapshots_for_tests()
    monkeypatch.setattr(po, "list_registry_assets", lambda enabled_only=True, searchable_only=True: [asset("AAA.BK")])
    po.run_penny_scan_once(lambda symbol: quote(symbol), lambda *_: history(), no_news, market="TH")
    payload = po.get_penny_opportunities_snapshot(limit=5)
    assert payload["scan"]["frequency_minutes"] == 60
    assert payload["scan"]["scan_completed_at"]
    assert payload["qualification"]["universe_size"] == 1


def test_thai_foreign_board_assets_are_excluded_before_provider_calls(monkeypatch) -> None:
    rows = [asset("AOT-F.BK"), asset("PTT.BK")]
    called = []
    monkeypatch.setattr(po, "list_registry_assets", lambda enabled_only=True, searchable_only=True: rows)

    def quote_fn(symbol):
        called.append(symbol)
        return quote(symbol)

    payload = po.build_penny_opportunities(quote_fn, lambda *_: history(), no_news, market="TH")
    assert "AOT-F.BK" not in called
    assert "PTT.BK" in called
    assert payload["qualification"]["prefilter_diagnostics"]["excluded_foreign_board_count"] == 1


def test_empty_snapshot_is_not_ready_without_starting_provider_work(monkeypatch) -> None:
    po.reset_penny_opportunity_snapshots_for_tests()
    payload = po.get_penny_opportunities_snapshot(market="TH", limit=5, thai_max_price=10)
    assert payload["status"] == "not_ready"
    assert payload["items"] == []
    assert "does not run a live full-universe scan" in payload["limitations"][0]
