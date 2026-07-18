from __future__ import annotations

from typing import Any, Dict


ASSET_CLASS_MODELS: Dict[str, Dict[str, Any]] = {
    "global_stock": {
        "asset_class": "Stocks",
        "risk_model": "equity_volatility_quality_liquidity",
        "evidence_sources": ["quote", "history", "financials", "news", "macro"],
        "factor_bias": {"fundamental": 1.15, "valuation": 1.1, "quality": 1.1, "liquidity": 1.05},
    },
    "thai_stock": {
        "asset_class": "Stocks",
        "risk_model": "equity_fx_liquidity",
        "evidence_sources": ["quote", "history", "financials", "fx", "local_macro"],
        "factor_bias": {"fundamental": 1.1, "liquidity": 1.15, "risk": 1.1},
    },
    "etf": {
        "asset_class": "ETF",
        "risk_model": "basket_tracking_liquidity",
        "evidence_sources": ["quote", "history", "holdings", "macro"],
        "factor_bias": {"liquidity": 1.2, "macro": 1.1, "risk": 1.1, "fundamental": 0.8},
    },
    "crypto": {
        "asset_class": "Crypto",
        "risk_model": "crypto_volatility_liquidity_regulatory",
        "evidence_sources": ["quote", "history", "liquidity", "regulatory_news", "sentiment"],
        "factor_bias": {"momentum": 1.2, "volatility": 1.3, "risk": 1.25, "valuation": 0.5},
    },
    "commodity": {
        "asset_class": "Commodity",
        "risk_model": "supply_demand_macro_volatility",
        "evidence_sources": ["quote", "history", "macro", "inventory", "geopolitical"],
        "factor_bias": {"macro": 1.25, "news": 1.15, "volatility": 1.2, "valuation": 0.6},
    },
    "fx": {
        "asset_class": "Forex",
        "risk_model": "rates_macro_liquidity",
        "evidence_sources": ["quote", "history", "rates", "macro", "central_bank"],
        "factor_bias": {"macro": 1.35, "technical": 1.1, "liquidity": 1.15, "fundamental": 0.6},
    },
    "macro": {
        "asset_class": "Bond",
        "risk_model": "duration_rates_macro",
        "evidence_sources": ["quote", "history", "rates", "inflation", "central_bank"],
        "factor_bias": {"macro": 1.4, "risk": 1.15, "volatility": 1.1, "valuation": 0.7},
    },
    "index": {
        "asset_class": "Index",
        "risk_model": "market_beta_macro_liquidity",
        "evidence_sources": ["quote", "history", "macro", "breadth", "earnings"],
        "factor_bias": {"macro": 1.15, "technical": 1.1, "liquidity": 1.1, "quality": 0.9},
    },
}


def get_asset_class_model(asset_type: str | None) -> Dict[str, Any]:
    return ASSET_CLASS_MODELS.get(asset_type or "", ASSET_CLASS_MODELS["global_stock"])
