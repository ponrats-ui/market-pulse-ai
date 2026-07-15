from __future__ import annotations

import csv
import json
import re
import unicodedata
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from difflib import SequenceMatcher
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, Iterable, List

from app.data_hub.exchange_master import ASSET_CLASS_MAP, CAPABILITY_DEFAULTS, ExchangeAsset, exchange_master_metadata, list_assets

PROJECT_DIR = Path(__file__).resolve().parents[3]
US_LISTED_SOURCE = PROJECT_DIR / "data" / "exchange_sources" / "us_listed_verified.csv"
THAI_LISTED_SOURCE = PROJECT_DIR / "data" / "exchange_sources" / "thai_listed_verified.csv"
THAI_LISTED_METADATA = PROJECT_DIR / "data" / "exchange_sources" / "thai_listed_verified.meta.json"

THAI_ALIAS_OVERRIDES: Dict[str, Dict[str, Any]] = {
    "KTB.BK": {"aliases": ["KTB", "กรุงไทย", "ธนาคารกรุงไทย"]},
    "SCB.BK": {"aliases": ["SCB", "ไทยพาณิชย์", "ธนาคารไทยพาณิชย์", "เอสซีบี"]},
    "TTB.BK": {"thai_name": "ทีเอ็มบีธนชาต", "aliases": ["TTB", "ทีทีบี", "ทหารไทยธนชาต", "ธนาคารทหารไทยธนชาต"]},
    "KBANK.BK": {"thai_name": "กสิกรไทย", "aliases": ["KBANK", "กสิกร", "ธนาคารกสิกรไทย"]},
    "AOT.BK": {"thai_name": "ท่าอากาศยานไทย", "aliases": ["AOT", "สนามบิน", "ท่าอากาศยานไทย"]},
    "ADVANC.BK": {"aliases": ["ADVANC", "แอดวานซ์", "เอไอเอส", "AIS"]},
    "PTT.BK": {"thai_name": "ปตท.", "aliases": ["PTT", "ปตท", "พลังงาน", "น้ำมัน", "ก๊าซ"]},
    "PTTEP.BK": {"aliases": ["PTTEP", "ปตท.สผ.", "ปตทสผ", "สำรวจและผลิตปิโตรเลียม"]},
    "CPALL.BK": {"aliases": ["CPALL", "ซีพีออลล์", "เซเว่น", "7-Eleven"]},
    "SCC.BK": {"aliases": ["SCC", "ปูนซิเมนต์ไทย", "ปูนใหญ่", "เอสซีจี"]},
    "BDMS.BK": {"aliases": ["BDMS", "กรุงเทพดุสิตเวชการ", "โรงพยาบาลกรุงเทพ"]},
    "BH.BK": {"aliases": ["BH", "บำรุงราษฎร์", "โรงพยาบาลบำรุงราษฎร์"]},
    "GLD": {"aliases": ["Gold", "ทอง", "ทองคำ"]},
    "GC=F": {"aliases": ["Gold", "ทอง", "ทองคำ"]},
    "SLV": {"aliases": ["Silver", "เงิน", "โลหะเงิน"]},
    "SI=F": {"aliases": ["Silver", "เงิน", "โลหะเงิน"]},
    "CL=F": {"aliases": ["Oil", "WTI", "น้ำมัน"]},
    "BZ=F": {"aliases": ["Oil", "Brent", "น้ำมัน"]},
}


