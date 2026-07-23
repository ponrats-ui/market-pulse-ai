from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from math import sqrt
from typing import Any, Callable, Dict, Iterable, List, Literal

from app.data_hub.master_asset_registry import MasterAsset, list_registry_assets

SignalState = Literal["PASS", "FAIL", "UNKNOWN"]

METHODOLOGY_VERSION = "penny-opportunity-v1"
CONFIGURATION_VERSION = "penny-opportunity-policy-v1"

PENNY_WARNING_EN = (
    "Warning: Penny stocks and very low-priced equities carry extreme risk, including poor liquidity, severe "
    "volatility, limited information, shareholder dilution, delisting risk, and speculative or manipulative "
    "trading activity.\n\n"
    "The displayed score is a ranking based on available evidence. It is not a buy or sell recommendation, "
    "does not guarantee returns, and does not predict multi-bagger performance.\n\n"
    "Investors must independently review financial statements, official filings, disclosures, and risks, "
    "and should use only capital they can afford to lose entirely."
)

PENNY_WARNING_TH = (
    "คำเตือน: หุ้นเพนนีหรือหุ้นราคาต่ำมีความเสี่ยงสูงมาก รวมถึงสภาพคล่องต่ำ ความผันผวนสูง "
    "ข้อมูลจำกัด การเพิ่มทุนที่ทำให้ผู้ถือหุ้นเดิมถูกลดสัดส่วน ความเสี่ยงถูกเพิกถอน "
    "และพฤติกรรมเก็งกำไรหรือปั่นราคา\n\n"
    "คะแนนที่แสดงเป็นการจัดอันดับจากข้อมูลที่ระบบเข้าถึงได้ ไม่ใช่คำแนะนำให้ซื้อหรือขาย "
    "ไม่รับประกันผลตอบแทน และไม่สามารถรับรองการเติบโตหลายเท่าได้\n\n"
    "ผู้ลงทุนควรตรวจสอบงบการเงิน ข่าวประกาศ และความเสี่ยงด้วยตนเอง "
    "และใช้เฉพาะเงินที่สามารถสูญเสียได้ทั้งหมด"
)


@dataclass(frozen=True)
class PennyMarketPolicy:
    market: str
    country: str
    currency: str
    penny_price_maximum: float
    extended_price_maximum: float | None
    minimum_market_cap: float | None
    maximum_market_cap: float | None
    minimum_average_daily_volume: float
    minimum_average_daily_value: float
    maximum_allowed_spread: float | None
    minimum_trading_history_days: int
    stale_data_threshold_hours: int
    minimum_data_completeness: float
    minimum_data_confidence: float
    minimum_opportunity_score: float


POLICIES: Dict[str, PennyMarketPolicy] = {
    "TH": PennyMarketPolicy(
        market="TH",
        country="Thailand",
        currency="THB",
        penny_price_maximum=5.0,
        extended_price_maximum=None,
        minimum_market_cap=None,
        maximum_market_cap=None,
        minimum_average_daily_volume=100_000,
        minimum_average_daily_value=500_000,
        maximum_allowed_spread=None,
        minimum_trading_history_days=15,
        stale_data_threshold_hours=96,
        minimum_data_completeness=45,
        minimum_data_confidence=35,
        minimum_opportunity_score=35,
    ),
    "US": PennyMarketPolicy(
        market="US",
        country="United States",
        currency="USD",
        penny_price_maximum=5.0,
        extended_price_maximum=10.0,
        minimum_market_cap=None,
        maximum_market_cap=None,
        minimum_average_daily_volume=100_000,
        minimum_average_daily_value=1_000_000,
        maximum_allowed_spread=None,
        minimum_trading_history_days=15,
        stale_data_threshold_hours=96,
        minimum_data_completeness=45,
        minimum_data_confidence=35,
        minimum_opportunity_score=35,
    ),
}

THAI_CANDIDATE_SYMBOLS = [
    "TTB.BK",
    "TRUE.BK",
    "AAV.BK",
    "BTS.BK",
    "BCH.BK",
    "CHG.BK",
    "HANA.BK",
    "KCE.BK",
    "OR.BK",
    "BGRIM.BK",
    "GPSC.BK",
    "PTTGC.BK",
    "IVL.BK",
    "TOP.BK",
    "BCP.BK",
]

