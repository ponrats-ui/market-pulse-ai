from __future__ import annotations

from threading import Lock
from typing import Dict, List

from app.opportunities.models import OpportunityEngineDefinition, OpportunityEngineRuntime

_registry_lock = Lock()
_engines: Dict[str, OpportunityEngineRuntime] = {}


def register_engine(runtime: OpportunityEngineRuntime) -> None:
    if not runtime.definition.engine_id:
        raise ValueError("Opportunity engine requires an engine_id.")
    with _registry_lock:
        _engines[runtime.definition.engine_id] = runtime


def get_engine(engine_id: str) -> OpportunityEngineRuntime:
    with _registry_lock:
        runtime = _engines.get(engine_id)
    if runtime is None:
        raise KeyError(f"Opportunity engine is not registered: {engine_id}")
    return runtime


def get_engine_definition(engine_id: str) -> OpportunityEngineDefinition:
    return get_engine(engine_id).definition


def list_enabled_engines() -> List[OpportunityEngineRuntime]:
    with _registry_lock:
        runtimes = list(_engines.values())
    return [runtime for runtime in runtimes if runtime.definition.enabled]


def reset_engine_registry_for_tests() -> None:
    with _registry_lock:
        _engines.clear()
