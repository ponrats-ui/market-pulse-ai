from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict

PLAN_FREE = "free"
PLAN_PREMIUM = "premium"
PLAN_ADMIN = "admin"
PLAN_DISABLED = "disabled"

CORE_FEATURES = {
    "market_data",
    "chart",
    "watchlist",
    "basic_comparison",
    "basic_fundamentals",
    "basic_risk",
    "basic_pia_analysis",
    "paper_portfolio",
}

PREMIUM_FEATURES = {
    "intelligent_alerts",
    "email_alerts",
    "line_alerts",
    "telegram_alerts",
    "web_push_alerts",
    "morning_brief",
    "evening_wrap",
    "weekly_portfolio_summary",
    "portfolio_monitoring",
    "risk_alerts",
    "important_news_alerts",
    "economic_event_alerts",
    "saved_alert_rules",
    "premium_report_export",
}


@dataclass(frozen=True)
class Entitlement:
    plan: str
    feature: str
    enabled: bool
    reason: str


def evaluate_entitlement(plan: str, feature: str) -> Entitlement:
    selected = (plan or PLAN_FREE).strip().lower()
    if selected == PLAN_DISABLED:
        return Entitlement(selected, feature, False, "Feature access is disabled.")
    if selected == PLAN_ADMIN:
        return Entitlement(selected, feature, True, "Admin plan can access architecture-preview features.")
    if feature in CORE_FEATURES:
        return Entitlement(selected or PLAN_FREE, feature, True, "Core market information remains available.")
    if feature in PREMIUM_FEATURES:
        if selected == PLAN_PREMIUM:
            return Entitlement(selected, feature, True, "Premium convenience feature is enabled for this plan.")
        return Entitlement(selected or PLAN_FREE, feature, False, "Premium convenience feature requires premium entitlement.")
    return Entitlement(selected or PLAN_FREE, feature, False, "Unknown feature.")


def entitlement_matrix() -> Dict[str, Any]:
    return {
        "states": [PLAN_FREE, PLAN_PREMIUM, PLAN_ADMIN, PLAN_DISABLED],
        "free": sorted(CORE_FEATURES),
        "premium_49_thb_month": sorted(CORE_FEATURES | PREMIUM_FEATURES),
        "premium_only": sorted(PREMIUM_FEATURES),
        "payments_enabled": False,
        "principle": "Premium sells convenience, monitoring, summaries, and saved time. Core market information remains free.",
    }
