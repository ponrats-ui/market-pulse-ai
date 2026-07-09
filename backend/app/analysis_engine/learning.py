from __future__ import annotations

from datetime import date
from typing import Any, Dict, List


def algorithm_registry(version: str) -> Dict[str, Any]:
    return {
        "version": version,
        "date": date.today().isoformat(),
        "performance": "Unavailable until live evaluation history is collected.",
        "accuracy": "Unavailable until forward tests are recorded.",
        "backtest": "Unavailable",
        "forward_test": "Unavailable",
        "benchmark": "Unavailable",
        "lifecycle": ["experiment", "promote", "rollback"],
    }


def list_supported_lifecycle_actions() -> List[str]:
    return ["rollback", "promote", "experiment"]
