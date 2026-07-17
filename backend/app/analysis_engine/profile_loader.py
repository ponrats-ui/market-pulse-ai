from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

PROJECT_DIR = Path(__file__).resolve().parents[3]
DEFAULT_PROFILE_PATH = PROJECT_DIR / "configs" / "analysis_profiles.json"


def load_profiles(path: Path | None = None) -> Dict[str, Any]:
    selected_path = path or DEFAULT_PROFILE_PATH
    with selected_path.open("r", encoding="utf-8") as file:
        payload = json.load(file)
    _validate_profiles(payload)
    return payload


def get_profile(name: str = "Balanced", path: Path | None = None) -> Dict[str, Any]:
    payload = load_profiles(path)
    profiles = payload["profiles"]
    selected_name = name if name in profiles else payload.get("default_profile", "Balanced")
    profile = profiles[selected_name]
    return {
        "algorithm_version": payload["algorithm_version"],
        "name": selected_name,
        "weights": profile["weights"],
        "description": profile.get("description", ""),
        "regime_adjustments": payload.get("regime_adjustments", {}),
    }


def _validate_profiles(payload: Dict[str, Any]) -> None:
    if not payload.get("algorithm_version"):
        raise ValueError("analysis_profiles.json must define algorithm_version")
    profiles = payload.get("profiles")
    if not isinstance(profiles, dict) or not profiles:
        raise ValueError("analysis_profiles.json must define profiles")
    for name, profile in profiles.items():
        weights = profile.get("weights")
        if not isinstance(weights, dict) or not weights:
            raise ValueError(f"Profile {name} must define weights")
        for factor, value in weights.items():
            if not isinstance(value, (int, float)) or value < 0:
                raise ValueError(f"Profile {name} has invalid weight for {factor}")