US_CANDIDATE_SYMBOLS = [
    "LUMN",
    "OPEN",
    "CLOV",
    "SNDL",
    "ACB",
    "WULF",
    "RIG",
    "BBAI",
    "IONQ",
    "SOFI",
    "RKLB",
    "OKLO",
    "SMR",
    "NNE",
    "PLTR",
]

QuoteFn = Callable[[str], Dict[str, Any]]
HistoryFn = Callable[[str, str, str], Dict[str, Any]]
NewsFn = Callable[[str, int], Dict[str, Any]]


def build_penny_opportunities(
    quote_fn: QuoteFn,
    history_fn: HistoryFn,
    news_fn: NewsFn | None = None,
    market: str | None = None,
    limit: int = 5,
) -> Dict[str, Any]:
    safe_limit = max(1, min(int(limit or 5), 20))
    selected_markets = _selected_markets(market)
    generated_at = datetime.now(timezone.utc).isoformat()
    registry = _candidate_registry(selected_markets)
    candidates = []
    excluded = 0
    unknown = 0
    provider_status: List[Dict[str, Any]] = []

    for asset in registry:
        try:
            policy = _policy_for_asset(asset)
            if policy is None:
                excluded += 1
                continue
            candidate = evaluate_candidate(asset, policy, quote_fn, history_fn, news_fn)
            provider_status.extend(candidate.get("provider_status", []))
            if candidate["hard_disqualified"]:
                excluded += 1
                continue
            if not candidate["eligible_for_top5"]:
                if candidate["data_completeness"] < policy.minimum_data_completeness:
                    unknown += 1
                else:
                    excluded += 1
                continue
            candidates.append(candidate)
        except Exception as exc:  # pragma: no cover - defensive API isolation
            excluded += 1
            provider_status.append({
                "symbol": getattr(asset, "canonical_symbol", "unknown"),
                "provider": "penny_opportunity_engine",
                "stage": "candidate_processing",
                "status": "error",
                "reason": exc.__class__.__name__,
                "timestamp": generated_at,
            })

    ranked = sorted(
        candidates,
        key=lambda item: (
            -item["penny_opportunity_score"],
            -item["data_confidence"],
            item["severe_risk_count"],
            -item["scores"]["liquidity"],
            item["symbol"],
        ),
    )
    items = [{**item, "rank": index + 1} for index, item in enumerate(ranked[:safe_limit])]
    status = "ok" if items else ("partial" if provider_status else "unavailable")
    return {
        "status": status,
        "category": "penny_opportunity",
        "methodology_version": METHODOLOGY_VERSION,
        "configuration_version": CONFIGURATION_VERSION,
        "generated_at": generated_at,
        "markets": selected_markets,
        "warning": {"th": PENNY_WARNING_TH, "en": PENNY_WARNING_EN},
        "qualification": {
            "universe_size": len(registry),
            "eligible_count": len(candidates),
            "ranked_count": len(items),
            "excluded_count": excluded,
            "unknown_count": unknown,
        },
        "items": [_public_item(item) for item in items],
        "limitations": [
            "Initial methodology uses bounded candidate pools to preserve production memory.",
            "Catalyst evidence is shown only when a configured provider returns verifiable items.",
            "Missing fundamentals, liquidity, or catalyst data reduce confidence instead of being replaced.",
            "Scores are transparent research rankings, not scientifically validated predictions.",
        ],
        "provider_status": provider_status[:50],
        "disclaimer": "This is not financial advice.",
    }


