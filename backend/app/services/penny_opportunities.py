from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeoutError, as_completed
from dataclasses import dataclass, replace
from copy import deepcopy
from datetime import datetime, timedelta, timezone
from math import sqrt
import os
import platform
from threading import Lock
from time import monotonic
from typing import Any, Callable, Dict, Iterable, List, Literal
from uuid import uuid4

from app.data_hub.master_asset_registry import MasterAsset, list_registry_assets
from app.data_hub.provider_symbol_mapper import ProviderSymbolMapping, map_thai_yfinance_symbol
from app.intelligence.business import build_business_intelligence_report
from app.intelligence.financial import build_financial_intelligence_report, validate_primary_evidence_policy
from app.opportunities.models import AlgorithmChangeRecord, AlgorithmDefinition, AlgorithmFactorDefinition, AlgorithmIdentity, AlgorithmNeutralityDeclaration, AlgorithmRiskDefinition, AlgorithmTextBlock, ConflictOfInterestPolicy, DecisionBoundaryPolicy, EvidenceIntegrityPolicy, OpportunityEngineDefinition, OpportunityEngineRuntime, ProviderLimitationDisclosure, RankingIntegrityPolicy, TrustDisclosure, TrustPrinciple, UncertaintyDisclosurePolicy
from app.opportunities.ranking import rank_candidates
from app.opportunities.registry import register_engine
from app.opportunities.scheduler import OpportunityScheduler
from app.opportunities.snapshots import OpportunitySnapshotStore
from app.opportunities.transparency import algorithm_to_dict, validate_algorithm_definition
from app.providers.registry import get_provider

SignalState = Literal["PASS", "FAIL", "UNKNOWN"]

METHODOLOGY_VERSION = "thai-emerging-opportunity-v1"
POLICY_VERSION = "thai-emerging-policy-v1"
CONFIGURATION_VERSION = "thai-emerging-config-v1"
SCORE_VERSION = "thai-emerging-score-v1"
TRUST_POLICY_VERSION = "trust-policy-v1"
SCAN_FREQUENCY_MINUTES = 60
SCAN_MAX_WORKERS = max(1, min(int(os.getenv("PENNY_SCAN_MAX_WORKERS", "6")), 12))
SCAN_DEADLINE_SECONDS = max(5, min(int(os.getenv("PENNY_SCAN_DEADLINE_SECONDS", "45")), 120))
SCAN_MAX_SYMBOLS = max(25, min(int(os.getenv("PENNY_SCAN_MAX_SYMBOLS", "160")), 500))
SCAN_MAX_PROVIDER_BATCH = max(10, min(int(os.getenv("PENNY_SCAN_MAX_PROVIDER_BATCH", "80")), 120))
SCAN_BATCH_SIZE = max(5, min(int(os.getenv("PENNY_SCAN_BATCH_SIZE", "20")), 50))
SCAN_PROVIDER_TIMEOUT_SECONDS = max(3, min(int(os.getenv("PENNY_SCAN_PROVIDER_TIMEOUT_SECONDS", "20")), 60))
SCAN_RETRY_LIMIT = max(0, min(int(os.getenv("PENNY_SCAN_RETRY_LIMIT", "0")), 3))
_DEFAULT_SNAPSHOT_KEY = ("ALL", 5)
PENNY_ENGINE_ID = "penny-opportunity"
PENNY_CATEGORY = "penny_opportunity"
PENNY_FACTOR_WEIGHTS = {
    "financial": 0.55,
    "business": 0.20,
    "liquidity": 0.10,
    "technical": 0.05,
    "catalyst": 0.05,
    "market_context": 0.05,
}
THAI_PENNY_DEFAULT_MAX_SHARE_PRICE = 10.0
THAI_PENNY_SUPPORTED_THRESHOLDS = (5.0, 7.5, 10.0, 15.0)
THAI_PENNY_CUSTOM_RANGE = (5.0, 15.0)

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
    default_price_maximum: float
    supported_price_options: tuple[float, ...]
    custom_price_range: tuple[float, float] | None
    methodology: str
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
        penny_price_maximum=THAI_PENNY_DEFAULT_MAX_SHARE_PRICE,
        extended_price_maximum=15.0,
        default_price_maximum=THAI_PENNY_DEFAULT_MAX_SHARE_PRICE,
        supported_price_options=THAI_PENNY_SUPPORTED_THRESHOLDS,
        custom_price_range=THAI_PENNY_CUSTOM_RANGE,
        methodology="Thai Emerging Opportunity",
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
        default_price_maximum=5.0,
        supported_price_options=(5.0, 10.0),
        custom_price_range=None,
        methodology="US Penny Opportunity",
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

PENNY_ENGINE_DEFINITION = OpportunityEngineDefinition(
    engine_id=PENNY_ENGINE_ID,
    category=PENNY_CATEGORY,
    display_name="Penny Opportunity",
    methodology_version=METHODOLOGY_VERSION,
    score_version=SCORE_VERSION,
    policy_version=POLICY_VERSION,
    config_version=CONFIGURATION_VERSION,
    supported_markets=["TH", "US"],
    schedule_frequency_minutes=SCAN_FREQUENCY_MINUTES,
    maximum_results=5,
    shortlist_limit=50,
    minimum_score=min(policy.minimum_opportunity_score for policy in POLICIES.values()),
    minimum_confidence=min(policy.minimum_data_confidence for policy in POLICIES.values()),
    minimum_completeness=min(policy.minimum_data_completeness for policy in POLICIES.values()),
    freshness_policy={
        "stale_data_threshold_hours": max(policy.stale_data_threshold_hours for policy in POLICIES.values()),
    },
    factor_weights=PENNY_FACTOR_WEIGHTS,
    risk_policy={
        "deduplicate_by_family": True,
        "confirmed_critical_disqualifies": True,
        "unknown_risk_is_not_confirmed": True,
    },
    tie_breaker_policy=[
        "penny_opportunity_score DESC",
        "data_confidence DESC",
        "data_completeness DESC",
        "liquidity_score DESC",
        "risk_penalty ASC",
        "symbol ASC",
    ],
)


def build_penny_trust_disclosure() -> TrustDisclosure:
    principles = [
        TrustPrinciple("evidence_over_opinion", "หลักฐานมาก่อนความเห็น", "Evidence over Opinion", "ระบบให้ความสำคัญกับหลักฐานมากกว่าความเห็นหรือกระแส", "Evidence takes priority over opinion and market hype."),
        TrustPrinciple("transparency_over_mystery", "ความโปร่งใสมาก่อนความลึกลับ", "Transparency over Mystery", "ระบบต้องอธิบายวิธีคิด ไม่ขอให้ผู้ใช้เชื่อคะแนนโดยไม่มีที่มา", "The system explains methodology rather than asking users to trust unexplained results."),
        TrustPrinciple("assist_never_decide", "ช่วยวิเคราะห์ ไม่ตัดสินใจแทน", "Assist, Never Decide", "ระบบช่วยสนับสนุนการตัดสินใจลงทุน แต่ไม่ตัดสินใจแทนนักลงทุน", "The system supports investment decisions. It never makes them for the investor."),
        TrustPrinciple("explain_every_score", "ทุกคะแนนต้องอธิบายได้", "Every Score Must Earn Its Explanation", "ทุกคะแนนต้องมีหลักฐาน องค์ประกอบ วิธีคำนวณ และเหตุผลที่ตรวจสอบได้", "Every score must be supported by inspectable evidence, components, calculations, and rationale."),
        TrustPrinciple("visible_risk", "ความเสี่ยงต้องมองเห็นได้", "Every Risk Must Be Visible", "ระบบต้องแสดงความเสี่ยงควบคู่กับโอกาสเสมอ", "Every opportunity must display its material risks."),
        TrustPrinciple("visible_uncertainty", "ไม่ซ่อนความไม่แน่นอน", "Uncertainty Must Never Be Hidden", "ข้อมูลที่ขาด ล่าช้า ไม่ครบ หรือผู้ให้บริการล้มเหลวต้องแสดงอย่างตรงไปตรงมา", "Uncertainty, missing data, stale evidence, and provider failures must remain visible."),
    ]
    neutrality = AlgorithmNeutralityDeclaration(
        considers=["price", "volume", "history", "available fundamentals", "provider-reported catalysts", "risk flags", "market context"],
        does_not_consider=["advertising", "sponsorship", "affiliate relationships", "broker relationships", "asset issuer payments", "user engagement", "page popularity", "watchlist popularity", "social engagement", "developer preference", "Founder preference", "provider promotional placement"],
        ranking_influences=PENNY_ENGINE_DEFINITION.tie_breaker_policy,
        ranking_exclusions=["advertising", "sponsorship", "affiliate relationships", "broker relationships", "asset issuer payments", "user click-through rate", "page popularity", "watchlist popularity", "social engagement", "developer preference", "Founder preference", "provider promotional placement"],
        sponsored_or_commercial_factors_exist=False,
        user_engagement_affects_scoring=False,
        asset_popularity_affects_scoring=False,
        editorial_opinion_affects_scoring=False,
        methodology_assumptions=["Available provider fields are used consistently.", "Missing fields reduce confidence and completeness instead of being fabricated.", "Penny opportunity score is a ranking heuristic, not a return model."],
        known_limitations=["Provider coverage varies by market and symbol.", "Catalyst evidence exists only when a configured provider returns verifiable items.", "The algorithm cannot determine personal suitability."],
        version_identifiers={"methodology": METHODOLOGY_VERSION, "score": SCORE_VERSION, "policy": POLICY_VERSION, "config": CONFIGURATION_VERSION, "trust": TRUST_POLICY_VERSION},
    )
    return TrustDisclosure(
        trust_policy_version=TRUST_POLICY_VERSION,
        principles=principles,
        neutrality=neutrality,
        evidence_integrity=EvidenceIntegrityPolicy(
            required_metadata=["evidence_id", "evidence_type", "provider", "source_timestamp", "retrieval_timestamp", "freshness_status", "availability_status", "verification_status", "supported_factor", "candidate_symbol", "transformation_summary", "data_limitations"],
            allowed_availability_statuses=["available", "partial", "unavailable", "stale", "failed", "unsupported"],
            allowed_verification_statuses=["verified", "provider_reported", "inferred", "unverified", "conflicting"],
            inferred_evidence_rule="Inferred evidence must be labeled inferred and must not be described as verified fact.",
            conflicting_evidence_rule="Conflicting evidence must remain visible and reduce confidence when material.",
        ),
        uncertainty=UncertaintyDisclosurePolicy(
            disclosed_conditions=["missing evidence", "stale evidence", "conflicting evidence", "unsupported evidence", "provider failures", "incomplete financial periods", "insufficient historical coverage", "weak catalyst verification", "uncertain risk status", "fallback use"],
            statement_th="ระบบพบข้อมูลไม่เพียงพอสำหรับข้อสรุปบางส่วน",
            statement_en="The system has insufficient evidence for some parts of this assessment.",
            false_precision_rule="Display whole-number scores and explain that small score gaps may not be meaningful.",
        ),
        conflict_of_interest=ConflictOfInterestPolicy(
            current_commercial_relationships="No sponsored, affiliate, broker, issuer-payment, or paid-placement influence is implemented for this engine.",
            sponsored_content_score_impact_allowed=False,
            commercial_relationship_rank_impact_allowed=False,
            paid_placement_in_rankings_allowed=False,
            future_sponsored_content_rule="Sponsored educational content, if ever introduced, must be labeled and visually separated from algorithmic rankings.",
            financial_interest_disclosure_rule="Material financial interests held by the company, Founder, or contributors must be disclosed where relevant.",
            configuration_change_rule="Algorithm configuration changes must not be made to favor a specific asset.",
            reproducibility_rule="Ranking output must be reproducible from declared methodology, active configuration, and scan evidence.",
        ),
        ranking_integrity=RankingIntegrityPolicy(
            declared_ranking_inputs=PENNY_ENGINE_DEFINITION.tie_breaker_policy,
            manual_override_supported=False,
            manual_override_rules=["Manual ranking intervention is not implemented. If supported later it must be visible, timestamped, include an authorized actor and reason, and preserve the original algorithmic rank."],
            prohibited_influences=["advertising", "sponsorship", "recently clicked symbols", "watchlist popularity", "social engagement", "team ownership", "manual reordering", "suppressed negative evidence", "hidden risk penalties"],
            original_rank_preservation_required=True,
        ),
        decision_boundary=DecisionBoundaryPolicy(
            statement_th="ระบบช่วยวิเคราะห์ แต่การตัดสินใจเป็นของคุณ",
            statement_en="The system supports your analysis. The decision remains yours.",
            prohibited_phrases=["guaranteed", "certain", "must buy", "must sell", "sure profit", "risk-free", "best investment", "high chance of profit"],
            non_directive_actions=["research further", "monitor", "compare", "review risks", "wait for more evidence"],
        ),
        provider_limitations=[
            ProviderLimitationDisclosure("yfinance", ["Quote, history, and fundamentals coverage may vary by asset.", "Provider fields may be delayed, partial, unavailable, or stale."], "latest available provider snapshot with stale status disclosed", "Provider failure is reported as unavailable, failed, or partial instead of being fabricated."),
            ProviderLimitationDisclosure("configured_news", ["Catalyst coverage is optional and may be absent."], "provider-published timestamp when available", "Missing catalyst provider data is shown as missing evidence."),
        ],
        score_interpretation={
            "represents": ["relative alignment with engine methodology", "available evidence at snapshot time", "declared version and configuration"],
            "does_not_represent": ["guaranteed return", "probability of profit", "expected return", "personal suitability", "portfolio allocation recommendation", "certainty of price appreciation", "absence of risk", "intrinsic value", "future performance prediction"],
            "rounding_policy": "whole-number display; internal weighted contributions remain reproducible",
            "small_gap_policy": "Differences inside a small score margin may not be materially meaningful.",
        },
        confidence_interpretation={
            "represents": ["evidence availability", "freshness", "consistency", "provider coverage", "verification quality"],
            "does_not_represent": ["probability of profit", "recommendation strength", "market certainty", "price forecast confidence", "suitability for the user"],
        },
        completeness_interpretation={
            "represents": ["expected evidence availability", "covered evidence groups", "missing expected inputs"],
            "does_not_represent": ["business quality", "investment quality", "investment attractiveness", "probability of success", "recommendation confidence"],
        },
        compact_disclosure=AlgorithmTextBlock(
            th="คะแนนนี้เกิดจากข้อมูลที่มีและอัลกอริทึมเวอร์ชันที่ระบุ ไม่ใช่คำแนะนำให้ซื้อหรือขาย และระบบไม่ตัดสินใจแทนคุณ",
            en="This score is based on available evidence and the stated algorithm version. It is not a buy or sell recommendation, and the system does not decide for you.",
        ),
        founder_trust_statement=AlgorithmTextBlock(
            th="เรายอมรับความไม่แน่นอน มากกว่าสร้างความมั่นใจที่ไม่มีหลักฐานรองรับ",
            en="We would rather admit uncertainty than manufacture certainty.",
        ),
    )


