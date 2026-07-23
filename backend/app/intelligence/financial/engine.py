from __future__ import annotations

from collections import OrderedDict
from dataclasses import asdict
from datetime import datetime, timezone
from typing import Any, Callable, Dict, List

from app.intelligence.financial.classification import classify_asset_for_intelligence
from app.intelligence.financial.formula_registry import FORMULA_VERSION, calculate_metric, metric_definitions
from app.data_hub.master_asset_registry import MasterAsset
from app.intelligence.financial.models import FinancialIntelligenceReport, FinancialIntelligenceVersionSet, FinancialRiskSignal, FinancialSubscore
from app.intelligence.financial.profiles import PRIMARY_FINANCIAL_WEIGHT_RANGE, PRIMARY_FINANCIAL_WEIGHT_TARGET, PROFILE_VERSION, get_profile

FINANCIAL_INTELLIGENCE_VERSION = "financial-intelligence-v1"
FINANCIAL_SCORING_VERSION = "financial-scoring-v1"
PRIMARY_EVIDENCE_POLICY_VERSION = "primary-evidence-policy-v1"
_REPORT_CACHE: OrderedDict[tuple[str, str, str, str, str], Dict[str, Any]] = OrderedDict()
_MAX_CACHE_SIZE = 128


def financial_intelligence_methodology() -> Dict[str, Any]:
    return {
        "status": "ok",
        "methodology_version": FINANCIAL_INTELLIGENCE_VERSION,
        "formula_version": FORMULA_VERSION,
        "scoring_version": FINANCIAL_SCORING_VERSION,
        "policy_version": PRIMARY_EVIDENCE_POLICY_VERSION,
        "profile_version": PROFILE_VERSION,
        "primary_evidence_policy": {
            "corporate_assets": "Financial Intelligence is the primary evidence layer for corporate assets.",
            "target_weight": PRIMARY_FINANCIAL_WEIGHT_TARGET,
            "allowed_range": PRIMARY_FINANCIAL_WEIGHT_RANGE,
            "rules": [
                "Corporate opportunity engines must not configure Financial Intelligence below 45% without a versioned exception.",
                "No other single positive domain may exceed the Financial Intelligence weight.",
                "Confidence and completeness remain metadata and eligibility controls, not positive score bonuses.",
                "Risk penalties remain separate from positive factor weights.",
            ],
        },
        "models": ["general_operating_company", "financial_institution_boundary", "insurance_boundary", "reit_boundary", "fund_boundary"],
        "metric_definitions": {key: asdict(value) for key, value in metric_definitions().items()},
        "limitations": [
            "Financial reporting may be delayed, incomplete, restated, unaudited, inconsistent, manipulated, or affected by accounting policy.",
            "The model does not predict returns and does not replace investor judgment.",
        ],
        "cache": {"cacheable": True, "bounded_entries": _MAX_CACHE_SIZE},
        "disclaimer": "This is not financial advice.",
    }


def build_financial_intelligence_report(symbol: str, provider_payload: Dict[str, Any] | None, quote: Dict[str, Any] | None = None, asset: MasterAsset | None = None) -> Dict[str, Any]:
    provider_payload = provider_payload or {}
    quote = quote or {}
    classification = classify_asset_for_intelligence(symbol, quote, asset)
    profile = get_profile(classification.selected_intelligence_profile)
    source_timestamp = str(provider_payload.get("timestamp") or quote.get("timestamp") or "latest_available")
    cache_key = (classification.symbol, FINANCIAL_INTELLIGENCE_VERSION, FORMULA_VERSION, FINANCIAL_SCORING_VERSION, source_timestamp)
    cached = _REPORT_CACHE.get(cache_key)
    if cached is not None:
        _REPORT_CACHE.move_to_end(cache_key)
        return {**cached, "cache_metadata": {**cached.get("cache_metadata", {}), "cache_hit": True, "cache_key": ":".join(cache_key)}}

    if profile.primary_evidence_domain != "financial_intelligence" or classification.fallback_status == "not_applicable":
        report = _not_applicable_report(symbol, provider_payload, quote, classification, profile, cache_key)
    elif profile.profile_type != "corporate_financial":
        report = _boundary_report(symbol, provider_payload, quote, classification, profile, cache_key)
    else:
        report = _general_corporate_report(symbol, provider_payload, quote, classification, profile, cache_key)
    _REPORT_CACHE[cache_key] = report
    _REPORT_CACHE.move_to_end(cache_key)
    while len(_REPORT_CACHE) > _MAX_CACHE_SIZE:
        _REPORT_CACHE.popitem(last=False)
    return report


