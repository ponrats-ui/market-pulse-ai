from __future__ import annotations

from app.main import AlertEvaluationRequest, DigestRequest, EntitlementRequest, alerts_evaluate, digests_build, premium_entitlement_check, premium_entitlements
from app.premium.alerts import build_digest, evaluate_alert_rules
from app.premium.channels import generate_notification
from app.premium.entitlements import evaluate_entitlement


def test_free_vs_premium_entitlement() -> None:
    assert evaluate_entitlement("free", "market_data").enabled is True
    assert evaluate_entitlement("free", "intelligent_alerts").enabled is False
    assert evaluate_entitlement("premium", "intelligent_alerts").enabled is True


def test_disabled_entitlement_blocks_features() -> None:
    entitlement = evaluate_entitlement("disabled", "market_data")

    assert entitlement.enabled is False
    assert entitlement.reason == "Feature access is disabled."


def test_alert_rule_evaluation_generates_unsent_notification() -> None:
    result = evaluate_alert_rules(
        [{"id": "nvda-move", "type": "price_move", "threshold": 3, "assets": ["NVDA"], "channel": "email"}],
        {"price_move_percent": 4},
        plan="premium",
    )

    assert result["entitled"] is True
    assert len(result["triggered_alerts"]) == 1
    assert result["notifications"][0]["generated"] is True
    assert result["notifications"][0]["sent"] is False
    assert result["audit"][0]["delivery_status"] == "provider_unavailable"


def test_quiet_hours_suppress_notification() -> None:
    result = evaluate_alert_rules(
        [{"id": "risk", "type": "risk_score_change", "threshold": 1, "assets": ["AAPL"], "channel": "telegram"}],
        {"risk_score_change": 2, "local_time": "23:00"},
        plan="premium",
        quiet_mode={"quiet_hours": {"start": "22:00", "end": "07:00"}},
    )

    assert result["triggered_alerts"][0]["suppressed"] is True
    assert result["notifications"] == []
    assert result["audit"][0]["suppressed"] is True


def test_no_duplicate_notification_for_same_rule_and_assets() -> None:
    rules = [
        {"id": "dup", "type": "volatility_spike", "threshold": 5, "assets": ["BTC-USD"], "channel": "line"},
        {"id": "dup", "type": "volatility_spike", "threshold": 5, "assets": ["BTC-USD"], "channel": "line"},
    ]

    result = evaluate_alert_rules(rules, {"volatility_percent": 8}, plan="premium")

    assert len(result["triggered_alerts"]) == 1
    assert len(result["notifications"]) == 1
    assert result["audit"][1]["duplicate"] is True


def test_delivery_provider_unavailable_and_no_outbound_send() -> None:
    delivery = generate_notification("telegram", {"why": "test"})

    assert delivery["generated"] is True
    assert delivery["sent"] is False
    assert delivery["status"] == "provider_unavailable"
    assert delivery["failure_reason"] == "Outbound delivery is disabled in Phase E."


def test_digest_is_generated_but_not_sent() -> None:
    digest = build_digest("evening_wrap", {"selected_assets": ["NVDA", "BTC-USD"]})

    assert digest["type"] == "evening_wrap"
    assert digest["generated"] is True
    assert digest["sent"] is False
    assert digest["personalization"]["selected_assets"] == ["NVDA", "BTC-USD"]


def test_premium_api_contracts() -> None:
    entitlements = premium_entitlements()
    entitlement_check = premium_entitlement_check(EntitlementRequest(plan="premium", feature="email_alerts"))
    alert_eval = alerts_evaluate(
        AlertEvaluationRequest(
            plan="premium",
            rules=[{"id": "move", "type": "price_move", "threshold": 2, "assets": ["NVDA"], "channel": "email"}],
            context={"price_move_percent": 3},
        )
    )
    digest = digests_build(DigestRequest(kind="morning_brief", context={"selected_assets": ["NVDA"]}))

    assert entitlements["payments_enabled"] is False
    assert entitlement_check["enabled"] is True
    assert alert_eval["outbound_delivery_enabled"] is False
    assert digest["sent"] is False