@dataclass(frozen=True)
class MasterAsset:
    canonical_symbol: str
    display_symbol: str
    company_name: str
    thai_name: str
    aliases: List[str]
    asset_class: str
    asset_type: str
    exchange: str
    market: str
    country: str
    currency: str
    sector: str
    industry: str
    provider_symbols: Dict[str, str]
    enabled: bool
    searchable: bool
    coverage_source: str
    coverage_timestamp: str | None
    live_data_capability: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return {**asdict(self), **self._profile_fields()}

    def to_search_asset(self) -> Dict[str, Any]:
        aliases = " ".join(self.aliases)
        coverage_status = _capability_status(self.live_data_capability)
        return {
            "symbol": self.canonical_symbol,
            "canonical_symbol": self.canonical_symbol,
            "display_symbol": self.display_symbol,
            "label": self.company_name,
            "company_name": self.company_name,
            "thai_name": self.thai_name,
            "asset_class": self.asset_class,
            "asset_type": self.asset_type,
            "market": self.market,
            "exchange": self.exchange,
            "sector": self.sector,
            "industry": self.industry,
            "country": self.country,
            "currency": self.currency,
            "keywords": aliases,
            "alias": aliases,
            "aliases": self.aliases,
            "enabled": self.enabled,
            "searchable": self.searchable,
            "provider_symbols": self.provider_symbols,
            "data_capabilities": self.live_data_capability,
            "live_data_capability": self.live_data_capability,
            "quote_capability": self.live_data_capability.get("quote", "provider_dependent"),
            "history_capability": self.live_data_capability.get("history", "provider_dependent"),
            "fundamentals_capability": self.live_data_capability.get("fundamentals", "provider_dependent"),
            "news_capability": self.live_data_capability.get("news", "provider_dependent"),
            "coverage_source": self.coverage_source,
            "coverage_status": coverage_status,
            **self._profile_fields(),
        }

    def _profile_fields(self) -> Dict[str, Any]:
        return {
            "company_name_en": self.company_name,
            "company_name_th": self.thai_name,
            "short_name_en": _short_english_name(self.company_name),
            "short_name_th": _short_thai_name(self.thai_name),
            "security_type": self.asset_type,
        }


@lru_cache(maxsize=1)
def load_master_asset_registry() -> Dict[str, Any]:
    seed_assets = [_from_exchange_asset(asset) for asset in list_assets(enabled_only=False)]
    imported_assets = _read_verified_us_source()
    thai_assets = _read_verified_thai_source()
    merged = _merge_assets([*seed_assets, *imported_assets, *thai_assets])
    validation = validate_master_asset_registry(merged)
    exchange_metadata = exchange_master_metadata()
    thai_metadata = _read_thai_source_metadata()
    sources = [
        {"name": "exchange_master_seed", "path": "configs/exchange_master.json", "record_count": len(seed_assets)},
        {
            "name": "verified_us_listed_offline_csv",
            "path": str(US_LISTED_SOURCE.relative_to(PROJECT_DIR)).replace("\\", "/"),
            "record_count": len(imported_assets),
        },
        {
            "name": "verified_set_public_listing_csv",
            "path": str(THAI_LISTED_SOURCE.relative_to(PROJECT_DIR)).replace("\\", "/"),
            "record_count": len(thai_assets),
            "source_url": thai_metadata.get("source"),
        },
    ]
    metadata = {
        "version": "master-registry-v1",
        "source": "master_asset_registry",
        "coverage_status": "partial_verified_registry",
        "search_coverage": "partial_verified_us_set_mai_global_registry",
        "live_data_coverage": "provider_dependent_partial",
        "record_count": len(merged),
        "count": len(merged),
        "searchable_count": len([asset for asset in merged if asset.searchable and asset.enabled]),
        "supported_exchanges": sorted({asset.exchange for asset in merged if asset.exchange}),
        "sources": sources,
        "fetched_at": None,
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "validation": validation,
        "limitations": [
            "This registry separates searchable securities from downstream live-data coverage.",
            "US coverage is an offline verified partial master for launch validation, not a complete licensed exchange feed.",
            "Thai coverage is sourced from SET public listing data for supported SET/mai security types.",
            "Live quote, fundamentals, news, and portfolio support remain provider dependent per symbol.",
            *exchange_metadata.get("limitations", []),
            *thai_metadata.get("limitations", []),
        ],
    }
    return {"assets": merged, "metadata": metadata}


def list_registry_assets(enabled_only: bool = True, searchable_only: bool = False) -> List[MasterAsset]:
    assets: List[MasterAsset] = load_master_asset_registry()["assets"]
    return [
        asset
        for asset in assets
        if (asset.enabled or not enabled_only) and (asset.searchable or not searchable_only)
    ]


def get_registry_asset(symbol: str) -> MasterAsset | None:
    target = _normalize_symbol(symbol)
    return next((asset for asset in list_registry_assets(False) if _normalize_symbol(asset.canonical_symbol) == target), None)


def master_asset_registry_metadata() -> Dict[str, Any]:
    return dict(load_master_asset_registry()["metadata"])


