from __future__ import annotations

from typing import Any, Dict, List, Tuple

from app.services.exchange_master import exchange_master_assets, exchange_master_metadata


ASSET_UNIVERSE: List[Dict[str, str]] = [
    {"symbol": "AAPL", "label": "Apple", "asset_type": "stock", "market": "NASDAQ", "keywords": "iphone services technology"},
    {"symbol": "MSFT", "label": "Microsoft", "asset_type": "stock", "market": "NASDAQ", "keywords": "cloud ai software"},
    {"symbol": "NVDA", "label": "NVIDIA", "asset_type": "stock", "market": "NASDAQ", "keywords": "ai gpu semiconductor cuda"},
    {"symbol": "TSLA", "label": "Tesla", "asset_type": "stock", "market": "NASDAQ", "keywords": "ev battery autonomous"},
    {"symbol": "AMZN", "label": "Amazon", "asset_type": "stock", "market": "NASDAQ", "keywords": "aws ecommerce cloud"},
    {"symbol": "META", "label": "Meta Platforms", "asset_type": "stock", "market": "NASDAQ", "keywords": "facebook instagram ai ads"},
    {"symbol": "GOOG", "label": "Alphabet Class C", "asset_type": "stock", "market": "NASDAQ", "keywords": "google search cloud ai"},
    {"symbol": "GOOGL", "label": "Alphabet Class A", "asset_type": "stock", "market": "NASDAQ", "keywords": "google search cloud ai"},
    {"symbol": "AMD", "label": "Advanced Micro Devices", "asset_type": "stock", "market": "NASDAQ", "keywords": "semiconductor ai gpu chip"},
    {"symbol": "TSM", "label": "Taiwan Semiconductor Manufacturing", "asset_type": "stock", "market": "NYSE", "keywords": "semiconductor foundry tsmc ai chip"},
    {"symbol": "SPY", "label": "SPDR S&P 500 ETF", "asset_type": "etf", "market": "NYSE Arca", "keywords": "s&p 500 etf"},
    {"symbol": "VOO", "label": "Vanguard S&P 500 ETF", "asset_type": "etf", "market": "NYSE Arca", "keywords": "s&p 500 etf"},
    {"symbol": "QQQ", "label": "Invesco QQQ ETF", "asset_type": "etf", "market": "NASDAQ", "keywords": "nasdaq 100 etf technology"},
    {"symbol": "VTI", "label": "Vanguard Total Stock Market ETF", "asset_type": "etf", "market": "NYSE Arca", "keywords": "total stock market etf"},
    {"symbol": "GLD", "label": "SPDR Gold Shares", "asset_type": "etf", "market": "NYSE Arca", "keywords": "gold etf precious metals"},
    {"symbol": "SLV", "label": "iShares Silver Trust", "asset_type": "etf", "market": "NYSE Arca", "keywords": "silver etf precious metals"},
    {"symbol": "TLT", "label": "iShares 20+ Year Treasury Bond ETF", "asset_type": "bond_etf", "market": "NASDAQ", "keywords": "bond etf treasury duration rates"},
    {"symbol": "VNQ", "label": "Vanguard Real Estate ETF", "asset_type": "reit", "market": "NYSE Arca", "keywords": "reit real estate dividend property"},
    {"symbol": "SOXX", "label": "iShares Semiconductor ETF", "asset_type": "etf", "market": "NASDAQ", "keywords": "semiconductor etf ai chips"},
    {"symbol": "BTC-USD", "label": "Bitcoin", "asset_type": "crypto", "market": "Crypto", "keywords": "btc bitcoin crypto"},
    {"symbol": "ETH-USD", "label": "Ethereum", "asset_type": "crypto", "market": "Crypto", "keywords": "eth ethereum crypto"},
    {"symbol": "SOL-USD", "label": "Solana", "asset_type": "crypto", "market": "Crypto", "keywords": "sol solana crypto"},
    {"symbol": "XRP-USD", "label": "XRP", "asset_type": "crypto", "market": "Crypto", "keywords": "ripple xrp crypto"},
    {"symbol": "^SET.BK", "label": "SET Index", "asset_type": "index", "market": "Thailand", "keywords": "set thailand index"},
    {"symbol": "^SET50.BK", "label": "SET50 Index", "asset_type": "index", "market": "Thailand", "keywords": "set50 thailand index"},
    {"symbol": "PTT.BK", "label": "PTT", "thai_name": "ปตท.", "asset_type": "stock", "market": "SET", "keywords": "energy oil gas thailand พลังงาน"},
    {"symbol": "AOT.BK", "label": "Airports of Thailand", "thai_name": "ท่าอากาศยานไทย", "asset_type": "stock", "market": "SET", "keywords": "airport tourism thailand สนามบิน"},
    {"symbol": "SCB.BK", "label": "SCB X", "thai_name": "เอสซีบี เอกซ์", "asset_type": "stock", "market": "SET", "keywords": "bank thailand scb ธนาคาร"},
    {"symbol": "KBANK.BK", "label": "Kasikornbank", "thai_name": "กสิกรไทย", "asset_type": "stock", "market": "SET", "keywords": "bank thailand kbank ธนาคาร"},
    {"symbol": "ADVANC.BK", "label": "Advanced Info Service", "thai_name": "แอดวานซ์ อินโฟร์ เซอร์วิส", "asset_type": "stock", "market": "SET", "keywords": "telecom mobile thailand ais สื่อสาร"},
    {"symbol": "CPALL.BK", "label": "CP All", "asset_type": "stock", "market": "SET", "keywords": "retail 7-eleven thailand"},
    {"symbol": "DELTA.BK", "label": "Delta Electronics Thailand", "asset_type": "stock", "market": "SET", "keywords": "electronics thailand"},
    {"symbol": "GC=F", "label": "Gold Futures", "asset_type": "commodity", "market": "COMEX", "keywords": "gold precious metals"},
    {"symbol": "SI=F", "label": "Silver Futures", "asset_type": "commodity", "market": "COMEX", "keywords": "silver precious metals"},
    {"symbol": "CL=F", "label": "WTI Crude Oil", "asset_type": "commodity", "market": "NYMEX", "keywords": "oil crude wti energy"},
    {"symbol": "BZ=F", "label": "Brent Crude Oil", "asset_type": "commodity", "market": "ICE", "keywords": "oil crude brent energy"},
    {"symbol": "NG=F", "label": "Natural Gas", "asset_type": "commodity", "market": "NYMEX", "keywords": "natural gas energy"},
    {"symbol": "HG=F", "label": "Copper Futures", "asset_type": "commodity", "market": "COMEX", "keywords": "copper industrial metals"},
    {"symbol": "USDTHB=X", "label": "USD/THB", "asset_type": "fx", "market": "FX", "keywords": "dollar baht forex"},
    {"symbol": "DX-Y.NYB", "label": "US Dollar Index", "asset_type": "fx", "market": "ICE", "keywords": "dxy dollar index"},
    {"symbol": "^TNX", "label": "US 10Y Treasury Yield", "asset_type": "macro", "market": "Bond Yield", "keywords": "us10y treasury yield rates"},
    {"symbol": "^GSPC", "label": "S&P 500", "asset_type": "index", "market": "US", "keywords": "s&p 500 index"},
    {"symbol": "^IXIC", "label": "Nasdaq Composite", "asset_type": "index", "market": "US", "keywords": "nasdaq index technology"},
    {"symbol": "^DJI", "label": "Dow Jones", "asset_type": "index", "market": "US", "keywords": "dow jones index"},
    {"symbol": "^N225", "label": "Nikkei 225", "asset_type": "index", "market": "Japan", "keywords": "nikkei japan index"},
    {"symbol": "^HSI", "label": "Hang Seng", "asset_type": "index", "market": "Hong Kong", "keywords": "hang seng hong kong index"},
    {"symbol": "^GDAXI", "label": "DAX", "asset_type": "index", "market": "Germany", "keywords": "dax germany index"},
]


