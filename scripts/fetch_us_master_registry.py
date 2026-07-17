from __future__ import annotations

import argparse
import csv
import json
import re
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

NASDAQ_LISTED_URL = "https://www.nasdaqtrader.com/dynamic/SymDir/nasdaqlisted.txt"
OTHER_LISTED_URL = "https://www.nasdaqtrader.com/dynamic/SymDir/otherlisted.txt"
NASDAQ_SCREENER_URL = "https://api.nasdaq.com/api/screener/stocks?tableonly=true&limit=10000&offset=0&download=true"

DEFAULT_OUTPUT = Path("data/exchange_sources/us_listed_verified.csv")
DEFAULT_REPORT = Path("data/exchange_sources/us_listed_verified.meta.json")

EXCHANGE_MAP = {
    "NASDAQ": "NASDAQ",
    "A": "NYSE American",
    "N": "NYSE",
    "P": "NYSE Arca",
    "Z": "Cboe BZX",
    "V": "IEX",
}

EXCLUDED_NAME_PATTERNS = [
    r"\bWarrants?\b",
    r"\bRights?\b",
    r"\bUnits?\b",
    r"\bUnit\b",
    r"\bRight\b",
    r"\bWarrant\b",
]


def main() -> None:
    parser = argparse.ArgumentParser(description="Fetch US listed securities from public exchange symbol directories.")
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT))
    parser.add_argument("--report", default=str(DEFAULT_REPORT))
    parser.add_argument("--nasdaq-listed-url", default=NASDAQ_LISTED_URL)
    parser.add_argument("--other-listed-url", default=OTHER_LISTED_URL)
    parser.add_argument("--screener-url", default=NASDAQ_SCREENER_URL)
    parser.add_argument("--screener-cache", help="Optional local Nasdaq screener JSON cache used for sector/industry enrichment.")
    args = parser.parse_args()

    screener = _read_screener_cache(args.screener_cache) if args.screener_cache else _fetch_screener(args.screener_url)
    nasdaq_rows = _parse_pipe_table(_fetch_text(args.nasdaq_listed_url))
    other_rows = _parse_pipe_table(_fetch_text(args.other_listed_url))

    rows = [
        *_normalize_nasdaq_rows(nasdaq_rows, screener),
        *_normalize_other_rows(other_rows, screener),
    ]
    rows = sorted(_dedupe_rows(rows), key=lambda row: row["symbol"])
    validation = _validate_rows(rows)
    if not validation["valid"]:
        raise SystemExit(json.dumps(validation, ensure_ascii=False, indent=2))

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=_fieldnames())
        writer.writeheader()
        writer.writerows(rows)

    report = {
        "sources": [
            args.nasdaq_listed_url,
            args.other_listed_url,
            args.screener_url,
        ],
        "source_name": "Nasdaq Trader symbol directories with Nasdaq screener metadata",
        "coverage_status": "verified_us_exchange_directory_partial",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "raw_record_count": len(nasdaq_rows) + len(other_rows),
        "included_record_count": len(rows),
        "exchanges": _counts(rows, "exchange"),
        "asset_types": _counts(rows, "asset_type"),
        "sectors": _counts(rows, "sector"),
        "industries": _counts(rows, "industry"),
        "validation": validation,
        "limitations": [
            "US security search coverage is built from public exchange symbol directories and Nasdaq screener metadata.",
            "Live quote, history, fundamentals, and news coverage remain provider dependent.",
            "Warrants, rights, units, test issues, file footer rows, and duplicate symbols are excluded.",
            "Sector and industry are populated when available from the screener source; otherwise the record is marked Unclassified.",
        ],
    }
    report_path = Path(args.report)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))


def _fetch_text(url: str) -> str:
    request = urllib.request.Request(url, headers=_headers("text/plain,*/*"))
    return _urlopen_with_retry(request).decode("utf-8", "replace")


def _fetch_screener(url: str) -> dict[str, dict[str, Any]]:
    request = urllib.request.Request(url, headers=_headers("application/json,*/*"))
    try:
        payload = json.loads(_urlopen_with_retry(request, attempts=2).decode("utf-8"))
    except Exception:
        return {}
    rows = payload.get("data", {}).get("rows", [])
    return {str(row.get("symbol") or "").strip().upper(): row for row in rows if row.get("symbol")}


