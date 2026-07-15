from __future__ import annotations

import csv
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from difflib import SequenceMatcher
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, Iterable, List

from app.data_hub.exchange_master import ASSET_CLASS_MAP, CAPABILITY_DEFAULTS, ExchangeAsset, exchange_master_metadata, list_assets

PROJECT_DIR = Path(__file__).resolve().parents[3]
US_LISTED_SOURCE = PROJECT_DIR / "data" / "exchange_sources" / "us_listed_verified.csv"

THAI_ALIAS_OVERRIDES: Dict[str, Dict[str, Any]] = {
    "TTB.BK": {
        "thai_name": "ทีเอ็มบีธนชาต",
        "aliases": ["TTB", "ทีทีบี", "ทหารไทยธนชาต", "ธนาคารทหารไทยธนชาต"],
    },
    "KBANK.BK": {
        "thai_name": "กสิกรไทย",
        "aliases": ["KBANK", "กสิกร", "ธนาคารกสิกรไทย"],
    },
    "AOT.BK": {
        "thai_name": "ท่าอากาศยานไทย",
        "aliases": ["AOT", "สนามบิน", "ท่าอากาศยานไทย"],
    },
    "PTT.BK": {
        "thai_name": "ปตท.",
        "aliases": ["PTT", "ปตท", "พลังงาน", "น้ำมัน", "ก๊าซ"],
    },
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
        return asdict(self)

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
            "coverage_source": self.coverage_source,
            "coverage_status": coverage_status,
        }


@lru_cache(maxsize=1)
def load_master_asset_registry() -> Dict[str, Any]:
    seed_assets = [_from_exchange_asset(asset) for asset in list_assets(enabled_only=False)]
    imported_assets = _read_verified_us_source()
    merged = _merge_assets([*seed_assets, *imported_assets])
    validation = validate_master_asset_registry(merged)
    exchange_metadata = exchange_master_metadata()
    sources = [
        {"name": "exchange_master_seed", "path": "configs/exchange_master.json", "record_count": len(seed_assets)},
        {
            "name": "verified_us_listed_offline_csv",
            "path": str(US_LISTED_SOURCE.relative_to(PROJECT_DIR)).replace("\\", "/"),
            "record_count": len(imported_assets),
        },
    ]
    metadata = {
        "version": "master-registry-v1",
        "source": "master_asset_registry",
        "coverage_status": "partial_verified_registry",
        "search_coverage": "partial_verified_us_thai_global_registry",
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
            "Live quote, fundamentals, news, and portfolio support remain provider dependent per symbol.",
            *exchange_metadata.get("limitations", []),
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
    duplicates: list[str] = []
    malformed: list[str] = []
    for asset in assets:
        symbol = asset.canonical_symbol
        if symbol in seen:
            duplicates.append(symbol)
        seen.add(symbol)
        if not symbol or not asset.company_name or not asset.exchange or not asset.provider_symbols.get("yfinance"):
            malformed.append(symbol or "<missing>")
    return {
        "valid": not duplicates and not malformed,
        "duplicates": sorted(duplicates),
        "malformed": sorted(malformed),
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
        matches = [asset for _, asset in sorted(scored, key=lambda item: (-item[0], item[1].canonical_symbol))[:safe_limit]]
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
        merged[asset.canonical_symbol] = MasterAsset(
            canonical_symbol=existing.canonical_symbol,
            display_symbol=existing.display_symbol or asset.display_symbol,
            company_name=existing.company_name if existing.coverage_source == "exchange_master_seed" else asset.company_name,
            thai_name=existing.thai_name or asset.thai_name,
            aliases=aliases,
            asset_class=existing.asset_class or asset.asset_class,
            asset_type=existing.asset_type or asset.asset_type,
            exchange=existing.exchange or asset.exchange,
            market=existing.market or asset.market,
            country=existing.country or asset.country,
            currency=existing.currency or asset.currency,
            sector=existing.sector or asset.sector,
            industry=existing.industry or asset.industry,
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
    metadata = [_normalize_text(value) for value in [asset.exchange, asset.market, asset.sector, asset.industry, asset.country, asset.currency]]
    candidates = [symbol, display, company, thai, *aliases, *metadata]
    if term == symbol or term == display:
        return 1000
    if symbol.startswith(term) or display.startswith(term):
        return 900 - min(len(symbol), 20)
    if any(candidate == term for candidate in [company, thai, *aliases]):
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
    return str(value or "").strip().casefold().replace(" ", "").replace("-", "").replace(".", "")


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
        key = normalized.casefold()
        if normalized and key not in seen:
            output.append(normalized)
            seen.add(key)
    return output
