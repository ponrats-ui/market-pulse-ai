from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List

PROJECT_DIR = Path(__file__).resolve().parents[3]
EXCHANGE_MASTER_PATH = PROJECT_DIR / "configs" / "exchange_master.json"

ASSET_CLASS_MAP = {
    "stock": "equity",
    "foreign_stock": "equity",
    "preferred_stock": "equity",
    "etf": "fund",
    "sector_etf": "fund",
    "bond_etf": "fund",
    "reit": "fund",
    "fund": "fund",
    "property_fund": "fund",
    "infrastructure_fund": "fund",
    "crypto": "crypto",
    "commodity": "commodity",
    "fx": "fx",
    "macro": "macro",
    "index": "index",
}

CAPABILITY_DEFAULTS = {
    "quote": True,
    "history": True,
    "technicals": True,
    "fundamentals": "partial",
    "news": "partial",
    "calendar": "provider_not_configured",
    "risk": True,
    "comparison": True,
    "portfolio": True,
}

THAI_ALIAS_OVERRIDES = {
    "TTB.BK": {"thai_name": "ทีเอ็มบีธนชาต", "aliases": ["TTB", "ทีทีบี", "ทหารไทยธนชาต", "ธนาคารทหารไทยธนชาต"]},
    "KBANK.BK": {"thai_name": "กสิกรไทย", "aliases": ["KBANK", "กสิกร", "ธนาคารกสิกรไทย"]},
    "AOT.BK": {"thai_name": "ท่าอากาศยานไทย", "aliases": ["AOT", "สนามบิน", "ท่าอากาศยานไทย"]},
    "PTT.BK": {"thai_name": "ปตท.", "aliases": ["PTT", "ปตท", "พลังงาน", "น้ำมัน", "ก๊าซ"]},
    "PTTEP.BK": {"aliases": ["PTTEP", "ปตท.สผ.", "ปตทสผ", "สำรวจและผลิตปิโตรเลียม"]},
    "CPALL.BK": {"aliases": ["CPALL", "ซีพีออลล์", "เซเว่น", "7-Eleven"]},
    "SCC.BK": {"aliases": ["SCC", "ปูนซิเมนต์ไทย", "ปูนใหญ่", "เอสซีจี"]},
    "GC=F": {"aliases": ["Gold", "ทอง", "ทองคำ"]},
    "GLD": {"aliases": ["Gold", "ทอง", "ทองคำ"]},
    "SI=F": {"aliases": ["Silver", "เงิน", "โลหะเงิน"]},
    "SLV": {"aliases": ["Silver", "เงิน", "โลหะเงิน"]},
    "CL=F": {"aliases": ["Oil", "WTI", "น้ำมัน"]},
    "BZ=F": {"aliases": ["Oil", "Brent", "น้ำมัน"]},
}


@dataclass(frozen=True)
class ExchangeAsset:
    canonical_symbol: str
    provider_symbols: Dict[str, str]
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
    index_memberships: List[str]
    enabled: bool
    data_capabilities: Dict[str, Any]

    def to_search_asset(self) -> Dict[str, Any]:
        aliases = " ".join(self.aliases)
        return {
            "symbol": self.canonical_symbol,
            "label": self.company_name,
            "thai_name": self.thai_name,
            "asset_type": self.asset_type,
            "market": self.market,
            "exchange": self.exchange,
            "sector": self.sector,
            "industry": self.industry,
            "country": self.country,
            "currency": self.currency,
            "keywords": aliases,
            "alias": aliases,
            "enabled": self.enabled,
            "data_capabilities": self.data_capabilities,
        }

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@lru_cache(maxsize=1)
def load_exchange_master() -> Dict[str, Any]:
    with EXCHANGE_MASTER_PATH.open("r", encoding="utf-8") as file:
        payload = json.load(file)
    assets = [_normalize_asset(asset) for asset in payload.get("assets", [])]
    metadata = {
        "version": payload.get("version", "unknown"),
        "source": payload.get("source", "exchange_master"),
        "fetched_at": payload.get("fetched_at"),
        "constituent_date": payload.get("constituent_date"),
        "record_count": len(assets),
        "validation_status": payload.get("validation_status", "partial_seed_validated"),
        "coverage_status": payload.get("coverage_status", "partial"),
        "provider_ready": payload.get("provider_ready", False),
        "updated_at": payload.get("updated_at") or datetime.now(timezone.utc).isoformat(),
        "limitations": payload.get("limitations", []),
        "universe_policy": payload.get("universe_policy", {}),
        "supported_exchanges": payload.get("supported_exchanges", []),
    }
    return {**payload, "assets": assets, "metadata": metadata}


