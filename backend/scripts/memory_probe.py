from __future__ import annotations

import gc
import json
import argparse
import sys
import time
import tracemalloc
from ctypes import POINTER, Structure, WinDLL, byref, c_size_t, c_ulong, sizeof, windll
from ctypes import wintypes
from pathlib import Path
from typing import Any, Callable

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


class _ProcessMemoryCounters(Structure):
    _fields_ = [
        ("cb", c_ulong),
        ("PageFaultCount", c_ulong),
        ("PeakWorkingSetSize", c_size_t),
        ("WorkingSetSize", c_size_t),
        ("QuotaPeakPagedPoolUsage", c_size_t),
        ("QuotaPagedPoolUsage", c_size_t),
        ("QuotaPeakNonPagedPoolUsage", c_size_t),
        ("QuotaNonPagedPoolUsage", c_size_t),
        ("PagefileUsage", c_size_t),
        ("PeakPagefileUsage", c_size_t),
    ]


def rss_mb() -> float:
    counters = _ProcessMemoryCounters()
    counters.cb = sizeof(counters)
    windll.kernel32.GetCurrentProcess.restype = wintypes.HANDLE
    handle = windll.kernel32.GetCurrentProcess()
    psapi = WinDLL("psapi.dll")
    psapi.GetProcessMemoryInfo.argtypes = [wintypes.HANDLE, POINTER(_ProcessMemoryCounters), wintypes.DWORD]
    psapi.GetProcessMemoryInfo.restype = wintypes.BOOL
    if not psapi.GetProcessMemoryInfo(handle, byref(counters), counters.cb):
        return 0.0
    return counters.WorkingSetSize / 1024 / 1024


def payload_mb(value: Any) -> float:
    try:
        return len(json.dumps(value, default=str).encode("utf-8")) / 1024 / 1024
    except Exception:
        return 0.0


def measure(name: str, fn: Callable[[], Any], loops: int = 1) -> dict[str, Any]:
    from app.services.cache import cache

    gc.collect()
    before = rss_mb()
    before_cache = cache.size()
    tracemalloc.start()
    peak_alloc = 0
    result: Any = None
    errors = 0
    error_text = ""
    started = time.perf_counter()
    for _ in range(loops):
        try:
            result = fn()
        except Exception as exc:  # pragma: no cover - diagnostic script
            result = {"error": repr(exc)}
            errors += 1
            error_text = repr(exc)
        _, peak = tracemalloc.get_traced_memory()
        peak_alloc = max(peak_alloc, peak)
    duration = time.perf_counter() - started
    tracemalloc.stop()
    after_call = rss_mb()
    gc.collect()
    after_gc = rss_mb()
    return {
        "endpoint": name,
        "loops": loops,
        "seconds": round(duration, 3),
        "rss_before_mb": round(before, 2),
        "rss_after_call_mb": round(after_call, 2),
        "rss_after_gc_mb": round(after_gc, 2),
        "rss_delta_after_gc_mb": round(after_gc - before, 2),
        "tracemalloc_peak_mb": round(peak_alloc / 1024 / 1024, 2),
        "payload_mb": round(payload_mb(result), 2),
        "cache_before": before_cache,
        "cache_after": cache.size(),
        "errors": errors,
        "error_text": error_text,
    }


def emit(payload: dict[str, Any]) -> None:
    print(json.dumps(payload, indent=2), flush=True)


def main() -> None:
    parser = argparse.ArgumentParser(description="Profile Market Pulse AI backend memory usage.")
    parser.add_argument("--repeat", type=int, default=100, help="Repeated request count per symbol.")
    parser.add_argument("--skip-live", action="store_true", help="Skip slow live provider endpoints.")
    args = parser.parse_args()

    from app import main as api
    from app.services.cache import cache

    probes: list[tuple[str, Callable[[], Any], int]] = [
        ("/health", api.health, 1),
        ("/api/watchlist", api.watchlist, 1),
        ("/api/assets/search?q=NVDA", lambda: api.asset_search(q="NVDA", limit=25), 1),
        ("/api/sectors", api.sectors, 1),
        ("/api/assets/BTC-USD", lambda: api.asset_quote("BTC-USD"), 1),
        ("/api/assets/BTC-USD/history", lambda: api.asset_history("BTC-USD", "1mo", "1d"), 1),
        ("/api/news?symbol=BTC-USD", lambda: api.news("BTC-USD", 10), 1),
        ("/api/financials/NVDA", lambda: api.financials("NVDA"), 1),
        ("/api/analysis/BTC-USD", lambda: api.analysis("BTC-USD"), 1),
        ("/api/risk/BTC-USD", lambda: api.risk("BTC-USD"), 1),
        ("/api/macro", api.macro, 1),
        ("/api/market-condition", api.market_condition, 1),
    ]
    if args.skip_live:
        probes = probes[:4]

    emit({"phase": "startup", "rss_mb": round(rss_mb(), 2), "cache_size": cache.size()})
    rows = []
    for name, fn, loops in probes:
        row = measure(name, fn, loops)
        rows.append(row)
        emit({"phase": "endpoint_row", "row": row})
    emit({"phase": "endpoint_profile", "rows": rows})

    repeated_symbols = ["BTC-USD", "NVDA", "AAPL", "PTT.BK", "AOT.BK", "ETH-USD"]
    repeated_rows = []
    if not args.skip_live:
        for symbol in repeated_symbols:
            row = measure(f"{args.repeat}x /api/assets/{symbol}", lambda symbol=symbol: api.asset_quote(symbol), args.repeat)
            repeated_rows.append(row)
            emit({"phase": "repeated_row", "row": row})
    emit({"phase": "repeated_profile", "rows": repeated_rows})

    batch_rows = []
    if not args.skip_live:
        concurrent_batch = measure(
            "10x /api/assets/quotes 25 symbols",
            lambda: api.asset_quotes(",".join(["BTC-USD", "ETH-USD", "NVDA", "AAPL", "PTT.BK"] * 5)),
            10,
        )
        batch_rows.append(concurrent_batch)
        emit({"phase": "batch_row", "row": concurrent_batch})
    emit({"phase": "batch_profile", "rows": batch_rows})


if __name__ == "__main__":
    main()
