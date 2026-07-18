# 10 API Reference

## Table of Contents

- [Purpose](#purpose)
- [Conventions](#conventions)
- [Authentication](#authentication)
- [Common Error Behavior](#common-error-behavior)
- [Endpoint Matrix](#endpoint-matrix)
- [Endpoint Details](#endpoint-details)
- [Current Production](#current-production)
- [Future Roadmap](#future-roadmap)
- [Known Limitations](#known-limitations)
- [Related Documents](#related-documents)

## Purpose

This document records the current production API surface implemented in `backend/app/main.py`. It does not invent future endpoints.

## Conventions

- Base path locally: `http://127.0.0.1:8000`.
- Production base path: Render service URL.
- Response examples are representative shapes, not guaranteed full payloads.
- Provider-dependent endpoints may return partial or unavailable fields.
- Authentication is not implemented in the current release.

## Authentication

Current production: no user authentication. The backend relies on CORS allowlists and public educational-data endpoints.

Future roadmap: authentication is required before cloud portfolio sync, private user data, or real notification delivery.

## Common Error Behavior

Validation errors use FastAPI/Pydantic behavior, usually HTTP 422. Provider failures should be represented as controlled payloads with unavailable, partial, warning, or error fields when the route can still respond.

## Endpoint Matrix

| Status | Method | Route | Purpose | Provider Dependency |
| --- | --- | --- | --- | --- |
| Implemented | GET | `/health` | health probe | none |
| Implemented | GET | `/api/watchlist` | default categories/assets | config/cache |
| Implemented | GET | `/api/assets/search` | search master registry | registry |
| Implemented | GET | `/api/exchange-master` | exchange metadata | config/data |
| Implemented | GET | `/api/master-asset-registry` | master registry metadata | config/data |
| Implemented | GET | `/api/data-hub/status` | provider/data hub status | provider router |
| Implemented | GET | `/api/data-hub/assets/{symbol}/capabilities` | data capability view | data hub |
| Implemented | GET | `/api/data-hub/resolve` | resolve query to symbol | data hub |
| Implemented | GET | `/api/data-hub/universe/metadata` | universe metadata | exchange master |
| Implemented | GET | `/api/sectors` | sector browser | registry |
| Implemented | GET | `/api/sectors/{sector}/assets` | assets by sector | registry |
| Implemented | GET | `/api/assets/quotes` | batch quotes | yfinance/cache |
| Implemented | GET | `/api/assets/sparklines` | seven-day sparklines | history provider |
| Implemented | GET | `/api/assets/{symbol}` | quote | yfinance/cache |
| Implemented | GET | `/api/assets/{symbol}/history` | history | yfinance/cache |
| Implemented | GET | `/api/technical/{symbol}` | technical analysis | history |
| Implemented | GET | `/api/dashboard` | grouped dashboard quotes | watchlist/quotes |
| Implemented | GET | `/api/compare` | compare assets | quotes/history |
| Implemented | POST | `/api/assistant/ask` | PIA answer | quote/history/risk/analysis |
| Implemented | POST | `/api/portfolio/evaluate` | simulated portfolio valuation | quote provider |
| Partial | GET | `/api/calendar` | economic calendar | provider optional |
| Partial | GET | `/api/news` | provider news | provider optional/Yahoo RSS |
| Partial | GET | `/api/news-impact/{symbol}` | news impact | news provider |
| Partial | GET | `/api/sentiment/{symbol}` | sentiment | provider optional |
| Partial | GET | `/api/macro` | macro indicators | provider optional |
| Implemented | GET | `/api/market-condition` | market proxy state | yfinance/sentiment |
| Implemented | GET | `/api/subscription/features` | feature catalog | config |
| Implemented | GET | `/api/premium/entitlements` | entitlement matrix | config |
| Implemented | POST | `/api/premium/entitlements/check` | entitlement check | config |
| Implemented | POST | `/api/alerts/evaluate` | alert rule evaluation | local rules |
| Implemented | POST | `/api/digests/build` | digest preview | local rules |
| Partial | GET | `/api/company-events/{symbol}` | company events | provider optional |
| Implemented | GET | `/api/analysis/{symbol}` | AI analysis | quote/history/analysis engine |
| Implemented | GET | `/api/risk/{symbol}` | risk analysis | quote/history/risk engine |
| Implemented | GET | `/api/financials/{symbol}` | financial analysis | fundamentals/quote |

## Endpoint Details

### GET `/health`

Purpose: Render and local health check.

Request: none.

Response: `{ "status": "ok", "service": "market-pulse-ai", "version": "..." }`.

Validation: none.

Error Codes: should be 200 when app starts.

Authentication: none.

Known Limitations: does not validate upstream providers.

### GET `/api/watchlist`

Purpose: returns configured default asset categories.

Request: none.

Response: `WatchlistResponse`.

Example: `{ "categories": [{ "id": "crypto", "assets": [] }] }`.

Validation: config shape.

Provider Dependency: local config/cache.

Known Limitations: user watchlist is frontend-local; this endpoint is default data.

### GET `/api/assets/search`

Purpose: search by symbol, company name, Thai name, alias, sector, country, or exchange filters.

Request: query params `q`, `asset_class`, `exchange`, `country`, `sector`, `industry`, `limit`.

Response: `AssetSearchResponse`.

Example: `{ "query": "NVDA", "count": 1, "assets": [], "source": "master_asset_registry" }`.

Validation: `limit` 1-100.

Known Limitations: search coverage depends on registry content.

### GET `/api/exchange-master`

Purpose: returns exchange master metadata.

Request: none.

Response: metadata object.

Known Limitations: metadata, not live market data.

### GET `/api/master-asset-registry`

Purpose: returns master asset registry metadata.

Request: none.

Response: metadata object.

Known Limitations: not a full quote endpoint.

### GET `/api/data-hub/status`

Purpose: provider router, exchange master, and registry validation status.

Request: none.

Response: provider status plus validation metadata.

Known Limitations: status does not guarantee every symbol quote succeeds.

### GET `/api/data-hub/assets/{symbol}/capabilities`

Purpose: report available capabilities for a symbol.

Request: path `symbol`.

Response: capabilities object.

Known Limitations: capability does not guarantee provider availability at request time.

### GET `/api/data-hub/resolve`

Purpose: resolve a user query to a canonical asset.

Request: query `q`.

Response: resolved asset/provider route object.

Known Limitations: unknown symbols may return unresolved/unavailable state.

### GET `/api/data-hub/universe/metadata`

Purpose: returns universe metadata from the exchange master.

Request: none.

Response: metadata object.

Known Limitations: metadata only.

### GET `/api/sectors`

Purpose: sector browser.

Request: none.

Response: `SectorResponse`.

Known Limitations: registry-derived, not live fundamentals.

### GET `/api/sectors/{sector}/assets`

Purpose: list assets in a sector.

Request: path `sector`, query `limit` 1-50.

Response: assets list.

Known Limitations: sector labels depend on registry/provider metadata.

### GET `/api/assets/quotes`

Purpose: quote up to 25 symbols.

Request: query `symbols=NVDA,AMD`.

Response: `QuotesResponse`.

Example: `{ "symbols": ["NVDA"], "items": [{ "symbol": "NVDA", "price": 123.45 }], "source": "yfinance" }`.

Validation: backend truncates to first 25 selected symbols.

Provider Dependency: yfinance/cache.

Known Limitations: local batch request can be slow.

### GET `/api/assets/sparklines`

Purpose: seven-day sparkline points from historical close data.

Request: query `symbols`.

Response: `SparklinesResponse`.

Known Limitations: unavailable if history provider returns no close prices.

### GET `/api/assets/{symbol}`

Purpose: one quote.

Request: path `symbol`.

Response: `AssetQuote`.

Provider Dependency: yfinance/cache.

Known Limitations: null fields remain null.

### GET `/api/assets/{symbol}/history`

Purpose: historical OHLCV data.

Request: path `symbol`, query `range`, `interval`.

Response: `AssetHistory`.

Known Limitations: provider may omit candles, volume, or full range.

### GET `/api/technical/{symbol}`

Purpose: technical analysis from history.

Request: path `symbol`, query `range`, `interval`.

Response: `TechnicalResponse`.

Known Limitations: unavailable if history is insufficient.

### GET `/api/dashboard`

Purpose: grouped categories enriched with quotes.

Request: none.

Response: categories with embedded quote payloads.

Known Limitations: slower than static watchlist because it fetches quotes.

### GET `/api/compare`

Purpose: compare selected assets.

Request: query `symbols=NVDA,AMD`.

Response: `CompareResponse`.

Known Limitations: correlation and performance require sufficient history.

### POST `/api/assistant/ask`

Purpose: rule-based PIA assistant answer using selected asset context.

Request: `{ "question": "...", "selected_symbol": "NVDA", "language": "th" }`.

Response: `AssistantResponse`.

Known Limitations: not a live LLM endpoint.

### POST `/api/portfolio/evaluate`

Purpose: evaluate simulated holdings or transactions.

Request: `{ "holdings": [{ "symbol": "NVDA", "quantity": 1, "averageCost": 100, "currency": "USD" }] }`.

Response: `PortfolioEvaluationResponse`.

Known Limitations: simulated only; no broker, tax, fee, slippage, or FX conversion provider.

### GET `/api/calendar`

Purpose: economic calendar provider surface.

Request: none.

Response: `CalendarResponse`.

Status: Partial.

Known Limitations: returns unavailable/provider-not-configured state unless a real provider is configured.

### GET `/api/news`

Purpose: provider-backed news list.

Request: query `symbol`, `limit` 1-25.

Response: news response with items or unavailable state.

Status: Partial.

Known Limitations: depends on configured provider/reachable RSS.

### GET `/api/news-impact/{symbol}`

Purpose: interpret news impact using provider-returned news only.

Request: path `symbol`.

Response: `NewsImpactResponse`.

Status: Partial.

Known Limitations: no fake articles; empty/unavailable when provider lacks data.

### GET `/api/sentiment/{symbol}`

Purpose: sentiment provider surface.

Request: path `symbol`.

Response: `SentimentResponse`.

Status: Partial.

Known Limitations: provider must be configured/enabled.

### GET `/api/macro`

Purpose: macro indicators provider surface.

Request: none.

Response: macro payload.

Status: Partial.

Known Limitations: optional provider credentials required.

### GET `/api/market-condition`

Purpose: broad market condition proxy from major symbols and sentiment response.

Request: none.

Response: `MarketConditionResponse`.

Known Limitations: proxy basket is heuristic and depends on quote availability.

### GET `/api/subscription/features`

Purpose: feature catalog for free/premium/admin/disabled states.

Request: none.

Response: subscription feature configuration.

Known Limitations: payments are not active.

### GET `/api/premium/entitlements`

Purpose: entitlement matrix.

Request: none.

Response: entitlement config.

Known Limitations: no paid billing enforcement in current release.

### POST `/api/premium/entitlements/check`

Purpose: evaluate one plan/feature pair.

Request: `{ "plan": "free", "feature": "market_data" }`.

Response: entitlement result.

Known Limitations: local policy check only.

### POST `/api/alerts/evaluate`

Purpose: evaluate alert rules without sending outbound notifications.

Request: `{ "plan": "free", "rules": [], "context": {}, "quiet_mode": {} }`.

Response: evaluated alerts/audit state.

Known Limitations: no real outbound channels in current release.

### POST `/api/digests/build`

Purpose: build digest preview content.

Request: `{ "kind": "morning_brief", "context": {} }`.

Response: digest payload.

Known Limitations: no automatic sending.

### GET `/api/company-events/{symbol}`

Purpose: company event provider surface.

Request: path `symbol`.

Response: events payload.

Status: Partial.

Known Limitations: provider unavailable unless configured.

### GET `/api/analysis/{symbol}`

Purpose: cautious AI analysis response.

Request: path `symbol`.

Response: `AnalysisResponse` plus real intelligence status.

Known Limitations: heuristic, educational, not guaranteed advice.

### GET `/api/risk/{symbol}`

Purpose: risk analysis from quote and history.

Request: path `symbol`.

Response: `RiskResponse`.

Known Limitations: no broker liquidity or order-book model.

### GET `/api/financials/{symbol}`

Purpose: financial statement/fundamental analysis when applicable.

Request: path `symbol`.

Response: `FinancialsResponse`.

Known Limitations: non-corporate assets return not-applicable explanation.

## Current Production

All routes above are present in `backend/app/main.py` on the release branch. Partial means the route exists but depends on optional providers or intentionally returns transparent unavailable state.

## Future Roadmap

- OpenAPI contract export
- request/response examples generated from tests
- authenticated user endpoints after privacy design

## Known Limitations

- No authentication.
- Provider results vary by upstream availability.
- Some endpoint examples are intentionally compact.

## Related Documents

- [09 Engineering Handbook](09_ENGINEERING_HANDBOOK.md)
- [11 Data Model](11_DATA_MODEL.md)
- [20 Provider Guide](20_PROVIDER_GUIDE.md)
- [15 Security Model](15_SECURITY_MODEL.md)

