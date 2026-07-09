from __future__ import annotations

from typing import Any, Dict, List, Tuple


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


def search_assets(query: str, limit: int = 12) -> Dict[str, Any]:
    term = query.strip().lower()
    if not term:
        matches = ASSET_UNIVERSE[:limit]
    else:
        scored: List[Tuple[int, Dict[str, str]]] = []
        for asset in ASSET_UNIVERSE:
            score = _score_asset(term, asset)
            if score:
                scored.append((score, asset))
        matches = [asset for _, asset in sorted(scored, key=lambda item: item[0], reverse=True)[:limit]]
    return {"query": query, "count": len(matches), "assets": matches, "source": "curated_symbol_universe"}


def _score_asset(term: str, asset: Dict[str, str]) -> int:
    symbol = asset["symbol"].lower()
    searchable = " ".join([
        symbol,
        asset.get("label", "").lower(),
        asset.get("thai_name", "").lower(),
        THAI_NAME_ALIASES.get(asset["symbol"], "").lower(),
        asset.get("asset_type", "").lower(),
        asset.get("market", "").lower(),
        asset.get("keywords", "").lower(),
    ])
    compact = searchable.replace(" ", "")
    if term == symbol:
        return 100
    if symbol.startswith(term):
        return 90
    if term in searchable:
        return 70
    if _is_subsequence(term, compact):
        return 40
    return 0


def _is_subsequence(needle: str, haystack: str) -> bool:
    if len(needle) < 2:
        return False
    position = 0
    for char in haystack:
        if position < len(needle) and needle[position] == char:
            position += 1
    return position == len(needle)