def validate_master_asset_registry(assets: List[MasterAsset] | None = None) -> Dict[str, Any]:
    assets = assets or list_registry_assets(enabled_only=False)
    seen: set[str] = set()
    provider_seen: dict[str, str] = {}
    duplicates: list[str] = []
    duplicate_provider_symbols: list[str] = []
    malformed: list[str] = []
    invalid_thai_mapping: list[str] = []
    invalid_exchange: list[str] = []
    invalid_currency: list[str] = []
    invalid_asset_class: list[str] = []
    searchable_without_symbol: list[str] = []
    broken_thai: list[str] = []
    for asset in assets:
        symbol = asset.canonical_symbol
        if symbol in seen:
            duplicates.append(symbol)
        seen.add(symbol)
        if not symbol or not asset.company_name or not asset.exchange or not asset.provider_symbols.get("yfinance"):
            malformed.append(symbol or "<missing>")
        if asset.searchable and not symbol:
            searchable_without_symbol.append(symbol or "<missing>")
        provider_symbol = asset.provider_symbols.get("yfinance")
        if provider_symbol:
            provider_key = provider_symbol.upper()
            previous = provider_seen.get(provider_key)
            if previous and previous != symbol:
                duplicate_provider_symbols.append(f"{provider_symbol}:{previous}/{symbol}")
            provider_seen[provider_key] = symbol
        if asset.country == "Thailand" and asset.exchange in {"SET", "mai"}:
            if not symbol.endswith(".BK") or asset.provider_symbols.get("yfinance") != symbol:
                invalid_thai_mapping.append(symbol)
            if asset.currency != "THB":
                invalid_currency.append(symbol)
        if asset.country == "Thailand" and asset.exchange not in {"SET", "mai"}:
            invalid_exchange.append(symbol)
        if asset.asset_type in {"stock", "foreign_stock", "preferred_stock", "adr"} and asset.asset_class != "equity":
            invalid_asset_class.append(symbol)
        if asset.asset_type in {"etf", "fund", "reit", "property_fund", "infrastructure_fund", "bond_etf", "sector_etf"} and asset.asset_class not in {"fund", "equity"}:
            invalid_asset_class.append(symbol)
        thai_values = [asset.thai_name, *[alias for alias in asset.aliases if _has_thai(alias) or _looks_mojibaked(alias)]]
        if any(_looks_mojibaked(value) for value in thai_values):
            broken_thai.append(symbol)
    return {
        "valid": not duplicates
        and not duplicate_provider_symbols
        and not malformed
        and not invalid_thai_mapping
        and not invalid_exchange
        and not invalid_currency
        and not invalid_asset_class
        and not searchable_without_symbol
        and not broken_thai,
        "duplicates": sorted(duplicates),
        "duplicate_provider_symbols": sorted(set(duplicate_provider_symbols)),
        "malformed": sorted(malformed),
        "invalid_thai_mapping": sorted(invalid_thai_mapping),
        "invalid_exchange": sorted(set(invalid_exchange)),
        "invalid_currency": sorted(set(invalid_currency)),
        "invalid_asset_class": sorted(set(invalid_asset_class)),
        "searchable_without_symbol": sorted(set(searchable_without_symbol)),
        "broken_thai": sorted(set(broken_thai)),
        "record_count": len(assets),
    }


def search_registry(
    query: str,
    *,
    asset_class: str | None = None,
    exchange: str | None = None,
    country: str | None = None,
    sector: str | None = None,
    industry: str | None = None,
    limit: int = 25,
) -> Dict[str, Any]:
    safe_limit = max(1, min(int(limit or 25), 100))
    term = str(query or "").strip()
    normalized_term = _normalize_text(term)
    filtered = [
        asset
        for asset in list_registry_assets(enabled_only=True, searchable_only=True)
        if _filter_match(asset, asset_class, exchange, country, sector, industry)
    ]
    if not normalized_term:
        matches = sorted(filtered, key=lambda asset: (asset.market, asset.exchange, asset.canonical_symbol))[:safe_limit]
    else:
        scored = [(score, asset) for asset in filtered for score in [_score_asset(normalized_term, asset)] if score > 0]
        matches = [
            asset
            for _, asset in sorted(scored, key=lambda item: (-item[0], _asset_rank_priority(item[1]), item[1].canonical_symbol))[:safe_limit]
        ]
    metadata = master_asset_registry_metadata()
    return {
        "query": query,
        "count": len(matches),
        "assets": [asset.to_search_asset() for asset in matches],
        "source": metadata["source"],
        "registry": metadata,
        "exchange_master": metadata,
    }


