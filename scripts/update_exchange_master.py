from __future__ import annotations

import argparse
import csv
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REQUIRED_COLUMNS = {"symbol", "label", "asset_type", "exchange", "market"}
DEFAULT_INPUTS = {
    "us_listed_verified": Path("data/exchange_sources/us_listed_verified.csv"),
    "thai_listed_verified": Path("data/exchange_sources/thai_listed_verified.csv"),
    "sp500": Path("data/exchange_sources/sp500.csv"),
    "nasdaq100": Path("data/exchange_sources/nasdaq100.csv"),
    "set": Path("data/exchange_sources/set.csv"),
}


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate and update configs/exchange_master.json from verified exchange/security master CSV files.")
    parser.add_argument("--input", action="append", help="Verified exchange/security master CSV file. Can be passed more than once.")
    parser.add_argument("--output", default="configs/exchange_master.json")
    parser.add_argument("--dry-run", action="store_true", help="Read inputs, validate, and report diff without writing.")
    parser.add_argument("--validate", action="store_true", help="Validate current output plus any provided inputs.")
    parser.add_argument("--apply", action="store_true", help="Write the updated exchange master only when validation passes.")
    parser.add_argument("--market", choices=["all", "us", "thailand"], default="all", help="Limit default verified sources to one market family.")
    parser.add_argument("--diff", action="store_true", help="Always include added/removed/changed symbols in the validation report.")
    args = parser.parse_args()

    output = Path(args.output)
    current = _read_json(output)
    input_paths = [Path(item) for item in args.input or []]
    if not input_paths:
        if args.market == "us":
            input_paths = [DEFAULT_INPUTS["us_listed_verified"]] if DEFAULT_INPUTS["us_listed_verified"].exists() else []
        elif args.market == "thailand":
            input_paths = [DEFAULT_INPUTS["thai_listed_verified"]] if DEFAULT_INPUTS["thai_listed_verified"].exists() else []
        else:
            input_paths = [path for path in DEFAULT_INPUTS.values() if path.exists()]

    if not input_paths:
        report = {
            "status": "no_verified_sources_found",
            "message": "No source CSV files were provided. Current exchange master was not modified.",
            "expected_sources": {key: str(path) for key, path in DEFAULT_INPUTS.items()},
            "current_record_count": len(current.get("assets", [])),
            "coverage_status": current.get("coverage_status", "partial"),
        }
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return

    imported_assets: list[dict[str, Any]] = []
    source_reports: list[dict[str, Any]] = []
    for path in input_paths:
        assets = _read_assets(path)
        imported_assets.extend(assets)
        source_reports.append({"source": str(path), "record_count": len(assets), "duplicates": _duplicate_symbols(assets)})

    merged = _merge_preserving_manual_fields(current.get("assets", []), imported_assets)
    validation = _validate_assets(merged)
    diff = _diff(current.get("assets", []), merged)
    next_payload = {
        **current,
        "version": f"generated-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}",
        "source": "verified_exchange_constituent_csv",
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "constituent_date": datetime.now(timezone.utc).date().isoformat(),
        "record_count": len(merged),
        "validation_status": "passed" if validation["valid"] else "failed",
        "coverage_status": "verified_ingestion_partial" if validation["valid"] else "validation_failed",
        "ingestion_sources": source_reports,
        "assets": sorted(merged, key=lambda item: item["symbol"]),
    }

    report = {
        "validation": validation,
        "diff": diff,
        "sources": source_reports,
        "coverage_status": next_payload["coverage_status"],
        "record_count": len(merged),
        "note": "Search coverage and live-data coverage remain separate; provider gaps must not remove searchable securities.",
    }
    if args.apply:
        if not validation["valid"]:
            raise SystemExit(json.dumps(report, ensure_ascii=False, indent=2))
        if output.exists():
            backup = output.with_suffix(f".backup-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}{output.suffix}")
            shutil.copy2(output, backup)
            report["backup"] = str(backup)
        output.write_text(json.dumps(next_payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        report["status"] = "applied"
    elif args.dry_run or args.validate:
        report["status"] = "validated_not_written"
    else:
        report["status"] = "no_write_without_apply"
    print(json.dumps(report, ensure_ascii=False, indent=2))


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {"assets": []}


def _read_assets(path: Path) -> list[dict[str, Any]]:
    with path.open("r", encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)
        missing = REQUIRED_COLUMNS - set(reader.fieldnames or [])
        if missing:
            raise SystemExit(f"{path} is missing required columns: {', '.join(sorted(missing))}")
        assets = [_normalize_row(row) for row in reader]
    return [asset for asset in assets if asset["symbol"]]


def _normalize_row(row: dict[str, str]) -> dict[str, Any]:
    symbol = (row.get("symbol") or "").strip().upper()
    provider_symbol = (row.get("yfinance_symbol") or symbol).strip()
    return {
        "symbol": symbol,
        "provider_symbols": {"yfinance": provider_symbol},
        "display_symbol": (row.get("display_symbol") or symbol.replace(".BK", "")).strip(),
        "label": (row.get("label") or symbol).strip(),
        "thai_name": (row.get("thai_name") or "").strip(),
        "asset_type": (row.get("asset_type") or "").strip(),
        "exchange": (row.get("exchange") or "").strip(),
        "market": (row.get("market") or "").strip(),
        "sector": (row.get("sector") or "").strip(),
        "industry": (row.get("industry") or "").strip(),
        "country": (row.get("country") or "").strip(),
        "currency": (row.get("currency") or "").strip(),
        "aliases": [alias.strip() for alias in (row.get("aliases") or "").split("|") if alias.strip()],
        "index_memberships": [item.strip() for item in (row.get("index_memberships") or "").split("|") if item.strip()],
        "enabled": (row.get("enabled") or "true").strip().lower() not in {"0", "false", "no"},
    }


def _merge_preserving_manual_fields(current: list[dict[str, Any]], imported: list[dict[str, Any]]) -> list[dict[str, Any]]:
    current_by_symbol = {str(asset.get("symbol", "")).upper(): asset for asset in current}
    merged: dict[str, dict[str, Any]] = {}
    for asset in imported:
        symbol = asset["symbol"]
        manual = current_by_symbol.get(symbol, {})
        aliases = _unique([*asset.get("aliases", []), *manual.get("aliases", [])])
        merged[symbol] = {**manual, **asset, "aliases": aliases, "thai_name": manual.get("thai_name") or asset.get("thai_name", "")}
    for symbol, asset in current_by_symbol.items():
        merged.setdefault(symbol, asset)
    return list(merged.values())


def _validate_assets(assets: list[dict[str, Any]]) -> dict[str, Any]:
    seen: set[str] = set()
    duplicates: list[str] = []
    malformed: list[str] = []
    for asset in assets:
        symbol = str(asset.get("symbol", "")).strip()
        if symbol in seen:
            duplicates.append(symbol)
        seen.add(symbol)
        if not symbol or not asset.get("label") or not asset.get("asset_type") or not asset.get("exchange"):
            malformed.append(symbol or "<missing>")
    return {"valid": not duplicates and not malformed, "duplicates": duplicates, "malformed": malformed, "record_count": len(assets)}


def _duplicate_symbols(assets: list[dict[str, Any]]) -> list[str]:
    seen: set[str] = set()
    duplicates: list[str] = []
    for asset in assets:
        symbol = str(asset.get("symbol", "")).upper()
        if symbol in seen:
            duplicates.append(symbol)
        seen.add(symbol)
    return sorted(duplicates)


def _diff(current: list[dict[str, Any]], updated: list[dict[str, Any]]) -> dict[str, list[str]]:
    current_symbols = {str(asset.get("symbol", "")).upper(): asset for asset in current}
    updated_symbols = {str(asset.get("symbol", "")).upper(): asset for asset in updated}
    added = sorted(set(updated_symbols) - set(current_symbols))
    removed = sorted(set(current_symbols) - set(updated_symbols))
    changed = sorted(symbol for symbol in set(current_symbols) & set(updated_symbols) if current_symbols[symbol] != updated_symbols[symbol])
    return {"added": added, "removed": removed, "changed": changed}


def _unique(values: list[str]) -> list[str]:
    output: list[str] = []
    seen: set[str] = set()
    for value in values:
        key = value.strip().casefold()
        if key and key not in seen:
            output.append(value.strip())
            seen.add(key)
    return output


if __name__ == "__main__":
    main()
