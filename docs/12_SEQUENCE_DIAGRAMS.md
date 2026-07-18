# 12 Sequence Diagrams

## Table of Contents

- [Purpose](#purpose)
- [Dashboard Load](#dashboard-load)
- [Opportunity Scan](#opportunity-scan)
- [Chart Request](#chart-request)
- [Search](#search)
- [Portfolio Analysis](#portfolio-analysis)
- [Chief AI](#chief-ai)
- [Risk Analysis](#risk-analysis)
- [Compare](#compare)
- [Provider Failure](#provider-failure)
- [Timeout Recovery](#timeout-recovery)
- [Current Production](#current-production)
- [Future Roadmap](#future-roadmap)
- [Known Limitations](#known-limitations)
- [Related Documents](#related-documents)

## Purpose

This document captures the main request and failure flows using Markdown diagrams. The diagrams are intentionally text-based so they survive code review and long-term maintenance.

## Dashboard Load

```mermaid
sequenceDiagram
  participant User
  participant UI as React Dashboard
  participant API as FastAPI
  participant Provider as Provider/Cache
  User->>UI: Open app
  UI->>API: GET /api/watchlist
  UI->>API: GET /api/assets/{symbol}
  UI->>API: GET /api/assets/{symbol}/history
  UI->>API: GET /api/analysis/{symbol}
  API->>Provider: Fetch or cache data
  Provider-->>API: Normalized data or unavailable
  API-->>UI: Responses
  UI-->>User: Render dashboard
```

## Opportunity Scan

```mermaid
sequenceDiagram
  participant UI
  participant API
  participant Cache
  participant Provider
  UI->>API: GET /api/assets/quotes?symbols=...
  API->>Cache: Check quote cache
  Cache-->>API: Hit or miss
  API->>Provider: Fetch missing quotes
  Provider-->>API: Quote or unavailable
  API-->>UI: Batch quote items
  UI-->>UI: Score only available evidence
  UI-->>User: Opportunity cards
```

## Chart Request

```mermaid
sequenceDiagram
  participant UI
  participant API
  participant Provider
  UI->>API: GET /api/assets/{symbol}/history?range=1mo&interval=1d
  API->>Provider: Historical OHLCV
  Provider-->>API: Candles or unavailable
  UI->>API: GET /api/technical/{symbol}
  API-->>UI: Indicators from history
  UI-->>User: Professional Chart
```

## Search

```mermaid
sequenceDiagram
  participant User
  participant UI
  participant API
  participant Registry
  User->>UI: Type symbol/name/Thai name
  UI->>UI: Debounce query
  UI->>API: GET /api/assets/search?q=...
  API->>Registry: Search master registry
  Registry-->>API: Ranked matches
  API-->>UI: AssetSearchResponse
  UI-->>User: Keyboard-selectable results
```

## Portfolio Analysis

```mermaid
sequenceDiagram
  participant User
  participant UI
  participant API
  participant Provider
  User->>UI: Add simulated trade
  UI->>API: POST /api/portfolio/evaluate
  API->>Provider: Current quotes
  Provider-->>API: Quotes or unavailable
  API-->>UI: PortfolioEvaluationResponse
  UI-->>User: P/L, allocation, risk, limitations
```

## Chief AI

```mermaid
sequenceDiagram
  participant UI
  participant API
  participant Analysis
  participant Provider
  UI->>API: GET /api/analysis/{symbol}
  API->>Provider: Quote + history
  Provider-->>API: Evidence
  API->>Analysis: Build cautious analysis
  Analysis-->>API: Facts, interpretation, risks, confidence
  API-->>UI: Analysis response
  UI-->>User: Chief AI compact card
```

## Risk Analysis

```mermaid
sequenceDiagram
  participant UI
  participant API
  participant Risk
  participant Provider
  UI->>API: GET /api/risk/{symbol}
  API->>Provider: Quote + history
  API->>Risk: Score downside and uncertainty
  Risk-->>API: RiskResponse
  API-->>UI: Risk categories and controls
```

## Compare

```mermaid
sequenceDiagram
  participant UI
  participant API
  participant Compare
  participant Provider
  UI->>API: GET /api/compare?symbols=NVDA,AMD
  API->>Provider: Quotes and histories
  API->>Compare: Build table and metrics
  Compare-->>API: CompareResponse
  API-->>UI: Comparison data
```

## Provider Failure

```mermaid
sequenceDiagram
  participant UI
  participant API
  participant Provider
  UI->>API: Request provider-backed data
  API->>Provider: Fetch
  Provider--xAPI: Failure, empty, or timeout
  API-->>UI: Unavailable or partial payload
  UI-->>User: Transparent unavailable state
```

## Timeout Recovery

```mermaid
sequenceDiagram
  participant UI
  participant API
  UI->>API: Request with timeout
  API-->>UI: Slow or no response
  UI->>UI: Abort active request after timeout
  UI-->>User: Controlled unavailable/loading state
  Note over UI: No fabricated fallback values
```

## Current Production

These flows reflect current local and production architecture. Batch quote timeout is intentionally longer than ordinary requests.

## Future Roadmap

- add deployment sequence diagrams
- add alert delivery diagrams once sending is enabled
- add cloud sync diagrams after authentication design

## Known Limitations

- Diagrams are conceptual and omit some cache internals.
- Mermaid rendering depends on the Markdown viewer.

## Related Documents

- [02 System Architecture](02_SYSTEM_ARCHITECTURE.md)
- [10 API Reference](10_API_REFERENCE.md)
- [13 State Management](13_STATE_MANAGEMENT.md)

