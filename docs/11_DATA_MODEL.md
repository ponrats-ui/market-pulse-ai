# 11 Data Model

## Table of Contents

- [Purpose](#purpose)
- [Model Conventions](#model-conventions)
- [Asset](#asset)
- [Quote](#quote)
- [Opportunity](#opportunity)
- [Portfolio](#portfolio)
- [Risk](#risk)
- [TechnicalAnalysis](#technicalanalysis)
- [FinancialHealth](#financialhealth)
- [ChiefAIResult](#chiefairesult)
- [Recommendation](#recommendation)
- [ConfidenceScore](#confidencescore)
- [Watchlist](#watchlist)
- [NewsItem](#newsitem)
- [CalendarEvent](#calendarevent)
- [PaperTrade](#papertrade)
- [Current Production](#current-production)
- [Future Roadmap](#future-roadmap)
- [Known Limitations](#known-limitations)
- [Related Documents](#related-documents)

## Purpose

This document describes the domain models used by Market Pulse AI and how they move through the system. The canonical frontend TypeScript reference is `frontend/src/types/market.ts`; backend services return compatible dictionaries.

## Model Conventions

- `null` means unknown or unavailable, not zero.
- `source`, `provider`, `timestamp`, `metadata`, or unavailable reason should be preserved where available.
- Financial data must not be invented.
- Some models are UI-domain concepts assembled from multiple API responses.

## Asset

Purpose: represent a searchable research target.

Fields: `symbol`, `canonical_symbol`, `display_symbol`, `label`, `company_name`, `thai_name`, `asset_type`, `market`, `sector`, `industry`, `country`, `currency`, `exchange`, aliases, coverage fields.

Relationships: quote, history, capabilities, search, sector browser, watchlist.

Validation: symbol should resolve through registry or provider.

Lifecycle: registry entry -> search result -> selected asset -> API requests.

## Quote

Purpose: current market snapshot.

Fields: symbol, name, asset type, currency, price, previous close, change, change percent, OHLC, volume, fundamentals, metadata, source, timestamp, warning/error.

Relationships: chart, risk, analysis, compare, portfolio, watchlist.

Validation: numeric fields may be null; source must identify provider or unavailable.

Lifecycle: provider response -> normalized quote -> cache -> API -> UI.

## Opportunity

Purpose: dashboard research candidate.

Fields: symbol, label, price, currency, change percent, score, recommendation label, reasons, source, timestamp, unavailable factors, sparkline.

Relationships: batch quotes, sparklines, selected asset.

Validation: must use real quote fields; no fake score from missing provider data.

Lifecycle: batch quote -> frontend scoring heuristic -> opportunity card.

## Portfolio

Purpose: simulated holdings and valuation.

Fields: holdings, cash balance, market value, cost basis, realized P/L, unrealized P/L, allocation, risk score, diversification, transaction history, stale quote list.

Relationships: quote provider, paper trades.

Validation: insufficient cash and insufficient shares must be surfaced.

Lifecycle: local user input -> backend evaluation -> UI state -> local persistence.

## Risk

Purpose: downside and uncertainty model.

Fields: symbol, asset type, risk score, volatility level, main risks, risk controls, facts, interpretation, categories, disclaimer, metadata.

Relationships: quote, history, analysis, Chief AI, AI Committee.

Validation: score may be null if evidence is insufficient.

Lifecycle: quote/history -> risk service -> dashboard risk panel.

## TechnicalAnalysis

Purpose: technical indicators from history.

Fields: symbol, status, available indicators, indicator map, series, interpretation, source, message, disclaimer.

Relationships: history, professional chart.

Validation: insufficient history returns unavailable status.

Lifecycle: history endpoint -> technical service -> chart overlays.

## FinancialHealth

Purpose: compact view of corporate fundamentals.

Fields: applicable, status, facts, interpretation, risks, cautious action plan, alternative fundamentals, metadata.

Relationships: financial statement analysis, Chief AI, AI Committee.

Validation: non-corporate assets must show not applicable.

Lifecycle: fundamentals provider -> financial service -> UI health cards.

## ChiefAIResult

Purpose: aggregate evidence into cautious educational view.

Fields: recommendation, confidence, reasons, positive factors, negative factors, monitor items, disclaimer.

Relationships: quote, risk, financials, analysis response.

Validation: no guaranteed investment advice.

Lifecycle: API responses -> frontend compact card or backend analysis payload.

## Recommendation

Purpose: cautious action label.

Fields: label, confidence, supporting reasons, risks, limitations.

Valid labels include educational terms such as wait, hold, reduce risk, watch closely, or avoid. They are not regulated advice.

Lifecycle: analysis evidence -> recommendation policy -> UI.

## ConfidenceScore

Purpose: describe evidence strength.

Fields: score or label, evidence count, missing data, conflicts, limitations.

Validation: low-data responses must not appear high confidence.

Lifecycle: evidence collection -> confidence engine -> analysis response.

## Watchlist

Purpose: user monitoring list.

Fields: assets, sort mode, selected symbol, quote map, sparklines, local persistence metadata.

Relationships: asset registry, quote batch, sparkline endpoint.

Validation: user-selected assets should remain stable locally.

Lifecycle: localStorage -> quote refresh -> watchlist UI.

## NewsItem

Purpose: provider-returned news article or impact item.

Fields: headline, source, URL, published time, impact level, sentiment, explanation, risk warning.

Validation: no fabricated headlines.

Lifecycle: provider article -> news service -> UI.

## CalendarEvent

Purpose: economic event item where provider exists.

Fields: date, name, region, impact level, related assets, Thai note, English note.

Validation: no generated economic events.

Lifecycle: provider calendar -> calendar endpoint -> UI.

## PaperTrade

Purpose: simulated transaction.

Fields: symbol, side, quantity, price, date.

Relationships: portfolio evaluation, realized P/L, average cost.

Validation: side is buy or sell, quantity and price should be positive, sell quantity cannot exceed holding.

Lifecycle: user input -> local transaction list -> backend portfolio evaluation.

## Current Production

The current model layer is shared by convention through TypeScript interfaces and Python dictionaries. The system relies on tests and contract consistency rather than generated shared packages.

## Future Roadmap

- shared OpenAPI or generated contract package
- stricter Pydantic response models
- schema examples generated from tests

## Known Limitations

- Some backend responses are dictionaries rather than explicit Pydantic response models.
- Frontend interfaces may not include every adaptive analysis field.

## Related Documents

- [10 API Reference](10_API_REFERENCE.md)
- [03 Algorithm Reference](03_ALGORITHM_REFERENCE.md)
- [13 State Management](13_STATE_MANAGEMENT.md)

