from __future__ import annotations

from contextlib import asynccontextmanager
from dataclasses import asdict
from concurrent.futures import ThreadPoolExecutor
import json
from datetime import datetime, timezone
import os
from pathlib import Path
from typing import Any, Dict

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from app.data_hub import provider_router
from app.data_hub.capabilities import capabilities_for_symbol
from app.data_hub.exchange_master import exchange_master_metadata, validate_exchange_master
from app.data_hub.master_asset_registry import master_asset_registry_metadata, validate_master_asset_registry
from app.data_hub.symbol_resolver import resolve_symbol
from app.intelligence.business import build_business_intelligence_report, business_intelligence_methodology
from app.intelligence.financial import build_financial_intelligence_report, classify_asset_for_intelligence, financial_intelligence_methodology
from app.premium.alerts import build_digest, evaluate_alert_rules
from app.premium.entitlements import entitlement_matrix, evaluate_entitlement
from app.services.analysis import build_ai_analysis, build_risk
from app.services.asset_universe import assets_for_sector, search_assets, sector_browser
from app.services.cache import FUNDAMENTALS_TTL_SECONDS, HISTORICAL_TTL_SECONDS, QUOTE_TTL_SECONDS, WATCHLIST_TTL_SECONDS, cache, cache_key
from app.services.calendar import economic_calendar
from app.services.comparison import build_comparison
from app.services.financials import build_financial_statement_analysis
from app.services.macro import company_events, intelligence_status, macro_indicators
from app.services.news import news_for_symbol, news_impact_for_symbol
from app.services.penny_opportunities import get_penny_algorithm_definition, get_penny_candidate_explanation, get_penny_opportunities_snapshot, get_penny_why_not, register_penny_opportunity_engine, start_penny_opportunity_scheduler, stop_penny_opportunity_scheduler
from app.services.portfolio import evaluate_portfolio
from app.services.qa_assistant import answer_question
from app.services.sentiment import sentiment_for_symbol
from app.services.subscription import subscription_features
from app.services.technical import build_technical_analysis

BACKEND_DIR = Path(__file__).resolve().parents[1]
PROJECT_DIR = BACKEND_DIR.parent
WATCHLIST_PATH = PROJECT_DIR / "configs" / "watchlist.json"
DEFAULT_PROVIDER = "yfinance"
DEFAULT_LOCAL_CORS_ORIGINS = (
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:4173",
    "http://127.0.0.1:4173",
    "https://market-pulse-ai.pages.dev",
)
DEFAULT_PRODUCTION_CORS_ORIGINS = ("https://market-pulse-ai.pages.dev",)
LOCAL_CORS_ORIGIN_REGEX = r"^http://(localhost|127\.0\.0\.1):(5173|5174|5175|5176|4173|4174|4175|4176)$"
BATCH_WORKERS = max(1, min(8, int(os.getenv("DATA_HUB_BATCH_WORKERS", "4"))))


class UTF8JSONResponse(JSONResponse):
    media_type = "application/json; charset=utf-8"


def _cors_allowed_origins() -> tuple[str, ...]:
    configured = os.getenv("CORS_ALLOWED_ORIGINS", "")
    app_env = os.getenv("APP_ENV", "development").strip().lower()
    origins = tuple(origin.strip() for origin in configured.split(",") if origin.strip())
    if app_env == "production":
        origins = tuple(origin for origin in origins if origin != "*")
        return origins or DEFAULT_PRODUCTION_CORS_ORIGINS
    return origins or DEFAULT_LOCAL_CORS_ORIGINS


def _cors_allowed_origin_regex() -> str | None:
    configured = os.getenv("CORS_ALLOWED_ORIGINS", "")
    app_env = os.getenv("APP_ENV", "development").strip().lower()
    if app_env == "production" or configured:
        return None
    return LOCAL_CORS_ORIGIN_REGEX


def _penny_scheduler_enabled() -> bool:
    configured = os.getenv("PENNY_OPPORTUNITY_SCHEDULER_ENABLED")
    if configured is not None:
        return configured.strip().lower() in {"1", "true", "yes", "on"}
    return os.getenv("APP_ENV", "development").strip().lower() == "production"


def _env_int(name: str, default: int) -> int:
    try:
        return int(os.getenv(name, str(default)))
    except ValueError:
        return default


