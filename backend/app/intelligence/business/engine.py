from __future__ import annotations

from collections import OrderedDict
from datetime import datetime, timezone
from typing import Any, Dict, List

from app.intelligence.business.models import (
    BusinessDomainAssessment,
    BusinessEvidenceItem,
    BusinessIntelligenceReport,
    BusinessIntelligenceVersionSet,
    BusinessRiskSignal,
)
from app.intelligence.financial import classify_asset_for_intelligence

BUSINESS_INTELLIGENCE_VERSION = "business-intelligence-v1"
BUSINESS_SCORING_VERSION = "business-scoring-v1"
BUSINESS_POLICY_VERSION = "business-policy-v1"
BUSINESS_EVIDENCE_VERSION = "business-evidence-v1"
_REPORT_CACHE: OrderedDict[tuple[str, str, str], Dict[str, Any]] = OrderedDict()
_MAX_CACHE_SIZE = 128

_UNVERIFIED_DOMAINS = {
    "competitive_advantage_evidence": ["market share evidence", "customer retention evidence", "brand power evidence"],
    "customer_concentration_risk": ["customer concentration disclosure", "revenue by customer"],
    "supplier_input_cost_risk": ["supplier dependency disclosure", "input cost sensitivity"],
    "management_execution_evidence": ["management track record evidence", "guidance delivery evidence"],
    "governance_evidence": ["board independence", "related-party transactions", "auditor observations"],
}


def business_intelligence_methodology() -> Dict[str, Any]:
    return {
        "status": "ok",
        "methodology_version": BUSINESS_INTELLIGENCE_VERSION,
        "scoring_version": BUSINESS_SCORING_VERSION,
        "policy_version": BUSINESS_POLICY_VERSION,
        "evidence_version": BUSINESS_EVIDENCE_VERSION,
        "objective": "Evaluate the quality and durability of the operating business using available evidence.",
        "relationship_to_financial_intelligence": {
            "financial_intelligence": "Primary evidence layer for corporate assets.",
            "business_intelligence": "Secondary evidence layer explaining why reported numbers may be sustainable, improving, weakening, or vulnerable.",
            "activation_policy": "Business Intelligence is not merged into opportunity scoring until a Founder-approved methodology migration is versioned.",
        },
        "domains": [
            "business_model_quality",
            "revenue_model_quality",
            "competitive_position",
            "competitive_advantage_evidence",
            "pricing_power_evidence",
            "customer_concentration_risk",
            "supplier_input_cost_risk",
            "management_execution_evidence",
            "capital_allocation_evidence",
            "governance_evidence",
            "industry_structure",
            "cyclicality",
            "regulatory_risk",
            "durability_of_growth",
            "business_risk",
        ],
        "non_claims": [
            "Does not fabricate competitive advantage, market share, management quality, governance quality, customer loyalty, or pricing power.",
            "Does not predict returns.",
            "Does not replace investor judgment.",
        ],
        "cache": {"cacheable": True, "bounded_entries": _MAX_CACHE_SIZE},
        "disclaimer": "This is not financial advice.",
    }


