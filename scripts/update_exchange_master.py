from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any


REQUIRED_COLUMNS = {"symbol", "label", "asset_type", "exchange", "market"}


def main() -> None:
    parser = argparse.ArgumentParser(description="Build configs/exchange_master.json from verified exchange constituent CSV files.")
    parser.add_argument("--input", action="append", required=True, help="CSV file exported from a verified source such as Nasdaq Data Link, official SET, or exchange-maintained constituent files.")
    parser.add_argument("--output", default="configs/exchange_master.json")
    args = parser.parse_args()

    assets: list[dict[str, Any]] = []
    for filename in args.input:
        path = Path(filename)
        with path.open("r", encoding="utf-8-sig", newline="") as file:
            reader = csv.DictReader(file)
            missing = REQUIRED_COLUMNS - set(reader.fieldnames or [])
            if missing:
                raise SystemExit(f"{path} is missing required columns: {', '.join(sorted(missing))}")
            for row in reader:
                symbol = (row.get("symbol") or "").strip()
                if not symbol:
                    continue
                assets.append({
                    "symbol": symbol,
                    "label": (row.get("label") or symbol).strip(),
                    "thai_name": (row.get("thai_name") or "").strip() or None,
                    "asset_type": (row.get("asset_type") or "").strip(),
                    "exchange": (row.get("exchange") or "").strip(),
                    "market": (row.get("market") or "").strip(),
                    "sector": (row.get("sector") or "").strip() or None,
                    "industry": (row.get("industry") or "").strip() or None,
                    "country": (row.get("country") or "").strip() or None,
                    "currency": (row.get("currency") or "").strip() or None,
                    "aliases": [alias.strip() for alias in (row.get("aliases") or "").split("|") if alias.strip()],
                })

    payload = {
        "version": "generated",
        "source": "verified_exchange_constituent_csv",
        "coverage_status": "requires_verified_source_files",
        "assets": sorted(_deduplicate(assets), key=lambda item: item["symbol"]),
    }
    output = Path(args.output)
    output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _deduplicate(assets: list[dict[str, Any]]) -> list[dict[str, Any]]:
    merged: dict[str, dict[str, Any]] = {}
    for asset in assets:
        merged[asset["symbol"]] = asset
    return list(merged.values())


if __name__ == "__main__":
    main()