def validate_primary_evidence_policy(active_weights: Dict[str, float]) -> Dict[str, Any]:
    financial = active_weights.get("financial_intelligence", active_weights.get("financial"))
    errors: List[str] = []
    if financial is None:
        errors.append("missing_financial_intelligence_weight")
    elif financial < PRIMARY_FINANCIAL_WEIGHT_RANGE[0]:
        errors.append("financial_intelligence_below_minimum")
    if financial is not None:
        for domain, weight in active_weights.items():
            if domain not in {"financial", "financial_intelligence"} and weight > financial:
                errors.append(f"domain_exceeds_financial_intelligence:{domain}")
    return {"valid": not errors, "errors": errors, "financial_weight": financial, "policy_version": PRIMARY_EVIDENCE_POLICY_VERSION}


def _general_corporate_report(symbol: str, provider_payload: Dict[str, Any], quote: Dict[str, Any], classification, profile, cache_key) -> Dict[str, Any]:
    facts = _normalize_facts(provider_payload, quote)
    metrics = {metric_id: calculate_metric(metric_id, facts) for metric_id in metric_definitions()}
    domains = [
        _domain("financial_health", 0.12, [metrics["current_ratio"], metrics["cash_to_debt"]], "context"),
        _domain("profitability", 0.15, [metrics["gross_margin"], metrics["operating_margin"], metrics["net_margin"], metrics["roe"], metrics["roa"]], "positive"),
        _domain("growth_quality", 0.10, [_simple_metric("revenue_growth", facts.get("revenue_growth")), _simple_metric("earnings_growth", facts.get("earnings_growth"))], "positive"),
        _domain("cash_flow_quality", 0.14, [metrics["free_cash_flow_margin"], metrics["cash_conversion"]], "positive"),
        _domain("balance_sheet_strength", 0.12, [metrics["debt_to_equity"], metrics["debt_to_assets"], metrics["cash_to_debt"]], "risk"),
        _domain("efficiency", 0.06, [metrics["roa"]], "positive"),
        _domain("earnings_quality", 0.10, [metrics["cash_conversion"]], "risk"),
        _domain("accounting_quality", 0.07, [_accounting_metric(provider_payload)], "risk"),
        _domain("valuation_context", 0.09, [metrics["pe"], metrics["pbv"]], "context"),
        _domain("financial_risk", 0.05, [], "risk"),
    ]
    measured_domains = [domain for domain in domains if domain.score is not None]
    completeness = _completeness(metrics, provider_payload)
    confidence = _confidence(completeness, measured_domains, provider_payload)
    score = round(sum((domain.score or 0) * domain.weight for domain in measured_domains) / max(sum(domain.weight for domain in measured_domains), 0.01)) if measured_domains else None
    risks = _risk_signals(facts, metrics)
    status = "measured" if score is not None and completeness >= 60 else "partial" if score is not None else "unavailable"
    report = FinancialIntelligenceReport(
        symbol=symbol,
        status=status,
        applicable=True,
        classification=classification,
        profile=profile,
        model_id="general_operating_company",
        financial_intelligence_score=score,
        score_status="measured" if status == "measured" else "partial" if score is not None else "unavailable",
        confidence=confidence,
        completeness=completeness,
        primary_evidence_domain="financial_intelligence",
        primary_evidence_weight=PRIMARY_FINANCIAL_WEIGHT_TARGET,
        domain_subscores=domains,
        risk_signals=risks,
        facts=facts,
        evidence_metadata=_evidence_metadata(symbol, provider_payload, facts, metrics),
        missing_evidence=sorted({missing for metric in metrics.values() for missing in metric.missing_inputs}),
        limitations=[*profile.limitations, "Missing values remain unavailable and are not replaced with zero."],
        explanation=_explanation(score, confidence, completeness, risks),
        formula_version=FORMULA_VERSION,
        versions=_versions(),
        cache_metadata=_cache_metadata(cache_key, False),
    ).to_dict()
    return report


