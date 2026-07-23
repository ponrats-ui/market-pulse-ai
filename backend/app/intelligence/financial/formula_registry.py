from __future__ import annotations

from typing import Any, Callable

from app.intelligence.financial.models import FinancialMetricDefinition, FinancialMetricValue

FORMULA_VERSION = "financial-formula-v1"


def metric_definitions() -> dict[str, FinancialMetricDefinition]:
    return {
        "gross_margin": FinancialMetricDefinition("gross_margin", "Gross margin", "gross_profit / revenue", ["gross_profit", "revenue"], "profitability", "positive", ["Negative or zero revenue makes this unavailable."]),
        "operating_margin": FinancialMetricDefinition("operating_margin", "Operating margin", "operating_income / revenue", ["operating_income", "revenue"], "profitability", "positive", ["Negative or zero revenue makes this unavailable."]),
        "net_margin": FinancialMetricDefinition("net_margin", "Net margin", "net_income / revenue", ["net_income", "revenue"], "profitability", "positive", ["One-time items can distort net income."]),
        "roe": FinancialMetricDefinition("roe", "Return on equity", "net_income / equity", ["net_income", "equity"], "profitability", "positive", ["Very small or negative equity makes ROE unreliable."]),
        "roa": FinancialMetricDefinition("roa", "Return on assets", "net_income / assets", ["net_income", "assets"], "efficiency", "positive", ["Asset-light business models require peer context."]),
        "current_ratio": FinancialMetricDefinition("current_ratio", "Current ratio", "current_assets / current_liabilities", ["current_assets", "current_liabilities"], "financial_health", "context", ["Unavailable when current asset/liability fields are missing."]),
        "debt_to_equity": FinancialMetricDefinition("debt_to_equity", "Debt to equity", "provider debt-to-equity or debt / equity", ["debt_to_equity"], "balance_sheet_strength", "risk", ["Not suitable for banks and insurers without sector adjustment."]),
        "debt_to_assets": FinancialMetricDefinition("debt_to_assets", "Debt to assets", "debt / assets", ["debt", "assets"], "balance_sheet_strength", "risk", ["Debt structure and maturity are not visible in generic provider payloads."]),
        "cash_to_debt": FinancialMetricDefinition("cash_to_debt", "Cash to debt", "cash / debt", ["cash", "debt"], "financial_health", "context", ["A high value does not alone prove solvency."]),
        "free_cash_flow_margin": FinancialMetricDefinition("free_cash_flow_margin", "Free cash flow margin", "free_cash_flow / revenue", ["free_cash_flow", "revenue"], "cash_flow_quality", "positive", ["Capital expenditure timing can distort a single period."]),
        "cash_conversion": FinancialMetricDefinition("cash_conversion", "Cash conversion", "operating_cash_flow / net_income", ["operating_cash_flow", "net_income"], "earnings_quality", "positive", ["Unavailable or noisy when net income is near zero."]),
        "pe": FinancialMetricDefinition("pe", "P/E", "provider trailing PE", ["pe"], "valuation_context", "context", ["Must be compared to peers and history."]),
        "pbv": FinancialMetricDefinition("pbv", "P/BV", "provider price to book", ["pbv"], "valuation_context", "context", ["Book value can be less meaningful for asset-light companies."]),
    }


def calculate_metric(metric_id: str, facts: dict[str, Any]) -> FinancialMetricValue:
    definitions = metric_definitions()
    definition = definitions[metric_id]
    missing = [field for field in definition.required_fields if _number(facts.get(field)) is None]
    if missing:
        return FinancialMetricValue(metric_id, None, "unavailable", definition.formula, {field: facts.get(field) for field in definition.required_fields}, missing, "Required evidence is unavailable.")
    value = _CALCULATORS.get(metric_id, lambda data: _number(data.get(metric_id)))(facts)
    if value is None:
        return FinancialMetricValue(metric_id, None, "unavailable", definition.formula, {field: facts.get(field) for field in definition.required_fields}, definition.required_fields, "Formula could not be calculated safely.")
    return FinancialMetricValue(metric_id, value, "measured", definition.formula, {field: facts.get(field) for field in definition.required_fields}, [], _interpret(metric_id, value))


def _ratio(numerator: Any, denominator: Any) -> float | None:
    top = _number(numerator)
    bottom = _number(denominator)
    if top is None or bottom in {None, 0}:
        return None
    return top / bottom


def _number(value: Any) -> float | None:
    return value if isinstance(value, (int, float)) and not isinstance(value, bool) else None


def _interpret(metric_id: str, value: float) -> str:
    if metric_id in {"gross_margin", "operating_margin", "net_margin", "free_cash_flow_margin"}:
        return f"{metric_id} measured at {value:.2%}."
    if metric_id in {"roe", "roa", "cash_conversion"}:
        return f"{metric_id} measured at {value:.2f}."
    return f"{metric_id} measured from provider evidence."


_CALCULATORS: dict[str, Callable[[dict[str, Any]], float | None]] = {
    "gross_margin": lambda data: _ratio(data.get("gross_profit"), data.get("revenue")),
    "operating_margin": lambda data: _ratio(data.get("operating_income"), data.get("revenue")),
    "net_margin": lambda data: _ratio(data.get("net_income"), data.get("revenue")),
    "roe": lambda data: _number(data.get("roe")) if _number(data.get("roe")) is not None else _ratio(data.get("net_income"), data.get("equity")),
    "roa": lambda data: _number(data.get("roa")) if _number(data.get("roa")) is not None else _ratio(data.get("net_income"), data.get("assets")),
    "current_ratio": lambda data: _ratio(data.get("current_assets"), data.get("current_liabilities")),
    "debt_to_equity": lambda data: _number(data.get("debt_to_equity")) if _number(data.get("debt_to_equity")) is not None else _ratio(data.get("debt"), data.get("equity")),
    "debt_to_assets": lambda data: _ratio(data.get("debt"), data.get("assets")),
    "cash_to_debt": lambda data: _ratio(data.get("cash"), data.get("debt")),
    "free_cash_flow_margin": lambda data: _ratio(data.get("free_cash_flow"), data.get("revenue")),
    "cash_conversion": lambda data: _number(data.get("cash_flow_quality")) if _number(data.get("cash_flow_quality")) is not None else _ratio(data.get("operating_cash_flow"), data.get("net_income")),
    "pe": lambda data: _number(data.get("pe")),
    "pbv": lambda data: _number(data.get("pbv")),
}