def evaluate_candidate(
    asset: MasterAsset,
    policy: PennyMarketPolicy,
    quote_fn: QuoteFn,
    history_fn: HistoryFn,
    news_fn: NewsFn | None = None,
) -> Dict[str, Any]:
    symbol = asset.canonical_symbol
    provider_symbol = asset.provider_symbols.get("yfinance") or symbol
    quote = quote_fn(provider_symbol)
    provider_status = [_provider_status(symbol, "quote", quote)]
    history: Dict[str, Any] = {"points": [], "source": "Unavailable", "error": "History not requested."}
    price = _number(quote.get("price"))
    classification = classify_price(price, policy)
    missing_data: List[str] = []
    hard_flags: List[Dict[str, Any]] = []
    risk_flags: List[Dict[str, Any]] = []

    if quote.get("error") or price is None:
        hard_flags.append(_risk_flag("invalid_price", "CRITICAL", "confirmed", 100, "Provider did not return a valid current price."))
    if classification["status"] == "FAIL":
        hard_flags.append(_risk_flag("outside_price_policy", "MEDIUM", "confirmed", 0, "Price is outside configured penny or low-priced policy."))
    if asset.asset_class != "equity" or asset.asset_type not in {"stock", "foreign_stock", "preferred_stock", "adr"}:
        hard_flags.append(_risk_flag("not_operating_company_equity", "CRITICAL", "confirmed", 100, "Instrument is not classified as an operating-company equity."))

    if not hard_flags:
        history = history_fn(provider_symbol, "3mo", "1d")
        provider_status.append(_provider_status(symbol, "history", history))

    closes = _history_closes(history)
    volumes = _history_volumes(history)
    history_status = _pass_fail_unknown(len(closes) >= policy.minimum_trading_history_days, bool(closes))
    if history_status == "FAIL":
        hard_flags.append(_risk_flag("insufficient_trading_history", "HIGH", "confirmed", 30, "Provider history has fewer active trading days than policy requires."))

    liquidity = _liquidity_score(price, quote, volumes, policy)
    if liquidity["status"] == "FAIL":
        hard_flags.append(_risk_flag("insufficient_liquidity", "CRITICAL", "confirmed", 45, "Real provider volume or traded value is below policy minimum."))
    elif liquidity["status"] == "UNKNOWN":
        risk_flags.append(_risk_flag("liquidity_unknown", "MEDIUM", "unknown", 12, "Liquidity metrics are unavailable from provider."))

    financial = _financial_score(quote, missing_data)
    growth = _growth_score(quote, missing_data)
    technical = _technical_score(closes, volumes, quote, missing_data, risk_flags)
    catalyst = _catalyst_score(symbol, news_fn, missing_data, provider_status)
    completeness = _data_completeness(quote, history, catalyst)
    confidence = _data_confidence(completeness, liquidity, financial, growth, technical, catalyst, risk_flags)
    risk_penalty = _risk_penalty([*hard_flags, *risk_flags], liquidity, technical)
    base_score = (
        liquidity["score"] * 0.24
        + financial["score"] * 0.18
        + growth["score"] * 0.18
        + technical["score"] * 0.25
        + (catalyst["score"] if catalyst["score"] is not None else 35) * 0.10
        + _market_context_score(asset, quote) * 0.05
    )
    score = _clamp(round(base_score - risk_penalty), 0, 100)
    risk_level = _risk_level(risk_penalty, [*hard_flags, *risk_flags])
    hard_disqualified = bool(hard_flags) or completeness < policy.minimum_data_completeness
    eligible = (
        not hard_disqualified
        and liquidity["status"] == "PASS"
        and score >= policy.minimum_opportunity_score
        and confidence >= policy.minimum_data_confidence
    )
    return {
        "rank": None,
        "symbol": symbol,
        "provider_symbol": provider_symbol,
        "name": asset.company_name,
        "market": policy.market,
        "exchange": asset.exchange or quote.get("exchange"),
        "currency": quote.get("currency") or policy.currency,
        "classification": classification["classification"],
        "classification_status": classification["status"],
        "market_classification": classification["label"],
        "price": price,
        "price_timestamp": quote.get("timestamp"),
        "penny_opportunity_score": score,
        "data_confidence": confidence,
        "data_completeness": completeness,
        "scores": {
            "financial": financial["score"],
            "growth": growth["score"],
            "technical": technical["score"],
            "liquidity": liquidity["score"],
            "catalyst": catalyst["score"],
            "market_context": _market_context_score(asset, quote),
        },
        "factor_availability": {
            "price": "PASS" if price is not None else "FAIL",
            "liquidity": liquidity["status"],
            "history": history_status,
            "fundamentals": financial["status"],
            "growth": growth["status"],
            "catalyst": catalyst["status"],
        },
        "risk_penalty": risk_penalty,
        "risk_level": risk_level,
        "severe_risk_count": len([flag for flag in [*hard_flags, *risk_flags] if flag["severity"] in {"HIGH", "CRITICAL"}]),
        "strengths": _strengths(liquidity, financial, growth, technical, catalyst),
        "risks": [*hard_flags, *risk_flags],
        "missing_data": sorted(set(missing_data)),
        "catalysts": catalyst["items"],
        "explanation": _explanation(symbol, score, confidence, [*hard_flags, *risk_flags], missing_data, catalyst),
        "provider_attribution": _provider_attribution(quote, history, catalyst),
        "provider_status": provider_status,
        "hard_disqualified": hard_disqualified,
        "eligible_for_top5": eligible,
    }