def _boundary_report(symbol: str, provider_payload: Dict[str, Any], quote: Dict[str, Any], classification, profile, cache_key) -> Dict[str, Any]:
    facts = _normalize_facts(provider_payload, quote)
    report = FinancialIntelligenceReport(
        symbol=symbol,
        status="unsupported",
        applicable=True,
        classification=classification,
        profile=profile,
        model_id=profile.financial_model,
        financial_intelligence_score=None,
        score_status="unavailable",
        confidence=classification.classification_confidence.score,
        completeness=0,
        primary_evidence_domain="financial_intelligence",
        primary_evidence_weight=PRIMARY_FINANCIAL_WEIGHT_TARGET,
        domain_subscores=[],
        risk_signals=[FinancialRiskSignal("sector_specific_model_required", "medium", "confirmed", [profile.limitations[0]], profile.limitations[0], profile.limitations[0])],
        facts=facts,
        evidence_metadata=_provider_metadata(symbol, provider_payload),
        missing_evidence=profile.minimum_evidence_requirements,
        limitations=profile.limitations,
        explanation={"summary_en": profile.limitations[0], "summary_th": profile.limitations[0], "decision_boundary": "Sector-specific evidence is required before measured scoring."},
        formula_version=FORMULA_VERSION,
        versions=_versions(),
        cache_metadata=_cache_metadata(cache_key, False),
    ).to_dict()
    return report


def _not_applicable_report(symbol: str, provider_payload: Dict[str, Any], quote: Dict[str, Any], classification, profile, cache_key) -> Dict[str, Any]:
    return FinancialIntelligenceReport(
        symbol=symbol,
        status="not_applicable",
        applicable=False,
        classification=classification,
        profile=profile,
        model_id=profile.financial_model,
        financial_intelligence_score=None,
        score_status="not_applicable",
        confidence=classification.classification_confidence.score,
        completeness=0,
        primary_evidence_domain=classification.primary_evidence_domain,
        primary_evidence_weight=None,
        domain_subscores=[],
        risk_signals=[],
        facts={},
        evidence_metadata=_provider_metadata(symbol, provider_payload),
        missing_evidence=[],
        limitations=profile.limitations,
        explanation={"summary_en": profile.limitations[0], "summary_th": profile.limitations[0], "alternative_fundamentals": profile.secondary_evidence_domains},
        formula_version=FORMULA_VERSION,
        versions=_versions(),
        cache_metadata=_cache_metadata(cache_key, False),
    ).to_dict()


def _normalize_facts(data: Dict[str, Any], quote: Dict[str, Any]) -> Dict[str, Any]:
    source = data or {}
    facts = {
        "revenue": _first(source, "revenue", "totalRevenue"),
        "gross_profit": _first(source, "grossProfit", "gross_profit"),
        "operating_income": _first(source, "operatingIncome", "operating_income"),
        "net_income": _first(source, "netIncome", "net_income"),
        "operating_cash_flow": _first(source, "operatingCashFlow", "operating_cash_flow"),
        "free_cash_flow": _first(source, "freeCashFlow", "free_cash_flow"),
        "assets": _first(source, "totalAssets", "assets"),
        "liabilities": _first(source, "totalLiabilities", "liabilities"),
        "equity": _first(source, "totalEquity", "equity"),
        "cash": _first(source, "totalCash", "cash"),
        "debt": _first(source, "totalDebt", "debt"),
        "current_assets": _first(source, "currentAssets"),
        "current_liabilities": _first(source, "currentLiabilities"),
        "revenue_growth": _first(source, "revenueGrowth", "revenueTrend", "revenue_growth"),
        "earnings_growth": _first(source, "earningsGrowth", "netProfitTrend", "earnings_growth"),
        "roe": _first(source, "roe", "returnOnEquity", "return_on_equity"),
        "roa": _first(source, "roa", "returnOnAssets", "return_on_assets"),
        "pe": _first(source, "pe", "trailingPE", "trailing_pe") or quote.get("trailing_pe"),
        "pbv": _first(source, "pbv", "priceToBook", "price_to_book"),
        "debt_to_equity": _first(source, "debtToEquity", "debt_to_equity"),
        "cash_flow_quality": _first(source, "cashFlowQuality", "cash_flow_quality"),
    }
    if facts["debt_to_equity"] is None:
        debt = _number(facts.get("debt"))
        equity = _number(facts.get("equity"))
        if debt is not None and equity not in {None, 0}:
            facts["debt_to_equity"] = debt / equity
    return facts


