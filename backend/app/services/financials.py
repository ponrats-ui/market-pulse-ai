from __future__ import annotations

from typing import Any, Dict

from app.services.analysis import get_asset_type


def build_financial_statement_analysis(symbol: str, provider_payload: Dict[str, Any] | None = None) -> Dict[str, Any]:
    asset_type = get_asset_type(symbol)
    if asset_type != "stock":
        return {
            "symbol": symbol,
            "applicable": False,
            "message": "Financial statement analysis is not applicable to this asset type",
            "alternativeFundamentals": _alternative_fundamentals(asset_type),
            "disclaimer": "This is not financial advice.",
        }

    data = provider_payload or {}
    return {
        "symbol": symbol,
        "applicable": True,
        "facts": {
            "revenueTrend": data.get("revenueTrend"),
            "netProfitTrend": data.get("netProfitTrend"),
            "grossMargin": data.get("grossMargin"),
            "netMargin": data.get("netMargin"),
            "debtToEquity": data.get("debtToEquity"),
            "cashFlowQuality": data.get("cashFlowQuality"),
            "roe": data.get("roe"),
            "roa": data.get("roa"),
            "eps": data.get("eps"),
            "pe": data.get("pe"),
            "pbv": data.get("pbv"),
            "dividendYield": data.get("dividendYield"),
            "threeToFiveYearTrend": data.get("threeToFiveYearTrend"),
        },
        "interpretation": {
            "balanceSheetStrength": data.get("balanceSheetStrength"),
            "earningsQuality": data.get("earningsQuality"),
            "valuationRisk": data.get("valuationRisk"),
        },
        "risks": [
            "Accounting figures may lag current business conditions.",
            "High valuation multiples increase sensitivity to earnings misses.",
            "Debt, currency, and refinancing risk should be reviewed carefully.",
        ],
        "cautiousActionPlan": [
            "Compare valuation against peers and the company's own 3-5 year range.",
            "Check whether earnings growth is supported by operating cash flow.",
            "Avoid relying on one metric; combine profitability, leverage, and valuation context.",
        ],
        "disclaimer": "This is not financial advice.",
    }


def _alternative_fundamentals(asset_type: str) -> Dict[str, Any]:
    alternatives = {
        "crypto": ["network activity", "liquidity", "token supply", "regulatory risk", "custody risk"],
        "commodity": ["supply/demand balance", "inventory levels", "geopolitical risk", "seasonality", "USD sensitivity"],
        "index": ["constituent earnings", "sector weights", "market breadth", "rates", "valuation multiples"],
        "macro": ["central bank policy", "inflation", "growth expectations", "yield differentials", "capital flows"],
    }
    return {
        "assetType": asset_type,
        "focusAreas": alternatives.get(asset_type, ["liquidity", "volatility", "macro context"]),
    }