def _from_exchange_asset(asset: ExchangeAsset) -> MasterAsset:
    override = THAI_ALIAS_OVERRIDES.get(asset.canonical_symbol, {})
    aliases = _unique([*asset.aliases, *list(override.get("aliases", []))])
    capabilities = dict(asset.data_capabilities)
    return MasterAsset(
        canonical_symbol=asset.canonical_symbol,
        display_symbol=asset.display_symbol,
        company_name=asset.company_name,
        thai_name=str(override.get("thai_name") or asset.thai_name or ""),
        aliases=aliases,
        asset_class=asset.asset_class,
        asset_type=asset.asset_type,
        exchange=asset.exchange,
        market=asset.market,
        country=asset.country,
        currency=asset.currency,
        sector=asset.sector,
        industry=asset.industry,
        provider_symbols=asset.provider_symbols,
        enabled=asset.enabled,
        searchable=asset.enabled,
        coverage_source="exchange_master_seed",
        coverage_timestamp=None,
        live_data_capability=capabilities,
    )


def _read_verified_us_source() -> List[MasterAsset]:
    if not US_LISTED_SOURCE.exists():
        return []
    assets: list[MasterAsset] = []
    with US_LISTED_SOURCE.open("r", encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)
        for row in reader:
            symbol = _normalize_symbol(row.get("symbol", ""))
            if not symbol:
                continue
            asset_type = str(row.get("asset_type") or "stock").strip()
            capabilities = dict(CAPABILITY_DEFAULTS)
            if asset_type in {"crypto", "commodity", "fx", "macro", "index"}:
                capabilities["fundamentals"] = "not_applicable"
            elif asset_type in {"etf", "sector_etf", "bond_etf", "reit", "adr"}:
                capabilities["fundamentals"] = "partial"
            aliases = _unique([symbol, symbol.replace(".BK", ""), row.get("label", ""), *_split_aliases(row.get("aliases"))])
            assets.append(
                MasterAsset(
                    canonical_symbol=symbol,
                    display_symbol=str(row.get("display_symbol") or symbol.replace(".BK", "")).strip(),
                    company_name=str(row.get("label") or symbol).strip(),
                    thai_name=str(row.get("thai_name") or "").strip(),
                    aliases=aliases,
                    asset_class=ASSET_CLASS_MAP.get(asset_type, "equity" if asset_type in {"stock", "adr"} else asset_type),
                    asset_type=asset_type,
                    exchange=str(row.get("exchange") or "").strip(),
                    market=str(row.get("market") or "").strip(),
                    country=str(row.get("country") or "").strip(),
                    currency=str(row.get("currency") or "").strip(),
                    sector=str(row.get("sector") or "").strip(),
                    industry=str(row.get("industry") or "").strip(),
                    provider_symbols={"yfinance": str(row.get("yfinance_symbol") or symbol).strip()},
                    enabled=str(row.get("enabled") or "true").strip().lower() not in {"0", "false", "no"},
                    searchable=True,
                    coverage_source="verified_us_listed_offline_csv",
                    coverage_timestamp=None,
                    live_data_capability=capabilities,
                )
            )
    return assets