def classify_price(price: float | None, policy: PennyMarketPolicy) -> Dict[str, Any]:
    if price is None:
        return {"status": "UNKNOWN", "classification": "unavailable", "label": "Data unavailable"}
    if price <= policy.penny_price_maximum:
        return {"status": "PASS", "classification": "penny_stock", "label": "Penny Stock"}
    if policy.extended_price_maximum is not None and price <= policy.extended_price_maximum:
        return {"status": "PASS", "classification": "low_priced_small_cap", "label": "Low-Priced Small Cap"}
    return {"status": "FAIL", "classification": "outside_policy", "label": "Outside configured low-price policy"}


def _candidate_registry(markets: Iterable[str]) -> List[MasterAsset]:
    wanted = set()
    if "TH" in markets:
        wanted.update(THAI_CANDIDATE_SYMBOLS)
    if "US" in markets:
        wanted.update(US_CANDIDATE_SYMBOLS)
    assets = {asset.canonical_symbol: asset for asset in list_registry_assets(enabled_only=True, searchable_only=True)}
    return [assets[symbol] for symbol in sorted(wanted) if symbol in assets]


def _selected_markets(market: str | None) -> List[str]:
    if not market:
        return ["TH", "US"]
    value = market.strip().upper()
    if value in POLICIES:
        return [value]
    return []


def _policy_for_asset(asset: MasterAsset) -> PennyMarketPolicy | None:
    if asset.country == "Thailand" or asset.canonical_symbol.endswith(".BK"):
        return POLICIES["TH"]
    if asset.country in {"US", "United States"} or asset.exchange in {"NASDAQ", "NYSE", "NYSE Arca", "AMEX"}:
        return POLICIES["US"]
    return None


def _liquidity_score(price: float | None, quote: Dict[str, Any], volumes: List[float], policy: PennyMarketPolicy) -> Dict[str, Any]:
    volume = _number(quote.get("volume"))
    average_volume = _average(volumes) if volumes else _number(quote.get("average_volume"))
    traded_value = price * average_volume if price is not None and average_volume is not None else None
    if average_volume is None and volume is None:
        return {"score": 25, "status": "UNKNOWN", "evidence": ["Volume unavailable from provider."]}
    effective_volume = average_volume if average_volume is not None else volume
    if effective_volume is None or effective_volume <= 0:
        return {"score": 0, "status": "FAIL", "evidence": ["No meaningful trading volume returned by provider."]}
    volume_score = _threshold_score(effective_volume, policy.minimum_average_daily_volume, policy.minimum_average_daily_volume * 8)
    value_score = 45 if traded_value is None else _threshold_score(traded_value, policy.minimum_average_daily_value, policy.minimum_average_daily_value * 10)
    consistency = 50
    if volumes:
        active_ratio = len([item for item in volumes if item > 0]) / len(volumes)
        consistency = round(active_ratio * 100)
    score = round(volume_score * 0.45 + value_score * 0.35 + consistency * 0.20)
    status = "PASS" if effective_volume >= policy.minimum_average_daily_volume and (traded_value is None or traded_value >= policy.minimum_average_daily_value) else "FAIL"
    return {"score": _clamp(score, 0, 100), "status": status, "evidence": [f"Average volume: {round(effective_volume, 2)}", f"Average traded value: {round(traded_value, 2) if traded_value is not None else 'UNKNOWN'}"]}