def build_penny_algorithm_definition() -> AlgorithmDefinition:
    identity = AlgorithmIdentity(
        engine_id=PENNY_ENGINE_DEFINITION.engine_id,
        algorithm_id="penny-opportunity-v1",
        category=PENNY_ENGINE_DEFINITION.category,
        display_name_th="อัลกอริทึมหาโอกาสหุ้นราคาต่ำ",
        display_name_en="Penny Opportunity Algorithm",
        short_description_th="ค้นหาหุ้นราคาต่ำที่มีหลักฐานสนับสนุนหลายด้าน พร้อมหักคะแนนความเสี่ยงอย่างโปร่งใส",
        short_description_en="Discovers low-priced equities with multi-factor evidence while transparently deducting risk penalties.",
        methodology_name="Evidence-Based Penny Opportunity Discovery",
        methodology_version=PENNY_ENGINE_DEFINITION.methodology_version,
        score_version=PENNY_ENGINE_DEFINITION.score_version,
        policy_version=PENNY_ENGINE_DEFINITION.policy_version,
        config_version=PENNY_ENGINE_DEFINITION.config_version,
        release_date="2026-07-23",
        last_updated_at="2026-07-23",
        status="active",
        supported_markets=PENNY_ENGINE_DEFINITION.supported_markets,
        schedule_frequency_minutes=PENNY_ENGINE_DEFINITION.schedule_frequency_minutes,
        maximum_results=PENNY_ENGINE_DEFINITION.maximum_results,
    )
    factors = [
        _factor_definition("liquidity", "สภาพคล่อง", "Liquidity", "วัดว่าหุ้นมีปริมาณและมูลค่าการซื้อขายเพียงพอหรือไม่", "Measures whether trading volume and traded value are sufficient.", "หุ้นราคาต่ำที่ซื้อขายเบาบางอาจเข้าออกยากและมีความเสี่ยงสูง", "Low-priced stocks with weak liquidity may be difficult to trade and carry higher execution risk.", ["volume", "average_volume", "price"], ["quote", "history"]),
        _factor_definition("financial", "สุขภาพการเงิน", "Financial Health", "ตรวจสอบความอยู่รอดทางการเงินจากตัวชี้วัดพื้นฐานที่มีข้อมูล", "Checks financial survivability using available fundamental indicators.", "หุ้นราคาต่ำที่ฐานะการเงินอ่อนแออาจเป็นภาวะวิกฤต ไม่ใช่โอกาส", "A low-priced company with weak finances may represent distress rather than opportunity.", ["debt_to_equity", "return_on_equity", "return_on_assets", "trailing_pe", "price_to_book"], ["quote"]),
        _factor_definition("business", "คุณภาพกิจการ", "Business Quality", "ดูหลักฐานคุณภาพกิจการ การฟื้นตัว และความเสี่ยงของธุรกิจจาก Business Intelligence", "Uses Business Intelligence evidence for quality, turnaround, value-trap, and emerging-quality context.", "ราคาต่ำเป็นเพียงขอบเขตการสแกน หลักฐานคุณภาพกิจการเป็นสิ่งที่ตัดสินว่าเป็นโอกาสหรือไม่", "Price defines the universe. Business evidence helps determine whether the candidate deserves research.", ["business_intelligence_score", "business_risk", "missing_business_evidence"], ["business_intelligence"]),
        _factor_definition("technical", "แรงส่งทางเทคนิค", "Technical Strength", "วัดแนวโน้มราคา โมเมนตัม และการมีส่วนร่วมของตลาดจากประวัติราคา", "Measures price trend, momentum, and market participation from historical prices.", "แรงส่งที่ยืนยันด้วยข้อมูลราคาช่วยบอกว่าตลาดเริ่มให้ความสนใจหรือไม่", "Price and volume participation can indicate whether the market is beginning to recognize the candidate.", ["history.close", "history.volume"], ["history"]),
        _factor_definition("catalyst", "ปัจจัยเร่ง", "Catalyst Evidence", "นับเฉพาะข่าวหรือเหตุการณ์ที่ผู้ให้บริการส่งกลับมาอย่างตรวจสอบได้", "Uses only provider-returned verifiable news or event evidence.", "ปัจจัยเร่งช่วยอธิบายว่าทำไมตลาดอาจกลับมาสนใจ แต่ถ้าไม่มีข้อมูลจะไม่สร้างคะแนนปลอม", "Catalysts may explain renewed interest, but missing catalyst evidence must not create synthetic score support.", ["news.items"], ["news"]),
        _factor_definition("market_context", "บริบทตลาด", "Market Context", "สะท้อนแรงส่งระยะสั้นจากการเปลี่ยนแปลงราคาปัจจุบัน", "Reflects short-term market context from current price change.", "บริบทตลาดช่วยลดการดูหุ้นแยกจากสภาวะการซื้อขายล่าสุด", "Market context prevents viewing the stock in isolation from recent trading conditions.", ["change_percent"], ["quote"]),
    ]
    risks = [
        AlgorithmRiskDefinition("invalid_price", "data_quality", "critical", "ไม่มีราคาปัจจุบันที่ใช้ได้ จึงไม่สามารถจัดอันดับอย่างโปร่งใส", "A valid current price is required for transparent ranking.", True),
        AlgorithmRiskDefinition("outside_price_policy", "eligibility", "medium", "ราคาอยู่นอกขอบเขตหุ้นราคาต่ำของตลาดนั้น", "The price is outside the configured low-price policy.", False),
        AlgorithmRiskDefinition("insufficient_trading_history", "data_coverage", "high", "ประวัติราคาน้อยเกินไปทำให้การวัดแนวโน้มไม่น่าเชื่อถือ", "Too little price history makes trend evidence unreliable.", True),
        AlgorithmRiskDefinition("insufficient_liquidity", "liquidity", "critical", "สภาพคล่องต่ำทำให้ความเสี่ยงในการซื้อขายสูง", "Low liquidity creates material trading and execution risk.", True),
        AlgorithmRiskDefinition("extreme_volatility", "volatility", "high", "ความผันผวนสูงมากทำให้ความเสี่ยงด้านขาลงเพิ่มขึ้น", "Extreme volatility increases downside uncertainty.", False),
    ]
    return AlgorithmDefinition(
        identity=identity,
        objective=AlgorithmTextBlock(
            th="ระบบค้นหาหุ้นราคาต่ำที่มีหลักฐานสนับสนุนด้านความอยู่รอดทางการเงิน การเติบโต สภาพคล่อง แรงส่งของตลาด และปัจจัยเร่งที่ตรวจสอบได้ จากนั้นหักคะแนนความเสี่ยงอย่างโปร่งใส ราคาหุ้นต่ำเพียงอย่างเดียวไม่ถือเป็นหลักฐานของโอกาสการลงทุน",
            en="The engine discovers low-priced equities supported by evidence of financial survivability, growth, liquidity, market participation, and verified catalysts. Material risks are deducted transparently. Low share price alone is not treated as evidence of investment opportunity.",
        ),
        hypothesis=AlgorithmTextBlock(
            th="หุ้นราคาต่ำอาจควรศึกษาต่อเมื่อหลักฐานหลายกลุ่มสอดคล้องกัน ไม่ใช่เพราะราคาถูก ข่าวเดียว หรือความนิยมระยะสั้น",
            en="A low-priced security may deserve further research only when multiple independent evidence groups agree, not because of price alone, a single headline, or popularity.",
        ),
        universe={
            "markets": PENNY_ENGINE_DEFINITION.supported_markets,
            "asset_class": "equity",
            "source": "Master Asset Registry",
            "scan_frequency_minutes": SCAN_FREQUENCY_MINUTES,
            "thai_penny_universe": {
                "name": "Thai Emerging Opportunities (Penny Stock)",
                "maximum_share_price": THAI_PENNY_DEFAULT_MAX_SHARE_PRICE,
                "currency": "THB",
                "supported_options": list(THAI_PENNY_SUPPORTED_THRESHOLDS),
                "custom_range": list(THAI_PENNY_CUSTOM_RANGE),
                "methodology": "Thai Emerging Opportunity",
                "version": METHODOLOGY_VERSION,
            },
            "principle": "Price defines the universe. Evidence determines the opportunity.",
        },
        eligibility={"minimum_score": PENNY_ENGINE_DEFINITION.minimum_score, "minimum_confidence": PENNY_ENGINE_DEFINITION.minimum_confidence, "minimum_completeness": PENNY_ENGINE_DEFINITION.minimum_completeness, "hard_disqualifiers": ["invalid_price", "insufficient_trading_history", "insufficient_liquidity", "critical_confirmed_risk"]},
        factors=factors,
        risks=risks,
        score_formula={"en": "Sum of weighted positive factor contributions minus evidence-supported risk penalties, bounded 0-100. Financial Intelligence is the primary evidence layer and Business Intelligence is the secondary evidence layer for corporate assets.", "th": "คะแนนโอกาสเกิดจากผลรวมของคะแนนปัจจัยเชิงบวกตามน้ำหนักที่กำหนด แล้วหักด้วยค่าปรับความเสี่ยงที่มีหลักฐานรองรับ โดย Financial Intelligence เป็นหลักฐานหลัก และ Business Intelligence เป็นหลักฐานรองสำหรับสินทรัพย์ที่เป็นบริษัท", "bounds": [0, 100], "weights": PENNY_FACTOR_WEIGHTS, "primary_evidence_policy": validate_primary_evidence_policy(PENNY_FACTOR_WEIGHTS)},
        confidence={"en": "Data Confidence measures evidence quality and availability. It is not probability of profit.", "th": "ความเชื่อมั่นของข้อมูลวัดคุณภาพและความพร้อมของหลักฐาน ไม่ใช่โอกาสทำกำไร"},
        completeness={"en": "Completeness measures which required evidence groups were available, missing, stale, or failed.", "th": "ความครบถ้วนวัดว่ากลุ่มข้อมูลสำคัญใดมีพร้อม ขาดหาย ล่าช้า หรือดึงข้อมูลไม่สำเร็จ"},
        ranking={"policy": PENNY_ENGINE_DEFINITION.tie_breaker_policy, "en": "Candidates rank by final score first; confidence and completeness break ties only.", "th": "จัดอันดับจากคะแนนสุดท้ายก่อน ความเชื่อมั่นและความครบถ้วนใช้เฉพาะกรณีคะแนนเท่ากัน"},
        data_dependencies=[{"provider": "yfinance", "data": ["quote", "history"]}, {"provider": "configured_news", "data": ["verified catalyst evidence"], "optional": True}],
        limitations=[
            AlgorithmTextBlock("ผู้ให้บริการข้อมูลอาจล่าช้า ไม่ครบถ้วน หรือไม่พร้อมใช้งาน", "Provider data may be delayed, incomplete, or unavailable."),
            AlgorithmTextBlock("วิธีนี้เป็น heuristic เพื่อจัดลำดับการศึกษาต่อ ไม่ใช่แบบจำลองทำนายผลตอบแทน", "This heuristic prioritizes research candidates; it is not a return prediction model."),
        ],
        non_claims=[
            AlgorithmTextBlock("ไม่ใช่คำแนะนำให้ซื้อหรือขาย", "This is not a buy or sell recommendation."),
            AlgorithmTextBlock("ไม่ทำนายผลตอบแทนในอนาคต", "The algorithm does not predict future returns."),
            AlgorithmTextBlock("อันดับสูงไม่รับประกันว่าราคาจะปรับขึ้น", "A higher rank does not guarantee price appreciation."),
        ],
        change_history=[AlgorithmChangeRecord("penny-opportunity-v1", "2026-07-23", "Initial transparent Penny Opportunity methodology.", "Introduces score-first ranking, risk penalties, confidence, completeness, and explainable Top 5 output.")],
        trust=build_penny_trust_disclosure(),
    )


