# Roadmap

## Sprint 0: Foundation

- Project scaffold for frontend, backend, configs, docs, and scripts
- Dashboard UI with mock fallback data
- FastAPI endpoints for health, watchlist, asset, analysis, risk, and financials
- yfinance provider abstraction
- Cloudflare Pages-ready frontend build

## Sprint 1: Real Market Data Layer

- Normalize quote and historical price responses
- Add provider registry
- Add in-memory TTL cache
- Add `/api/assets/{symbol}/history`
- Add `/api/dashboard`
- Integrate frontend with backend when `VITE_API_BASE_URL` is set
- Preserve mock fallback for Cloudflare static deployments
- Add lightweight backend tests

## Sprint 2: Thai Localization and AI Investment Committee

- Add Thai-first and English localization
- Add language selector with localStorage persistence
- Replace single analysis surface with Chief Investment AI plus five specialist panels
- Improve financial statement card grouping
- Upgrade news placeholder to a clearer impact panel
- Add Fear & Greed / market sentiment widget
- Improve spacing, contrast, and mobile responsiveness

## Sprint 3: Research Terminal

- Add professional chart controls and indicator calculations
- Add asset comparison charts
- Add rule-based AI Q&A assistant
- Add portfolio analyzer placeholder
- Add economic calendar and news impact endpoints

## Sprint 4: Production Readiness

- Stabilize MVP quality before adding more product scope
- Add provider failover and retry policies
- Add monitoring and error tracking
- Add CI build/test workflow
- Add backend deployment pipeline
- Evaluate workspace migration to `apps/` and `packages/`

## Sprint 3 Completed Scope

- Timeframe chart controls using backend history.
- Real-data asset comparison endpoint and UI.
- Rule-based AI Q&A assistant endpoint and UI.
- LocalStorage portfolio analyzer.
- Economic calendar placeholder.
- News impact provider interface and mock implementation.
- Sentiment placeholder endpoint and widget.

## Sprint 4 Candidates

- Batch quote endpoint for full portfolio valuation.
- Real news provider integration.
- Real economic calendar provider.
- Technical indicators calculated from OHLCV history.
- Optional LLM provider interface with safety policies.
