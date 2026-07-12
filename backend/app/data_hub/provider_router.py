from __future__ import annotations

import logging
import os
from datetime import datetime, timezone
from typing import Any, Callable, Dict, List

from app.data_hub.exchange_master import exchange_master_metadata
from app.data_hub.provider_health import provider_health_snapshot, record_provider_result, timed_provider_call
from app.data_hub.symbol_resolver import ResolutionResult, resolve_symbol
from app.providers.news import get_news_aggregator
from app.providers.registry import get_provider

logger = logging.getLogger("market_pulse.data_hub")

DEFAULT_POLICY = {
    "quote": ["yfinance"],
    "history": ["yfinance"],
    "fundamentals": ["yfinance"],
    "news": ["yahoo_finance_news", "rss", "configured_news"],
    "calendar": ["configured_calendar"],
}


def routing_policy() -> Dict[str, List[str]]:
    return {
        data_type: [part.strip() for part in os.getenv(f"DATA_HUB_{data_type.upper()}_PROVIDERS", ",".join(providers)).split(",") if part.strip()]
        for data_type, providers in DEFAULT_POLICY.items()
    }


def resolve(query: str, provider: str = "yfinance") -> Dict[str, Any]:
    result = resolve_symbol(query, provider)
    if not result.ok:
        logger.info("symbol_resolution_failure", extra={"query": query, "reason": result.reason})
    return result.to_dict()


def get_quote(query: str) -> Dict[str, Any]:
    return _with_market_provider("quote", query, lambda provider, symbol: provider.get_quote(symbol))


def get_history(query: str, range: str = "1mo", interval: str = "1d") -> Dict[str, Any]:
    return _with_market_provider("history", query, lambda provider, symbol: provider.get_history(symbol, range, interval))


def get_fundamentals(query: str) -> Dict[str, Any]:
    return _with_market_provider("fundamentals", query, lambda provider, symbol: provider.get_financials(symbol))


def get_news(query: str, limit: int = 10) -> Dict[str, Any]:
    resolved = resolve_symbol(query)
    if not resolved.ok or not resolved.canonical_symbol:
        logger.info("unsupported_asset", extra={"query": query, "data_type": "news", "reason": resolved.reason})
        return _unavailable(query, "news", resolved)
    payload = get_news_aggregator().fetch(resolved.canonical_symbol, limit)
    return {
        **payload,
        "symbol": resolved.canonical_symbol,
        "data_hub": _metadata("news", resolved, payload.get("provider", "news_aggregator"), None),
    }


def status() -> Dict[str, Any]:
    return {
        "status": "ok",
        "policy": routing_policy(),
        "provider_health": provider_health_snapshot(),
        "universe": exchange_master_metadata(),
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "limitations": [
            "Coverage is partial until verified S&P 500, Nasdaq-100, and SET constituent files are ingested.",
            "Provider fallback is configured but currently relies on yfinance/Yahoo Finance RSS for live data.",
        ],
    }


def _with_market_provider(data_type: str, query: str, call: Callable[[Any, str], Dict[str, Any]]) -> Dict[str, Any]:
    resolved = resolve_symbol(query)
    if not resolved.ok or not resolved.canonical_symbol or not resolved.provider_symbols:
        logger.info("unsupported_asset", extra={"query": query, "data_type": data_type, "reason": resolved.reason})
        return _unavailable(query, data_type, resolved)
    failures: list[dict[str, str]] = []
    for provider_name in routing_policy().get(data_type, []):
        provider_symbol = resolved.provider_symbols.get(provider_name)
        if not provider_symbol:
            failures.append({"provider": provider_name, "reason": "provider_symbol_unavailable"})
            record_provider_result(provider_name, False, False, reason="provider_symbol_unavailable")
            continue
        provider = get_provider(provider_name)
        logger.info("provider_selected", extra={"provider": provider.name, "data_type": data_type, "symbol": resolved.canonical_symbol})
        try:
            payload = timed_provider_call(provider.name, True, lambda: call(provider, provider_symbol))
            if payload.get("error"):
                failures.append({"provider": provider.name, "reason": str(payload.get("error"))})
                logger.warning("provider_failure", extra={"provider": provider.name, "data_type": data_type, "symbol": resolved.canonical_symbol})
                continue
            return {
                **payload,
                "symbol": resolved.canonical_symbol,
                "provider_symbol": provider_symbol,
                "data_hub": _metadata(data_type, resolved, provider.name, failures),
            }
        except Exception as exc:
            failures.append({"provider": provider_name, "reason": str(exc)})
            record_provider_result(provider_name, True, False, reason=str(exc))
            logger.warning("provider_failure", extra={"provider": provider_name, "data_type": data_type, "symbol": resolved.canonical_symbol})
    return _unavailable(resolved.canonical_symbol, data_type, resolved, failures)


def _metadata(data_type: str, resolved: ResolutionResult, provider: str, failures: List[Dict[str, str]] | None) -> Dict[str, Any]:
    return {
        "canonical_symbol": resolved.canonical_symbol,
        "display_symbol": resolved.display_symbol,
        "provider": provider,
        "data_type": data_type,
        "provider_failures": failures or [],
        "universe_version": exchange_master_metadata().get("version"),
        "coverage_status": exchange_master_metadata().get("coverage_status", "partial"),
    }


def _unavailable(query: str, data_type: str, resolved: ResolutionResult, failures: List[Dict[str, str]] | None = None) -> Dict[str, Any]:
    return {
        "symbol": resolved.canonical_symbol or query,
        "source": "Unavailable",
        "provider_configured": False,
        "error": resolved.reason or "provider_unavailable",
        "data_hub": {
            "canonical_symbol": resolved.canonical_symbol,
            "data_type": data_type,
            "provider_failures": failures or [],
            "universe_version": exchange_master_metadata().get("version"),
            "coverage_status": exchange_master_metadata().get("coverage_status", "partial"),
        },
    }
