from __future__ import annotations

from copy import deepcopy
from threading import Lock
from typing import Any, Dict


class OpportunitySnapshotStore:
    def __init__(self) -> None:
        self._lock = Lock()
        self._latest: Dict[str, Dict[str, Any]] = {}
        self._failures: Dict[str, Dict[str, Any]] = {}

    def publish(self, engine_id: str, snapshot: Dict[str, Any]) -> Dict[str, Any]:
        stable = deepcopy(snapshot)
        with self._lock:
            self._latest[engine_id] = stable
        return deepcopy(stable)

    def latest(self, engine_id: str) -> Dict[str, Any] | None:
        with self._lock:
            snapshot = self._latest.get(engine_id)
        return deepcopy(snapshot) if snapshot is not None else None

    def record_failure(self, engine_id: str, failure: Dict[str, Any]) -> Dict[str, Any]:
        stable = deepcopy(failure)
        with self._lock:
            self._failures[engine_id] = stable
        return deepcopy(stable)

    def failure(self, engine_id: str) -> Dict[str, Any] | None:
        with self._lock:
            failure = self._failures.get(engine_id)
        return deepcopy(failure) if failure is not None else None

    def reset(self, engine_id: str | None = None) -> None:
        with self._lock:
            if engine_id is None:
                self._latest.clear()
                self._failures.clear()
                return
            self._latest.pop(engine_id, None)
            self._failures.pop(engine_id, None)
