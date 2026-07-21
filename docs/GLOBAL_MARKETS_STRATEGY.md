# Global Markets Strategy

## Table of Contents

- [Purpose](#purpose)
- [Global Equity Markets](#global-equity-markets)
- [Asset Classes](#asset-classes)
- [Cross-Market Intelligence](#cross-market-intelligence)
- [Example Relationship Maps](#example-relationship-maps)
- [Architecture Principles](#architecture-principles)
- [Long-Term Product Standard](#long-term-product-standard)

## Purpose

Market Pulse AI should eventually understand global markets as connected systems, not isolated tickers.

The long-term strategy is to expand coverage across regions, asset classes, and market relationships while preserving explainability, transparent unavailable states, and production data integrity.

## Global Equity Markets

Long-term market coverage should include:

| Region | Markets |
| --- | --- |
| Southeast Asia | Thailand, Singapore, Vietnam, Indonesia, Malaysia, Philippines |
| North America | USA, Canada, Mexico |
| Europe | United Kingdom, Germany, France, Netherlands, Switzerland, Italy, Spain |
| East Asia | Japan, South Korea, China, Hong Kong, Taiwan |
| South Asia | India |
| Oceania | Australia |
| Latin America | Brazil |
| Africa | South Africa |
| Middle East | Saudi Arabia, United Arab Emirates |

Coverage should expand only when data quality, symbol normalization, exchange mapping, and unavailable-state handling are reliable enough for production.

## Asset Classes

Long-term asset-class coverage should include:

- Stocks
- ETF
- REIT
- Crypto
- Forex
- Indices
- Government Bonds
- Corporate Bonds
- Precious Metals
- Energy
- Agriculture

Each asset class may require different analysis methods. The product should not force stock-style financial statement analysis onto assets where it is not applicable.

## Cross-Market Intelligence

The platform should eventually understand relationships between assets instead of analysing each asset independently.

Cross-market intelligence should help answer questions such as:

- Which macro variables matter for this asset?
- Which commodities, currencies, yields, or indices influence this company or sector?
- Which related markets confirm or contradict the asset signal?
- Which risks come from the broader market rather than the selected asset?
- Which relationships are supported by current evidence and which are only theoretical?

Cross-market output must remain explainable. It should show the relationship, evidence, confidence, and limitations.

## Example Relationship Maps

### PTT

```text
PTT
↓
Oil
USDTHB
Energy Index
OPEC
```

Potential interpretation:

- Oil prices may affect revenue and margins.
- USDTHB may affect imported costs, exports, and reported financials.
- Energy sector strength may influence investor appetite.
- OPEC decisions may influence supply expectations and oil volatility.

### AOT

```text
AOT
↓
Tourism
Oil
Airlines
USDTHB
```

Potential interpretation:

- Tourism flows may affect passenger volume.
- Oil prices may influence airline profitability and travel costs.
- Airline capacity may affect airport traffic.
- USDTHB may affect tourist affordability and international flows.

### NVDA

```text
NVDA
↓
NASDAQ
Semiconductor Index
US Bond Yield
Dollar Index
AI Sector
Data Center
```

Potential interpretation:

- NASDAQ direction may affect growth-stock sentiment.
- Semiconductor index movement may confirm or weaken sector momentum.
- US bond yields may affect valuation multiples.
- Dollar strength may affect global revenue translation.
- AI and data-center demand may influence growth expectations.

### Gold

```text
Gold
↓
Dollar Index
Real Yield
Inflation
Federal Reserve
```

Potential interpretation:

- Dollar strength can pressure gold prices.
- Real yields may influence opportunity cost.
- Inflation expectations may affect safe-haven demand.
- Federal Reserve policy can change liquidity and yield expectations.

### Bitcoin

```text
Bitcoin
↓
Dollar
Nasdaq
Risk Appetite
Liquidity
```

Potential interpretation:

- Dollar strength can affect crypto market liquidity and risk appetite.
- Nasdaq movement may reflect appetite for high-beta assets.
- Global liquidity can influence speculative demand.
- Market stress can change correlations quickly.

## Architecture Principles

Future architecture should preserve these principles:

- **Single Source of Truth:** Each data domain should have a clear owner and a clear normalized contract.
- **Production is Source of Truth:** A feature is not accepted only because it works locally. Production verification is required for production-facing changes.
- **One Prompt, One Commit, One Deploy, Founder Review, Approve:** Future work should remain reviewable and reversible.
- **Explainability above complexity:** Prefer understandable models and visible evidence over opaque sophistication.
- **Avoid black-box AI whenever possible:** If a score or view can be explained deterministically, it should be.
- **Transparent fallback:** If a relationship, data provider, or macro input is unavailable, the product should say so directly.

## Long-Term Product Standard

Global expansion must not weaken trust.

Before adding a new market, provider, or asset class, the product should confirm:

- Symbol normalization is reliable.
- Provider attribution is clear.
- Missing data behavior is honest.
- Analysis logic is appropriate for the asset type.
- UI labels and explanations remain understandable.
- The user can distinguish facts, interpretation, risk, and educational actions.
