from __future__ import annotations

from copy import deepcopy
import json
import os
from pathlib import Path
from threading import Lock
from typing import Any, Dict


class OpportunitySnapshotStore:
    def __init__(self, storage_dir: str | Path | None = None) -> None:
        self._lock = Lock()
        self._latest: Dict[str, Dict[str, Any]] = {}
        self._failures: Dict[str, Dict[str, Any]] = {}
        self._storage_dir = Path(storage_dir or os.getenv("OPPORTUNITY_SNAPSHOT_DIR", Path(__file__).resolve().parents[3] / "runtime" / "opportunity_snapshots"))

    def publish(self, engine_id: str, snapshot: Dict[str, Any]) -> Dict[str, Any]:
        stable = deepcopy(snapshot)
        with self._lock:
            self._latest[engine_id] = stable
            self._write_json(self._snapshot_path(engine_id), stable)
        return deepcopy(stable)

    def latest(self, engine_id: str) -> Dict[str, Any] | None:
        with self._lock:
            snapshot = self._latest.get(engine_id)
            if snapshot is None:
                snapshot = self._read_json(self._snapshot_path(engine_id))
                if snapshot is not None:
                    self._latest[engine_id] = snapshot
        return deepcopy(snapshot) if snapshot is not None else None

    def record_failure(self, engine_id: str, failure: Dict[str, Any]) -> Dict[str, Any]:
        stable = deepcopy(failure)
        with self._lock:
            self._failures[engine_id] = stable
            self._write_json(self._failure_path(engine_id), stable)
        return deepcopy(stable)

    def failure(self, engine_id: str) -> Dict[str, Any] | None:
        with self._lock:
            failure = self._failures.get(engine_id)
            if failure is None:
                failure = self._read_json(self._failure_path(engine_id))
                if failure is not None:
                    self._failures[engine_id] = failure
        return deepcopy(failure) if failure is not None else None

    def reset(self, engine_id: str | None = None) -> None:
        with self._lock:
            if engine_id is None:
                self._latest.clear()
                self._failures.clear()
                for path in self._storage_dir.glob("*.json"):
                    try:
                        path.unlink()
                    except OSError:
                        continue
                return
            self._latest.pop(engine_id, None)
            self._failures.pop(engine_id, None)
            for path in (self._snapshot_path(engine_id), self._failure_path(engine_id)):
                try:
                    path.unlink()
                except OSError:
                    continue

    def _snapshot_path(self, engine_id: str) -> Path:
        return self._storage_dir / f"{_safe_engine_id(engine_id)}.latest.json"

    def _failure_path(self, engine_id: str) -> Path:
        return self._storage_dir / f"{_safe_engine_id(engine_id)}.failure.json"

    def _write_json(self, path: Path, payload: Dict[str, Any]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        temp_path = path.with_suffix(path.suffix + ".tmp")
        temp_path.write_text(json.dumps(payload, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
        temp_path.replace(path)

    def _read_json(self, path: Path) -> Dict[str, Any] | None:
        if not path.exists():
            return None
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
            return payload if isinstance(payload, dict) else None
        except (OSError, json.JSONDecodeError):
            return None


def _safe_engine_id(engine_id: str) -> str:
    return "".join(char if char.isalnum() or char in {"-", "_"} else "_" for char in str(engine_id or "unknown"))
