from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.providers.yfinance_provider import YFinanceProvider
from app.services.analysis import build_ai_analysis, build_risk
from app.services.financials import build_financial_statement_analysis

BACKEND_DIR = Path(__file__).resolve().parents[1]
PROJECT_DIR = BACKEND_DIR.parent
WATCHLIST_PATH = PROJECT_DIR / "configs" / "watchlist.json"

app = FastAPI(title="Market Pulse AI API", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
provider = YFinanceProvider()


@app.get("/health")
def health() -> Dict[str, str]:
    return {"status": "ok", "service": "market-pulse-ai"}


@app.get("/api/watchlist")
def watchlist() -> Dict[str, Any]:
    return _load_watchlist()


@app.get("/api/assets/{symbol}")
def asset_price(symbol: str) -> Dict[str, Any]:
    try:
        return provider.get_asset_snapshot(symbol)
    except Exception as exc:
        return _mock_asset(symbol, error=str(exc))


@app.get("/api/analysis/{symbol}")
def analysis(symbol: str) -> Dict[str, Any]:
    snapshot = asset_price(symbol)
    return build_ai_analysis(symbol, snapshot)


@app.get("/api/risk/{symbol}")
def risk(symbol: str) -> Dict[str, Any]:
    snapshot = asset_price(symbol)
    return build_risk(symbol, snapshot)


@app.get("/api/financials/{symbol}")
def financials(symbol: str) -> Dict[str, Any]:
    try:
        provider_payload = provider.get_financials(symbol)
    except Exception:
        provider_payload = {}
    return build_financial_statement_analysis(symbol, provider_payload)


@lru_cache(maxsize=1)
def _load_watchlist() -> Dict[str, Any]:
    with WATCHLIST_PATH.open("r", encoding="utf-8") as file:
        return json.load(file)


def _mock_asset(symbol: str, error: str | None = None) -> Dict[str, Any]:
    history = [
        {"date": "2026-06-01", "close": 100, "volume": 1000000},
        {"date": "2026-06-08", "close": 103, "volume": 1250000},
        {"date": "2026-06-15", "close": 101, "volume": 1180000},
        {"date": "2026-06-22", "close": 106, "volume": 1400000},
        {"date": "2026-06-29", "close": 108, "volume": 1510000},
    ]
    return {
        "symbol": symbol,
        "price": 108,
        "previousClose": 106,
        "change": 2,
        "changePercent": 1.89,
        "currency": "USD",
        "asOf": "mock",
        "source": "mock-fallback",
        "history": history,
        "providerError": error,
    }
