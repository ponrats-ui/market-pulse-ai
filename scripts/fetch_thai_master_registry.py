from __future__ import annotations

import argparse
import csv
import json
import re
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SET_STOCK_LIST_URL = "https://www.set.or.th/api/set/stock/list?lang=en"
DEFAULT_OUTPUT = Path("data/exchange_sources/thai_listed_verified.csv")
DEFAULT_REPORT = Path("data/exchange_sources/thai_listed_verified.meta.json")

SUPPORTED_SECURITY_TYPES = {"S", "F", "L", "P", "Q", "U"}
EXCLUDED_SECURITY_TYPES = {"V", "W", "X"}

SECTOR_NAMES = {
    "AGRI": "Agribusiness",
    "AUTO": "Automotive",
    "BANK": "Banking",
    "COMM": "Commerce",
    "CONMAT": "Construction Materials",
    "CONS": "Construction Services",
    "ENERG": "Energy & Utilities",
    "ETRON": "Electronic Components",
    "FASHION": "Fashion",
    "FIN": "Finance & Securities",
    "FOOD": "Food & Beverage",
    "HELTH": "Healthcare Services",
    "HOME": "Home & Office Products",
    "ICT": "Information & Communication Technology",
    "IMM": "Industrial Materials & Machinery",
    "INSUR": "Insurance",
    "MEDIA": "Media & Publishing",
    "MINE": "Mining",
    "PAPER": "Paper & Printing Materials",
    "PERSON": "Personal Products & Pharmaceuticals",
    "PETRO": "Petrochemicals & Chemicals",
    "PF&REIT": "Property Fund & REITs",
    "PKG": "Packaging",
    "PROP": "Property Development",
    "PROF": "Professional Services",
    "STEEL": "Steel",
    "TOURISM": "Tourism & Leisure",
    "TRANS": "Transportation & Logistics",
}

INDUSTRY_NAMES = {
    "AGRO": "Agro & Food Industry",
    "CONSUMP": "Consumer Products",
    "FINCIAL": "Financials",
    "INDUS": "Industrials",
    "PROPCON": "Property & Construction",
    "RESOURC": "Resources",
    "SERVICE": "Services",
    "TECH": "Technology",
}


def main() -> None:
    parser = argparse.ArgumentParser(description="Fetch SET/mai securities from SET's public listing API and write a normalized Thai registry CSV.")
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT))
    parser.add_argument("--report", default=str(DEFAULT_REPORT))
    parser.add_argument("--source-url", default=SET_STOCK_LIST_URL)
    args = parser.parse_args()

    payload = _fetch_set_payload(args.source_url)
    records = payload.get("securitySymbols", [])
    rows = [_normalize_security(record) for record in records if _is_supported(record)]
    rows = sorted(rows, key=lambda row: row["symbol"])
    validation = _validate_rows(rows)
    if not validation["valid"]:
        raise SystemExit(json.dumps(validation, ensure_ascii=False, indent=2))

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=_fieldnames())
        writer.writeheader()
        writer.writerows(rows)

    excluded_counts: dict[str, int] = {}
    for record in records:
        security_type = str(record.get("securityType") or "").strip()
        if security_type in EXCLUDED_SECURITY_TYPES:
            excluded_counts[security_type] = excluded_counts.get(security_type, 0) + 1

    report = {
        "source": args.source_url,
        "source_name": "Stock Exchange of Thailand public stock list API",
        "coverage_status": "verified_set_public_listing_partial",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "raw_record_count": len(records),
        "included_record_count": len(rows),
        "included_security_types": sorted(SUPPORTED_SECURITY_TYPES),
        "excluded_security_types": excluded_counts,
        "markets": _counts(rows, "exchange"),
        "exchanges": _counts(rows, "exchange"),
        "countries": _counts(rows, "country"),
        "asset_types": _counts(rows, "asset_type"),
        "security_types": _counts(rows, "security_type"),
        "sectors": _counts(rows, "sector"),
        "industries": _counts(rows, "industry"),
        "validation": validation,
        "limitations": [
            "SET public listing API coverage is used as the verified source available to this project.",
            "Derivative warrants, warrants, and depositary receipts are excluded from this phase.",
            "Live provider support remains separate and depends on Yahoo Finance/yfinance symbol coverage.",
        ],
    }
    report_path = Path(args.report)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))


def _fetch_set_payload(url: str) -> dict[str, Any]:
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor())
    home = urllib.request.Request(
        "https://www.set.or.th/en/market/product/stock/search",
        headers={
            "User-Agent": _user_agent(),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9,th;q=0.8",
        },
    )
    opener.open(home, timeout=30).read()
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": _user_agent(),
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "en-US,en;q=0.9,th;q=0.8",
            "Referer": "https://www.set.or.th/en/market/product/stock/search",
        },
    )
    raw = opener.open(request, timeout=30).read()
    return json.loads(raw.decode("utf-8"))