THAI_NAME_ALIASES = {
    "PTT.BK": "ปตท. พลังงาน น้ำมัน ก๊าซ",
    "AOT.BK": "ท่าอากาศยานไทย สนามบิน ท่องเที่ยว",
    "SCB.BK": "เอสซีบี เอกซ์ ธนาคาร",
    "KBANK.BK": "กสิกรไทย ธนาคาร",
    "ADVANC.BK": "แอดวานซ์ อินโฟร์ เซอร์วิส เอไอเอส สื่อสาร",
    "GC=F": "ทอง ทองคำ",
    "GLD": "ทอง ทองคำ",
    "SI=F": "เงิน โลหะเงิน",
    "CL=F": "น้ำมัน ดิบ พลังงาน",
    "BZ=F": "น้ำมัน เบรนท์ พลังงาน",
}

LEGACY_THAI_QUERY_ALIASES = {
    "กสิกร": "กสิกร",
    "ทอง": "ทอง",
    "น้ำมัน": "น้ำมัน",
}

SECTOR_MAP = {
    "Technology": ["AAPL", "MSFT", "GOOG", "GOOGL", "META", "QQQ", "SPY", "VOO"],
    "Semiconductor": ["NVDA", "AMD", "TSM", "SOXX"],
    "AI": ["NVDA", "MSFT", "GOOG", "GOOGL", "META", "AMD", "TSM", "SOXX"],
    "Cloud": ["MSFT", "AMZN", "GOOG", "GOOGL"],
    "Cybersecurity": ["QQQ"],
    "Banking": ["SCB.BK", "KBANK.BK"],
    "Insurance": [],
    "Energy": ["PTT.BK", "CL=F", "BZ=F", "NG=F"],
    "Utilities": [],
    "Healthcare": [],
    "Biotech": [],
    "Consumer": ["AMZN", "TSLA", "CPALL.BK"],
    "Industrial": ["AOT.BK", "DELTA.BK"],
    "Defense": [],
    "Real Estate": ["VNQ"],
    "REIT": ["VNQ"],
    "ETF": ["SPY", "VOO", "QQQ", "VTI", "GLD", "SLV", "TLT", "VNQ", "SOXX"],
    "Crypto Layer1": ["BTC-USD", "ETH-USD", "SOL-USD", "XRP-USD"],
    "Crypto Infrastructure": ["ETH-USD", "SOL-USD"],
    "Gold": ["GC=F", "GLD"],
    "Oil": ["CL=F", "BZ=F", "PTT.BK"],
}