def _factor_definition(factor_id: str, name_th: str, name_en: str, purpose_th: str, purpose_en: str, rationale_th: str, rationale_en: str, input_fields: List[str], providers: List[str]) -> AlgorithmFactorDefinition:
    weight = PENNY_FACTOR_WEIGHTS[factor_id]
    return AlgorithmFactorDefinition(
        factor_id=factor_id,
        display_name_th=name_th,
        display_name_en=name_en,
        purpose_th=purpose_th,
        purpose_en=purpose_en,
        rationale_th=rationale_th,
        rationale_en=rationale_en,
        weight=weight,
        maximum_contribution=round(weight * 100, 2),
        input_fields=input_fields,
        evidence_requirements=["provider_returned_data"],
        provider_dependencies=providers,
        freshness_expectation="latest available provider snapshot",
        missing_data_behavior="reported as missing and reduces data completeness/confidence",
        partial_data_behavior="uses available measured evidence; does not fabricate unavailable fields",
        score_interpretation="higher means stronger evidence for this factor under the active methodology",
        limitations=["Provider availability and field coverage may vary by market and symbol."],
        factor_version="v1",
    )


PENNY_ALGORITHM_DEFINITION = build_penny_algorithm_definition()

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

_scan_execution_lock = Lock()
_snapshot_store = OpportunitySnapshotStore()
_scheduler = OpportunityScheduler()


def build_penny_opportunities(
    quote_fn: QuoteFn,
    history_fn: HistoryFn,
    news_fn: NewsFn | None = None,
    market: str | None = None,
    limit: int = 5,
    thai_max_price: float | None = None,
) -> Dict[str, Any]:
    safe_limit = max(1, min(int(limit or 5), 20))
    scan_id = f"penny-{uuid4().hex[:12]}"
    scan_started_at = datetime.now(timezone.utc)
    scan_started_iso = scan_started_at.isoformat()
    timer_started = monotonic()
    selected_markets = _selected_markets(market)
    active_policies = _configured_policies(thai_max_price)
    generated_at = scan_started_iso
    memory_start_mb = _process_memory_mb()
    registry_context = _candidate_registry_context(selected_markets)
    registry = registry_context["assets"]
    universe_diagnostics = registry_context["diagnostics"]
    candidates = []
    why_not_index: Dict[str, Any] = {}
    excluded = 0
    unknown = 0
    classified = 0
    failed_candidate_count = 0
    provider_status: List[Dict[str, Any]] = []
    scan_deadline_at = timer_started + SCAN_DEADLINE_SECONDS
    batches_processed = 0
    for registry_batch in _chunked(registry, SCAN_BATCH_SIZE):
        remaining_seconds = scan_deadline_at - monotonic()
        if remaining_seconds <= 0:
            provider_status.append({
                "provider": "penny_opportunity_engine",
                "stage": "scan_deadline",
                "status": "partial",
                "reason": "scan_deadline_exceeded",
                "deadline_seconds": SCAN_DEADLINE_SECONDS,
                "timestamp": generated_at,
            })
            break
        batches_processed += 1
        scan_quotes = _scan_quote_map(registry_batch, quote_fn)
        workers = min(SCAN_MAX_WORKERS, max(1, len(registry_batch)))
        if workers == 1:
            results = [
                _evaluate_registry_asset(asset, quote_fn, history_fn, news_fn, generated_at, scan_quotes, active_policies)
                for asset in registry_batch
            ]
        else:
            results = []
            with ThreadPoolExecutor(max_workers=workers, thread_name_prefix="penny-scan") as executor:
                futures = [
                    executor.submit(_evaluate_registry_asset, asset, quote_fn, history_fn, news_fn, generated_at, scan_quotes, active_policies)
                    for asset in registry_batch
                ]
                try:
                    for future in as_completed(futures, timeout=max(0.1, remaining_seconds)):
                        results.append(future.result())
                except FuturesTimeoutError:
                    provider_status.append({
                        "provider": "penny_opportunity_engine",
                        "stage": "scan_deadline",
                        "status": "partial",
                        "reason": "scan_deadline_exceeded",
                        "deadline_seconds": SCAN_DEADLINE_SECONDS,
                        "timestamp": generated_at,
                    })
                    for future in futures:
                        if not future.done():
                            future.cancel()

        for result in results:
            provider_status.extend(result.get("provider_status", []))
            if result["status"] == "unsupported":
                excluded += 1
                continue
            if result["status"] == "error":
                excluded += 1
                failed_candidate_count += 1
                continue

            candidate = result["candidate"]
            policy = result["policy"]
            if candidate.get("classification_status") == "PASS":
                classified += 1
            if candidate["hard_disqualified"]:
                excluded += 1
                why_not_index[candidate["symbol"]] = _candidate_exclusion_explanation(candidate, "disqualified")
                continue
            if not candidate["eligible_for_top5"]:
                why_not_index[candidate["symbol"]] = _candidate_exclusion_explanation(candidate, "below_threshold")
                if candidate["data_completeness"] < policy.minimum_data_completeness:
                    unknown += 1
                else:
                    excluded += 1
                continue
            candidates.append(candidate)
        del results
        del scan_quotes

    items = _add_ranking_explanations(rank_candidates(candidates, score_field="penny_opportunity_score", limit=safe_limit))
    completed_at = datetime.now(timezone.utc)
    completed_iso = completed_at.isoformat()
    scan_duration_ms = round((monotonic() - timer_started) * 1000)
    memory_end_mb = _process_memory_mb()
    status = "ok" if items else ("partial" if provider_status else "unavailable")
    diagnostics = {
        "scan_id": scan_id,
        "duration_seconds": round(scan_duration_ms / 1000, 3),
        "memory_start_mb": memory_start_mb,
        "memory_end_mb": memory_end_mb,
        "memory_peak_observed_mb": _max_optional(memory_start_mb, memory_end_mb),
        "symbols_seen": len(registry),
        "symbols_eligible": len(candidates),
        "symbols_excluded": excluded,
        "failed_symbol_count": failed_candidate_count,
        "candidates_scored": len(candidates),
        "batches_processed": batches_processed,
        "batch_size": SCAN_BATCH_SIZE,
        "provider_batch_limit": SCAN_MAX_PROVIDER_BATCH,
        "worker_cap": SCAN_MAX_WORKERS,
        "total_deadline_seconds": SCAN_DEADLINE_SECONDS,
        "provider_timeout_seconds": SCAN_PROVIDER_TIMEOUT_SECONDS,
        "retry_limit": SCAN_RETRY_LIMIT,
        "snapshot_persisted": False,
    }
    return {
        "status": status,
        "category": PENNY_ENGINE_DEFINITION.category,
        "engine": {
            "engine_id": PENNY_ENGINE_DEFINITION.engine_id,
            "category": PENNY_ENGINE_DEFINITION.category,
            "methodology_version": PENNY_ENGINE_DEFINITION.methodology_version,
            "score_version": PENNY_ENGINE_DEFINITION.score_version,
            "policy_version": PENNY_ENGINE_DEFINITION.policy_version,
            "config_version": PENNY_ENGINE_DEFINITION.config_version,
        },
        "methodology_version": PENNY_ENGINE_DEFINITION.methodology_version,
        "score_version": PENNY_ENGINE_DEFINITION.score_version,
        "policy_version": PENNY_ENGINE_DEFINITION.policy_version,
        "configuration_version": PENNY_ENGINE_DEFINITION.config_version,
        "trust": _trust_api_metadata(),
        "generated_at": completed_iso,
        "scan": {
            "snapshot_id": scan_id,
            "scan_id": scan_id,
            "scan_started_at": scan_started_iso,
            "scan_completed_at": completed_iso,
            "last_successful_scan_at": completed_iso if status in {"ok", "partial"} else None,
            "next_scan_at": (completed_at + timedelta(minutes=SCAN_FREQUENCY_MINUTES)).isoformat(),
            "frequency_minutes": SCAN_FREQUENCY_MINUTES,
            "is_stale": False,
            "scan_duration_ms": scan_duration_ms,
            "diagnostics": diagnostics,
        },
        "diagnostics": diagnostics,
        "markets": selected_markets,
        "universe": {**_universe_response(active_policies, selected_markets), "diagnostics": universe_diagnostics},
        "warning": {"th": PENNY_WARNING_TH, "en": PENNY_WARNING_EN},
        "qualification": {
            "universe_size": len(registry),
            "prefiltered_count": classified,
            "classified_count": classified,
            "eligible_count": len(candidates),
            "qualified_count": len(candidates),
            "failed_candidate_count": failed_candidate_count,
            "ranked_count": len(items),
            "result_count": len(items),
            "excluded_count": excluded,
            "unknown_count": unknown,
            "active_thresholds": {market_id: active_policies[market_id].penny_price_maximum for market_id in selected_markets if market_id in active_policies},
            "prefilter_diagnostics": universe_diagnostics,
        },
        "items": [_public_item(item) for item in items],
        "why_not_index": dict(list(why_not_index.items())[:250]),
        "limitations": [
            "The scanner evaluates a bounded provider-safe candidate universe before ranking qualified candidates.",
            "Price defines the scanning universe only. Price is not a positive score factor.",
            "Catalyst evidence is shown only when a configured provider returns verifiable items.",
            "Missing fundamentals, liquidity, or catalyst data reduce confidence instead of being replaced.",
            "Scores are transparent research rankings, not scientifically validated predictions.",
        ],
        "provider_status": provider_status[:50],
        "disclaimer": "This is not financial advice.",
    }


