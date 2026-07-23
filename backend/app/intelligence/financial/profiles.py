from __future__ import annotations

from app.intelligence.financial.models import AssetIntelligenceProfile

PROFILE_VERSION = "asset-intelligence-profile-v1"
PRIMARY_FINANCIAL_WEIGHT_TARGET = 0.55
PRIMARY_FINANCIAL_WEIGHT_RANGE = (0.45, 0.65)

CORPORATE_DOMAINS = [
    "financial_health",
    "profitability",
    "growth_quality",
    "cash_flow_quality",
    "balance_sheet_strength",
    "efficiency",
    "earnings_quality",
    "accounting_quality",
    "valuation_context",
    "financial_risk",
]


def profile_catalog() -> dict[str, AssetIntelligenceProfile]:
    return {
        "corporate_financial": AssetIntelligenceProfile(
            "corporate_financial",
            "General Operating Company",
            "financial_intelligence",
            PRIMARY_FINANCIAL_WEIGHT_TARGET,
            PRIMARY_FINANCIAL_WEIGHT_RANGE,
            ["valuation_context", "liquidity", "market_participation", "technical_context", "verified_catalysts", "market_context"],
            CORPORATE_DOMAINS,
            ["on_chain_network_metrics", "commodity_inventory", "metal_real_yield_model"],
            "general_operating_company",
            ["revenue_or_income", "cash_flow_or_balance_sheet", "valuation_or_profitability"],
            ["latest provider-returned annual or trailing data"],
            {"minimum_for_measured": 55, "minimum_for_partial": 25},
            {"minimum_for_measured": 60, "minimum_for_partial": 20},
            "financial_reporting_and_balance_sheet_risk_v1",
            PROFILE_VERSION,
            ["Financial reporting may be delayed, incomplete, restated, unaudited, inconsistent, manipulated, or affected by accounting policy."],
            ["Does not predict future returns.", "Does not guarantee that a financially stronger company is a good investment."],
        ),
        "financial_institution": _special_boundary("financial_institution", "Financial Institution Boundary", "financial_institution_boundary", "Banks and finance companies must not be evaluated with ordinary-company debt metrics without adjustment."),
        "insurance": _special_boundary("insurance", "Insurance Company Boundary", "insurance_boundary", "Insurers require reserve, underwriting, and capital evidence beyond the generic provider payload."),
        "reit_financial": _special_boundary("reit_financial", "REIT / Property Trust Boundary", "reit_boundary", "REITs require distribution, occupancy, property cash-flow, and debt-maturity evidence."),
        "fund_intelligence": _non_corporate("fund_intelligence", "Fund Intelligence Boundary", "fund_intelligence", "Funds and ETFs are not operating companies and require holdings, concentration, tracking, liquidity, expense, and structure evidence."),
        "on_chain": _non_corporate("on_chain", "On-chain Intelligence Boundary", "on_chain", "Crypto assets require network, liquidity, custody, and regulatory evidence."),
        "macro": _non_corporate("macro", "Macro Intelligence Boundary", "macro", "Macro assets require rates, inflation, currency, liquidity, and policy context."),
        "commodity_supply_demand": _non_corporate("commodity_supply_demand", "Commodity Supply and Demand Boundary", "commodity_supply_demand", "Commodities require supply, demand, inventory, seasonality, and geopolitical context."),
        "unsupported": _non_corporate("unsupported", "Unsupported Intelligence Boundary", "unsupported", "No supported intelligence profile can be selected from available classification evidence."),
        "unknown": _non_corporate("unknown", "Unknown Intelligence Boundary", "unknown", "Classification is insufficient to safely select an intelligence model."),
    }


def get_profile(profile_type: str) -> AssetIntelligenceProfile:
    return profile_catalog().get(profile_type, profile_catalog()["unknown"])


def _special_boundary(profile_type: str, display_name: str, model: str, limitation: str) -> AssetIntelligenceProfile:
    return AssetIntelligenceProfile(
        profile_type,
        display_name,
        "financial_intelligence",
        PRIMARY_FINANCIAL_WEIGHT_TARGET,
        PRIMARY_FINANCIAL_WEIGHT_RANGE,
        ["sector_specific_financial_evidence", "valuation_context", "liquidity"],
        ["profile_boundary", "provider_availability", "valuation_context"],
        ["ordinary_company_debt_threshold", "generic_cash_flow_only_model"],
        model,
        ["sector_specific_provider_fields"],
        ["latest provider-returned sector data"],
        {"minimum_for_measured": 65, "minimum_for_partial": 30},
        {"minimum_for_measured": 70, "minimum_for_partial": 25},
        f"{model}_risk_v1",
        PROFILE_VERSION,
        [limitation, "This sprint implements the boundary contract and does not fabricate sector-specific evidence."],
        ["Boundary profile only until sector-specific provider evidence is configured."],
    )


def _non_corporate(profile_type: str, display_name: str, primary: str, limitation: str) -> AssetIntelligenceProfile:
    return AssetIntelligenceProfile(
        profile_type,
        display_name,
        primary,
        None,
        None,
        [],
        [],
        ["corporate_financial_statement_model"],
        f"{profile_type}_boundary",
        [],
        [],
        {},
        {},
        f"{profile_type}_boundary_v1",
        PROFILE_VERSION,
        [limitation],
        ["Architecture contract only in this sprint."],
    )