def _read_verified_thai_source() -> List[MasterAsset]:
    if not THAI_LISTED_SOURCE.exists():
        return []
    assets: list[MasterAsset] = []
    with THAI_LISTED_SOURCE.open("r", encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)
        for row in reader:
            symbol = _normalize_symbol(row.get("symbol", ""))
            if not symbol:
                continue
            asset_type = str(row.get("asset_type") or "stock").strip()
            capabilities = dict(CAPABILITY_DEFAULTS)
            if asset_type in {"etf", "fund", "reit", "property_fund", "infrastructure_fund"}:
                capabilities["fundamentals"] = "partial"
            aliases = _unique([
                symbol,
                symbol.replace(".BK", ""),
                row.get("display_symbol", ""),
                row.get("label", ""),
                row.get("thai_name", ""),
                *_split_aliases(row.get("aliases")),
                *list(THAI_ALIAS_OVERRIDES.get(symbol, {}).get("aliases", [])),
            ])
            if asset_type in {"foreign_stock", "preferred_stock"}:
                aliases = _non_primary_share_aliases(aliases, symbol)
            override = THAI_ALIAS_OVERRIDES.get(symbol, {})
            assets.append(
                MasterAsset(
                    canonical_symbol=symbol,
                    display_symbol=str(row.get("display_symbol") or symbol.replace(".BK", "")).strip(),
                    company_name=str(row.get("label") or symbol).strip(),
                    thai_name=str(override.get("thai_name") or row.get("thai_name") or "").strip(),
                    aliases=aliases,
                    asset_class=ASSET_CLASS_MAP.get(asset_type, "fund" if "fund" in asset_type else "equity"),
                    asset_type=asset_type,
                    exchange=str(row.get("exchange") or "SET").strip(),
                    market=str(row.get("market") or "Thailand").strip(),
                    country=str(row.get("country") or "Thailand").strip(),
                    currency=str(row.get("currency") or "THB").strip(),
                    sector=str(row.get("sector") or "Unclassified").strip(),
                    industry=str(row.get("industry") or "Unclassified").strip(),
                    provider_symbols={"yfinance": str(row.get("yfinance_symbol") or symbol).strip()},
                    enabled=str(row.get("enabled") or "true").strip().lower() not in {"0", "false", "no"},
                    searchable=str(row.get("searchable") or "true").strip().lower() not in {"0", "false", "no"},
                    coverage_source="verified_set_public_listing_csv",
                    coverage_timestamp=None,
                    live_data_capability=capabilities,
                )
            )
    return assets