def run_penny_scan_once(
    quote_fn: QuoteFn,
    history_fn: HistoryFn,
    news_fn: NewsFn | None = None,
    market: str | None = None,
    limit: int = 5,
    thai_max_price: float | None = None,
) -> Dict[str, Any]:
    if not _scan_execution_lock.acquire(blocking=False):
        current = _snapshot_store.latest(PENNY_ENGINE_ID)
        if current:
            current["status"] = "scan_in_progress"
            current.setdefault("limitations", []).append("Scheduled penny scan skipped because a previous scan is still running.")
            current.setdefault("provider_status", []).append({
                "provider": "penny_opportunity_scheduler",
                "stage": "scan_lock",
                "status": "skipped",
                "reason": "active_scan_running",
                "timestamp": datetime.now(timezone.utc).isoformat(),
            })
            return current
        return _empty_snapshot("scan_in_progress", "A scheduled penny scan is already running.")
    try:
        snapshot = build_penny_opportunities(quote_fn, history_fn, news_fn, market=market, limit=limit, thai_max_price=thai_max_price)
        snapshot["snapshot_status"] = snapshot["status"]
        qualification = snapshot.get("qualification", {})
        failed_all_candidates = (
            qualification.get("universe_size", 0) > 0
            and qualification.get("failed_candidate_count", 0) >= qualification.get("universe_size", 0)
            and not snapshot.get("items")
        )
        if failed_all_candidates:
            failed_at = datetime.now(timezone.utc).isoformat()
            failure = {
                "failed_scan_timestamp": failed_at,
                "failure_stage": "candidate_processing",
                "reason": "all_candidates_failed",
            }
            _snapshot_store.record_failure(PENNY_ENGINE_ID, failure)
            current = _snapshot_store.latest(PENNY_ENGINE_ID)
            if current:
                current["status"] = "stale"
                current["snapshot_status"] = current.get("snapshot_status", "ok")
                current.setdefault("limitations", []).append("Latest hourly penny scan failed for every candidate; serving the last successful snapshot.")
                current["scan"]["is_stale"] = True
                current["scan"]["failed_scan_timestamp"] = failed_at
                current["scan"]["failure_stage"] = failure["failure_stage"]
                return current
            return _empty_snapshot("failed", "No successful Penny Opportunity scan has been published yet.", failure)
        snapshot.setdefault("diagnostics", {})["snapshot_persisted"] = True
        snapshot.setdefault("scan", {}).setdefault("diagnostics", snapshot["diagnostics"])
        snapshot["scan"]["diagnostics"]["snapshot_persisted"] = True
        return _snapshot_store.publish(PENNY_ENGINE_ID, snapshot)
    except Exception as exc:  # pragma: no cover - defensive scheduler isolation
        failed_at = datetime.now(timezone.utc).isoformat()
        failure = {
            "failed_scan_timestamp": failed_at,
            "failure_stage": "penny_opportunity_scan",
            "reason": exc.__class__.__name__,
        }
        _snapshot_store.record_failure(PENNY_ENGINE_ID, failure)
        current = _snapshot_store.latest(PENNY_ENGINE_ID)
        if current:
            current["status"] = "stale"
            current["snapshot_status"] = current.get("snapshot_status", "ok")
            current.setdefault("limitations", []).append("Latest hourly penny scan failed; serving the last successful snapshot.")
            current["scan"]["is_stale"] = True
            current["scan"]["failed_scan_timestamp"] = failed_at
            current["scan"]["failure_stage"] = failure["failure_stage"]
            return current
        return _empty_snapshot("failed", "No successful Penny Opportunity scan has been published yet.", failure)
    finally:
        _scan_execution_lock.release()


def get_penny_opportunities_snapshot(market: str | None = None, limit: int = 5, thai_max_price: float | None = None) -> Dict[str, Any]:
    safe_limit = max(1, min(int(limit or 5), 20))
    active_policies = _configured_policies(thai_max_price)
    selected_markets = _selected_markets(market)
    snapshot = _snapshot_store.latest(PENNY_ENGINE_ID)
    failed = _snapshot_store.failure(PENNY_ENGINE_ID)
    if not snapshot:
        if _scan_execution_lock.locked():
            return _empty_snapshot("scan_in_progress", "Initial Penny Opportunity scan is running; no successful snapshot has been published yet.", failed, selected_markets, active_policies)
        return _empty_snapshot("not_ready", "No successful Penny Opportunity snapshot has been published yet. The endpoint does not run a live full-universe scan inside the user request.", failed, selected_markets, active_policies)

    items = snapshot.get("items", [])
    if market:
        selected = set(selected_markets)
        items = [item for item in items if item.get("market") in selected]
    requested_threshold = active_policies.get("TH", POLICIES["TH"]).penny_price_maximum
    latest_threshold = _snapshot_threshold(snapshot)
    if thai_max_price is not None:
        items = [
            item for item in items
            if item.get("market") != "TH" or (_number(item.get("price")) is not None and (_number(item.get("price")) or 0) <= requested_threshold)
        ]
        snapshot["universe"] = _universe_response(active_policies, selected_markets)
        snapshot.setdefault("qualification", {})["active_thresholds"] = {
            market_id: active_policies[market_id].penny_price_maximum for market_id in selected_markets if market_id in active_policies
        }
        if latest_threshold is not None and requested_threshold > latest_threshold:
            snapshot["status"] = "partial"
            snapshot.setdefault("limitations", []).append(
                "Requested Thai threshold exceeds the latest published snapshot threshold; extended candidates will appear after a scheduled bounded scan publishes them."
            )
    snapshot["items"] = items[:safe_limit]
    snapshot["qualification"] = {**snapshot.get("qualification", {}), "ranked_count": len(snapshot["items"]), "result_count": len(snapshot["items"])}
    scan = snapshot.setdefault("scan", {})
    completed = _parse_dt(scan.get("scan_completed_at"))
    if completed and datetime.now(timezone.utc) - completed > timedelta(minutes=SCAN_FREQUENCY_MINUTES + 15):
        snapshot["status"] = "stale"
        scan["is_stale"] = True
        snapshot.setdefault("limitations", []).append("Data may be stale because the latest published scan is older than the expected hourly window.")
    if failed:
        scan["failed_scan_timestamp"] = failed.get("failed_scan_timestamp")
        scan["failure_stage"] = failed.get("failure_stage")
    return snapshot


def build_custom_penny_opportunities(
    quote_fn: QuoteFn,
    history_fn: HistoryFn,
    news_fn: NewsFn | None = None,
    market: str | None = None,
    limit: int = 5,
    thai_max_price: float | None = None,
) -> Dict[str, Any]:
    return build_penny_opportunities(quote_fn, history_fn, news_fn, market=market, limit=limit, thai_max_price=thai_max_price)


def start_penny_opportunity_scheduler(
    quote_fn: QuoteFn,
    history_fn: HistoryFn,
    news_fn: NewsFn | None = None,
    market: str | None = None,
    limit: int = 5,
    frequency_minutes: int = SCAN_FREQUENCY_MINUTES,
    thai_max_price: float | None = None,
    initial_delay_seconds: int = 0,
) -> bool:
    definition = PENNY_ENGINE_DEFINITION
    if frequency_minutes != definition.schedule_frequency_minutes:
        definition = OpportunityEngineDefinition(
            **{**definition.__dict__, "schedule_frequency_minutes": max(1, frequency_minutes)}
        )
    return _scheduler.start(
        definition,
        lambda: run_penny_scan_once(quote_fn, history_fn, news_fn, market=market, limit=limit, thai_max_price=thai_max_price),
        initial_delay_seconds=max(0, initial_delay_seconds),
    )


def stop_penny_opportunity_scheduler() -> None:
    _scheduler.stop(PENNY_ENGINE_ID)


def reset_penny_opportunity_snapshots_for_tests() -> None:
    stop_penny_opportunity_scheduler()
    _snapshot_store.reset(PENNY_ENGINE_ID)
    _scheduler.reset_for_tests()


def register_penny_opportunity_engine() -> None:
    validation = validate_penny_algorithm_definition()
    if not validation["valid"]:
        raise ValueError(f"Penny algorithm transparency validation failed: {validation['errors']}")
    register_engine(
        OpportunityEngineRuntime(
            definition=PENNY_ENGINE_DEFINITION,
            scan_once=run_penny_scan_once,
            get_snapshot=get_penny_opportunities_snapshot,
            start_scheduler=start_penny_opportunity_scheduler,
            stop_scheduler=stop_penny_opportunity_scheduler,
        )
    )


def get_penny_algorithm_definition() -> Dict[str, Any]:
    definition = algorithm_to_dict(PENNY_ALGORITHM_DEFINITION)
    validation = validate_penny_algorithm_definition()
    return {
        "status": "ok" if validation["valid"] else "failed",
        "algorithm": definition,
        "trust": _trust_api_metadata(),
        "validation": validation,
        "cache": {"cacheable": True, "recommended_ttl_seconds": 3600},
        "disclaimer": "This is not financial advice.",
    }


def validate_penny_algorithm_definition() -> Dict[str, Any]:
    return validate_algorithm_definition(PENNY_ALGORITHM_DEFINITION, PENNY_FACTOR_WEIGHTS).__dict__


