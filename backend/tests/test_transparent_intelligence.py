from __future__ import annotations

from dataclasses import replace

from app import main
from app.services import penny_opportunities as po
from tests.test_penny_opportunities import asset, candidate_payload, history, no_news, quote


def test_penny_algorithm_definition_loads_and_validates() -> None:
    payload = po.get_penny_algorithm_definition()
    assert payload["status"] == "ok"
    assert payload["validation"]["valid"] is True
    assert payload["algorithm"]["identity"]["engine_id"] == po.PENNY_ENGINE_ID


def test_missing_objective_blocks_algorithm_validation(monkeypatch) -> None:
    broken = replace(po.PENNY_ALGORITHM_DEFINITION, objective=replace(po.PENNY_ALGORITHM_DEFINITION.objective, en=""))
    result = po.validate_algorithm_definition(broken, po.PENNY_FACTOR_WEIGHTS)
    assert result.valid is False
    assert "missing_objective" in result.errors


def test_factor_weights_match_active_configuration() -> None:
    definition = po.get_penny_algorithm_definition()["algorithm"]
    documented = {factor["factor_id"]: factor["weight"] for factor in definition["factors"]}
    assert documented == po.PENNY_FACTOR_WEIGHTS


def test_score_breakdown_reconciles_with_final_score() -> None:
    result = po.evaluate_candidate(asset(), po.POLICIES["TH"], lambda symbol: quote(symbol), lambda *_: history(), no_news)
    breakdown = result["score_breakdown"]
    expected = round(breakdown["raw_positive_score"] - breakdown["total_risk_penalty"])
    assert result["penny_opportunity_score"] == max(0, min(100, expected))


def test_missing_factor_remains_visible_not_measured_zero() -> None:
    result = po.evaluate_candidate(asset(), po.POLICIES["TH"], lambda symbol: quote(symbol), lambda *_: history(), no_news)
    catalyst = [row for row in result["score_breakdown"]["factor_contributions"] if row["factor_id"] == "catalyst"][0]
    assert catalyst["missing"] is True
    assert catalyst["raw_score"] is None
    assert catalyst["substituted_score"] == 35


def test_ranking_explanation_matches_rank_order(monkeypatch) -> None:
    rows = [asset("AAA.BK"), asset("BBB.BK")]
    monkeypatch.setattr(po, "list_registry_assets", lambda enabled_only=True, searchable_only=True: rows)
    payloads = {"AAA.BK": candidate_payload("AAA.BK", 90), "BBB.BK": candidate_payload("BBB.BK", 80)}
    monkeypatch.setattr(po, "evaluate_candidate", lambda asset_obj, *_: payloads[asset_obj.canonical_symbol])
    payload = po.build_penny_opportunities(lambda symbol: quote(symbol), lambda *_: history(), no_news, market="TH")
    assert payload["items"][0]["ranking_explanation"]["score_gap_to_next"] == 10
    assert "Rank 1" in payload["items"][0]["ranking_explanation"]["ranking_reason_en"]


def test_why_not_uses_latest_snapshot_without_scan(monkeypatch) -> None:
    po.reset_penny_opportunity_snapshots_for_tests()
    rows = [asset("AAA.BK"), asset("LOW.BK")]
    monkeypatch.setattr(po, "list_registry_assets", lambda enabled_only=True, searchable_only=True: rows)
    low_payload = candidate_payload("LOW.BK", 10)
    low_payload["eligible_for_top5"] = False
    payloads = {"AAA.BK": candidate_payload("AAA.BK", 90), "LOW.BK": low_payload}
    monkeypatch.setattr(po, "evaluate_candidate", lambda asset_obj, *_: payloads[asset_obj.canonical_symbol])
    po.run_penny_scan_once(lambda symbol: quote(symbol), lambda *_: history(), no_news, market="TH")
    why_not = po.get_penny_why_not("LOW.BK")
    assert why_not["status"] == "below_cutoff"
    assert "does not trigger a new scan" in why_not["explanation_en"]


def test_algorithm_api_endpoint_returns_contract() -> None:
    payload = main.penny_algorithm()
    assert payload["status"] == "ok"
    assert payload["algorithm"]["identity"]["algorithm_id"] == "penny-opportunity-v1"


def test_candidate_explanation_endpoint_returns_not_ranked_when_snapshot_missing() -> None:
    po.reset_penny_opportunity_snapshots_for_tests()
    payload = main.penny_explain("AAA.BK")
    assert payload["status"] in {"not_ranked", "unavailable"}
