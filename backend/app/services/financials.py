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
            "message": "This asset does not publish corporate financial statements.",
            "message_th": "สินทรัพย์นี้ไม่มีงบการเงินบริษัท",
            "alternative_fundamentals": _alternative_fundamentals(asset_type),
            "disclaimer": "This is not financial advice.",
        }

    data = provider_payload or {}
    facts = {
        "revenue": _first(data, "revenue", "totalRevenue"),
        "gross_profit": _first(data, "grossProfit"),
        "operating_income": _first(data, "operatingIncome"),
        "net_income": _first(data, "netIncome"),
        "eps": _first(data, "eps", "trailingEps"),
        "ebitda": _first(data, "ebitda"),
        "free_cash_flow": _first(data, "freeCashFlow"),
        "operating_cash_flow": _first(data, "operatingCashFlow"),
        "assets": _first(data, "totalAssets"),
        "liabilities": _first(data, "totalLiabilities"),
        "equity": _first(data, "totalEquity"),
        "cash": _first(data, "totalCash"),
        "debt": _first(data, "totalDebt"),
        "roe": _first(data, "roe", "returnOnEquity"),
        "roa": _first(data, "roa", "returnOnAssets"),
        "gross_margin": data.get("grossMargin"),
        "operating_margin": data.get("operatingMargin"),
        "net_margin": data.get("netMargin"),
        "pe": data.get("pe"),
        "pbv": data.get("pbv"),
        "ps": data.get("ps"),
        "peg": data.get("peg"),
        "dividend_yield": data.get("dividendYield"),
        "debt_to_equity": data.get("debtToEquity"),
        "cash_flow_quality": data.get("cashFlowQuality"),
        "revenue_trend": _first(data, "revenueTrend", "revenueGrowth"),
        "net_profit_trend": _first(data, "netProfitTrend", "earningsGrowth"),
        "revenue_growth": data.get("revenueGrowth"),
        "earnings_growth": data.get("earningsGrowth"),
        "three_to_five_year_trend": data.get("threeToFiveYearTrend"),
        "intrinsic_value": data.get("intrinsicValue"),
    }
    if data.get("error") or all(value is None for value in facts.values()):
        return {
            "symbol": symbol,
            "applicable": True,
            "status": "unavailable",
            "message": "Financial statement data is currently unavailable from the configured provider.",
            "message_th": "ยังไม่มีข้อมูลงบการเงินจากผู้ให้บริการที่ตั้งค่าไว้",
            "facts": facts,
            "interpretation": {},
            "risks": ["Financial statement analysis is unavailable until provider data is returned."],
            "cautious_action_plan": ["Review official company filings before making any decision."],
            "source": data.get("source", "yfinance"),
            "provider_gap": data.get("error") or "Provider returned no equivalent statement, balance sheet, cash flow, valuation, or margin fields.",
            "disclaimer": "This is not financial advice.",
        }
    return {
        "symbol": symbol,
        "applicable": True,
        "status": "partial",
        "facts": facts,
        "interpretation": {
            "balance_sheet_strength": data.get("balanceSheetStrength"),
            "earnings_quality": data.get("earningsQuality"),
            "valuation_risk": data.get("valuationRisk"),
            "explanation_th": {
                "financial_health": "ดูหนี้สิน เงินสด และความสามารถในการสร้างกระแสเงินสดร่วมกัน",
                "growth": "ดูการเติบโตของรายได้และกำไร ไม่ใช้ตัวเลขเดียวตัดสิน",
                "profitability": "ROE ROA และ margin ช่วยบอกคุณภาพกำไร",
                "valuation": "P/E P/BV PEG และ dividend yield ต้องเทียบกับคู่แข่งและประวัติย้อนหลัง",
                "cash_flow": "Free cash flow ช่วยยืนยันว่ากำไรเป็นเงินสดจริงหรือไม่",
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


def _first(data: Dict[str, Any], *keys: str) -> Any:
    for key in keys:
        value = data.get(key)
        if value is not None:
            return value
    return None
