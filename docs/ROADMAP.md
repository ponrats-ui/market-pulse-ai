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

## Sprint 2: Analysis Engine

- Add deterministic technical indicators
- Add support/resistance calculation
- Add financial statement ingestion and normalization
- Add source citations and timestamped data provenance
- Add stricter safety policy checks

## Sprint 3: Production Readiness

- Add provider failover and retry policies
- Add monitoring and error tracking
- Add CI build/test workflow
- Add backend deployment pipeline
- Add Cloudflare Pages preview and production environments
