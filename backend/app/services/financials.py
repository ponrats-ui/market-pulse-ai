from __future__ import annotations

from typing import Any, Dict

from app.services.analysis import get_asset_type


def build_financial_statement_analysis(symbol: str, provider_payload: Dict[str, Any] | None = None, quote: Dict[str, Any] | None = None) -> Dict[str, Any]:
    asset_type = get_asset_type(symbol, quote)
    if asset_type not in {"thai_stock", "global_stock"}:
        return {
            "symbol": symbol,
            "applicable": False,
            "status": "not_applicable",
            "message": "Financial statement analysis is not applicable to this asset type",
            "alternative_fundamentals": _alternative_fundamentals(asset_type),
            "disclaimer": "This is not financial advice.",
        }

    data = provider_payload or {}
    return {
        "symbol": symbol,
        "applicable": True,
        "status": "partial",
        "facts": {
            "revenue_trend": data.get("revenueTrend"),
            "net_profit_trend": data.get("netProfitTrend"),
            "gross_margin": data.get("grossMargin"),
            "net_margin": data.get("netMargin"),
            "debt_to_equity": data.get("debtToEquity"),
            "cash_flow_quality": data.get("cashFlowQuality"),
            "roe": data.get("roe"),
            "roa": data.get("roa"),
            "eps": data.get("eps"),
            "pe": data.get("pe"),
            "pbv": data.get("pbv"),
            "dividend_yield": data.get("dividendYield"),
            "three_to_five_year_trend": data.get("threeToFiveYearTrend"),
        },
        "interpretation": {
            "balance_sheet_strength": data.get("balanceSheetStrength"),
            "earnings_quality": data.get("earningsQuality"),
            "valuation_risk": data.get("valuationRisk"),
        },
        "risks": [
            "Accounting figures may lag current business conditions.",
            "High valuation multiples increase sensitivity to earnings misses.",
            "Debt, currency, and refinancing risk should be reviewed carefully.",
        ],
        "cautious_action_plan": [
            "Compare valuation against peers and the company's own 3-5 year range.",
            "Check whether earnings growth is supported by operating cash flow.",
            "Avoid relying on one metric; combine profitability, leverage, and valuation context.",
        ],
        "source": data.get("source", "yfinance"),
        "disclaimer": "This is not financial advice.",
    }


def _alternative_fundamentals(asset_type: str) -> Dict[str, Any]:
    alternatives = {
        "crypto": ["network activity", "liquidity", "token supply", "regulatory risk", "custody risk"],
        "commodity": ["supply/demand balance", "inventory levels", "geopolitical risk", "seasonality", "USD sensitivity"],
        "index": ["constituent earnings", "sector weights", "market breadth", "rates", "valuation multiples"],
        "macro": ["central bank policy", "inflation", "growth expectations", "yield differentials", "capital flows"],
        "fx": ["rate differentials", "central bank policy", "trade balance", "capital flows", "USD liquidity"],
    }
    return {
        "asset_type": asset_type,
        "focus_areas": alternatives.get(asset_type, ["liquidity", "volatility", "macro context"]),
    }