def _read_thai_source_metadata() -> Dict[str, Any]:
    if not THAI_LISTED_METADATA.exists():
        return {}
    try:
        return json.loads(THAI_LISTED_METADATA.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def _merge_assets(assets: Iterable[MasterAsset]) -> List[MasterAsset]:
    merged: Dict[str, MasterAsset] = {}
    for asset in assets:
        existing = merged.get(asset.canonical_symbol)
        if not existing:
            merged[asset.canonical_symbol] = asset
            continue
        aliases = _unique([*existing.aliases, *asset.aliases])
        capabilities = dict(existing.live_data_capability)
        capabilities.update(asset.live_data_capability)
        prefer_new = asset.coverage_source == "verified_set_public_listing_csv"
        primary = asset if prefer_new else existing
        secondary = existing if prefer_new else asset
        merged[asset.canonical_symbol] = MasterAsset(
            canonical_symbol=existing.canonical_symbol,
            display_symbol=primary.display_symbol or secondary.display_symbol,
            company_name=primary.company_name or secondary.company_name,
            thai_name=primary.thai_name or secondary.thai_name,
            aliases=aliases,
            asset_class=primary.asset_class or secondary.asset_class,
            asset_type=primary.asset_type or secondary.asset_type,
            exchange=primary.exchange or secondary.exchange,
            market=primary.market or secondary.market,
            country=primary.country or secondary.country,
            currency=primary.currency or secondary.currency,
            sector=primary.sector or secondary.sector,
            industry=primary.industry or secondary.industry,
            provider_symbols={**asset.provider_symbols, **existing.provider_symbols},
            enabled=existing.enabled or asset.enabled,
            searchable=existing.searchable or asset.searchable,
            coverage_source=f"{existing.coverage_source}+{asset.coverage_source}",
            coverage_timestamp=existing.coverage_timestamp or asset.coverage_timestamp,
            live_data_capability=capabilities,
        )
    return sorted(merged.values(), key=lambda asset: asset.canonical_symbol)


def _score_asset(term: str, asset: MasterAsset) -> int:
    symbol = _normalize_text(asset.canonical_symbol)
    display = _normalize_text(asset.display_symbol)
    company = _normalize_text(asset.company_name)
    thai = _normalize_text(asset.thai_name)
    aliases = [_normalize_text(alias) for alias in asset.aliases]
    curated_aliases = [_normalize_text(alias) for alias in THAI_ALIAS_OVERRIDES.get(asset.canonical_symbol, {}).get("aliases", [])]
    metadata = [_normalize_text(value) for value in [asset.exchange, asset.market, asset.sector, asset.industry, asset.country, asset.currency]]
    candidates = [symbol, display, company, thai, *aliases, *metadata]
    if term == symbol or term == display:
        return 1000
    if symbol.startswith(term) or display.startswith(term):
        return 900 - min(len(symbol), 20)
    if term in curated_aliases:
        return 875
    if term == thai:
        return 860
    if any(candidate == term for candidate in [company, *aliases]):
        return 820
    if company.startswith(term) or thai.startswith(term):
        return 760
    if any(candidate.startswith(term) for candidate in aliases):
        return 720
    if term in company or term in thai or any(term in alias for alias in aliases):
        return 640
    best_ratio = max((SequenceMatcher(None, term, candidate).ratio() for candidate in candidates if candidate), default=0)
    if best_ratio >= 0.74:
        return int(450 + best_ratio * 100)
    return 0


def _asset_rank_priority(asset: MasterAsset) -> int:
    if asset.country == "Thailand":
        if asset.asset_type == "stock" and "-" not in asset.display_symbol:
            return 0
        if asset.asset_type in {"foreign_stock", "preferred_stock"}:
            return 4
        if asset.asset_class == "fund":
            return 2
    return 1


def _filter_match(
    asset: MasterAsset,
    asset_class: str | None,
    exchange: str | None,
    country: str | None,
    sector: str | None,
    industry: str | None,
) -> bool:
    filters = [
        (asset.asset_class, asset_class),
        (asset.asset_type, asset_class),
        (asset.exchange, exchange),
        (asset.country, country),
        (asset.sector, sector),
        (asset.industry, industry),
    ]
    for value, expected in filters:
        if expected and _normalize_text(value) != _normalize_text(expected):
            return False
    return True


def _capability_status(capabilities: Dict[str, Any]) -> str:
    values = {str(value) for value in capabilities.values()}
    if "unavailable" in values:
        return "partial"
    if "partial" in values or "provider_not_configured" in values:
        return "partial"
    if values and values <= {"True", "true"}:
        return "available"
    return "partial"


def _normalize_symbol(value: str) -> str:
    return str(value or "").strip().upper()


def _normalize_text(value: str) -> str:
    text = unicodedata.normalize("NFKC", str(value or "")).casefold()
    text = re.sub(r"[\s\-.()/,']", "", text)
    text = text.replace("ฯ", "").replace("ๆ", "")
    return text


def _has_thai(value: str) -> bool:
    return any("\u0e00" <= char <= "\u0e7f" for char in str(value or ""))


def _looks_mojibaked(value: str) -> bool:
    text = str(value or "")
    return any(marker in text for marker in ["à¸", "à¹", "Â", "Ã"])


def _split_aliases(value: Any) -> List[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    return [part.strip() for part in str(value).split("|") if part.strip()]


def _unique(values: Iterable[str]) -> List[str]:
    output: list[str] = []
    seen: set[str] = set()
    for value in values:
        normalized = str(value or "").strip()
        if _looks_mojibaked(normalized) or _is_low_quality_alias(normalized):
            continue
        key = normalized.casefold()
        if normalized and key not in seen:
            output.append(normalized)
            seen.add(key)
    return output


def _is_low_quality_alias(value: str) -> bool:
    normalized = _normalize_text(value)
    return normalized in {
        "บริษัท",
        "จำกัด",
        "มหาชน",
        "บริษัทจำกัดมหาชน",
        "ธนาคาร",
        "กองทุนรวม",
        "กองทรัสต์",
        "public",
        "company",
        "limited",
        "the",
    }


def _non_primary_share_aliases(aliases: Iterable[str], symbol: str) -> List[str]:
    display = symbol.replace(".BK", "")
    ordinary = display.replace("-F", "").replace("-P", "").replace("-Q", "")
    blocked = {_normalize_text(ordinary)}
    return [alias for alias in aliases if _normalize_text(alias) not in blocked]


def _short_english_name(value: str) -> str:
    cleaned = re.sub(r"\b(PUBLIC|COMPANY|LIMITED|PCL|PLC|THE)\b", " ", str(value or ""), flags=re.IGNORECASE)
    return re.sub(r"\s+", " ", cleaned).strip() or str(value or "").strip()


def _short_thai_name(value: str) -> str:
    cleaned = str(value or "")
    for token in ["บริษัท", "ธนาคาร", "จำกัด", "(มหาชน)", "มหาชน", "กองทุนรวม", "กองทรัสต์"]:
        cleaned = cleaned.replace(token, " ")
    return re.sub(r"\s+", "", cleaned).strip() or str(value or "").strip()