def _normalize_security(record: dict[str, Any]) -> dict[str, str]:
    raw_symbol = str(record.get("symbol") or "").strip().upper()
    canonical = f"{raw_symbol}.BK"
    security_type = str(record.get("securityType") or "").strip().upper()
    sector_code = str(record.get("sector") or "").strip().upper()
    industry_code = str(record.get("industry") or "").strip().upper()
    asset_type = _asset_type(record, security_type)
    company_name = _clean_name(str(record.get("nameEN") or raw_symbol).strip())
    thai_name = str(record.get("nameTH") or "").strip()
    aliases = _aliases(raw_symbol, company_name, thai_name, record)
    return {
        "symbol": canonical,
        "display_symbol": raw_symbol,
        "label": company_name,
        "thai_name": thai_name,
        "asset_type": asset_type,
        "exchange": str(record.get("market") or "SET").strip(),
        "market": "Thailand",
        "sector": SECTOR_NAMES.get(sector_code, sector_code or "Unclassified"),
        "industry": INDUSTRY_NAMES.get(industry_code, industry_code or "Unclassified"),
        "country": "Thailand",
        "currency": "THB",
        "aliases": "|".join(aliases),
        "index_memberships": "",
        "yfinance_symbol": canonical,
        "enabled": "true",
        "searchable": "true",
        "coverage_status": "verified_set_public_listing_partial",
        "security_type": security_type,
        "set_symbol": raw_symbol,
        "source": "set_public_stock_list_api",
    }


def _is_supported(record: dict[str, Any]) -> bool:
    symbol = str(record.get("symbol") or "").strip()
    security_type = str(record.get("securityType") or "").strip().upper()
    market = str(record.get("market") or "").strip().lower()
    return bool(symbol) and market in {"set", "mai"} and security_type in SUPPORTED_SECURITY_TYPES


def _asset_type(record: dict[str, Any], security_type: str) -> str:
    name = f"{record.get('nameEN') or ''} {record.get('nameTH') or ''}".upper()
    if security_type == "L":
        return "etf"
    if security_type == "U":
        return "fund"
    if security_type in {"P", "Q"}:
        return "preferred_stock"
    if bool(record.get("isIFF")):
        return "infrastructure_fund"
    if "REAL ESTATE INVESTMENT TRUST" in name or " REIT" in name:
        return "reit"
    if "PROPERTY FUND" in name:
        return "property_fund"
    if security_type == "F":
        return "foreign_stock"
    return "stock"


def _aliases(symbol: str, company_name: str, thai_name: str, record: dict[str, Any]) -> list[str]:
    values = [
        symbol,
        symbol.replace("-F", ""),
        symbol.replace("-P", ""),
        company_name,
        _compact_english_company(company_name),
        thai_name,
        _compact_thai_company(thai_name),
        *_thai_word_aliases(thai_name),
        *[str(item) for item in record.get("oldSymbols") or []],
    ]
    return _unique([value for value in values if value])


def _clean_name(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def _compact_english_company(value: str) -> str:
    cleaned = re.sub(r"\b(PUBLIC|COMPANY|LIMITED|PCL|PLC|THE)\b", " ", value, flags=re.IGNORECASE)
    return re.sub(r"\s+", " ", cleaned).strip()


def _compact_thai_company(value: str) -> str:
    cleaned = value
    for token in ["บริษัท", "ธนาคาร", "จำกัด", "(มหาชน)", "มหาชน", "กองทุนรวม", "กองทรัสต์"]:
        cleaned = cleaned.replace(token, " ")
    return re.sub(r"\s+", "", cleaned).strip()


def _thai_word_aliases(value: str) -> list[str]:
    cleaned = value.replace("(", " ").replace(")", " ").replace(".", " ")
    ignored = {"บริษัท", "ธนาคาร", "จำกัด", "มหาชน", "กองทุนรวม", "กองทรัสต์"}
    words = [word.strip() for word in re.split(r"\s+", cleaned) if len(word.strip()) >= 3 and word.strip() not in ignored]
    return words[:8]


def _validate_rows(rows: list[dict[str, str]]) -> dict[str, Any]:
    symbols: set[str] = set()
    duplicates: list[str] = []
    malformed: list[str] = []
    broken_thai: list[str] = []
    invalid_mapping: list[str] = []
    for row in rows:
        symbol = row["symbol"]
        if symbol in symbols:
            duplicates.append(symbol)
        symbols.add(symbol)
        if not symbol or not row["label"] or not row["exchange"] or not row["yfinance_symbol"]:
            malformed.append(symbol or "<missing>")
        if not symbol.endswith(".BK") or row["yfinance_symbol"] != symbol:
            invalid_mapping.append(symbol)
        thai_name = row["thai_name"]
        if thai_name and not any("\u0e00" <= char <= "\u0e7f" for char in thai_name):
            broken_thai.append(symbol)
    return {
        "valid": not duplicates and not malformed and not broken_thai and not invalid_mapping,
        "duplicates": sorted(duplicates),
        "malformed": sorted(malformed),
        "broken_thai": sorted(broken_thai),
        "invalid_mapping": sorted(invalid_mapping),
        "record_count": len(rows),
    }


def _counts(rows: list[dict[str, str]], key: str) -> dict[str, int]:
    counts: dict[str, int] = {}
    for row in rows:
        value = row.get(key) or "Unclassified"
        counts[value] = counts.get(value, 0) + 1
    return dict(sorted(counts.items(), key=lambda item: (-item[1], item[0])))


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
        "set_symbol",
        "source",
    ]


def _user_agent() -> str:
    return "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36"


def _unique(values: list[str]) -> list[str]:
    output: list[str] = []
    seen: set[str] = set()
    for value in values:
        normalized = re.sub(r"\s+", " ", str(value or "")).strip()
        key = normalized.casefold()
        if normalized and key not in seen:
            output.append(normalized)
            seen.add(key)
    return output


if __name__ == "__main__":
    main()
