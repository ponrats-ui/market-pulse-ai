from __future__ import annotations

from app.opportunities.models import OpportunityEngineDefinition
from app.opportunities.ranking import rank_candidates
from app.opportunities.registry import get_engine, register_engine, reset_engine_registry_for_tests
from app.opportunities.scheduler import OpportunityScheduler
from app.opportunities.snapshots import OpportunitySnapshotStore
from app.services import penny_opportunities as po


def test_engine_registry_resolves_penny_engine() -> None:
    reset_engine_registry_for_tests()
    po.register_penny_opportunity_engine()
    runtime = get_engine(po.PENNY_ENGINE_ID)
    assert runtime.definition.engine_id == po.PENNY_ENGINE_ID
    assert runtime.definition.factor_weights == po.PENNY_FACTOR_WEIGHTS


def test_unregistered_engine_is_rejected_safely() -> None:
    reset_engine_registry_for_tests()
    try:
        get_engine("missing-opportunity")
    except KeyError as exc:
        assert "missing-opportunity" in str(exc)
    else:  # pragma: no cover
        raise AssertionError("Unregistered engine lookup should fail.")


def test_shared_ranking_uses_penny_tie_breaker_order() -> None:
    items = [
        {"symbol": "BBB", "penny_opportunity_score": 80, "data_confidence": 70, "data_completeness": 80, "scores": {"liquidity": 50}, "risk_penalty": 4},
        {"symbol": "AAA", "penny_opportunity_score": 80, "data_confidence": 70, "data_completeness": 80, "scores": {"liquidity": 50}, "risk_penalty": 4},
        {"symbol": "CCC", "penny_opportunity_score": 81, "data_confidence": 10, "data_completeness": 10, "scores": {"liquidity": 1}, "risk_penalty": 99},
    ]
    ranked = rank_candidates(items, score_field="penny_opportunity_score", limit=3)
    assert [item["symbol"] for item in ranked] == ["CCC", "AAA", "BBB"]


def test_snapshot_store_publishes_atomic_copy() -> None:
    store = OpportunitySnapshotStore()
    snapshot = {"status": "ok", "items": [{"symbol": "AAA"}]}
    published = store.publish("test-engine", snapshot)
    snapshot["items"][0]["symbol"] = "MUTATED"
    published["items"][0]["symbol"] = "MUTATED_AGAIN"
    assert store.latest("test-engine")["items"][0]["symbol"] == "AAA"


def test_snapshot_store_preserves_failure_separately() -> None:
    store = OpportunitySnapshotStore()
    store.publish("test-engine", {"status": "ok", "items": [{"symbol": "AAA"}]})
    store.record_failure("test-engine", {"failure_stage": "candidate_processing"})
    assert store.latest("test-engine")["status"] == "ok"
    assert store.failure("test-engine")["failure_stage"] == "candidate_processing"


def test_snapshot_store_persists_snapshot_between_instances(tmp_path) -> None:
    first = OpportunitySnapshotStore(tmp_path)
    first.publish("test-engine", {"status": "ok", "items": [{"symbol": "AAA"}]})

    second = OpportunitySnapshotStore(tmp_path)
    assert second.latest("test-engine")["items"][0]["symbol"] == "AAA"


def test_snapshot_store_reset_removes_persisted_snapshot(tmp_path) -> None:
    store = OpportunitySnapshotStore(tmp_path)
    store.publish("test-engine", {"status": "ok", "items": []})
    store.record_failure("test-engine", {"failure_stage": "candidate_processing"})

    store.reset("test-engine")

    assert store.latest("test-engine") is None
    assert store.failure("test-engine") is None


def test_scheduler_prevents_duplicate_engine_threads() -> None:
    scheduler = OpportunityScheduler()
    calls = {"count": 0}

    definition = OpportunityEngineDefinition(
        engine_id="test-engine",
        category="test",
        display_name="Test Engine",
        methodology_version="m1",
        score_version="s1",
        policy_version="p1",
        config_version="c1",
        supported_markets=["US"],
        schedule_frequency_minutes=60,
        maximum_results=5,
        shortlist_limit=5,
        minimum_score=0,
        minimum_confidence=0,
        minimum_completeness=0,
        freshness_policy={},
        factor_weights={},
        risk_policy={},
        tie_breaker_policy=[],
    )

    assert scheduler.start(definition, lambda: calls.__setitem__("count", calls["count"] + 1)) is True
    assert scheduler.start(definition, lambda: None) is False
    scheduler.stop("test-engine")
    scheduler.reset_for_tests()
