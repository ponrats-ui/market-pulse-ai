from __future__ import annotations

from typing import Any, Dict

from app.services.analysis import get_asset_type

FIELD_MAP = {
    "revenue": ("revenue", "totalRevenue"),
    "gross_profit": ("grossProfit",),
    "operating_income": ("operatingIncome",),
    "net_income": ("netIncome",),
    "eps": ("eps", "trailingEps"),
    "ebitda": ("ebitda",),
    "operating_cash_flow": ("operatingCashFlow",),
    "free_cash_flow": ("freeCashFlow",),
    "assets": ("totalAssets",),
    "liabilities": ("totalLiabilities",),
    "equity": ("totalEquity",),
    "cash": ("totalCash",),
    "debt": ("totalDebt",),
    "roe": ("roe", "returnOnEquity"),
    "roa": ("roa", "returnOnAssets"),
    "gross_margin": ("grossMargin",),
    "operating_margin": ("operatingMargin",),
    "net_margin": ("netMargin",),
    "pe": ("pe",),
    "pbv": ("pbv",),
    "ps": ("ps",),
    "peg": ("peg",),
    "dividend_yield": ("dividendYield",),
    "debt_to_equity": ("debtToEquity",),
    "cash_flow_quality": ("cashFlowQuality",),
    "revenue_trend": ("revenueTrend", "revenueGrowth"),
    "net_profit_trend": ("netProfitTrend", "earningsGrowth"),
    "revenue_growth": ("revenueGrowth",),
    "earnings_growth": ("earningsGrowth",),
    "three_to_five_year_trend": ("threeToFiveYearTrend",),
    "intrinsic_value": ("intrinsicValue",),
}


def build_financial_statement_analysis(symbol: str, provider_payload: Dict[str, Any] | None = None, quote: Dict[str, Any] | None = None) -> Dict[str, Any]:
    asset_type = get_asset_type(symbol, quote)
    if asset_type not in {"thai_stock", "global_stock"}:
        return {
            "symbol": symbol,
            "applicable": False,
            "status": "not_applicable",
            "message": "This asset does not publish corporate financial statements.",
            "message_th": "สินทรัพย์นี้ไม่มีงบการเงินของบริษัท",
            "alternative_fundamentals": _alternative_fundamentals(asset_type),
            "field_provenance": {},
            "disclaimer": "This is not financial advice.",
        }

    data = provider_payload or {}
    source = data.get("source", "yfinance")
    facts = {field: _first(data, *keys) for field, keys in FIELD_MAP.items()}
    provenance = _field_provenance(data, facts, source)
    if data.get("error") or all(value is None for value in facts.values()):
        return {
            "symbol": symbol,
            "applicable": True,
            "status": "unavailable",
            "message": "Financial statement data is currently unavailable from the configured provider.",
            "message_th": "ยังไม่มีข้อมูลงบการเงินจากผู้ให้บริการที่ตั้งค่าไว้",
            "facts": facts,
            "field_provenance": provenance,
            "interpretation": {},
            "risks": ["Financial statement analysis is unavailable until provider data is returned."],
            "cautious_action_plan": ["Review official company filings before making any decision."],
            "source": source,
            "provider_gap": data.get("error") or "Provider returned no equivalent statement, balance sheet, cash flow, valuation, or margin fields.",
            "disclaimer": "This is not financial advice.",
        }
    return {
        "symbol": symbol,
        "applicable": True,
        "status": "partial",
        "facts": facts,
        "field_provenance": provenance,
        "interpretation": {
            "balance_sheet_strength": data.get("balanceSheetStrength"),
            "earnings_quality": data.get("earningsQuality"),
            "valuation_risk": data.get("valuationRisk"),
            "explanation_th": {
                "financial_health": "พิจารณาหนี้สิน เงินสด และความสามารถในการสร้างกระแสเงินสดร่วมกัน",
                "growth": "ดูการเติบโตของรายได้และกำไร โดยไม่ใช้ตัวเลขเดียวตัดสิน",
                "profitability": "ROE ROA และ margin ช่วยบอกคุณภาพกำไร",
                "valuation": "P/E P/BV PEG และ dividend yield ต้องเทียบกับคู่แข่งและประวัติย้อนหลัง",
                "cash_flow": "Free cash flow ช่วยยืนยันว่ากำไรเปลี่ยนเป็นเงินสดจริงหรือไม่",
                "intrinsic_value": "Intrinsic value ยังไม่คำนวณจนกว่าจะมีโมเดลและสมมติฐานที่ตรวจสอบได้",
            },
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
        "source": source,
        "disclaimer": "This is not financial advice.",
    }


def _field_provenance(data: Dict[str, Any], facts: Dict[str, Any], source: str) -> Dict[str, Dict[str, Any]]:
    provider_provenance = data.get("field_provenance") or {}
    result: Dict[str, Dict[str, Any]] = {}
    for field, value in facts.items():
        provider_key = next((key for key in FIELD_MAP[field] if key in provider_provenance), None)
        base = provider_provenance.get(provider_key or field, {})
        result[field] = {
            "provider": base.get("provider", source),
            "source": base.get("source", source),
            "available": value is not None,
        }
    return result


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


def _first(data: Dict[str, Any], *keys: str) -> Any:
    for key in keys:
        value = data.get(key)
        if value is not None:
            return value
    return None
