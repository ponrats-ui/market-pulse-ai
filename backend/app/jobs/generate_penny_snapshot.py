from __future__ import annotations

import argparse
import json
import sys
from typing import Any, Dict, Sequence

from app.data_hub import provider_router
from app.services.news import news_for_symbol
from app.services.penny_opportunities import run_penny_scan_once


def get_cached_quote(symbol: str) -> Dict[str, Any]:
    return provider_router.get_quote(symbol)


def get_cached_history(symbol: str, range: str, interval: str) -> Dict[str, Any]:
    return provider_router.get_history(symbol, range, interval)


def generate_snapshot(argv: Sequence[str] | None = None) -> Dict[str, Any]:
    parser = argparse.ArgumentParser(description="Generate a bounded Thai Penny Opportunity snapshot.")
    parser.add_argument("--market", default="TH", help="Market to scan. Default: TH.")
    parser.add_argument("--max-price", type=float, default=10.0, help="Thai maximum share price threshold. Default: 10.0.")
    parser.add_argument("--limit", type=int, default=5, help="Maximum public ranked items to publish. Default: 5.")
    args = parser.parse_args(argv)

    snapshot = run_penny_scan_once(
        get_cached_quote,
        get_cached_history,
        news_for_symbol,
        market=args.market,
        limit=args.limit,
        thai_max_price=args.max_price,
    )
    return {
        "status": snapshot.get("status"),
        "snapshot_status": snapshot.get("snapshot_status"),
        "items": len(snapshot.get("items", [])),
        "scan": snapshot.get("scan", {}),
        "qualification": snapshot.get("qualification", {}),
        "diagnostics": snapshot.get("diagnostics", {}),
        "limitations": snapshot.get("limitations", []),
    }


def main(argv: Sequence[str] | None = None) -> int:
    result = generate_snapshot(argv)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result.get("status") in {"ok", "partial", "stale"} else 1


if __name__ == "__main__":
    sys.exit(main())