def _financial_score(quote: Dict[str, Any], missing: List[str]) -> Dict[str, Any]:
    fields = {
        "debt_to_equity": quote.get("debt_to_equity"),
        "return_on_equity": quote.get("return_on_equity"),
        "return_on_assets": quote.get("return_on_assets"),
        "trailing_pe": quote.get("trailing_pe"),
        "price_to_book": quote.get("price_to_book"),
    }
    available = {key: _number(value) for key, value in fields.items() if _number(value) is not None}
    for key in fields:
        if key not in available:
            missing.append(key)
    if not available:
        return {"score": 35, "status": "UNKNOWN"}
    score = 50.0
    roe = available.get("return_on_equity")
    if roe is not None:
        score += _clamp(roe * 120, -25, 25)
    roa = available.get("return_on_assets")
    if roa is not None:
        score += _clamp(roa * 130, -20, 20)
    debt = available.get("debt_to_equity")
    if debt is not None:
        score += 12 if debt < 80 else -15 if debt > 200 else 0
    pe = available.get("trailing_pe")
    if pe is not None:
        score += 8 if 0 < pe < 25 else -8 if pe <= 0 or pe > 80 else 0
    return {"score": _clamp(round(score), 0, 100), "status": "PASS"}


def _growth_score(quote: Dict[str, Any], missing: List[str]) -> Dict[str, Any]:
    revenue = _number(quote.get("revenue_growth"))
    earnings = _number(quote.get("earnings_growth"))
    if revenue is None:
        missing.append("revenue_growth")
    if earnings is None:
        missing.append("earnings_growth")
    if revenue is None and earnings is None:
        return {"score": 35, "status": "UNKNOWN"}
    values = []
    if revenue is not None:
        values.append(_clamp(50 + revenue * 100, 15, 90))
    if earnings is not None:
        values.append(_clamp(50 + earnings * 80, 15, 90))
    return {"score": round(sum(values) / len(values)), "status": "PASS"}


def _technical_score(closes: List[float], volumes: List[float], quote: Dict[str, Any], missing: List[str], risk_flags: List[Dict[str, Any]]) -> Dict[str, Any]:
    if len(closes) < 10:
        missing.append("sufficient_price_history")
        return {"score": 35, "status": "UNKNOWN"}
    latest = closes[-1]
    first = closes[0]
    performance = ((latest - first) / first * 100) if first else 0
    ma_short = _average(closes[-10:])
    ma_long = _average(closes[-30:]) if len(closes) >= 30 else _average(closes)
    volatility = _volatility(closes)
    volume_confirmed = False
    if len(volumes) >= 10 and volumes[-1] > 0:
        volume_confirmed = volumes[-1] >= (_average(volumes[-10:]) or 0) * 1.15
    score = 50 + _clamp(performance * 1.3, -25, 25)
    if ma_short is not None and ma_long is not None:
        score += 12 if ma_short >= ma_long else -10
    score += 8 if volume_confirmed else 0
    if volatility > 8:
        score -= 12
        risk_flags.append(_risk_flag("extreme_volatility", "HIGH", "confirmed", 16, "Recent provider history shows extreme daily volatility."))
    return {"score": _clamp(round(score), 0, 100), "status": "PASS"}


