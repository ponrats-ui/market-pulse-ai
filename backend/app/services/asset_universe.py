from __future__ import annotations

from typing import Any, Dict, List


ASSET_UNIVERSE: List[Dict[str, str]] = [
    {"symbol": "AAPL", "label": "Apple", "asset_type": "stock", "market": "NASDAQ", "keywords": "iphone services technology"},
    {"symbol": "MSFT", "label": "Microsoft", "asset_type": "stock", "market": "NASDAQ", "keywords": "cloud ai software"},
    {"symbol": "NVDA", "label": "NVIDIA", "asset_type": "stock", "market": "NASDAQ", "keywords": "ai gpu semiconductor cuda"},
    {"symbol": "TSLA", "label": "Tesla", "asset_type": "stock", "market": "NASDAQ", "keywords": "ev battery autonomous"},
    {"symbol": "AMZN", "label": "Amazon", "asset_type": "stock", "market": "NASDAQ", "keywords": "aws ecommerce cloud"},
    {"symbol": "META", "label": "Meta Platforms", "asset_type": "stock", "market": "NASDAQ", "keywords": "facebook instagram ai ads"},
    {"symbol": "GOOGL", "label": "Alphabet", "asset_type": "stock", "market": "NASDAQ", "keywords": "google search cloud ai"},
    {"symbol": "SPY", "label": "SPDR S&P 500 ETF", "asset_type": "etf", "market": "NYSE Arca", "keywords": "s&p 500 etf"},
    {"symbol": "VOO", "label": "Vanguard S&P 500 ETF", "asset_type": "etf", "market": "NYSE Arca", "keywords": "s&p 500 etf"},
    {"symbol": "QQQ", "label": "Invesco QQQ ETF", "asset_type": "etf", "market": "NASDAQ", "keywords": "nasdaq 100 etf technology"},
    {"symbol": "BTC-USD", "label": "Bitcoin", "asset_type": "crypto", "market": "Crypto", "keywords": "btc bitcoin crypto"},
    {"symbol": "ETH-USD", "label": "Ethereum", "asset_type": "crypto", "market": "Crypto", "keywords": "eth ethereum crypto"},
    {"symbol": "SOL-USD", "label": "Solana", "asset_type": "crypto", "market": "Crypto", "keywords": "sol solana crypto"},
    {"symbol": "XRP-USD", "label": "XRP", "asset_type": "crypto", "market": "Crypto", "keywords": "ripple xrp crypto"},
    {"symbol": "^SET.BK", "label": "SET Index", "asset_type": "index", "market": "Thailand", "keywords": "set thailand index"},
    {"symbol": "^SET50.BK", "label": "SET50 Index", "asset_type": "index", "market": "Thailand", "keywords": "set50 thailand index"},
    {"symbol": "PTT.BK", "label": "PTT", "asset_type": "stock", "market": "SET", "keywords": "energy oil gas thailand"},
    {"symbol": "AOT.BK", "label": "Airports of Thailand", "asset_type": "stock", "market": "SET", "keywords": "airport tourism thailand"},
    {"symbol": "SCB.BK", "label": "SCB X", "asset_type": "stock", "market": "SET", "keywords": "bank thailand scb"},
    {"symbol": "KBANK.BK", "label": "Kasikornbank", "asset_type": "stock", "market": "SET", "keywords": "bank thailand kbank"},
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


def search_assets(query: str, limit: int = 12) -> Dict[str, Any]:
    term = query.strip().lower()
    if not term:
        matches = ASSET_UNIVERSE[:limit]
    else:
        matches = [
            asset for asset in ASSET_UNIVERSE
            if term in asset["symbol"].lower()
            or term in asset["label"].lower()
            or term in asset["asset_type"].lower()
            or term in asset["market"].lower()
            or term in asset["keywords"].lower()
        ][:limit]
    return {"query": query, "count": len(matches), "assets": matches, "source": "curated_symbol_universe"}