def _domain(domain: str, weight: float, metrics: List[Any], role: str) -> FinancialSubscore:
    measured = [metric for metric in metrics if metric.status == "measured"]
    score = _score_metrics(domain, measured) if measured else None
    status = "measured" if measured and len(measured) == len(metrics) else "partial" if measured else "unavailable"
    return FinancialSubscore(domain, score, status, role, weight, metrics, f"{domain} uses {len(measured)} measured metric(s).", f"{domain} ใช้ตัวชี้วัดที่มีข้อมูล {len(measured)} รายการ", [] if measured else ["Required inputs unavailable."])


def _score_metrics(domain: str, metrics: List[Any]) -> int:
    values = [_metric_to_score(metric.metric_id, metric.value) for metric in metrics if metric.value is not None]
    return round(sum(values) / len(values)) if values else None


def _metric_to_score(metric_id: str, value: float) -> int:
    if metric_id in {"debt_to_equity", "debt_to_assets", "pe", "pbv"}:
        return _clamp(round(85 - min(abs(value), 10) * 6), 5, 95)
    if metric_id in {"cash_to_debt", "cash_conversion", "current_ratio"}:
        return _clamp(round(45 + min(value, 2) * 25), 5, 95)
    return _clamp(round(50 + value * 120), 5, 95)


def _simple_metric(metric_id: str, value: Any):
    from app.intelligence.financial.models import FinancialMetricValue

    numeric = _number(value)
    return FinancialMetricValue(metric_id, numeric, "measured" if numeric is not None else "unavailable", "provider field", {metric_id: value}, [] if numeric is not None else [metric_id], "Provider reported field." if numeric is not None else "Provider field unavailable.")


def _accounting_metric(provider_payload: Dict[str, Any]):
    from app.intelligence.financial.models import FinancialMetricValue

    missing = bool(provider_payload.get("error"))
    return FinancialMetricValue("accounting_quality", None if missing else 50, "unavailable" if missing else "partial", "provider status and field consistency", {"provider_error": provider_payload.get("error")}, ["provider_status"] if missing else [], "Accounting quality is limited to provider status in this sprint.")


def _risk_signals(facts: Dict[str, Any], metrics: Dict[str, Any]) -> List[FinancialRiskSignal]:
    rows: List[FinancialRiskSignal] = []
    if _number(facts.get("equity")) is not None and facts["equity"] <= 0:
        rows.append(FinancialRiskSignal("negative_equity", "high", "confirmed", ["equity <= 0"], "Negative equity is a material balance-sheet warning.", "ส่วนของผู้ถือหุ้นติดลบเป็นสัญญาณเตือนด้านงบดุล"))
    if metrics["cash_conversion"].status == "measured" and metrics["cash_conversion"].value is not None and metrics["cash_conversion"].value < 0.5:
        rows.append(FinancialRiskSignal("weak_cash_conversion", "medium", "confirmed", ["operating cash flow is weak relative to net income"], "Reported earnings are not strongly supported by operating cash flow.", "กำไรยังไม่แปลงเป็นกระแสเงินสดได้ดี"))
    if metrics["debt_to_equity"].status == "measured" and metrics["debt_to_equity"].value is not None and metrics["debt_to_equity"].value > 2:
        rows.append(FinancialRiskSignal("high_leverage", "medium", "confirmed", ["debt to equity above 2"], "Leverage is elevated and should be reviewed with maturity context.", "ภาระหนี้สูงและควรตรวจสอบกำหนดชำระหนี้เพิ่มเติม"))
    return rows


