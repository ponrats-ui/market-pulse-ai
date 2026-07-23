from __future__ import annotations

from app.data_hub.master_asset_registry import MasterAsset, get_registry_asset
from app.intelligence.financial.models import AssetClassification, AssetClassificationConfidence, AssetClassificationEvidence


def classify_asset_for_intelligence(symbol: str, quote: dict | None = None, asset: MasterAsset | None = None) -> AssetClassification:
    registry_asset = asset or get_registry_asset(symbol)
    quote = quote or {}
    raw_class = ((registry_asset.asset_class if registry_asset else quote.get("asset_class")) or "").lower()
    raw_type = ((registry_asset.asset_type if registry_asset else quote.get("asset_type")) or quote.get("type") or "").lower()
    sector = (registry_asset.sector if registry_asset else quote.get("sector")) or None
    industry = (registry_asset.industry if registry_asset else quote.get("industry")) or None
    exchange = (registry_asset.exchange if registry_asset else quote.get("exchange")) or None
    market = (registry_asset.market if registry_asset else quote.get("market")) or None
    canonical = registry_asset.canonical_symbol if registry_asset else symbol
    symbol_upper = canonical.upper()
    sector_text = f"{sector or ''} {industry or ''} {raw_type}".lower()
    evidence = [
        AssetClassificationEvidence("asset_class", raw_class or None, "master_asset_registry" if registry_asset else "quote", "Base asset class used for intelligence routing."),
        AssetClassificationEvidence("asset_type", raw_type or None, "master_asset_registry" if registry_asset else "quote", "Security subtype used for profile selection."),
        AssetClassificationEvidence("sector", sector, "master_asset_registry" if registry_asset else "quote", "Sector used for financial institution, insurance, and REIT boundaries."),
    ]
    asset_class = "unknown"
    subtype = raw_type or "unknown"
    profile = "unknown"
    primary = "unknown"
    fallback = "unknown"
    limitations: list[str] = []
    confidence = 75 if registry_asset else 30

    if raw_class in {"equity", "stock", "thai_stock", "global_stock"} or raw_type in {"stock", "common_stock", "equity"}:
        asset_class = "corporate_equity"
        profile = "corporate_financial"
        primary = "financial_intelligence"
        fallback = "selected"
        if any(token in sector_text for token in ["bank", "financial", "finance", "securities"]):
            profile = "financial_institution"
            limitations.append("Financial institution boundary selected; ordinary leverage thresholds are not applied.")
        elif "insurance" in sector_text:
            profile = "insurance"
            limitations.append("Insurance boundary selected; insurer-specific evidence is required for measured scoring.")
        elif any(token in sector_text for token in ["reit", "property trust", "real estate investment trust"]) or symbol_upper.endswith(".REIT"):
            asset_class = "reit"
            profile = "reit_financial"
            limitations.append("REIT boundary selected; ordinary EPS and free cash flow alone are insufficient.")
    elif raw_class in {"etf", "fund"} or raw_type in {"etf", "fund", "mutual_fund"}:
        asset_class = "etf" if raw_type == "etf" or raw_class == "etf" else "mutual_fund"
        profile = "fund_intelligence"
        primary = "fund_intelligence"
        fallback = "not_applicable"
        limitations.append("Funds and ETFs are not ordinary operating companies.")
    elif raw_class == "crypto" or raw_type == "crypto" or (symbol_upper.endswith("-USD") and symbol_upper.split("-")[0] in {"BTC", "ETH", "SOL", "XRP"}):
        asset_class = "crypto"
        profile = "on_chain"
        primary = "on_chain"
        fallback = "not_applicable"
        limitations.append("Crypto assets do not publish corporate financial statements.")
    elif raw_class in {"commodity", "precious_metal"} or raw_type in {"commodity", "metal", "future"}:
        asset_class = "precious_metal" if any(token in symbol_upper for token in ["GC=", "SI=", "GLD", "SLV"]) else "commodity"
        profile = "commodity_supply_demand"
        primary = "commodity_supply_demand"
        fallback = "not_applicable"
        limitations.append("Commodity instruments require supply and demand evidence, not corporate financial statements.")
    elif raw_class in {"currency", "fx", "macro"} or raw_type in {"currency", "fx", "macro"} or "=X" in symbol_upper:
        asset_class = "currency"
        profile = "macro"
        primary = "macro"
        fallback = "not_applicable"
        limitations.append("Currency and macro instruments require macro evidence, not corporate financial statements.")
    elif raw_class == "index" or raw_type == "index" or symbol_upper.startswith("^"):
        asset_class = "index"
        profile = "macro"
        primary = "macro"
        fallback = "not_applicable"
        limitations.append("Indices require constituent and macro context, not one corporate statement model.")
    else:
        limitations.append("Asset classification is insufficient to safely select an intelligence model.")
        confidence = 15

    level = "high" if confidence >= 70 else "medium" if confidence >= 45 else "low" if confidence > 0 else "unknown"
    return AssetClassification(canonical, exchange, market, asset_class, subtype, sector, industry, profile, primary, "master_asset_registry" if registry_asset else "quote_or_symbol_fallback", AssetClassificationConfidence(confidence, level, ["Registry asset found."] if registry_asset else ["Used quote or symbol fallback."]), limitations, fallback, evidence)
