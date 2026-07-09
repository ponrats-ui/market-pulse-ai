from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Dict

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app.providers.registry import get_provider
from app.services.analysis import build_ai_analysis, build_risk
from app.services.asset_universe import search_assets
from app.services.cache import HISTORICAL_TTL_SECONDS, QUOTE_TTL_SECONDS, WATCHLIST_TTL_SECONDS, cache, cache_key
from app.services.calendar import economic_calendar
from app.services.comparison import build_comparison
from app.services.financials import build_financial_statement_analysis
from app.services.portfolio import evaluate_portfolio
from app.services.qa_assistant import answer_question
from app.services.sentiment import sentiment_for_symbol

BACKEND_DIR = Path(__file__).resolve().parents[1]
PROJECT_DIR = BACKEND_DIR.parent
WATCHLIST_PATH = PROJECT_DIR / "configs" / "watchlist.json"
DEFAULT_PROVIDER = "yfinance"
DEFAULT_LOCAL_CORS_ORIGINS = (
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "https://market-pulse-ai.pages.dev",
)
DEFAULT_PRODUCTION_CORS_ORIGINS = ("https://market-pulse-ai.pages.dev",)


def _cors_allowed_origins() -> tuple[str, ...]:
    configured = os.getenv("CORS_ALLOWED_ORIGINS", "")
    app_env = os.getenv("APP_ENV", "development").strip().lower()
    origins = tuple(origin.strip() for origin in configured.split(",") if origin.strip())
    if app_env == "production":
        origins = tuple(origin for origin in origins if origin != "*")
        return origins or DEFAULT_PRODUCTION_CORS_ORIGINS
    return origins or DEFAULT_LOCAL_CORS_ORIGINS


class AssistantRequest(BaseModel):
    question: str
    selected_symbol: str = "BTC-USD"
    language: str = "th"


class PortfolioRequest(BaseModel):
    holdings: list[dict[str, Any]] = []


app = FastAPI(title="Market Pulse AI API", version="0.3.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=list(_cors_allowed_origins()),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> Dict[str, str]:
    return {"status": "ok", "service": "market-pulse-ai", "version": "0.3.0"}


@app.get("/api/watchlist")
def watchlist() -> Dict[str, Any]:
    key = cache_key(DEFAULT_PROVIDER, "watchlist")
    cached = cache.get(key)
    if cached is not None:
        return cached
    return cache.set(key, _load_watchlist(), WATCHLIST_TTL_SECONDS)


@app.get("/api/assets/search")
def asset_search(q: str = Query(""), limit: int = Query(12, ge=1, le=25)) -> Dict[str, Any]:
    return search_assets(q, limit)


@app.get("/api/assets/quotes")
def asset_quotes(symbols: str = Query("BTC-USD")) -> Dict[str, Any]:
    selected = [symbol.strip() for symbol in symbols.split(",") if symbol.strip()][:25]
    return {"symbols": selected, "items": [get_cached_quote(symbol) for symbol in selected], "source": DEFAULT_PROVIDER}


@app.get("/api/assets/{symbol}")
def asset_quote(symbol: str) -> Dict[str, Any]:
    return get_cached_quote(symbol)


@app.get("/api/assets/{symbol}/history")
def asset_history(symbol: str, range: str = Query("1mo"), interval: str = Query("1d")) -> Dict[str, Any]:
    return get_cached_history(symbol, range, interval)


@app.get("/api/dashboard")
def dashboard() -> Dict[str, Any]:
    grouped = []
    for category in watchlist().get("categories", []):
        assets = []
        for asset in category.get("assets", []):
            symbol = asset.get("symbol")
            if not symbol:
                continue
            quote = get_cached_quote(symbol)
            assets.append({**asset, "quote": quote})
        grouped.append({"id": category.get("id"), "name": category.get("name"), "assets": assets})
    return {"categories": grouped, "source": DEFAULT_PROVIDER}


@app.get("/api/compare")
def compare(symbols: str = Query("BTC-USD,ETH-USD")) -> Dict[str, Any]:
    selected = [symbol.strip() for symbol in symbols.split(",") if symbol.strip()]
    return build_comparison(selected, get_cached_quote, get_cached_history)


@app.post("/api/assistant/ask")
def assistant_ask(payload: AssistantRequest) -> Dict[str, Any]:
    quote = get_cached_quote(payload.selected_symbol)
    history = get_cached_history(payload.selected_symbol, "1mo", "1d")
    risk_payload = build_risk(payload.selected_symbol, quote, history)
    analysis_payload = build_ai_analysis(payload.selected_symbol, quote, history)
    return answer_question(payload.question, payload.selected_symbol, payload.language, quote, risk_payload, analysis_payload)


@app.post("/api/portfolio/evaluate")
def portfolio_evaluate(payload: PortfolioRequest) -> Dict[str, Any]:
    return evaluate_portfolio(payload.holdings, get_cached_quote)


@app.get("/api/calendar")
def calendar() -> Dict[str, Any]:
    return economic_calendar()


@app.get("/api/news-impact/{symbol}")
def news_impact(symbol: str) -> Dict[str, Any]:
    return {
        "symbol": symbol,
        "source": "Unavailable",
        "provider_configured": False,
        "items": [],
        "message": "No news provider configured.",
        "message_th": "ยังไม่ได้ตั้งค่าผู้ให้บริการข่าว",
        "disclaimer": "This is not financial advice.",
    }


@app.get("/api/sentiment/{symbol}")
def sentiment(symbol: str) -> Dict[str, Any]:
    return sentiment_for_symbol(symbol)


@app.get("/api/analysis/{symbol}")
def analysis(symbol: str) -> Dict[str, Any]:
    quote = get_cached_quote(symbol)
    history = get_cached_history(symbol, "1mo", "1d")
    return build_ai_analysis(symbol, quote, history)


@app.get("/api/risk/{symbol}")
def risk(symbol: str) -> Dict[str, Any]:
    quote = get_cached_quote(symbol)
    history = get_cached_history(symbol, "1mo", "1d")
    return build_risk(symbol, quote, history)


@app.get("/api/financials/{symbol}")
def financials(symbol: str) -> Dict[str, Any]:
    provider = get_provider(DEFAULT_PROVIDER)
    provider_payload = provider.get_financials(symbol)
    quote = get_cached_quote(symbol)
    return build_financial_statement_analysis(symbol, provider_payload, quote)


def get_cached_quote(symbol: str) -> Dict[str, Any]:
    provider = get_provider(DEFAULT_PROVIDER)
    key = cache_key(provider.name, "quote", symbol)
    cached = cache.get(key)
    if cached is not None:
        return cached
    return cache.set(key, provider.get_quote(symbol), QUOTE_TTL_SECONDS)


def get_cached_history(symbol: str, range: str, interval: str) -> Dict[str, Any]:
    provider = get_provider(DEFAULT_PROVIDER)
    key = cache_key(provider.name, "history", symbol, range, interval)
    cached = cache.get(key)
    if cached is not None:
        return cached
    return cache.set(key, provider.get_history(symbol, range, interval), HISTORICAL_TTL_SECONDS)


def _load_watchlist() -> Dict[str, Any]:
    with WATCHLIST_PATH.open("r", encoding="utf-8") as file:
        return json.load(file)