ASSET_METADATA = {
    "AAPL": {"sector": "Technology", "industry": "Consumer Electronics", "country": "US", "currency": "USD", "exchange": "NASDAQ"},
    "MSFT": {"sector": "Technology", "industry": "Software Infrastructure", "country": "US", "currency": "USD", "exchange": "NASDAQ"},
    "NVDA": {"sector": "Semiconductor", "industry": "AI Accelerators", "country": "US", "currency": "USD", "exchange": "NASDAQ"},
    "AMD": {"sector": "Semiconductor", "industry": "Semiconductors", "country": "US", "currency": "USD", "exchange": "NASDAQ"},
    "TSM": {"sector": "Semiconductor", "industry": "Foundry", "country": "Taiwan", "currency": "USD", "exchange": "NYSE"},
    "PTT.BK": {"sector": "Energy", "industry": "Integrated Oil and Gas", "country": "Thailand", "currency": "THB", "exchange": "SET"},
    "AOT.BK": {"sector": "Industrial", "industry": "Airport Services", "country": "Thailand", "currency": "THB", "exchange": "SET"},
    "SCB.BK": {"sector": "Banking", "industry": "Financial Services", "country": "Thailand", "currency": "THB", "exchange": "SET"},
    "KBANK.BK": {"sector": "Banking", "industry": "Commercial Bank", "country": "Thailand", "currency": "THB", "exchange": "SET"},
    "ADVANC.BK": {"sector": "Technology", "industry": "Telecommunications", "country": "Thailand", "currency": "THB", "exchange": "SET"},
    "CPALL.BK": {"sector": "Consumer", "industry": "Retail", "country": "Thailand", "currency": "THB", "exchange": "SET"},
    "DELTA.BK": {"sector": "Industrial", "industry": "Electronics", "country": "Thailand", "currency": "THB", "exchange": "SET"},
    "BTC-USD": {"sector": "Crypto Layer1", "industry": "Digital Asset", "country": "Global", "currency": "USD", "exchange": "Crypto"},
    "ETH-USD": {"sector": "Crypto Infrastructure", "industry": "Smart Contract Platform", "country": "Global", "currency": "USD", "exchange": "Crypto"},
    "SOL-USD": {"sector": "Crypto Layer1", "industry": "Smart Contract Platform", "country": "Global", "currency": "USD", "exchange": "Crypto"},
    "QQQ": {"sector": "Technology", "industry": "ETF", "country": "US", "currency": "USD", "exchange": "NASDAQ"},
    "TLT": {"sector": "ETF", "industry": "Long Duration Treasury ETF", "country": "US", "currency": "USD", "exchange": "NASDAQ"},
    "VNQ": {"sector": "REIT", "industry": "Real Estate ETF", "country": "US", "currency": "USD", "exchange": "NYSE Arca"},
    "SOXX": {"sector": "Semiconductor", "industry": "Semiconductor ETF", "country": "US", "currency": "USD", "exchange": "NASDAQ"},
    "GLD": {"sector": "Gold", "industry": "Gold ETF", "country": "US", "currency": "USD", "exchange": "NYSE Arca"},
    "GC=F": {"sector": "Gold", "industry": "Gold Futures", "country": "US", "currency": "USD", "exchange": "COMEX"},
    "CL=F": {"sector": "Oil", "industry": "WTI Crude Oil Futures", "country": "US", "currency": "USD", "exchange": "NYMEX"},
    "BZ=F": {"sector": "Oil", "industry": "Brent Crude Oil Futures", "country": "Global", "currency": "USD", "exchange": "ICE"},
}