def get_penny_candidate_explanation(symbol: str) -> Dict[str, Any]:
    requested = symbol.strip().upper()
    snapshot = get_penny_opportunities_snapshot()
    for item in snapshot.get("items", []):
        if item.get("symbol", "").upper() == requested:
            return {
                "status": "ok",
                "symbol": item.get("symbol"),
                "engine": snapshot.get("engine"),
                "scan": snapshot.get("scan"),
                "trust": _trust_api_metadata(),
                "score_explanation": item.get("score_explanation"),
                "score_breakdown": item.get("score_breakdown"),
                "risk_explanation": item.get("risks", []),
                "confidence_explanation": item.get("confidence_explanation"),
                "completeness_explanation": item.get("completeness_explanation"),
                "ranking_explanation": item.get("ranking_explanation"),
                "trust": _trust_api_metadata(),
                "disclaimer": "This is not financial advice.",
            }
    why_not = get_penny_why_not(symbol)
    return {"status": "not_ranked", "symbol": symbol, "why_not": why_not, "disclaimer": "This is not financial advice."}


def get_penny_why_not(symbol: str) -> Dict[str, Any]:
    requested = symbol.strip().upper()
    snapshot = get_penny_opportunities_snapshot()
    for item in snapshot.get("items", []):
        if item.get("symbol", "").upper() == requested:
            return {
                "status": "ranked",
                "symbol": item.get("symbol"),
                "rank": item.get("rank"),
                "explanation_en": "This symbol is already ranked in the latest Penny Opportunity snapshot.",
                "explanation_th": "สัญลักษณ์นี้ติดอันดับใน Penny Opportunity snapshot ล่าสุดแล้ว",
                "scan": snapshot.get("scan"),
            }
    index = snapshot.get("why_not_index") or {}
    row = index.get(requested)
    if row:
        return {**row, "scan": snapshot.get("scan"), "trust": _trust_api_metadata()}
    return {
        "status": "not_in_universe",
        "symbol": symbol,
        "explanation_en": "This symbol is not present in the bounded Why Not index for the latest snapshot. The endpoint does not trigger a new scan.",
        "explanation_th": "ไม่พบสัญลักษณ์นี้ใน Why Not index ของ snapshot ล่าสุด endpoint นี้ไม่เริ่มการสแกนใหม่",
        "scan": snapshot.get("scan"),
        "trust": _trust_api_metadata(),
    }


def _trust_api_metadata() -> Dict[str, Any]:
    trust = PENNY_ALGORITHM_DEFINITION.trust
    return {
        "evidence_based": True,
        "methodology_inspectable": True,
        "score_is_not_probability": True,
        "confidence_is_not_profit_probability": True,
        "completeness_is_not_investment_quality": True,
        "user_decision_required": True,
        "commercial_influence_on_ranking": trust.neutrality.sponsored_or_commercial_factors_exist,
        "engagement_influence_on_ranking": trust.neutrality.user_engagement_affects_scoring,
        "popularity_influence_on_ranking": trust.neutrality.asset_popularity_affects_scoring,
        "editorial_influence_on_ranking": trust.neutrality.editorial_opinion_affects_scoring,
        "limitations_visible": True,
        "uncertainty_visible": True,
        "trust_policy_version": trust.trust_policy_version,
        "decision_boundary": {"th": trust.decision_boundary.statement_th, "en": trust.decision_boundary.statement_en},
        "compact_disclosure": {"th": trust.compact_disclosure.th, "en": trust.compact_disclosure.en},
        "founder_trust_statement": {"th": trust.founder_trust_statement.th, "en": trust.founder_trust_statement.en},
    }


def _empty_snapshot(
    status: str,
    reason: str,
    failure: Dict[str, Any] | None = None,
    selected_markets: List[str] | None = None,
    policies: Dict[str, PennyMarketPolicy] | None = None,
) -> Dict[str, Any]:
    now = datetime.now(timezone.utc)
    selected = selected_markets or []
    active_policies = policies or _configured_policies()
    diagnostics = {
        "scan_id": None,
        "duration_seconds": 0,
        "memory_start_mb": None,
        "memory_end_mb": None,
        "memory_peak_observed_mb": None,
        "symbols_seen": 0,
        "symbols_eligible": 0,
        "symbols_excluded": 0,
        "failed_symbol_count": 0,
        "candidates_scored": 0,
        "batches_processed": 0,
        "batch_size": SCAN_BATCH_SIZE,
        "provider_batch_limit": SCAN_MAX_PROVIDER_BATCH,
        "worker_cap": SCAN_MAX_WORKERS,
        "total_deadline_seconds": SCAN_DEADLINE_SECONDS,
        "provider_timeout_seconds": SCAN_PROVIDER_TIMEOUT_SECONDS,
        "retry_limit": SCAN_RETRY_LIMIT,
        "snapshot_persisted": False,
    }
    payload = {
        "status": status,
        "category": PENNY_ENGINE_DEFINITION.category,
        "engine": {
            "engine_id": PENNY_ENGINE_DEFINITION.engine_id,
            "category": PENNY_ENGINE_DEFINITION.category,
            "methodology_version": PENNY_ENGINE_DEFINITION.methodology_version,
            "score_version": PENNY_ENGINE_DEFINITION.score_version,
            "policy_version": PENNY_ENGINE_DEFINITION.policy_version,
            "config_version": PENNY_ENGINE_DEFINITION.config_version,
        },
        "methodology_version": PENNY_ENGINE_DEFINITION.methodology_version,
        "score_version": PENNY_ENGINE_DEFINITION.score_version,
        "policy_version": PENNY_ENGINE_DEFINITION.policy_version,
        "configuration_version": PENNY_ENGINE_DEFINITION.config_version,
        "trust": _trust_api_metadata(),
        "generated_at": now.isoformat(),
        "scan": {
            "snapshot_id": None,
            "scan_id": None,
            "scan_started_at": None,
            "scan_completed_at": None,
            "last_successful_scan_at": None,
            "next_scan_at": (now + timedelta(minutes=SCAN_FREQUENCY_MINUTES)).isoformat(),
            "frequency_minutes": SCAN_FREQUENCY_MINUTES,
            "is_stale": True,
            "scan_duration_ms": 0,
            "diagnostics": diagnostics,
        },
        "diagnostics": diagnostics,
        "markets": selected,
        "universe": _universe_response(active_policies, selected),
        "warning": {"th": PENNY_WARNING_TH, "en": PENNY_WARNING_EN},
        "qualification": {
            "universe_size": 0,
            "prefiltered_count": 0,
            "classified_count": 0,
            "eligible_count": 0,
            "qualified_count": 0,
            "excluded_count": 0,
            "failed_candidate_count": 0,
            "ranked_count": 0,
            "result_count": 0,
            "unknown_count": 0,
        },
        "items": [],
        "limitations": [reason],
        "provider_status": [],
        "disclaimer": "This is not financial advice.",
    }
    if failure:
        payload["scan"]["failed_scan_timestamp"] = failure.get("failed_scan_timestamp")
        payload["scan"]["failure_stage"] = failure.get("failure_stage")
    return payload


def _parse_dt(value: Any) -> datetime | None:
    if not isinstance(value, str):
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def _process_memory_mb() -> float | None:
    try:
        if platform.system().lower() == "windows":
            import ctypes
            import ctypes.wintypes

            class ProcessMemoryCounters(ctypes.Structure):
                _fields_ = [
                    ("cb", ctypes.wintypes.DWORD),
                    ("PageFaultCount", ctypes.wintypes.DWORD),
                    ("PeakWorkingSetSize", ctypes.c_size_t),
                    ("WorkingSetSize", ctypes.c_size_t),
                    ("QuotaPeakPagedPoolUsage", ctypes.c_size_t),
                    ("QuotaPagedPoolUsage", ctypes.c_size_t),
                    ("QuotaPeakNonPagedPoolUsage", ctypes.c_size_t),
                    ("QuotaNonPagedPoolUsage", ctypes.c_size_t),
                    ("PagefileUsage", ctypes.c_size_t),
                    ("PeakPagefileUsage", ctypes.c_size_t),
                ]

            counters = ProcessMemoryCounters()
            counters.cb = ctypes.sizeof(ProcessMemoryCounters)
            ctypes.windll.kernel32.GetCurrentProcess.restype = ctypes.wintypes.HANDLE
            ctypes.windll.psapi.GetProcessMemoryInfo.argtypes = [
                ctypes.wintypes.HANDLE,
                ctypes.POINTER(ProcessMemoryCounters),
                ctypes.wintypes.DWORD,
            ]
            ctypes.windll.psapi.GetProcessMemoryInfo.restype = ctypes.wintypes.BOOL
            handle = ctypes.windll.kernel32.GetCurrentProcess()
            if ctypes.windll.psapi.GetProcessMemoryInfo(handle, ctypes.byref(counters), counters.cb):
                return round(counters.WorkingSetSize / (1024 * 1024), 2)
            return None
        import resource

        usage = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        multiplier = 1 if platform.system().lower() == "darwin" else 1024
        return round((usage * multiplier) / (1024 * 1024), 2)
    except Exception:
        return None


def _max_optional(*values: float | None) -> float | None:
    present = [value for value in values if value is not None]
    return max(present) if present else None


def _snapshot_threshold(snapshot: Dict[str, Any]) -> float | None:
    thresholds = snapshot.get("qualification", {}).get("active_thresholds", {})
    value = thresholds.get("TH") if isinstance(thresholds, dict) else None
    if value is not None:
        return _number(value)
    markets = snapshot.get("universe", {}).get("markets", {})
    thai = markets.get("TH") if isinstance(markets, dict) else None
    if isinstance(thai, dict):
        return _number(thai.get("maximum_share_price"))
    return None


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

    financial_report = build_financial_intelligence_report(symbol, quote, quote, asset)
    business_report = build_business_intelligence_report(symbol, quote, financial_report)
    financial = _financial_score_from_report(financial_report, quote, missing_data)
    business = _business_score_from_report(business_report, missing_data)
    growth = _growth_score(quote, missing_data)
    technical = _technical_score(closes, volumes, quote, missing_data, risk_flags)
    catalyst = _catalyst_score(symbol, news_fn, missing_data, provider_status)
    setup = _opportunity_setup(financial, business, growth, liquidity, risk_flags)
    if setup["value_trap_detected"]:
        risk_flags.append(_risk_flag("value_trap_evidence", "HIGH", "confirmed", 22, "Low price is accompanied by weak financial or business evidence."))
    completeness = _data_completeness(quote, history, catalyst, business)
    confidence = _data_confidence(completeness, liquidity, financial, business, technical, catalyst, risk_flags)
    risk_penalty = _risk_penalty([*hard_flags, *risk_flags], liquidity, technical)
    market_context = _market_context_score(asset, quote)
    factor_scores = {
        "financial": financial["score"],
        "business": business["score"],
        "technical": technical["score"],
        "liquidity": liquidity["score"],
        "catalyst": catalyst["score"],
        "market_context": market_context,
    }
    score_breakdown = _score_breakdown(factor_scores, risk_penalty, [*hard_flags, *risk_flags], missing_data)
    base_score = score_breakdown["raw_positive_score"]
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
        "scores": factor_scores,
        "factor_availability": {
            "price": "PASS" if price is not None else "FAIL",
            "liquidity": liquidity["status"],
            "history": history_status,
            "fundamentals": financial["status"],
            "business": business["status"],
            "growth": growth["status"],
            "catalyst": catalyst["status"],
        },
        "universe_filter": _universe_filter_response(policy, classification),
        "price_tier": classification["tier"],
        "price_tier_label": classification["label"],
        "opportunity_setup": setup,
        "risk_penalty": risk_penalty,
        "risk_level": risk_level,
        "severe_risk_count": len([flag for flag in [*hard_flags, *risk_flags] if flag["severity"] in {"HIGH", "CRITICAL"}]),
        "strengths": _strengths(liquidity, financial, business, growth, technical, catalyst, setup),
        "risks": [*hard_flags, *risk_flags],
        "missing_data": sorted(set(missing_data)),
        "catalysts": catalyst["items"],
        "explanation": _explanation(symbol, score, confidence, [*hard_flags, *risk_flags], missing_data, catalyst),
        "score_explanation": _candidate_score_explanation(symbol, score, score_breakdown, confidence, completeness, factor_scores, [*hard_flags, *risk_flags], missing_data),
        "score_breakdown": score_breakdown,
        "confidence_explanation": _confidence_explanation(confidence, completeness, liquidity, financial, business, technical, catalyst, risk_flags),
        "completeness_explanation": _completeness_explanation(completeness, quote, history, catalyst, business),
        "uncertainty_disclosure": _uncertainty_disclosure(missing_data, provider_status, [*hard_flags, *risk_flags]),
        "evidence_integrity": _evidence_integrity_records(symbol, quote, history, catalyst, provider_status),
        "financial_intelligence": financial_report,
        "business_intelligence": business_report,
        "trust": _trust_api_metadata(),
        "provider_attribution": _provider_attribution(quote, history, catalyst),
        "provider_status": provider_status,
        "hard_disqualified": hard_disqualified,
        "eligible_for_top5": eligible,
    }


