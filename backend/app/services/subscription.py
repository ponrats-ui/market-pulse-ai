from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

from app.premium.entitlements import entitlement_matrix

PROJECT_DIR = Path(__file__).resolve().parents[3]
SUBSCRIPTION_CONFIG_PATH = PROJECT_DIR / "configs" / "subscription_features.json"


def subscription_features() -> Dict[str, Any]:
    with SUBSCRIPTION_CONFIG_PATH.open("r", encoding="utf-8") as file:
        payload = json.load(file)
    return {
        **payload,
        "entitlements": entitlement_matrix(),
        "status": "architecture_only",
        "payments_enabled": False,
        "disclaimer": "Payment, billing, and notification delivery are not implemented in Phase E.",
    }