def search_assets(query: str, limit: int = 12) -> Dict[str, Any]:
    term = LEGACY_THAI_QUERY_ALIASES.get(query.strip(), query.strip()).lower()
    universe = exchange_master_assets() or ASSET_UNIVERSE
    if not term:
        matches = universe[:limit]
    else:
        scored: List[Tuple[int, Dict[str, Any]]] = []
        for asset in universe:
            score = _score_asset(term, asset)
            if score:
                scored.append((score, asset))
        matches = [asset for _, asset in sorted(scored, key=lambda item: item[0], reverse=True)[:limit]]
    enriched = [_enrich_asset(asset) for asset in matches]
    metadata = exchange_master_metadata()
    return {"query": query, "count": len(enriched), "assets": enriched, "source": metadata.get("source", "exchange_master"), "exchange_master": metadata}


def sector_browser() -> Dict[str, Any]:
    universe = exchange_master_assets() or ASSET_UNIVERSE
    sectors_by_name: Dict[str, List[Dict[str, Any]]] = {}
    for asset in universe:
        sector = asset.get("sector") or asset.get("asset_type") or "Unclassified"
        sectors_by_name.setdefault(str(sector), []).append(_enrich_asset(asset))
    sectors = []
    for name, assets in sorted(sectors_by_name.items()):
        sectors.append({"name": name, "count": len(assets), "assets": assets})
    metadata = exchange_master_metadata()
    return {
        "sectors": sectors,
        "source": metadata.get("source", "exchange_master"),
        "exchange_master": metadata,
        "limitations": metadata.get("limitations", ["Sector membership should be verified against exchange or issuer classifications."]),
    }


def assets_for_sector(sector: str, limit: int = 25) -> Dict[str, Any]:
    target = sector.strip().lower()
    safe_limit = limit if isinstance(limit, int) else 25
    universe = exchange_master_assets() or ASSET_UNIVERSE
    assets = [_enrich_asset(asset) for asset in universe if str(asset.get("sector") or asset.get("asset_type") or "").lower() == target][:safe_limit]
    return {"sector": sector, "count": len(assets), "assets": assets, "source": exchange_master_metadata().get("source", "exchange_master")}


def _score_asset(term: str, asset: Dict[str, Any]) -> int:
    symbol = asset["symbol"].lower()
    searchable = " ".join([
        symbol,
        asset.get("label", "").lower(),
        asset.get("thai_name", "").lower(),
        THAI_NAME_ALIASES.get(asset["symbol"], "").lower(),
        asset.get("asset_type", "").lower(),
        asset.get("market", "").lower(),
        asset.get("exchange", "").lower(),
        asset.get("sector", "").lower(),
        asset.get("industry", "").lower(),
        asset.get("country", "").lower(),
        asset.get("currency", "").lower(),
        asset.get("alias", "").lower(),
        asset.get("keywords", "").lower(),
    ])
    compact = searchable.replace(" ", "")
    if term == symbol:
        return 100
    if symbol.startswith(term):
        return 90
    if term in searchable:
        return 70
    return 0


def _enrich_asset(asset: Dict[str, Any]) -> Dict[str, Any]:
    metadata = ASSET_METADATA.get(asset["symbol"], {})
    thai_alias = THAI_NAME_ALIASES.get(asset["symbol"])
    return {
        **asset,
        **metadata,
        "thai_name": thai_alias or asset.get("thai_name", ""),
        "alias": " ".join(part for part in [asset.get("keywords", ""), thai_alias or ""] if part),
    }