def _read_screener_cache(path: str | None) -> dict[str, dict[str, Any]]:
    if not path:
        return {}
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    rows = payload.get("data", {}).get("rows", [])
    return {str(row.get("symbol") or "").strip().upper(): row for row in rows if row.get("symbol")}


def _urlopen_with_retry(request: urllib.request.Request, attempts: int = 3) -> bytes:
    last_error: Exception | None = None
    for attempt in range(attempts):
        try:
            return urllib.request.urlopen(request, timeout=60).read()
        except Exception as exc:  # noqa: BLE001 - network fetcher reports final exception after retry.
            last_error = exc
            if attempt < attempts - 1:
                time.sleep(1.5 * (attempt + 1))
    assert last_error is not None
    raise last_error


def _headers(accept: str) -> dict[str, str]:
    return {
        "User-Agent": "Mozilla/5.0 (compatible; MarketPulseAI/1.0; +https://github.com/ponrats-ui/market-pulse-ai)",
        "Accept": accept,
        "Accept-Language": "en-US,en;q=0.9",
        "Origin": "https://www.nasdaq.com",
        "Referer": "https://www.nasdaq.com/market-activity/stocks/screener",
    }


def _parse_pipe_table(text: str) -> list[dict[str, str]]:
    lines = [line.rstrip("\r") for line in text.splitlines() if line.strip()]
    if not lines:
        return []
    reader = csv.DictReader(lines, delimiter="|")
    return [row for row in reader if row and not str(next(iter(row.values()), "")).startswith("File Creation Time")]


def _normalize_nasdaq_rows(rows: list[dict[str, str]], screener: dict[str, dict[str, Any]]) -> list[dict[str, str]]:
    output: list[dict[str, str]] = []
    for row in rows:
        symbol = _clean_symbol(row.get("Symbol", ""))
        name = _clean_name(row.get("Security Name", ""))
        if not _is_supported(symbol, name, row.get("Test Issue", ""), row.get("ETF", "")):
            continue
        output.append(_make_row(symbol=symbol, name=name, exchange="NASDAQ", is_etf=row.get("ETF") == "Y", screener=screener))
    return output


def _normalize_other_rows(rows: list[dict[str, str]], screener: dict[str, dict[str, Any]]) -> list[dict[str, str]]:
    output: list[dict[str, str]] = []
    for row in rows:
        symbol = _clean_symbol(row.get("ACT Symbol", ""))
        name = _clean_name(row.get("Security Name", ""))
        exchange = EXCHANGE_MAP.get(str(row.get("Exchange") or "").strip(), str(row.get("Exchange") or "").strip())
        if not _is_supported(symbol, name, row.get("Test Issue", ""), row.get("ETF", "")):
            continue
        if exchange not in {"NYSE", "NASDAQ", "NYSE American", "NYSE Arca", "Cboe BZX", "IEX"}:
            continue
        output.append(_make_row(symbol=symbol, name=name, exchange=exchange, is_etf=row.get("ETF") == "Y", screener=screener))
    return output


def _make_row(symbol: str, name: str, exchange: str, is_etf: bool, screener: dict[str, dict[str, Any]]) -> dict[str, str]:
    metadata = screener.get(symbol, {})
    label = _clean_name(metadata.get("name") or name or symbol)
    asset_type = _asset_type(symbol, label, is_etf)
    sector = _sector(metadata.get("sector"), asset_type, label)
    industry = _industry(metadata.get("industry"), asset_type, label)
    return {
        "symbol": symbol,
        "display_symbol": symbol,
        "label": label,
        "thai_name": "",
        "asset_type": asset_type,
        "exchange": exchange,
        "market": exchange,
        "sector": sector,
        "industry": industry,
        "country": "US",
        "currency": "USD",
        "aliases": "|".join(_aliases(symbol, label)),
        "index_memberships": "",
        "yfinance_symbol": _yfinance_symbol(symbol),
        "enabled": "true",
        "searchable": "true",
        "coverage_status": "verified_us_exchange_directory_partial",
        "security_type": asset_type,
        "source": "nasdaq_trader_symbol_directories",
    }


def _is_supported(symbol: str, name: str, test_issue: str, etf: str) -> bool:
    if not symbol or symbol.startswith("File Creation Time"):
        return False
    if str(test_issue or "").strip().upper() == "Y":
        return False
    if any(re.search(pattern, name, flags=re.IGNORECASE) for pattern in EXCLUDED_NAME_PATTERNS):
        return False
    if "$" in symbol:
        return False
    return True


