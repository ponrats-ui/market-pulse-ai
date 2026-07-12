from __future__ import annotations

from datetime import datetime, time, timezone
from typing import Any, Dict, List

from app.premium.channels import generate_notification
from app.premium.entitlements import evaluate_entitlement

RULE_TYPES = {
    "price_move",
    "volatility_spike",
    "news_impact",
    "economic_event",
    "risk_score_change",
    "portfolio_concentration",
    "ai_recommendation_change",
    "earnings_event",
}


def evaluate_alert_rules(rules: List[Dict[str, Any]], context: Dict[str, Any], plan: str = "free", quiet_mode: Dict[str, Any] | None = None) -> Dict[str, Any]:
    entitlement = evaluate_entitlement(plan, "intelligent_alerts")
    audit: List[Dict[str, Any]] = []
    notifications: List[Dict[str, Any]] = []
    triggered: List[Dict[str, Any]] = []
    seen: set[tuple[str, str]] = set()
    for rule in rules:
        rule_id = str(rule.get("id") or rule.get("type") or "unnamed")
        rule_type = str(rule.get("type") or "")
        result = _evaluate_rule(rule, context) if rule_type in RULE_TYPES else _unsupported(rule_type)
        suppressed = _suppressed(result, context, quiet_mode or {})
        key = (rule_id, ",".join(result.get("affected_assets", [])))
        duplicate = key in seen
        if result["triggered"]:
            seen.add(key)
        delivery = None
        if result["triggered"] and entitlement.enabled and not suppressed and not duplicate:
            delivery = generate_notification(str(rule.get("channel", "email")), result)
            notifications.append(delivery)
        audit.append({
            "rule_id": rule_id,
            "rule_type": rule_type,
            "rule_triggered": result["triggered"],
            "notification_generated": delivery is not None,
            "channel_selected": rule.get("channel"),
            "delivery_status": delivery.get("status") if delivery else "not_sent",
            "failure_reason": delivery.get("failure_reason") if delivery else result.get("reason"),
            "suppressed": suppressed,
            "duplicate": duplicate,
            "timestamp": _now(),
        })
        if result["triggered"] and not duplicate:
            triggered.append({**result, "suppressed": suppressed})
    return {
        "plan": entitlement.plan,
        "entitled": entitlement.enabled,
        "entitlement_reason": entitlement.reason,
        "triggered_alerts": triggered,
        "notifications": notifications,
        "audit": audit,
        "outbound_delivery_enabled": False,
        "disclaimer": "Alerts are educational monitoring signals, not financial advice.",
    }


def build_digest(kind: str, context: Dict[str, Any]) -> Dict[str, Any]:
    selected = kind if kind in {"morning_brief", "evening_wrap", "weekly_portfolio_summary"} else "morning_brief"
    assets = context.get("selected_assets") or context.get("affected_assets") or []
    return {
        "type": selected,
        "title": selected.replace("_", " ").title(),
        "summary": f"{selected.replace('_', ' ').title()} prepared for {len(assets)} selected asset(s).",
        "sections": ["market context", "portfolio monitoring", "risk watch", "important events"],
        "personalization": {"selected_assets": assets},
        "generated": True,
        "sent": False,
        "timestamp": _now(),
    }


def _evaluate_rule(rule: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
    rule_type = str(rule.get("type") or "")
    threshold = _num(rule.get("threshold"))
    assets = _assets(rule, context)
    triggered = False
    evidence: List[str] = []
    confidence = "medium"
    severity = "medium"
    if rule_type == "price_move":
        move = abs(_num(context.get("price_move_percent")) or 0)
        triggered = threshold is not None and move >= threshold
        evidence.append(f"Price move {move}% vs threshold {threshold}%.")
    elif rule_type == "volatility_spike":
        vol = _num(context.get("volatility_percent"))
        triggered = threshold is not None and vol is not None and vol >= threshold
        evidence.append(f"Volatility {vol}% vs threshold {threshold}%.")
    elif rule_type == "risk_score_change":
        change = abs(_num(context.get("risk_score_change")) or 0)
        triggered = threshold is not None and change >= threshold
        evidence.append(f"Risk score change {change} vs threshold {threshold}.")
    elif rule_type == "portfolio_concentration":
        concentration = _num(context.get("largest_position_percent"))
        triggered = threshold is not None and concentration is not None and concentration >= threshold
        evidence.append(f"Largest position {concentration}% vs threshold {threshold}%.")
        severity = "high" if concentration and concentration >= 60 else "medium"
    elif rule_type in {"news_impact", "economic_event", "ai_recommendation_change", "earnings_event"}:
        triggered = bool(context.get(rule_type))
        evidence.append(f"{rule_type} flag is {triggered}.")
        confidence = "low" if not triggered else "medium"
    return {
        "type": rule_type,
        "triggered": triggered,
        "why": _why(rule_type, triggered),
        "evidence": evidence,
        "confidence": confidence if triggered else "low",
        "severity": severity if triggered else "low",
        "timestamp": _now(),
        "affected_assets": assets,
        "reason": None if triggered else "Rule condition was not met.",
    }


def _unsupported(rule_type: str) -> Dict[str, Any]:
    return {
        "type": rule_type,
        "triggered": False,
        "why": "No alert was generated because the rule type is unsupported.",
        "evidence": ["Unsupported rule."],
        "confidence": "low",
        "severity": "low",
        "timestamp": _now(),
        "affected_assets": [],
        "reason": "Unsupported alert rule type.",
    }


def _suppressed(alert: Dict[str, Any], context: Dict[str, Any], quiet: Dict[str, Any]) -> bool:
    if not alert.get("triggered"):
        return False
    if quiet.get("daily_digest_only"):
        return True
    if quiet.get("only_critical_alerts") and alert.get("severity") != "high":
        return True
    selected = quiet.get("selected_assets")
    if isinstance(selected, list) and selected:
        if not set(alert.get("affected_assets", [])).intersection({str(item) for item in selected}):
            return True
    hours = quiet.get("quiet_hours")
    if isinstance(hours, dict) and _within_quiet_hours(str(context.get("local_time", "")), str(hours.get("start", "")), str(hours.get("end", ""))):
        return True
    return False


def _within_quiet_hours(current: str, start: str, end: str) -> bool:
    try:
        current_time = time.fromisoformat(current)
        start_time = time.fromisoformat(start)
        end_time = time.fromisoformat(end)
    except ValueError:
        return False
    if start_time <= end_time:
        return start_time <= current_time <= end_time
    return current_time >= start_time or current_time <= end_time


def _assets(rule: Dict[str, Any], context: Dict[str, Any]) -> List[str]:
    assets = rule.get("assets") or context.get("affected_assets") or context.get("selected_assets") or []
    return [str(asset) for asset in assets]


def _why(rule_type: str, triggered: bool) -> str:
    if not triggered:
        return "No alert was generated because the rule condition was not met."
    return {
        "price_move": "Price movement crossed the configured threshold.",
        "volatility_spike": "Volatility crossed the configured threshold.",
        "news_impact": "Important news impact flag was present.",
        "economic_event": "Economic event flag was present.",
        "risk_score_change": "Risk score changed beyond the configured threshold.",
        "portfolio_concentration": "Portfolio concentration crossed the configured threshold.",
        "ai_recommendation_change": "PIA recommendation change flag was present.",
        "earnings_event": "Earnings event flag was present.",
    }.get(rule_type, "Alert rule triggered.")


def _num(value: Any) -> float | None:
    try:
        if value in (None, ""):
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()