def _env_float(name: str, default: float) -> float:
    try:
        return float(os.getenv(name, str(default)))
    except ValueError:
        return default


class AssistantRequest(BaseModel):
    question: str
    selected_symbol: str = "BTC-USD"
    language: str = "th"


class PortfolioRequest(BaseModel):
    holdings: list[dict[str, Any]] = []


class EntitlementRequest(BaseModel):
    plan: str = "free"
    feature: str = "market_data"


class AlertEvaluationRequest(BaseModel):
    plan: str = "free"
    rules: list[dict[str, Any]] = []
    context: dict[str, Any] = {}
    quiet_mode: dict[str, Any] = {}


class DigestRequest(BaseModel):
    kind: str = "morning_brief"
    context: dict[str, Any] = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    register_penny_opportunity_engine()
    if _penny_scheduler_enabled():
        start_penny_opportunity_scheduler(
            get_cached_quote,
            get_cached_history,
            news_for_symbol,
            market=os.getenv("PENNY_OPPORTUNITY_MARKET", "TH"),
            limit=_env_int("PENNY_OPPORTUNITY_LIMIT", 5),
            frequency_minutes=_env_int("PENNY_OPPORTUNITY_SCHEDULE_MINUTES", 60),
            thai_max_price=_env_float("PENNY_OPPORTUNITY_MAX_PRICE", 10.0),
            initial_delay_seconds=_env_int("PENNY_OPPORTUNITY_INITIAL_DELAY_SECONDS", 30),
        )
    try:
        yield
    finally:
        stop_penny_opportunity_scheduler()