def _completeness(metrics: Dict[str, Any], provider_payload: Dict[str, Any]) -> int:
    if provider_payload.get("error"):
        return 0
    total = len(metrics)
    measured = sum(1 for metric in metrics.values() if metric.status == "measured")
    return round(measured / total * 100) if total else 0


def _confidence(completeness: int, domains: List[FinancialSubscore], provider_payload: Dict[str, Any]) -> int:
    if provider_payload.get("error"):
        return 0
    base = min(90, max(10, completeness))
    if any(domain.status == "partial" for domain in domains):
        base -= 5
    return _clamp(base, 0, 100)


def _evidence_metadata(symbol: str, provider_payload: Dict[str, Any], facts: Dict[str, Any], metrics: Dict[str, Any]) -> List[Dict[str, Any]]:
    source = provider_payload.get("source", "Unavailable")
    now = datetime.now(timezone.utc).isoformat()
    return [
        {
            "evidence_id": f"{symbol}:{key}:{now}",
            "evidence_type": "financial_metric",
            "provider": source,
            "source_timestamp": provider_payload.get("timestamp"),
            "retrieval_timestamp": now,
            "availability_status": "available" if value is not None else "unavailable",
            "verification_status": "provider_reported" if value is not None else "unverified",
            "supported_factor": key,
            "candidate_symbol": symbol,
            "transformation_summary": "Provider financial field normalized into Financial Intelligence facts.",
        }
        for key, value in facts.items()
    ]


def _provider_metadata(symbol: str, provider_payload: Dict[str, Any]) -> List[Dict[str, Any]]:
    return [{"evidence_id": f"{symbol}:provider-status", "provider": provider_payload.get("source", "Unavailable"), "availability_status": "failed" if provider_payload.get("error") else "unavailable", "data_limitations": [provider_payload.get("error")] if provider_payload.get("error") else []}]


def _explanation(score: int | None, confidence: int, completeness: int, risks: List[FinancialRiskSignal]) -> Dict[str, Any]:
    summary = "Financial Intelligence is unavailable because provider evidence is insufficient." if score is None else f"Financial Intelligence Score is {score}/100 from measured provider financial evidence."
    return {"summary_en": summary, "summary_th": summary, "confidence_note": f"Confidence {confidence}/100 measures evidence reliability, not probability of profit.", "completeness_note": f"Completeness {completeness}/100 measures evidence availability.", "risk_note": [risk.explanation_en for risk in risks], "decision_boundary": "Financial Intelligence supports analysis. It does not decide for the user."}


def _versions() -> FinancialIntelligenceVersionSet:
    return FinancialIntelligenceVersionSet(FINANCIAL_INTELLIGENCE_VERSION, FORMULA_VERSION, FINANCIAL_SCORING_VERSION, PRIMARY_EVIDENCE_POLICY_VERSION, PROFILE_VERSION)


def _cache_metadata(cache_key: tuple[str, str, str, str, str], hit: bool) -> Dict[str, Any]:
    return {"cacheable": True, "cache_hit": hit, "cache_key": ":".join(cache_key), "bounded_entries": _MAX_CACHE_SIZE, "versioned": True}


def _first(data: Dict[str, Any], *keys: str) -> Any:
    for key in keys:
        if data.get(key) is not None:
            return data.get(key)
    return None


def _number(value: Any) -> float | None:
    return value if isinstance(value, (int, float)) and not isinstance(value, bool) else None


def _clamp(value: int, low: int, high: int) -> int:
    return max(low, min(high, value))