def list_assets(enabled_only: bool = True) -> List[ExchangeAsset]:
    assets = load_exchange_master().get("assets", [])
    return [asset for asset in assets if asset.enabled or not enabled_only]


def get_asset(canonical_symbol: str) -> ExchangeAsset | None:
    target = canonical_symbol.strip().upper()
    return next((asset for asset in list_assets(False) if asset.canonical_symbol.upper() == target), None)


def exchange_master_metadata() -> Dict[str, Any]:
    payload = load_exchange_master()
    metadata = dict(payload.get("metadata", {}))
    metadata["count"] = metadata.get("record_count", len(payload.get("assets", [])))
    return metadata


def validate_exchange_master() -> Dict[str, Any]:
    assets = list_assets(False)
    seen: set[str] = set()
    duplicates: list[str] = []
    malformed: list[str] = []
    for asset in assets:
        if asset.canonical_symbol in seen:
            duplicates.append(asset.canonical_symbol)
        seen.add(asset.canonical_symbol)
        if not asset.canonical_symbol or not asset.company_name or not asset.provider_symbols.get("yfinance"):
            malformed.append(asset.canonical_symbol or "<missing>")
    return {
        "valid": not duplicates and not malformed,
        "duplicates": duplicates,
        "malformed": malformed,
        "record_count": len(assets),
        "metadata": exchange_master_metadata(),
    }


def _normalize_asset(asset: Dict[str, Any]) -> ExchangeAsset:
    symbol = str(asset.get("canonical_symbol") or asset.get("symbol") or "").strip().upper()
    override = THAI_ALIAS_OVERRIDES.get(symbol, {})
    aliases = _list(asset.get("aliases")) + _list(asset.get("alias")) + _list(asset.get("keywords")) + _list(override.get("aliases"))
    provider_symbols = asset.get("provider_symbols") if isinstance(asset.get("provider_symbols"), dict) else {"yfinance": symbol}
    asset_type = str(asset.get("asset_type") or "unknown").strip()
    capabilities = dict(CAPABILITY_DEFAULTS)
    capabilities.update(asset.get("data_capabilities") if isinstance(asset.get("data_capabilities"), dict) else {})
    if asset_type in {"crypto", "commodity", "fx", "macro", "index"}:
        capabilities["fundamentals"] = "not_applicable"
    return ExchangeAsset(
        canonical_symbol=symbol,
        provider_symbols={str(k): str(v) for k, v in provider_symbols.items() if v},
        display_symbol=str(asset.get("display_symbol") or symbol.replace(".BK", "")).strip(),
        company_name=str(asset.get("company_name") or asset.get("label") or symbol).strip(),
        thai_name=str(override.get("thai_name") or asset.get("thai_name") or "").strip(),
        aliases=_unique([symbol, symbol.replace(".BK", ""), *aliases]),
        asset_class=str(asset.get("asset_class") or ASSET_CLASS_MAP.get(asset_type, asset_type)).strip(),
        asset_type=asset_type,
        exchange=str(asset.get("exchange") or asset.get("market") or "Unknown").strip(),
        market=str(asset.get("market") or asset.get("exchange") or "Unknown").strip(),
        country=str(asset.get("country") or "").strip(),
        currency=str(asset.get("currency") or "").strip(),
        sector=str(asset.get("sector") or "").strip(),
        industry=str(asset.get("industry") or "").strip(),
        index_memberships=_list(asset.get("index_memberships")),
        enabled=bool(asset.get("enabled", True)),
        data_capabilities=capabilities,
    )


def _list(value: Any) -> List[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    return [part.strip() for part in str(value).split("|") if part.strip()]


def _unique(values: List[str]) -> List[str]:
    seen: set[str] = set()
    output: list[str] = []
    for value in values:
        normalized = value.strip()
        key = normalized.lower()
        if normalized and key not in seen:
            output.append(normalized)
            seen.add(key)
    return output