def _asset_type(symbol: str, name: str, is_etf: bool) -> str:
    lower = name.casefold()
    if is_etf or " exchange traded fund" in lower or lower.endswith(" etf") or " etf " in lower:
        return "etf"
    if "preferred" in lower or "preference" in lower or "depositary shares" in lower:
        return "preferred_stock"
    if "american depositary" in lower or " adr" in lower:
        return "adr"
    if "real estate investment trust" in lower or " reit" in lower:
        return "reit"
    if "closed-end" in lower or "closed end" in lower or "municipal income" in lower:
        return "closed_end_fund"
    return "stock"


def _sector(value: Any, asset_type: str, name: str) -> str:
    sector = str(value or "").strip()
    if sector:
        return sector
    if asset_type == "etf":
        return "ETF"
    if asset_type in {"reit", "closed_end_fund"}:
        return "Real Estate" if asset_type == "reit" else "Closed-End Fund"
    if asset_type == "adr":
        return "International Equity"
    return "Unclassified"


def _industry(value: Any, asset_type: str, name: str) -> str:
    industry = str(value or "").strip()
    if industry:
        return industry
    if asset_type == "etf":
        return "Exchange Traded Fund"
    if asset_type == "preferred_stock":
        return "Preferred Stock"
    if asset_type == "reit":
        return "REIT"
    if asset_type == "adr":
        return "ADR"
    return "Unclassified"


def _aliases(symbol: str, label: str) -> list[str]:
    compact = _compact_company_name(label)
    values = [symbol, symbol.replace(".", "-"), label, compact]
    return _unique([value for value in values if value])


def _compact_company_name(value: str) -> str:
    cleaned = re.sub(r"\b(Common Stock|Ordinary Shares|Class [A-Z]|Inc\.?|Corp\.?|Corporation|Company|Ltd\.?|PLC|N\.V\.|S\.A\.)\b", " ", value, flags=re.IGNORECASE)
    return re.sub(r"\s+", " ", cleaned).strip()


def _clean_symbol(value: str) -> str:
    return str(value or "").strip().upper()


def _clean_name(value: Any) -> str:
    return re.sub(r"\s+", " ", str(value or "")).strip()


def _yfinance_symbol(symbol: str) -> str:
    return symbol.replace(".", "-")


def _dedupe_rows(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    output: dict[str, dict[str, str]] = {}
    for row in rows:
        symbol = row["symbol"]
        existing = output.get(symbol)
        if not existing:
            output[symbol] = row
            continue
        if existing["sector"] == "Unclassified" and row["sector"] != "Unclassified":
            output[symbol] = row
    return list(output.values())


def _validate_rows(rows: list[dict[str, str]]) -> dict[str, Any]:
    seen: set[str] = set()
    duplicates: list[str] = []
    malformed: list[str] = []
    for row in rows:
        symbol = row["symbol"]
        if symbol in seen:
            duplicates.append(symbol)
        seen.add(symbol)
        if not symbol or not row["label"] or not row["exchange"] or not row["yfinance_symbol"]:
            malformed.append(symbol or "<missing>")
    return {
        "valid": not duplicates and not malformed,
        "duplicates": sorted(duplicates),
        "malformed": sorted(malformed),
        "record_count": len(rows),
    }


def _counts(rows: list[dict[str, str]], key: str) -> dict[str, int]:
    counts: dict[str, int] = {}
    for row in rows:
        value = row.get(key) or "Unclassified"
        counts[value] = counts.get(value, 0) + 1
    return dict(sorted(counts.items(), key=lambda item: (-item[1], item[0])))


def _unique(values: list[str]) -> list[str]:
    output: list[str] = []
    seen: set[str] = set()
    for value in values:
        key = value.strip().casefold()
        if key and key not in seen:
            output.append(value.strip())
            seen.add(key)
    return output


def _fieldnames() -> list[str]:
    return [
        "symbol",
        "display_symbol",
        "label",
        "thai_name",
        "asset_type",
        "exchange",
        "market",
        "sector",
        "industry",
        "country",
        "currency",
        "aliases",
        "index_memberships",
        "yfinance_symbol",
        "enabled",
        "searchable",
        "coverage_status",
        "security_type",
        "source",
    ]


if __name__ == "__main__":
    main()
