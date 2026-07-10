from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

PROJECT_DIR = Path(__file__).resolve().parents[3]
SUBSCRIPTION_CONFIG_PATH = PROJECT_DIR / "configs" / "subscription_features.json"


def subscription_features() -> Dict[str, Any]:
    with SUBSCRIPTION_CONFIG_PATH.open("r", encoding="utf-8") as file:
        payload = json.load(file)
    return {
        **payload,
        "status": "architecture_only",
        "disclaimer": "Payment, billing, and notification delivery are not implemented in RC4.",
    }