def _catalyst_score(symbol: str, news_fn: NewsFn | None, missing: List[str], provider_status: List[Dict[str, Any]]) -> Dict[str, Any]:
    if news_fn is None:
        missing.append("verified_catalyst_data")
        return {"score": None, "status": "UNKNOWN", "items": []}
    payload = news_fn(symbol, 5)
    provider_status.append(_provider_status(symbol, "news", payload))
    items = payload.get("items") if isinstance(payload, dict) else []
    if not items:
        missing.append("verified_catalyst_data")
        return {"score": None, "status": "UNKNOWN", "items": []}
    catalysts = []
    for item in items[:3]:
        title = item.get("headline") or item.get("title")
        source = item.get("source") or payload.get("source") or "provider"
        if title:
            catalysts.append({
                "type": "provider_news",
                "title": title,
                "evidence_source": source,
                "source_timestamp": item.get("published_at"),
                "source_url": item.get("url"),
                "freshness": "provider_returned",
                "confidence": "medium",
                "affected_score_component": "catalyst",
            })
    if not catalysts:
        missing.append("verified_catalyst_data")
        return {"score": None, "status": "UNKNOWN", "items": []}
    return {"score": min(80, 45 + len(catalysts) * 10), "status": "PASS", "items": catalysts}


def _data_completeness(quote: Dict[str, Any], history: Dict[str, Any], catalyst: Dict[str, Any]) -> int:
    checks = [
        quote.get("price") is not None,
        quote.get("volume") is not None,
        quote.get("change_percent") is not None,
        quote.get("market_cap") is not None,
        quote.get("debt_to_equity") is not None,
        quote.get("return_on_equity") is not None,
        quote.get("revenue_growth") is not None,
        len(_history_closes(history)) >= 10,
        catalyst.get("status") == "PASS",
        quote.get("timestamp") is not None,
    ]
    return round(sum(1 for item in checks if item) / len(checks) * 100)


def _data_confidence(completeness: int, liquidity: Dict[str, Any], financial: Dict[str, Any], growth: Dict[str, Any], technical: Dict[str, Any], catalyst: Dict[str, Any], risks: List[Dict[str, Any]]) -> int:
    score = completeness
    for factor in [liquidity, financial, growth, technical, catalyst]:
        if factor.get("status") == "UNKNOWN":
            score -= 6
        elif factor.get("status") == "FAIL":
            score -= 12
    score -= min(20, len([risk for risk in risks if risk["status"] == "unknown"]) * 4)
    return _clamp(round(score), 0, 100)


def _risk_penalty(risks: List[Dict[str, Any]], liquidity: Dict[str, Any], technical: Dict[str, Any]) -> int:
    penalty = sum(_number(risk.get("penalty")) or 0 for risk in risks)
    if liquidity.get("status") == "UNKNOWN":
        penalty += 6
    if technical.get("status") == "UNKNOWN":
        penalty += 5
    return _clamp(round(penalty), 0, 100)


def _market_context_score(asset: MasterAsset, quote: Dict[str, Any]) -> int:
    change = _number(quote.get("change_percent"))
    if change is None:
        return 45
    return _clamp(round(50 + change * 3), 20, 80)


def _public_item(item: Dict[str, Any]) -> Dict[str, Any]:
    return {key: value for key, value in item.items() if key not in {"hard_disqualified", "eligible_for_top5", "severe_risk_count", "provider_status"}}


def _strengths(liquidity: Dict[str, Any], financial: Dict[str, Any], growth: Dict[str, Any], technical: Dict[str, Any], catalyst: Dict[str, Any]) -> List[str]:
    rows = []
    if liquidity["status"] == "PASS":
        rows.append("Liquidity requirement passed with provider volume evidence.")
    if technical["score"] >= 60:
        rows.append("Technical and momentum evidence is constructive.")
    if growth["score"] >= 55:
        rows.append("Available growth metrics are improving.")
    if financial["score"] >= 55:
        rows.append("Available financial quality metrics are supportive.")
    if catalyst["status"] == "PASS":
        rows.append("Verified provider catalyst evidence is available.")
    return rows[:5]


