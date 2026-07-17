from __future__ import annotations

from datetime import datetime, timezone
from time import perf_counter
from typing import Any, Callable, Dict

_HEALTH: Dict[str, Dict[str, Any]] = {}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def record_provider_result(provider: str, configured: bool, success: bool, response_time_ms: float | None = None, reason: str | None = None, cache_hit: bool = False) -> Dict[str, Any]:
    previous = _HEALTH.get(provider, {})
    status = _status(configured, success, reason)
    payload = {
        "provider": provider,
        "configured": configured,
        "status": status,
        "healthy": status == "healthy",
        "degraded": status == "degraded",
        "last_success": utc_now() if success else previous.get("last_success"),
        "last_failure": utc_now() if not success else previous.get("last_failure"),
        "response_time_ms": round(response_time_ms, 2) if response_time_ms is not None else previous.get("response_time_ms"),
        "cache_usage": "hit" if cache_hit else "miss",
        "failure_reason": None if success else reason,
    }
    _HEALTH[provider] = payload
    return payload


def timed_provider_call(provider: str, configured: bool, call: Callable[[], Dict[str, Any]]) -> Dict[str, Any]:
    started = perf_counter()
    try:
        payload = call()
    except Exception as exc:
        response_time = (perf_counter() - started) * 1000
        record_provider_result(provider, configured, False, response_time, str(exc))
        raise
    response_time = (perf_counter() - started) * 1000
    reason = str(payload.get("error") or payload.get("unavailable_reason") or "")
    success = not reason and bool(payload)
    record_provider_result(provider, configured, success, response_time, reason or None)
    return payload


def provider_health_snapshot() -> Dict[str, Any]:
    return {
        "providers": _HEALTH,
        "updated_at": utc_now(),
        "allowed_statuses": ["configured", "healthy", "degraded", "rate_limited", "unavailable"],
    }


def clear_provider_health() -> None:
    _HEALTH.clear()


def _status(configured: bool, success: bool, reason: str | None) -> str:
    if not configured:
        return "unavailable"
    if success:
        return "healthy"
    if reason and "rate" in reason.lower():
        return "rate_limited"
    return "degraded"