def classify_price(price: float | None, policy: PennyMarketPolicy) -> Dict[str, Any]:
    if price is None:
        return {"status": "UNKNOWN", "classification": "unavailable", "label": "Data unavailable", "tier": "unavailable"}
    if policy.market == "TH":
        if price <= 2.0:
            tier = ("micro_penny", "Micro Penny")
        elif price <= 5.0:
            tier = ("classic_penny", "Classic Penny")
        elif price <= 10.0:
            tier = ("thai_emerging", "Thai Emerging")
        elif price <= 15.0:
            tier = ("extended_emerging", "Extended Emerging")
        else:
            tier = ("outside_policy", "Outside Thai Emerging Opportunity universe")
        if price <= policy.penny_price_maximum:
            return {"status": "PASS", "classification": "thai_emerging_opportunity_universe", "label": tier[1], "tier": tier[0], "maximum_share_price": policy.penny_price_maximum, "methodology": policy.methodology}
        return {"status": "FAIL", "classification": "outside_policy", "label": tier[1], "tier": tier[0], "maximum_share_price": policy.penny_price_maximum, "methodology": policy.methodology}
    if price <= policy.penny_price_maximum:
        return {"status": "PASS", "classification": "penny_stock", "label": "Penny Stock", "tier": "penny_stock"}
    if policy.extended_price_maximum is not None and price <= policy.extended_price_maximum:
        return {"status": "PASS", "classification": "low_priced_small_cap", "label": "Low-Priced Small Cap", "tier": "low_priced_small_cap"}
    return {"status": "FAIL", "classification": "outside_policy", "label": "Outside configured low-price policy", "tier": "outside_policy"}


def _candidate_registry(markets: Iterable[str]) -> List[MasterAsset]:
    return _candidate_registry_context(markets)["assets"]


def _chunked(items: List[MasterAsset], size: int) -> Iterable[List[MasterAsset]]:
    safe_size = max(1, int(size or 1))
    for start in range(0, len(items), safe_size):
        yield items[start:start + safe_size]


def _candidate_registry_context(markets: Iterable[str]) -> Dict[str, Any]:
    selected = set(markets)
    assets = list_registry_assets(enabled_only=True, searchable_only=True)
    diagnostics = {
        "total_registry_assets": len(assets),
        "included_common_share_count": 0,
        "excluded_foreign_board_count": 0,
        "excluded_special_board_count": 0,
        "excluded_malformed_symbol_count": 0,
        "excluded_other_count": 0,
        "scan_symbol_limit": SCAN_MAX_SYMBOLS,
        "scan_symbol_limit_applied": False,
        "excluded_examples": [],
    }
    candidates: List[MasterAsset] = []
    for asset in assets:
        market = _asset_market(asset)
        if market not in selected or not _asset_is_supported_equity(asset):
            continue
        if market == "TH":
            mapped = _thai_asset_mapping(asset)
            if not mapped.supported:
                _record_symbol_exclusion(diagnostics, asset, mapped)
                continue
            provider_symbols = {**asset.provider_symbols, "yfinance": mapped.provider_symbol or asset.provider_symbols.get("yfinance", "")}
            candidates.append(replace(asset, provider_symbols=provider_symbols))
            continue
        candidates.append(asset)
    candidates = sorted(candidates, key=lambda item: item.canonical_symbol)
    diagnostics["included_common_share_count"] = len(candidates)
    if len(candidates) > SCAN_MAX_SYMBOLS:
        diagnostics["scan_symbol_limit_applied"] = True
        diagnostics["unbounded_candidate_count"] = len(candidates)
        candidates = candidates[:SCAN_MAX_SYMBOLS]
        diagnostics["included_common_share_count"] = len(candidates)
    return {"assets": candidates, "diagnostics": diagnostics}


def _thai_asset_mapping(asset: MasterAsset) -> ProviderSymbolMapping:
    provider_symbol = asset.provider_symbols.get("yfinance") or asset.canonical_symbol
    return map_thai_yfinance_symbol(provider_symbol)


def _record_symbol_exclusion(diagnostics: Dict[str, Any], asset: MasterAsset, mapping: ProviderSymbolMapping) -> None:
    reason = mapping.exclusion_reason or "unsupported_symbol"
    if reason == "foreign_board_excluded":
        diagnostics["excluded_foreign_board_count"] += 1
    elif reason == "special_board_excluded":
        diagnostics["excluded_special_board_count"] += 1
    elif reason in {"malformed_symbol", "duplicate_exchange_suffix", "empty_symbol"}:
        diagnostics["excluded_malformed_symbol_count"] += 1
    else:
        diagnostics["excluded_other_count"] += 1
    examples = diagnostics.setdefault("excluded_examples", [])
    if len(examples) < 10:
        examples.append({
            "symbol": asset.canonical_symbol,
            "provider_symbol": asset.provider_symbols.get("yfinance"),
            "reason": reason,
            "board": mapping.board,
        })


def _evaluate_registry_asset(
    asset: MasterAsset,
    quote_fn: QuoteFn,
    history_fn: HistoryFn,
    news_fn: NewsFn | None,
    generated_at: str,
    scan_quotes: Dict[str, Dict[str, Any]],
    policies: Dict[str, PennyMarketPolicy] | None = None,
) -> Dict[str, Any]:
    try:
        policy = _policy_for_asset(asset, policies)
        if policy is None:
            return {"status": "unsupported", "provider_status": []}
        provider_symbol = asset.provider_symbols.get("yfinance") or asset.canonical_symbol
        scan_quote = scan_quotes.get(provider_symbol) or scan_quotes.get(asset.canonical_symbol)

        def selected_quote_fn(symbol: str) -> Dict[str, Any]:
            if scan_quote and _can_use_scan_quote_only(scan_quote, policy):
                return scan_quote
            return quote_fn(symbol)

        candidate = evaluate_candidate(asset, policy, selected_quote_fn, history_fn, news_fn)
        return {
            "status": "candidate",
            "candidate": candidate,
            "policy": policy,
            "provider_status": candidate.get("provider_status", []),
        }
    except Exception as exc:  # pragma: no cover - defensive API isolation
        return {
            "status": "error",
            "provider_status": [{
                "symbol": getattr(asset, "canonical_symbol", "unknown"),
                "provider": "penny_opportunity_engine",
                "stage": "candidate_processing",
                "status": "error",
                "reason": exc.__class__.__name__,
                "timestamp": generated_at,
            }],
        }


def _scan_quote_map(registry: List[MasterAsset], quote_fn: QuoteFn) -> Dict[str, Dict[str, Any]]:
    if not registry or getattr(quote_fn, "__name__", "") != "get_cached_quote":
        return {}
    try:
        provider = get_provider("yfinance")
        get_scan_quotes = getattr(provider, "get_scan_quotes", None)
        if not callable(get_scan_quotes):
            return {}
        symbols = [asset.provider_symbols.get("yfinance") or asset.canonical_symbol for asset in registry]
        results: Dict[str, Dict[str, Any]] = {}
        for start in range(0, len(symbols), SCAN_MAX_PROVIDER_BATCH):
            chunk = symbols[start:start + SCAN_MAX_PROVIDER_BATCH]
            results.update(get_scan_quotes(chunk, chunk_size=SCAN_MAX_PROVIDER_BATCH))
        return results
    except Exception:
        return {}


def _can_use_scan_quote_only(quote: Dict[str, Any], policy: PennyMarketPolicy) -> bool:
    price = _number(quote.get("price"))
    return classify_price(price, policy)["status"] != "PASS"


def _selected_markets(market: str | None) -> List[str]:
    if not market:
        return ["TH", "US"]
    value = market.strip().upper()
    if value in POLICIES:
        return [value]
    return []


def _configured_policies(thai_max_price: float | None = None) -> Dict[str, PennyMarketPolicy]:
    policies = dict(POLICIES)
    active_thai_threshold = _validated_thai_threshold(thai_max_price)
    policies["TH"] = replace(
        POLICIES["TH"],
        penny_price_maximum=active_thai_threshold,
        extended_price_maximum=15.0,
    )
    return policies


def _validated_thai_threshold(value: float | None) -> float:
    if value is None:
        return THAI_PENNY_DEFAULT_MAX_SHARE_PRICE
    selected = float(value)
    low, high = THAI_PENNY_CUSTOM_RANGE
    if selected < low or selected > high:
        raise ValueError("Thai Penny maximum share price must be between 5.00 and 15.00 THB.")
    return round(selected, 2)


def _thai_universe_disclosure(policy: PennyMarketPolicy) -> Dict[str, Any]:
    return {
        "name": "Thai Emerging Opportunities (Penny Stock)",
        "current_penny_universe": "Thai Penny Stock Universe",
        "maximum_share_price": policy.penny_price_maximum,
        "currency": policy.currency,
        "default_maximum_share_price": policy.default_price_maximum,
        "supported_options": list(policy.supported_price_options),
        "custom_range": list(policy.custom_price_range or ()),
        "methodology": policy.methodology,
        "version": METHODOLOGY_VERSION,
        "principle": "Price defines the universe. Evidence determines the opportunity.",
        "price_tiers": [
            {"tier": "micro_penny", "label": "Micro Penny", "range": "0.01-2.00 THB"},
            {"tier": "classic_penny", "label": "Classic Penny", "range": "2.00-5.00 THB"},
            {"tier": "thai_emerging", "label": "Thai Emerging", "range": "5.00-10.00 THB"},
            {"tier": "extended_emerging", "label": "Extended Emerging", "range": "10.00-15.00 THB"},
        ],
    }