def _explanation(symbol: str, score: int, confidence: int, risks: List[Dict[str, Any]], missing: List[str], catalyst: Dict[str, Any]) -> Dict[str, str]:
    catalyst_text = "verified catalyst evidence is available" if catalyst["status"] == "PASS" else "no verified catalyst data is available"
    risk_text = ", ".join(risk["code"] for risk in risks[:3]) or "no confirmed critical risk in available data"
    missing_text = ", ".join(sorted(set(missing))[:4]) or "no major missing factor from configured checks"
    return {
        "en": f"{symbol} ranked from real provider data with score {score}/100 and data confidence {confidence}/100. The ranking reflects liquidity, available fundamentals, growth, technical evidence, risk penalty, and {catalyst_text}. Main risk evidence: {risk_text}. Missing data: {missing_text}. This is a research ranking, not a buy or sell recommendation.",
        "th": f"{symbol} ถูกจัดอันดับจากข้อมูลผู้ให้บริการจริงด้วยคะแนน {score}/100 และ Data Confidence {confidence}/100 คะแนนนี้พิจารณาสภาพคล่อง พื้นฐานที่มีอยู่ การเติบโต เทคนิค ความเสี่ยง และสถานะ catalyst โดย {catalyst_text}. ความเสี่ยงหลัก: {risk_text}. ข้อมูลที่ยังขาด: {missing_text}. นี่คือการจัดอันดับเพื่อการศึกษา ไม่ใช่คำแนะนำซื้อขาย",
    }


def _risk_level(penalty: int, risks: List[Dict[str, Any]]) -> str:
    if any(risk["severity"] == "CRITICAL" for risk in risks) or penalty >= 60:
        return "critical"
    if any(risk["severity"] == "HIGH" for risk in risks) or penalty >= 35:
        return "high"
    if penalty >= 18:
        return "medium"
    return "elevated"


def _risk_flag(code: str, severity: str, status: str, penalty: int, explanation_en: str) -> Dict[str, Any]:
    return {
        "code": code,
        "severity": severity,
        "status": status,
        "penalty": penalty,
        "evidence": [explanation_en],
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "explanation": {"en": explanation_en, "th": explanation_en},
    }


def _provider_status(symbol: str, stage: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "symbol": symbol,
        "provider": payload.get("source") or payload.get("provider") or "Unavailable",
        "stage": stage,
        "status": "error" if payload.get("error") else "ok",
        "reason": payload.get("error") or payload.get("unavailable_reason") or payload.get("message"),
        "duration_ms": None,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


def _provider_attribution(quote: Dict[str, Any], history: Dict[str, Any], catalyst: Dict[str, Any]) -> List[Dict[str, Any]]:
    providers = [
        {"provider": quote.get("source", "Unavailable"), "data_type": "quote", "timestamp": quote.get("timestamp")},
        {"provider": history.get("source") or history.get("provider") or "Unavailable", "data_type": "history", "timestamp": history.get("data_timestamp") or history.get("requested_at")},
    ]
    if catalyst.get("status") == "PASS":
        providers.append({"provider": "news_provider", "data_type": "catalyst", "timestamp": None})
    return providers


def _history_closes(history: Dict[str, Any]) -> List[float]:
    return [_number(point.get("close")) for point in history.get("points", []) if isinstance(point, dict) and _number(point.get("close")) is not None]


def _history_volumes(history: Dict[str, Any]) -> List[float]:
    return [_number(point.get("volume")) for point in history.get("points", []) if isinstance(point, dict) and _number(point.get("volume")) is not None]


def _number(value: Any) -> float | None:
    return value if isinstance(value, (int, float)) and not isinstance(value, bool) else None


def _average(values: List[float]) -> float | None:
    return sum(values) / len(values) if values else None


def _volatility(closes: List[float]) -> float:
    returns = [((closes[index] - closes[index - 1]) / closes[index - 1]) * 100 for index in range(1, len(closes)) if closes[index - 1]]
    if len(returns) < 2:
        return 0
    mean = sum(returns) / len(returns)
    variance = sum((item - mean) ** 2 for item in returns) / (len(returns) - 1)
    return sqrt(variance)


def _threshold_score(value: float, minimum: float, strong: float) -> int:
    if value < minimum:
        return _clamp(round(value / minimum * 45), 0, 45)
    return _clamp(round(55 + (value - minimum) / max(strong - minimum, 1) * 45), 55, 100)


def _pass_fail_unknown(condition: bool, available: bool) -> SignalState:
    if not available:
        return "UNKNOWN"
    return "PASS" if condition else "FAIL"


def _clamp(value: float | int, low: int, high: int) -> int:
    return int(max(low, min(high, value)))