app = FastAPI(title="Market Pulse AI API", version="1.0.0-rc1", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=list(_cors_allowed_origins()),
    allow_origin_regex=_cors_allowed_origin_regex(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> Dict[str, str]:
    return {"status": "ok", "service": "market-pulse-ai", "version": "1.0.0-rc1"}


@app.get("/api/watchlist")
def watchlist() -> Dict[str, Any]:
    key = cache_key(DEFAULT_PROVIDER, "watchlist")
    cached = cache.get(key)
    if cached is not None:
        return cached
    return cache.set(key, _load_watchlist(), WATCHLIST_TTL_SECONDS)


@app.get("/api/assets/search")
def asset_search(
    q: str = Query(""),
    asset_class: str | None = Query(None),
    exchange: str | None = Query(None),
    country: str | None = Query(None),
    sector: str | None = Query(None),
    industry: str | None = Query(None),
    limit: int = Query(25, ge=1, le=100),
) -> Dict[str, Any]:
    return search_assets(q, limit, asset_class, exchange, country, sector, industry)


@app.get("/api/exchange-master")
def exchange_master() -> Dict[str, Any]:
    return exchange_master_metadata()


@app.get("/api/master-asset-registry")
def master_asset_registry() -> Dict[str, Any]:
    return master_asset_registry_metadata()


@app.get("/api/data-hub/status")
def data_hub_status() -> Dict[str, Any]:
    return {
        **provider_router.status(),
        "validation": validate_exchange_master(),
        "master_registry": master_asset_registry_metadata(),
        "master_registry_validation": validate_master_asset_registry(),
    }


@app.get("/api/data-hub/assets/{symbol}/capabilities")
def data_hub_capabilities(symbol: str) -> Dict[str, Any]:
    return capabilities_for_symbol(symbol)


@app.get("/api/data-hub/resolve")
def data_hub_resolve(q: str = Query("")) -> Dict[str, Any]:
    return provider_router.resolve(q)


@app.get("/api/data-hub/universe/metadata")
def data_hub_universe_metadata() -> Dict[str, Any]:
    return exchange_master_metadata()


@app.get("/api/intelligence/assets/{symbol}/classification")
def asset_intelligence_classification(symbol: str) -> Dict[str, Any]:
    quote = get_cached_quote(symbol)
    return asdict(classify_asset_for_intelligence(symbol, quote))


@app.get("/api/intelligence/financial/methodology")
def financial_intelligence_methodology_endpoint() -> Dict[str, Any]:
    return financial_intelligence_methodology()


@app.get("/api/intelligence/financial/{symbol}")
def financial_intelligence(symbol: str) -> Dict[str, Any]:
    provider_payload = get_cached_fundamentals(symbol)
    quote = get_cached_quote(symbol)
    return build_financial_intelligence_report(symbol, provider_payload, quote)


@app.get("/api/intelligence/business/methodology")
def business_intelligence_methodology_endpoint() -> Dict[str, Any]:
    return business_intelligence_methodology()


@app.get("/api/intelligence/business/{symbol}")
def business_intelligence(symbol: str) -> Dict[str, Any]:
    provider_payload = get_cached_fundamentals(symbol)
    quote = get_cached_quote(symbol)
    financial_report = build_financial_intelligence_report(symbol, provider_payload, quote)
    return build_business_intelligence_report(symbol, quote, financial_report)


@app.get("/api/sectors")
def sectors() -> Dict[str, Any]:
    return sector_browser()


@app.get("/api/sectors/{sector}/assets")
def sector_assets(sector: str, limit: int = Query(25, ge=1, le=50)) -> Dict[str, Any]:
    return assets_for_sector(sector, limit)


@app.get("/api/assets/quotes")
def asset_quotes(symbols: str = Query("BTC-USD")) -> Dict[str, Any]:
    selected = _dedupe_symbols([symbol.strip() for symbol in symbols.split(",") if symbol.strip()])[:25]
    return {"symbols": selected, "items": _bounded_map(selected, get_cached_quote), "source": DEFAULT_PROVIDER}


@app.get("/api/assets/sparklines")
def asset_sparklines(symbols: str = Query("BTC-USD")) -> Dict[str, Any]:
    selected = _dedupe_symbols([symbol.strip() for symbol in symbols.split(",") if symbol.strip()])[:25]
    return {
        "symbols": selected,
        "items": _bounded_map(selected, build_sparkline),
        "source": DEFAULT_PROVIDER,
        "ttl_seconds": HISTORICAL_TTL_SECONDS,
    }


@app.get("/api/assets/{symbol}")
def asset_quote(symbol: str) -> Dict[str, Any]:
    return get_cached_quote(symbol)


@app.get("/api/assets/{symbol}/history")
def asset_history(symbol: str, range: str = Query("1mo"), interval: str = Query("1d")) -> Dict[str, Any]:
    return get_cached_history(symbol, range, interval)


@app.get("/api/technical/{symbol}")
def technical(symbol: str, range: str = Query("1y"), interval: str = Query("1d")) -> Dict[str, Any]:
    history = get_cached_history(symbol, range, interval)
    return build_technical_analysis(symbol, history)


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


@app.get("/api/opportunities/penny", response_class=UTF8JSONResponse)
def penny_opportunities(
    market: str | None = Query(None),
    limit: int = Query(5, ge=1, le=20),
    language: str = Query("th"),
    max_price: float | None = None,
) -> Dict[str, Any]:
    if max_price is not None:
        if max_price < 5 or max_price > 15:
            raise HTTPException(status_code=400, detail="max_price must be between 5.00 and 15.00 THB for Thai Emerging Opportunities.")
    return get_penny_opportunities_snapshot(market=market, limit=limit, thai_max_price=max_price)


@app.get("/api/opportunities/penny/algorithm")
def penny_algorithm() -> Dict[str, Any]:
    return get_penny_algorithm_definition()


@app.get("/api/opportunities/penny/explain/{symbol}")
def penny_explain(symbol: str) -> Dict[str, Any]:
    return get_penny_candidate_explanation(symbol)


@app.get("/api/opportunities/penny/why-not/{symbol}")
def penny_why_not(symbol: str) -> Dict[str, Any]:
    return get_penny_why_not(symbol)


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


@app.get("/api/news")
def news(symbol: str = Query("BTC-USD"), limit: int = Query(10, ge=1, le=25)) -> Dict[str, Any]:
    return news_for_symbol(symbol, limit)


@app.get("/api/news-impact/{symbol}")
def news_impact(symbol: str) -> Dict[str, Any]:
    return news_impact_for_symbol(symbol)


@app.get("/api/sentiment/{symbol}")
def sentiment(symbol: str) -> Dict[str, Any]:
    return sentiment_for_symbol(symbol)


@app.get("/api/macro")
def macro() -> Dict[str, Any]:
    return macro_indicators()


@app.get("/api/market-condition", response_class=UTF8JSONResponse)
def market_condition() -> Dict[str, Any]:
    proxies = [
        {"key": "vix", "label": "VIX", "symbol": "^VIX"},
        {"key": "sp500", "label": "S&P 500", "symbol": "^GSPC"},
        {"key": "nasdaq100", "label": "NASDAQ100", "symbol": "^NDX"},
        {"key": "set", "label": "SET Index", "symbol": "^SET.BK"},
        {"key": "usdthb", "label": "USD/THB", "symbol": "USDTHB=X"},
        {"key": "gold", "label": "Gold", "symbol": "GC=F"},
        {"key": "oil", "label": "WTI Oil", "symbol": "CL=F"},
        {"key": "bitcoin", "label": "Bitcoin", "symbol": "BTC-USD"},
        {"key": "us10y", "label": "US 10Y Yield", "symbol": "^TNX"},
    ]
    quotes = _bounded_map(proxies, lambda proxy: get_cached_quote(proxy["symbol"]))
    metrics = [
        {
            **proxy,
            "value": quote.get("price"),
            "change": quote.get("change"),
            "change_percent": quote.get("change_percent"),
            "timestamp": quote.get("timestamp"),
            "provider": quote.get("source") or quote.get("metadata", {}).get("provider"),
            "available": quote.get("price") is not None,
            "error": quote.get("error") or quote.get("data_warning"),
        }
        for proxy, quote in zip(proxies, quotes)
    ]
    sentiment_payload = sentiment_for_symbol("BTC-USD")
    available_changes = [item["change_percent"] for item in metrics if isinstance(item.get("change_percent"), (int, float))]
    average_change = sum(available_changes) / len(available_changes) if available_changes else None
    if average_change is None:
        state_th = "รอข้อมูล"
        state_en = "Awaiting data"
    elif average_change > 0.5:
        state_th = "เชิงบวก"
        state_en = "Constructive"
    elif average_change < -0.5:
        state_th = "ระมัดระวัง"
        state_en = "Cautious"
    else:
        state_th = "เป็นกลาง"
        state_en = "Neutral"
    evidence = [
        f"{item['label']} {item['change_percent']:.2f}%" for item in metrics if isinstance(item.get("change_percent"), (int, float))
    ][:6]
    unavailable = [item["label"] for item in metrics if not item.get("available")]
    return {
        "state_th": state_th,
        "state_en": state_en,
        "average_change_percent": average_change,
        "sentiment": sentiment_payload,
        "metrics": metrics,
        "evidence": evidence,
        "unavailable": unavailable,
        "provider": DEFAULT_PROVIDER,
        "disclaimer": "This is not financial advice.",
    }


@app.get("/api/subscription/features")
def subscription() -> Dict[str, Any]:
    return subscription_features()


@app.get("/api/premium/entitlements")
def premium_entitlements() -> Dict[str, Any]:
    return entitlement_matrix()


@app.post("/api/premium/entitlements/check")
def premium_entitlement_check(payload: EntitlementRequest) -> Dict[str, Any]:
    return evaluate_entitlement(payload.plan, payload.feature).__dict__


@app.post("/api/alerts/evaluate")
def alerts_evaluate(payload: AlertEvaluationRequest) -> Dict[str, Any]:
    return evaluate_alert_rules(payload.rules, payload.context, payload.plan, payload.quiet_mode)


@app.post("/api/digests/build")
def digests_build(payload: DigestRequest) -> Dict[str, Any]:
    return build_digest(payload.kind, payload.context)


@app.get("/api/company-events/{symbol}")
def events(symbol: str) -> Dict[str, Any]:
    return company_events(symbol)


@app.get("/api/analysis/{symbol}")
def analysis(symbol: str) -> Dict[str, Any]:
    quote = get_cached_quote(symbol)
    history = get_cached_history(symbol, "1mo", "1d")
    payload = build_ai_analysis(symbol, quote, history)
    return {**payload, "real_intelligence": intelligence_status(symbol)}


@app.get("/api/risk/{symbol}")
def risk(symbol: str) -> Dict[str, Any]:
    quote = get_cached_quote(symbol)
    history = get_cached_history(symbol, "1mo", "1d")
    return build_risk(symbol, quote, history)


@app.get("/api/financials/{symbol}")
def financials(symbol: str) -> Dict[str, Any]:
    provider_payload = get_cached_fundamentals(symbol)
    quote = get_cached_quote(symbol)
    return build_financial_statement_analysis(symbol, provider_payload, quote)


def build_sparkline(symbol: str) -> Dict[str, Any]:
    history = get_cached_history(symbol, "1mo", "1d")
    raw_points = history.get("points", []) if isinstance(history, dict) else []
    closes = [
        {"time": point.get("time"), "close": point.get("close")}
        for point in raw_points
        if isinstance(point, dict) and isinstance(point.get("close"), (int, float))
    ][-7:]
    timestamp = closes[-1]["time"] if closes else datetime.now(timezone.utc).isoformat()
    unavailable_reason = None
    if not closes:
        unavailable_reason = history.get("error") if isinstance(history, dict) else "History provider returned no close prices."
    elif len(closes) < 5:
        unavailable_reason = "Fewer than five recent provider close points were available."
    start_price = closes[0]["close"] if closes else None
    end_price = closes[-1]["close"] if closes else None
    change_percent = ((end_price - start_price) / start_price * 100) if isinstance(start_price, (int, float)) and start_price else None
    stale = _sparkline_is_stale(timestamp) if closes else False
    return {
        "symbol": symbol,
        "points": closes,
        "start_price": start_price,
        "end_price": end_price,
        "change_percent": change_percent,
        "provider": history.get("source", DEFAULT_PROVIDER) if isinstance(history, dict) else DEFAULT_PROVIDER,
        "timestamp": timestamp,
        "stale": stale,
        "unavailable_reason": unavailable_reason,
    }


def _sparkline_is_stale(timestamp: str | None) -> bool:
    if not timestamp:
        return False
    try:
        normalized = timestamp.replace("Z", "+00:00")
        value = datetime.fromisoformat(normalized)
        if value.tzinfo is None:
            value = value.replace(tzinfo=timezone.utc)
        return (datetime.now(timezone.utc) - value.astimezone(timezone.utc)).days > 4
    except Exception:
        return False


def _dedupe_symbols(symbols: list[str]) -> list[str]:
    seen: set[str] = set()
    deduped: list[str] = []
    for symbol in symbols:
        key = symbol.upper()
        if key in seen:
            continue
        seen.add(key)
        deduped.append(symbol)
    return deduped


def _bounded_map(items: list[Any], fn: Any) -> list[Any]:
    if len(items) <= 1:
        return [fn(item) for item in items]
    with ThreadPoolExecutor(max_workers=min(BATCH_WORKERS, len(items))) as executor:
        return list(executor.map(fn, items))


def get_cached_quote(symbol: str) -> Dict[str, Any]:
    resolved = resolve_symbol(symbol)
    canonical = resolved.canonical_symbol or symbol
    key = cache_key(DEFAULT_PROVIDER, "quote", canonical)
    return cache.get_or_set(key, lambda: provider_router.get_quote(symbol), QUOTE_TTL_SECONDS)


def get_cached_history(symbol: str, range: str, interval: str) -> Dict[str, Any]:
    resolved = resolve_symbol(symbol)
    canonical = resolved.canonical_symbol or symbol
    key = cache_key(DEFAULT_PROVIDER, "history", canonical, range, interval)
    cached, age = cache.get_with_age(key)
    if cached is not None:
        if isinstance(cached, dict):
            return {**cached, "cache_age_seconds": age}
        return cached
    return cache.get_or_set(key, lambda: provider_router.get_history(symbol, range, interval), HISTORICAL_TTL_SECONDS)


def get_cached_fundamentals(symbol: str) -> Dict[str, Any]:
    resolved = resolve_symbol(symbol)
    canonical = resolved.canonical_symbol or symbol
    key = cache_key(DEFAULT_PROVIDER, "fundamentals", canonical)
    return cache.get_or_set(key, lambda: provider_router.get_fundamentals(symbol), FUNDAMENTALS_TTL_SECONDS)


def _load_watchlist() -> Dict[str, Any]:
    with WATCHLIST_PATH.open("r", encoding="utf-8") as file:
        return json.load(file)