def build_business_intelligence_report(
    symbol: str,
    quote: Dict[str, Any] | None = None,
    financial_report: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    quote = quote or {}
    financial_report = financial_report or {}
    classification = financial_report.get("classification") or classify_asset_for_intelligence(symbol, quote).__dict__
    normalized_symbol = str(classification.get("symbol") or symbol)
    source_timestamp = str(quote.get("timestamp") or financial_report.get("facts", {}).get("timestamp") or "latest_available")
    cache_key = (normalized_symbol, BUSINESS_INTELLIGENCE_VERSION, source_timestamp)
    cached = _REPORT_CACHE.get(cache_key)
    if cached is not None:
        _REPORT_CACHE.move_to_end(cache_key)
        return {**cached, "cache_metadata": {**cached.get("cache_metadata", {}), "cache_hit": True, "cache_key": ":".join(cache_key)}}

    if classification.get("primary_evidence_domain") != "financial_intelligence" or classification.get("fallback_status") == "not_applicable":
        report = _not_applicable_report(symbol, quote, financial_report, classification, cache_key)
    elif classification.get("selected_intelligence_profile") != "corporate_financial":
        report = _unsupported_boundary_report(symbol, financial_report, classification, cache_key)
    else:
        report = _corporate_report(symbol, quote, financial_report, classification, cache_key)

    _REPORT_CACHE[cache_key] = report
    _REPORT_CACHE.move_to_end(cache_key)
    while len(_REPORT_CACHE) > _MAX_CACHE_SIZE:
        _REPORT_CACHE.popitem(last=False)
    return report


def _corporate_report(symbol: str, quote: Dict[str, Any], financial_report: Dict[str, Any], classification: Dict[str, Any], cache_key: tuple[str, str, str]) -> Dict[str, Any]:
    facts = financial_report.get("facts") or {}
    provider = quote.get("source") or quote.get("provider") or "financial_intelligence"
    domains = [
        _business_model_quality(symbol, provider, classification, facts),
        _revenue_model_quality(symbol, provider, facts),
        _competitive_position(symbol, provider, classification),
        _unavailable_domain("competitive_advantage_evidence", "quality"),
        _pricing_power(symbol, provider, facts),
        _unavailable_domain("customer_concentration_risk", "risk"),
        _unavailable_domain("supplier_input_cost_risk", "risk"),
        _unavailable_domain("management_execution_evidence", "quality"),
        _capital_allocation(symbol, provider, facts),
        _unavailable_domain("governance_evidence", "governance"),
        _industry_structure(symbol, provider, classification),
        _cyclicality(symbol, provider, classification),
        _regulatory_risk(symbol, provider, classification),
        _durability_of_growth(symbol, provider, facts),
        _business_risk(symbol, provider, facts, financial_report),
    ]
    scored = [domain for domain in domains if domain.score is not None]
    score = round(sum(domain.score or 0 for domain in scored) / len(scored)) if scored else None
    completeness = round(sum(1 for domain in domains if domain.status in {"measured", "partial"}) / len(domains) * 100)
    confidence = _clamp(round((financial_report.get("confidence") or 0) * 0.55 + completeness * 0.45), 0, 100) if score is not None else 0
    risk_signals = _risk_signals(facts, financial_report)
    business_risk = _risk_level(risk_signals, score)
    all_evidence = [item for domain in domains for item in domain.evidence]
    missing = sorted({item for domain in domains for item in domain.missing_evidence})
    status = "measured" if score is not None and completeness >= 60 else "partial" if score is not None else "unavailable"
    return BusinessIntelligenceReport(
        symbol=symbol,
        status=status,
        applicable=True,
        asset_class=str(classification.get("asset_class") or "unknown"),
        profile=str(classification.get("selected_intelligence_profile") or "unknown"),
        business_intelligence_score=score,
        business_quality_score=score,
        business_risk=business_risk,
        business_confidence=confidence,
        business_completeness=completeness,
        domain_assessments=domains,
        business_evidence=all_evidence,
        missing_business_evidence=missing,
        risk_signals=risk_signals,
        limitations=[
            "Business evidence is limited to currently available provider and Financial Intelligence fields.",
            "Unavailable domains remain unavailable and are not inferred as facts.",
            "Business Intelligence is separate from Financial Intelligence and is not yet active in opportunity ranking weights.",
        ],
        evidence_based_narrative=_narrative(score, confidence, completeness, domains, missing),
        financial_intelligence_reference=_financial_reference(financial_report),
        versions=_versions(),
        cache_metadata=_cache_metadata(cache_key, False),
    ).to_dict()


def _not_applicable_report(symbol: str, quote: Dict[str, Any], financial_report: Dict[str, Any], classification: Dict[str, Any], cache_key: tuple[str, str, str]) -> Dict[str, Any]:
    asset_class = str(classification.get("asset_class") or quote.get("asset_type") or "unknown")
    return BusinessIntelligenceReport(
        symbol=symbol,
        status="not_applicable",
        applicable=False,
        asset_class=asset_class,
        profile=str(classification.get("selected_intelligence_profile") or "unknown"),
        business_intelligence_score=None,
        business_quality_score=None,
        business_risk="not_applicable",
        business_confidence=0,
        business_completeness=0,
        domain_assessments=[],
        business_evidence=[],
        missing_business_evidence=[],
        risk_signals=[],
        limitations=[f"Business Intelligence is designed for operating companies and is not applicable to asset class '{asset_class}'."],
        evidence_based_narrative={
            "summary_en": "Business Intelligence is not applicable to this asset type.",
            "alternative_fundamentals": ["macro context", "supply-demand context", "fund holdings", "on-chain context"],
            "decision_boundary": "Use the asset-specific evidence profile instead of corporate business quality.",
        },
        financial_intelligence_reference=_financial_reference(financial_report),
        versions=_versions(),
        cache_metadata=_cache_metadata(cache_key, False),
    ).to_dict()


def _unsupported_boundary_report(symbol: str, financial_report: Dict[str, Any], classification: Dict[str, Any], cache_key: tuple[str, str, str]) -> Dict[str, Any]:
    profile = str(classification.get("selected_intelligence_profile") or "unknown")
    return BusinessIntelligenceReport(
        symbol=symbol,
        status="unsupported",
        applicable=True,
        asset_class=str(classification.get("asset_class") or "unknown"),
        profile=profile,
        business_intelligence_score=None,
        business_quality_score=None,
        business_risk="unsupported",
        business_confidence=classification.get("classification_confidence", {}).get("score", 0),
        business_completeness=0,
        domain_assessments=[],
        business_evidence=[],
        missing_business_evidence=["sector-specific business evidence model"],
        risk_signals=[BusinessRiskSignal("sector_specific_business_model_required", "medium", "confirmed", [profile], "Sector-specific evidence is required before Business Intelligence can score this asset.")],
        limitations=[f"Profile '{profile}' requires a sector-specific Business Intelligence model."],
        evidence_based_narrative={"summary_en": "Business Intelligence needs a sector-specific model before scoring this asset.", "decision_boundary": "Unsupported is not a negative score."},
        financial_intelligence_reference=_financial_reference(financial_report),
        versions=_versions(),
        cache_metadata=_cache_metadata(cache_key, False),
    ).to_dict()


def _business_model_quality(symbol: str, provider: str, classification: Dict[str, Any], facts: Dict[str, Any]) -> BusinessDomainAssessment:
    evidence = []
    if classification.get("sector"):
        evidence.append(_evidence(symbol, "business_model_quality", "sector", provider, "available", classification.get("sector"), "Sector identifies the broad operating context but does not prove business quality."))
    if _number(facts.get("revenue")) is not None:
        evidence.append(_evidence(symbol, "business_model_quality", "revenue", provider, "available", facts.get("revenue"), "Reported revenue confirms an operating activity base."))
    score = _average_scores([60 if evidence else None, _growth_score(facts.get("revenue_growth")), _margin_score(facts.get("net_income"), facts.get("revenue"))])
    return _domain("business_model_quality", score, "quality", evidence, ["segment economics", "unit economics", "customer retention"], "Business model quality uses operating scale, growth, and margin evidence when available.")


def _revenue_model_quality(symbol: str, provider: str, facts: Dict[str, Any]) -> BusinessDomainAssessment:
    evidence = []
    if _number(facts.get("revenue")) is not None:
        evidence.append(_evidence(symbol, "revenue_model_quality", "revenue", provider, "available", facts.get("revenue"), "Revenue is available from provider financial evidence."))
    if _number(facts.get("revenue_growth")) is not None:
        evidence.append(_evidence(symbol, "revenue_model_quality", "revenue_growth", provider, "available", facts.get("revenue_growth"), "Revenue growth indicates direction, not durability by itself."))
    score = _average_scores([_growth_score(facts.get("revenue_growth")), _margin_score(facts.get("gross_profit"), facts.get("revenue"))])
    return _domain("revenue_model_quality", score, "quality", evidence, ["recurring revenue", "customer churn", "pricing terms"], "Revenue model quality uses growth and gross-margin evidence when available.")


def _competitive_position(symbol: str, provider: str, classification: Dict[str, Any]) -> BusinessDomainAssessment:
    evidence = []
    if classification.get("sector"):
        evidence.append(_evidence(symbol, "competitive_position", "sector", provider, "partial", classification.get("sector"), "Sector evidence gives context but does not prove market position."))
    if classification.get("industry"):
        evidence.append(_evidence(symbol, "competitive_position", "industry", provider, "partial", classification.get("industry"), "Industry evidence gives context but does not prove market share."))
    return _domain("competitive_position", None, "context", evidence, ["market share", "peer rank", "share change over time"], "Competitive position is context-only until peer and market-share evidence exists.")


def _pricing_power(symbol: str, provider: str, facts: Dict[str, Any]) -> BusinessDomainAssessment:
    evidence = []
    gross_margin = _ratio(facts.get("gross_profit"), facts.get("revenue"))
    if gross_margin is not None:
        evidence.append(_evidence(symbol, "pricing_power_evidence", "gross_margin", provider, "partial", gross_margin, "Gross margin can support pricing-power context but is not definitive proof."))
    score = _margin_to_score(gross_margin)
    return _domain("pricing_power_evidence", score, "quality", evidence, ["margin trend", "price increases", "unit volume trend"], "Pricing power is assessed conservatively from margin evidence only when available.")


def _capital_allocation(symbol: str, provider: str, facts: Dict[str, Any]) -> BusinessDomainAssessment:
    evidence = []
    if _number(facts.get("free_cash_flow")) is not None:
        evidence.append(_evidence(symbol, "capital_allocation_evidence", "free_cash_flow", provider, "available", facts.get("free_cash_flow"), "Free cash flow supports capital allocation flexibility."))
    if _number(facts.get("debt_to_equity")) is not None:
        evidence.append(_evidence(symbol, "capital_allocation_evidence", "debt_to_equity", provider, "available", facts.get("debt_to_equity"), "Debt level affects future capital allocation flexibility."))
    score = _average_scores([_cash_flow_score(facts.get("free_cash_flow"), facts.get("revenue")), _leverage_score(facts.get("debt_to_equity"))])
    return _domain("capital_allocation_evidence", score, "capital_allocation", evidence, ["dividend policy", "buyback policy", "capital expenditure discipline"], "Capital allocation uses cash-flow and leverage evidence where available.")


def _industry_structure(symbol: str, provider: str, classification: Dict[str, Any]) -> BusinessDomainAssessment:
    evidence = []
    if classification.get("industry"):
        evidence.append(_evidence(symbol, "industry_structure", "industry", provider, "inferred", classification.get("industry"), "Industry label is contextual and does not prove industry attractiveness."))
    return _domain("industry_structure", None, "context", evidence, ["industry concentration", "barriers to entry", "profit pool"], "Industry structure remains contextual until external industry evidence is connected.")


def _cyclicality(symbol: str, provider: str, classification: Dict[str, Any]) -> BusinessDomainAssessment:
    sector = str(classification.get("sector") or "").lower()
    cyclical = any(term in sector for term in ["energy", "materials", "industrial", "consumer cyclical", "real estate"])
    evidence = [_evidence(symbol, "cyclicality", "sector_mapping", provider, "inferred", classification.get("sector"), "Cyclicality is inferred from sector mapping and should be treated as contextual.")] if sector else []
    score = 45 if cyclical else 60 if sector else None
    return _domain("cyclicality", score, "risk", evidence, ["cycle sensitivity by segment", "historical margin cycle"], "Cyclicality uses sector context only and is not a confirmed company-specific risk.")


def _regulatory_risk(symbol: str, provider: str, classification: Dict[str, Any]) -> BusinessDomainAssessment:
    sector = str(classification.get("sector") or "").lower()
    regulated = any(term in sector for term in ["financial", "health", "energy", "utilities", "communication"])
    evidence = [_evidence(symbol, "regulatory_risk", "sector_mapping", provider, "inferred", classification.get("sector"), "Regulatory exposure is inferred from sector mapping and is not a legal assessment.")] if sector else []
    score = 45 if regulated else 60 if sector else None
    return _domain("regulatory_risk", score, "risk", evidence, ["specific regulation", "license conditions", "policy exposure"], "Regulatory risk uses sector context only until provider event evidence is available.")


def _durability_of_growth(symbol: str, provider: str, facts: Dict[str, Any]) -> BusinessDomainAssessment:
    evidence = []
    for key in ("revenue_growth", "earnings_growth", "free_cash_flow"):
        if _number(facts.get(key)) is not None:
            evidence.append(_evidence(symbol, "durability_of_growth", key, provider, "available", facts.get(key), f"{key} contributes to growth durability context."))
    score = _average_scores([_growth_score(facts.get("revenue_growth")), _growth_score(facts.get("earnings_growth")), _cash_flow_score(facts.get("free_cash_flow"), facts.get("revenue"))])
    return _domain("durability_of_growth", score, "quality", evidence, ["multi-year history", "retention", "reinvestment runway"], "Durability of growth requires multi-year evidence; current version uses available growth and cash-flow fields.")


def _business_risk(symbol: str, provider: str, facts: Dict[str, Any], financial_report: Dict[str, Any]) -> BusinessDomainAssessment:
    evidence = []
    if financial_report.get("risk_signals"):
        evidence.append(_evidence(symbol, "business_risk", "financial_risk_signals", provider, "available", len(financial_report.get("risk_signals") or []), "Financial risk signals are treated as business risk context."))
    score = 65
    if financial_report.get("risk_signals"):
        score -= min(35, len(financial_report.get("risk_signals") or []) * 12)
    leverage = _number(facts.get("debt_to_equity"))
    if leverage is not None and leverage > 2:
        score -= 15
    return _domain("business_risk", _clamp(score, 5, 95), "risk", evidence, ["litigation", "supplier risk", "customer concentration", "regulation"], "Business risk combines available financial risk signals with missing operational risk evidence.")


def _unavailable_domain(name: str, role: str) -> BusinessDomainAssessment:
    return BusinessDomainAssessment(name, None, "unavailable", role, [], _UNVERIFIED_DOMAINS.get(name, ["provider evidence"]), f"{name} is unavailable because no verified provider evidence is connected.", ["No synthetic evidence is created."])


def _domain(name: str, score: int | None, role: str, evidence: List[BusinessEvidenceItem], missing: List[str], explanation: str) -> BusinessDomainAssessment:
    status = "measured" if score is not None and evidence else "partial" if evidence else "unavailable"
    return BusinessDomainAssessment(name, score, status, role, evidence, missing, explanation, [] if evidence else ["Required evidence unavailable."])


def _risk_signals(facts: Dict[str, Any], financial_report: Dict[str, Any]) -> List[BusinessRiskSignal]:
    rows: List[BusinessRiskSignal] = []
    for signal in financial_report.get("risk_signals") or []:
        rows.append(BusinessRiskSignal(f"financial_{signal.get('code')}", signal.get("severity", "medium"), signal.get("status", "possible"), signal.get("evidence", []), signal.get("explanation_en", "Financial risk signal is present.")))
    if _number(facts.get("free_cash_flow")) is not None and facts["free_cash_flow"] < 0:
        rows.append(BusinessRiskSignal("negative_free_cash_flow", "medium", "confirmed", ["free_cash_flow < 0"], "Negative free cash flow can reduce business flexibility."))
    return rows


def _narrative(score: int | None, confidence: int, completeness: int, domains: List[BusinessDomainAssessment], missing: List[str]) -> Dict[str, Any]:
    strongest = [domain.domain for domain in domains if domain.score is not None and domain.score >= 65][:3]
    weakest = [domain.domain for domain in domains if domain.score is not None and domain.score <= 45][:3]
    summary = "Business Intelligence is unavailable because provider evidence is insufficient." if score is None else f"Business Intelligence Score is {score}/100 from available operating-business evidence."
    return {
        "summary_en": summary,
        "interpretation_en": "The score reflects evidence quality and business durability context, not a prediction of returns.",
        "strongest_supported_domains": strongest,
        "weakest_supported_domains": weakest,
        "missing_evidence": missing[:12],
        "confidence_note": f"Confidence {confidence}/100 measures evidence reliability and coverage.",
        "completeness_note": f"Completeness {completeness}/100 measures available business evidence coverage.",
        "decision_boundary": "Business Intelligence supports research. It does not issue personal investment advice.",
    }


def _financial_reference(financial_report: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "financial_intelligence_score": financial_report.get("financial_intelligence_score"),
        "financial_status": financial_report.get("status"),
        "financial_confidence": financial_report.get("confidence"),
        "financial_completeness": financial_report.get("completeness"),
        "versions": financial_report.get("versions"),
    }


def _evidence(symbol: str, domain: str, evidence_type: str, provider: str, status: str, value: Any, interpretation: str) -> BusinessEvidenceItem:
    now = datetime.now(timezone.utc).isoformat()
    return BusinessEvidenceItem(
        evidence_id=f"{symbol}:{domain}:{evidence_type}:{now}",
        domain=domain,
        evidence_type=evidence_type,
        provider=provider,
        status=status,
        verification_status="inferred" if status == "inferred" else "provider_reported",
        value=value,
        interpretation=interpretation,
        limitations=[] if status == "available" else ["Contextual evidence only."],
    )


def _versions() -> BusinessIntelligenceVersionSet:
    return BusinessIntelligenceVersionSet(BUSINESS_INTELLIGENCE_VERSION, BUSINESS_SCORING_VERSION, BUSINESS_POLICY_VERSION, BUSINESS_EVIDENCE_VERSION)


def _cache_metadata(cache_key: tuple[str, str, str], hit: bool) -> Dict[str, Any]:
    return {"cacheable": True, "cache_hit": hit, "cache_key": ":".join(cache_key), "bounded_entries": _MAX_CACHE_SIZE, "versioned": True}


def _average_scores(values: List[int | None]) -> int | None:
    measured = [value for value in values if value is not None]
    return round(sum(measured) / len(measured)) if measured else None


def _growth_score(value: Any) -> int | None:
    number = _number(value)
    if number is None:
        return None
    return _clamp(round(50 + number * 120), 5, 95)


def _margin_score(numerator: Any, denominator: Any) -> int | None:
    return _margin_to_score(_ratio(numerator, denominator))


def _margin_to_score(value: float | None) -> int | None:
    if value is None:
        return None
    return _clamp(round(45 + value * 100), 5, 95)


def _cash_flow_score(cash_flow: Any, revenue: Any) -> int | None:
    return _margin_score(cash_flow, revenue)


def _leverage_score(value: Any) -> int | None:
    number = _number(value)
    if number is None:
        return None
    return _clamp(round(85 - min(abs(number), 10) * 8), 5, 95)


def _ratio(numerator: Any, denominator: Any) -> float | None:
    top = _number(numerator)
    bottom = _number(denominator)
    if top is None or bottom in {None, 0}:
        return None
    return top / bottom


def _risk_level(risks: List[BusinessRiskSignal], score: int | None) -> str:
    if any(risk.severity == "critical" for risk in risks):
        return "critical"
    if any(risk.severity == "high" for risk in risks) or (score is not None and score < 40):
        return "high"
    if any(risk.severity == "medium" for risk in risks) or (score is not None and score < 55):
        return "medium"
    return "elevated" if score is not None else "unknown"


def _number(value: Any) -> float | None:
    return value if isinstance(value, (int, float)) and not isinstance(value, bool) else None


def _clamp(value: int, low: int, high: int) -> int:
    return max(low, min(high, value))