def _universe_response(policies: Dict[str, PennyMarketPolicy], selected_markets: List[str]) -> Dict[str, Any]:
    return {
        "principle": "Price defines the universe. Evidence determines the opportunity.",
        "markets": {
            market: _thai_universe_disclosure(policy) if market == "TH" else {
                "name": "US Penny Opportunity",
                "maximum_share_price": policy.penny_price_maximum,
                "currency": policy.currency,
                "methodology": policy.methodology,
                "version": METHODOLOGY_VERSION,
            }
            for market, policy in policies.items()
            if market in selected_markets
        },
    }


def _universe_filter_response(policy: PennyMarketPolicy, classification: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "market": policy.market,
        "methodology": policy.methodology,
        "maximum_share_price": policy.penny_price_maximum,
        "currency": policy.currency,
        "supported_options": list(policy.supported_price_options),
        "custom_range": list(policy.custom_price_range or ()),
        "price_tier": classification.get("tier"),
        "eligible": classification.get("status") == "PASS",
        "principle": "Price defines the universe. Evidence determines the opportunity.",
    }


def _policy_for_asset(asset: MasterAsset, policies: Dict[str, PennyMarketPolicy] | None = None) -> PennyMarketPolicy | None:
    active_policies = policies or POLICIES
    market = _asset_market(asset)
    if market == "TH":
        return active_policies["TH"]
    if market == "US":
        return active_policies["US"]
    return None


def _asset_market(asset: MasterAsset) -> str | None:
    if asset.country == "Thailand" or asset.canonical_symbol.endswith(".BK"):
        return "TH"
    if asset.country in {"US", "United States"} or asset.exchange in {"NASDAQ", "NYSE", "NYSE Arca", "AMEX"}:
        return "US"
    return None


def _asset_is_supported_equity(asset: MasterAsset) -> bool:
    return asset.asset_class == "equity" and asset.asset_type in {"stock", "foreign_stock", "preferred_stock", "adr"}


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


def _financial_score_from_report(report: Dict[str, Any], quote: Dict[str, Any], missing: List[str]) -> Dict[str, Any]:
    score = _number(report.get("financial_intelligence_score"))
    status = report.get("status")
    if score is not None:
        missing.extend(report.get("missing_evidence") or [])
        return {
            "score": _clamp(round(score), 0, 100),
            "status": "PASS" if status in {"measured", "partial"} else "UNKNOWN",
            "source": "financial_intelligence",
            "confidence": report.get("confidence"),
            "completeness": report.get("completeness"),
            "profile": (report.get("profile") or {}).get("profile_type"),
        }
    missing.extend(report.get("missing_evidence") or [])
    if report.get("applicable") is False:
        missing.append("corporate_financial_intelligence_not_applicable")
        return {"score": None, "status": "UNKNOWN", "source": "financial_intelligence", "profile": (report.get("profile") or {}).get("profile_type")}
    fallback = _financial_score(quote, missing)
    return {**fallback, "source": "legacy_quote_fallback", "profile": (report.get("profile") or {}).get("profile_type")}


def _business_score_from_report(report: Dict[str, Any], missing: List[str]) -> Dict[str, Any]:
    score = _number(report.get("business_intelligence_score"))
    missing.extend(report.get("missing_business_evidence") or [])
    if score is not None:
        return {
            "score": _clamp(round(score), 0, 100),
            "status": "PASS" if report.get("status") in {"measured", "partial"} else "UNKNOWN",
            "source": "business_intelligence",
            "confidence": report.get("business_confidence"),
            "completeness": report.get("business_completeness"),
            "risk": report.get("business_risk"),
        }
    if report.get("applicable") is False:
        missing.append("corporate_business_intelligence_not_applicable")
    return {
        "score": None,
        "status": "UNKNOWN",
        "source": "business_intelligence",
        "confidence": report.get("business_confidence"),
        "completeness": report.get("business_completeness"),
        "risk": report.get("business_risk"),
    }


def _opportunity_setup(financial: Dict[str, Any], business: Dict[str, Any], growth: Dict[str, Any], liquidity: Dict[str, Any], risk_flags: List[Dict[str, Any]]) -> Dict[str, Any]:
    financial_score = _number(financial.get("score"))
    business_score = _number(business.get("score"))
    growth_score = _number(growth.get("score"))
    liquidity_score = _number(liquidity.get("score"))
    turnaround = bool(
        financial_score is not None
        and business_score is not None
        and growth_score is not None
        and financial_score >= 45
        and business_score >= 45
        and growth_score >= 58
    )
    value_trap = bool(
        (financial_score is not None and financial_score < 40)
        or (business_score is not None and business_score < 40)
        or liquidity.get("status") == "FAIL"
    )
    emerging_quality = bool(
        financial_score is not None
        and business_score is not None
        and liquidity_score is not None
        and financial_score >= 60
        and business_score >= 60
        and liquidity_score >= 55
        and not value_trap
    )
    category = "emerging_quality" if emerging_quality else "turnaround_candidate" if turnaround else "value_trap_risk" if value_trap else "insufficient_evidence"
    return {
        "turnaround_detected": turnaround,
        "value_trap_detected": value_trap,
        "emerging_quality_detected": emerging_quality,
        "category": category,
        "evidence": {
            "financial_score": financial_score,
            "business_score": business_score,
            "growth_score": growth_score,
            "liquidity_score": liquidity_score,
            "risk_flags": [risk["code"] for risk in risk_flags],
        },
        "interpretation": "Price defines eligibility only. The category is determined by Financial Intelligence, Business Intelligence, growth, liquidity, and risk evidence.",
    }


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


def _data_completeness(quote: Dict[str, Any], history: Dict[str, Any], catalyst: Dict[str, Any], business: Dict[str, Any] | None = None) -> int:
    business = business or {}
    checks = [
        quote.get("price") is not None,
        quote.get("volume") is not None,
        quote.get("change_percent") is not None,
        quote.get("market_cap") is not None,
        quote.get("debt_to_equity") is not None,
        quote.get("return_on_equity") is not None,
        quote.get("revenue_growth") is not None,
        len(_history_closes(history)) >= 10,
        business.get("status") == "PASS",
        catalyst.get("status") == "PASS",
        quote.get("timestamp") is not None,
    ]
    return round(sum(1 for item in checks if item) / len(checks) * 100)


def _data_confidence(completeness: int, liquidity: Dict[str, Any], financial: Dict[str, Any], business: Dict[str, Any], technical: Dict[str, Any], catalyst: Dict[str, Any], risks: List[Dict[str, Any]]) -> int:
    score = completeness
    for factor in [liquidity, financial, business, technical, catalyst]:
        if factor.get("status") == "UNKNOWN":
            score -= 6
        elif factor.get("status") == "FAIL":
            score -= 12
    score -= min(20, len([risk for risk in risks if risk["status"] == "unknown"]) * 4)
    return _clamp(round(score), 0, 100)


def _score_breakdown(factor_scores: Dict[str, Any], risk_penalty: int, risks: List[Dict[str, Any]], missing_data: List[str]) -> Dict[str, Any]:
    contributions = []
    raw_positive = 0.0
    for factor_id, weight in PENNY_FACTOR_WEIGHTS.items():
        measured = factor_scores.get(factor_id)
        raw_score = 35 if measured is None else _number(measured) or 0
        weighted = round(raw_score * weight, 2)
        raw_positive += weighted
        contributions.append({
            "factor_id": factor_id,
            "raw_score": measured,
            "substituted_score": raw_score if measured is None else None,
            "weight": weight,
            "weighted_contribution": weighted,
            "status": "unavailable" if measured is None else "available",
            "missing": measured is None,
        })
    risk_penalties = [{"code": risk["code"], "severity": risk["severity"], "status": risk["status"], "penalty": risk["penalty"], "evidence": risk["evidence"]} for risk in risks]
    explicit_penalty = sum(_number(item.get("penalty")) or 0 for item in risk_penalties)
    residual_penalty = max(0, risk_penalty - explicit_penalty)
    if residual_penalty:
        risk_penalties.append({"code": "data_uncertainty_penalty", "severity": "medium", "status": "unknown", "penalty": residual_penalty, "evidence": "Penalty added for unavailable liquidity or technical evidence."})
    final_before_bound = raw_positive - risk_penalty
    return {
        "raw_positive_score": round(raw_positive, 2),
        "factor_contributions": contributions,
        "total_risk_penalty": risk_penalty,
        "risk_penalties": risk_penalties,
        "final_score_before_bound": round(final_before_bound, 2),
        "rounding_policy": "round weighted positive score minus risk penalty, then bound to 0-100",
        "display_precision": "whole_number",
        "small_gap_policy": "Score differences inside a small configured margin should not be treated as materially superior.",
        "small_gap_margin_points": 3,
        "score_version": SCORE_VERSION,
        "config_version": CONFIGURATION_VERSION,
        "trust_policy_version": TRUST_POLICY_VERSION,
        "primary_evidence_policy": validate_primary_evidence_policy(PENNY_FACTOR_WEIGHTS),
        "missing_evidence": sorted(set(missing_data)),
    }


def _candidate_score_explanation(symbol: str, score: int, breakdown: Dict[str, Any], confidence: int, completeness: int, factor_scores: Dict[str, Any], risks: List[Dict[str, Any]], missing_data: List[str]) -> Dict[str, Any]:
    available = [row for row in breakdown["factor_contributions"] if not row["missing"]]
    strongest = sorted(available, key=lambda row: row["weighted_contribution"], reverse=True)[:2]
    weakest = sorted(available, key=lambda row: row["weighted_contribution"])[:1]
    largest_risk = sorted(risks, key=lambda risk: risk.get("penalty", 0), reverse=True)[:1]
    strongest_names = ", ".join(row["factor_id"] for row in strongest) or "no measured positive factor"
    weakest_name = weakest[0]["factor_id"] if weakest else "unavailable measured factors"
    risk_text = largest_risk[0]["code"] if largest_risk else "no explicit risk penalty"
    return {
        "title_th": "ทำไมได้คะแนนนี้",
        "title_en": "Why this score",
        "summary_th": f"{symbol} ได้คะแนน {score}/100 จากปัจจัยเด่นคือ {strongest_names} โดยมีปัจจัยอ่อนคือ {weakest_name} และความเสี่ยงหลักคือ {risk_text}",
        "summary_en": f"{symbol} scored {score}/100. Strongest contributors: {strongest_names}. Weakest measured factor: {weakest_name}. Largest risk: {risk_text}.",
        "strongest_factors": strongest,
        "weakest_factors": weakest,
        "largest_risks": largest_risk,
        "missing_evidence": sorted(set(missing_data)),
        "confidence_note_en": f"Data Confidence is {confidence}/100 and does not represent probability of profit.",
        "confidence_note_th": f"ความเชื่อมั่นของข้อมูลอยู่ที่ {confidence}/100 และไม่ใช่โอกาสทำกำไร",
        "completeness_note_en": f"Data Completeness is {completeness}/100 based on available evidence groups.",
        "completeness_note_th": f"ความครบถ้วนของข้อมูลอยู่ที่ {completeness}/100 จากกลุ่มหลักฐานที่มีอยู่",
        "factor_scores": factor_scores,
    }


