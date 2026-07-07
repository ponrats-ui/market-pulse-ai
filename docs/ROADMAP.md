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

- Add provider failover and retry policies
- Add monitoring and error tracking
- Add CI build/test workflow
- Add backend deployment pipeline
- Evaluate workspace migration to `apps/` and `packages/`