def _confidence_explanation(confidence: int, completeness: int, liquidity: Dict[str, Any], financial: Dict[str, Any], business: Dict[str, Any], technical: Dict[str, Any], catalyst: Dict[str, Any], risks: List[Dict[str, Any]]) -> Dict[str, Any]:
    factor_status = {name: value.get("status") for name, value in {"liquidity": liquidity, "financial": financial, "business": business, "technical": technical, "catalyst": catalyst}.items()}
    reducers = [name for name, status in factor_status.items() if status in {"UNKNOWN", "FAIL"}]
    return {
        "score": confidence,
        "completeness_input": completeness,
        "factor_status": factor_status,
        "positive_drivers": [name for name, status in factor_status.items() if status == "PASS"],
        "negative_drivers": reducers,
        "unknown_risk_count": len([risk for risk in risks if risk.get("status") == "unknown"]),
        "statement_en": "Data Confidence measures evidence quality and availability. It is not probability of profit.",
        "statement_th": "ความเชื่อมั่นของข้อมูลวัดคุณภาพและความพร้อมของหลักฐาน ไม่ใช่โอกาสทำกำไร",
    }


def _completeness_explanation(completeness: int, quote: Dict[str, Any], history: Dict[str, Any], catalyst: Dict[str, Any], business: Dict[str, Any] | None = None) -> Dict[str, Any]:
    business = business or {}
    checks = {
        "price": quote.get("price") is not None,
        "volume": quote.get("volume") is not None,
        "change_percent": quote.get("change_percent") is not None,
        "market_cap": quote.get("market_cap") is not None,
        "debt_to_equity": quote.get("debt_to_equity") is not None,
        "return_on_equity": quote.get("return_on_equity") is not None,
        "revenue_growth": quote.get("revenue_growth") is not None,
        "history_coverage": len(_history_closes(history)) >= 10,
        "business_intelligence": business.get("status") == "PASS",
        "verified_catalyst": catalyst.get("status") == "PASS",
        "timestamp": quote.get("timestamp") is not None,
    }
    return {
        "score": completeness,
        "available": [key for key, ok in checks.items() if ok],
        "missing": [key for key, ok in checks.items() if not ok],
        "statement_en": "Completeness shows which evidence groups were available, missing, stale, or failed.",
        "statement_th": "ความครบถ้วนแสดงว่ากลุ่มหลักฐานใดมีพร้อม ขาดหาย ล่าช้า หรือดึงข้อมูลไม่สำเร็จ",
    }


def _uncertainty_disclosure(missing_data: List[str], provider_status: List[Dict[str, Any]], risks: List[Dict[str, Any]]) -> Dict[str, Any]:
    provider_failures = [row for row in provider_status if row.get("status") == "error"]
    uncertain_risks = [risk for risk in risks if risk.get("status") == "unknown"]
    stale = [row for row in provider_status if row.get("freshness_status") == "stale"]
    return {
        "statement_th": PENNY_ALGORITHM_DEFINITION.trust.uncertainty.statement_th,
        "statement_en": PENNY_ALGORITHM_DEFINITION.trust.uncertainty.statement_en,
        "missing_evidence": sorted(set(missing_data)),
        "provider_failures": provider_failures,
        "stale_evidence": stale,
        "uncertain_risks": uncertain_risks,
        "false_precision_note": PENNY_ALGORITHM_DEFINITION.trust.uncertainty.false_precision_rule,
    }


def _evidence_integrity_records(symbol: str, quote: Dict[str, Any], history: Dict[str, Any], catalyst: Dict[str, Any], provider_status: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    now = datetime.now(timezone.utc).isoformat()
    rows = [
        _evidence_record(symbol, "quote", quote.get("source") or quote.get("provider") or "Unavailable", quote.get("timestamp"), now, "price/liquidity/fundamentals", "available" if quote.get("price") is not None else "unavailable", "provider_reported", "Raw quote fields are normalized into price, liquidity, financial, and growth factors.", quote.get("error")),
        _evidence_record(symbol, "history", history.get("source") or history.get("provider") or "Unavailable", history.get("data_timestamp") or history.get("timestamp"), now, "technical", "available" if _history_closes(history) else "unavailable", "provider_reported", "Historical closes and volumes are transformed into technical and liquidity evidence.", history.get("error")),
        _evidence_record(symbol, "catalyst", catalyst.get("source") or "configured_news", None, now, "catalyst", "available" if catalyst.get("status") == "PASS" else "unavailable", "verified" if catalyst.get("status") == "PASS" else "unverified", "Provider-returned news items are used only when available; no synthetic catalyst is created.", None),
    ]
    for status in provider_status:
        if status.get("status") == "error":
            rows.append(_evidence_record(symbol, status.get("stage") or "provider", status.get("provider") or "Unavailable", status.get("timestamp"), now, status.get("stage") or "unknown", "failed", "unverified", "Provider request failed and remains visible.", status.get("reason")))
    return rows


def _evidence_record(symbol: str, evidence_type: str, provider: str, source_timestamp: Any, retrieval_timestamp: str, supported_factor: str, availability_status: str, verification_status: str, transformation_summary: str, limitation: Any) -> Dict[str, Any]:
    return {
        "evidence_id": f"{symbol}:{evidence_type}:{retrieval_timestamp}",
        "evidence_type": evidence_type,
        "provider": provider,
        "source_timestamp": source_timestamp,
        "retrieval_timestamp": retrieval_timestamp,
        "freshness_status": "stale" if availability_status == "stale" else "current_or_latest_available",
        "availability_status": availability_status,
        "verification_status": verification_status,
        "supported_factor": supported_factor,
        "candidate_symbol": symbol,
        "transformation_summary": transformation_summary,
        "data_limitations": [str(limitation)] if limitation else [],
    }


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


def _add_ranking_explanations(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    rows = []
    for index, item in enumerate(items):
        previous_item = items[index - 1] if index > 0 else None
        next_item = items[index + 1] if index + 1 < len(items) else None
        gap_previous = None if previous_item is None else round(previous_item["penny_opportunity_score"] - item["penny_opportunity_score"], 2)
        gap_next = None if next_item is None else round(item["penny_opportunity_score"] - next_item["penny_opportunity_score"], 2)
        tie_breaker = _ranking_tie_breaker(previous_item, item) if previous_item else None
        rank = item.get("rank")
        if rank == 1 and next_item:
            reason_en = f"Rank 1 because its final score is {gap_next} points above Rank 2 under the active score-first policy."
            reason_th = f"อยู่อันดับ 1 เพราะคะแนนสุดท้ายสูงกว่าอันดับ 2 อยู่ {gap_next} คะแนนตามนโยบายจัดอันดับจากคะแนนก่อน"
        elif previous_item:
            reason_en = f"Rank {rank} because it is {gap_previous} points below the previous candidate and {gap_next if gap_next is not None else 'no'} points above the next candidate."
            reason_th = f"อยู่อันดับ {rank} เพราะคะแนนต่ำกว่าตัวก่อนหน้า {gap_previous} คะแนน และสูงกว่าตัวถัดไป {gap_next if gap_next is not None else 'ไม่มี'} คะแนน"
        else:
            reason_en = "Only one qualified candidate is available in the current snapshot."
            reason_th = "มีผู้ผ่านเกณฑ์เพียงตัวเดียวใน snapshot ปัจจุบัน"
        rows.append({
            **item,
            "ranking_explanation": {
                "rank": rank,
                "final_score": item["penny_opportunity_score"],
                "score_gap_to_previous": gap_previous,
                "score_gap_to_next": gap_next,
                "tie_breaker_used": tie_breaker,
                "ranking_reason_en": reason_en,
                "ranking_reason_th": reason_th,
                "non_suitability_note_en": "Rank does not imply personal suitability or a buy recommendation.",
                "non_suitability_note_th": "อันดับไม่ได้แปลว่าเหมาะกับนักลงทุนทุกคนหรือเป็นคำแนะนำให้ซื้อ",
            },
        })
    return rows


def _ranking_tie_breaker(previous_item: Dict[str, Any] | None, item: Dict[str, Any]) -> str | None:
    if previous_item is None or previous_item.get("penny_opportunity_score") != item.get("penny_opportunity_score"):
        return None
    checks = [
        ("data_confidence", True),
        ("data_completeness", True),
        ("liquidity_score", True),
        ("risk_penalty", False),
        ("symbol", True),
    ]
    for field, higher_is_better in checks:
        previous_value = (previous_item.get("scores") or {}).get("liquidity") if field == "liquidity_score" else previous_item.get(field)
        value = (item.get("scores") or {}).get("liquidity") if field == "liquidity_score" else item.get(field)
        if previous_value != value:
            return field + (" DESC" if higher_is_better else " ASC")
    return "symbol ASC"


def _candidate_exclusion_explanation(candidate: Dict[str, Any], reason: str) -> Dict[str, Any]:
    risks = candidate.get("risks", [])
    missing = candidate.get("missing_data", [])
    if candidate.get("hard_disqualified"):
        status = "disqualified"
        primary = risks[0]["code"] if risks else "data_completeness_below_minimum"
    elif candidate.get("data_confidence", 0) < PENNY_ENGINE_DEFINITION.minimum_confidence:
        status = "low_confidence"
        primary = "data_confidence_below_minimum"
    elif candidate.get("data_completeness", 0) < PENNY_ENGINE_DEFINITION.minimum_completeness:
        status = "low_completeness"
        primary = "data_completeness_below_minimum"
    elif candidate.get("penny_opportunity_score", 0) < PENNY_ENGINE_DEFINITION.minimum_score:
        status = "below_cutoff"
        primary = "score_below_minimum"
    else:
        status = reason
        primary = "not_in_top_results"
    return {
        "symbol": candidate.get("symbol"),
        "status": status,
        "primary_reason": primary,
        "score": candidate.get("penny_opportunity_score"),
        "minimum_score": PENNY_ENGINE_DEFINITION.minimum_score,
        "data_confidence": candidate.get("data_confidence"),
        "minimum_confidence": PENNY_ENGINE_DEFINITION.minimum_confidence,
        "data_completeness": candidate.get("data_completeness"),
        "minimum_completeness": PENNY_ENGINE_DEFINITION.minimum_completeness,
        "risks": risks[:5],
        "missing_evidence": missing,
        "explanation_en": f"{candidate.get('symbol')} did not qualify because {primary}. This explanation uses the latest snapshot and does not trigger a new scan.",
        "explanation_th": f"{candidate.get('symbol')} ไม่ผ่านเกณฑ์เพราะ {primary} คำอธิบายนี้อ้างอิง snapshot ล่าสุดและไม่เริ่มการสแกนใหม่",
    }


def _strengths(liquidity: Dict[str, Any], financial: Dict[str, Any], business: Dict[str, Any], growth: Dict[str, Any], technical: Dict[str, Any], catalyst: Dict[str, Any], setup: Dict[str, Any]) -> List[str]:
    rows = []
    if liquidity["status"] == "PASS":
        rows.append("Liquidity requirement passed with provider volume evidence.")
    if technical["score"] >= 60:
        rows.append("Technical and momentum evidence is constructive.")
    if growth["score"] >= 55:
        rows.append("Available growth metrics are improving.")
    if financial["score"] >= 55:
        rows.append("Available financial quality metrics are supportive.")
    if business["score"] is not None and business["score"] >= 55:
        rows.append("Business Intelligence evidence is supportive.")
    if setup.get("turnaround_detected"):
        rows.append("Turnaround evidence is present from improving financial or business signals.")
    if setup.get("emerging_quality_detected"):
        rows.append("Emerging quality evidence is present across financial, business, and liquidity signals.")
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
