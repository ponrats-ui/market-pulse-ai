# Production Sync Checklist

## Scope

This checklist prepares Market Pulse AI for production synchronization. No deployment was executed during LP-1.

## Current Production Gap

Production backend currently returns 404 for these endpoints:

- `/api/news`
- `/api/macro`
- `/api/subscription/features`

The release branch includes these routes locally, so the finding is deployment drift rather than a missing route in the release candidate.

## Release Branch Endpoint Verification

Expected release branch routes:

- `/health`
- `/api/assets/search?q=NVDA`
- `/api/assets/BTC-USD`
- `/api/assets/BTC-USD/history?range=1mo&interval=1d`
- `/api/analysis/BTC-USD`
- `/api/risk/BTC-USD`
- `/api/financials/NVDA`
- `/api/compare?symbols=NVDA,AMD`
- `/api/news?symbol=NVDA`
- `/api/macro`
- `/api/calendar`
- `/api/subscription/features`
- `/api/premium/entitlements`

## Render Readiness

Render service configuration:

- Root directory: `backend`
- Runtime: Python
- Build command: `pip install -r requirements.txt`
- Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- Health check path: `/health`

Required Render environment variables:

- `APP_ENV=production`
- `LOG_LEVEL=info`
- `CORS_ALLOWED_ORIGINS=https://market-pulse-ai.pages.dev`
- Optional provider variables: `FINNHUB_API_KEY`, `ALPHA_VANTAGE_API_KEY`, `FRED_API_KEY`, `NEWSAPI_KEY`, `TRADING_ECONOMICS_KEY`, `NEWS_RSS_URL`
- Optional provider flags: `ENABLE_YAHOO_FINANCE_NEWS=true`, `ENABLE_ALTERNATIVE_ME_FEAR_GREED=false`

## Cloudflare Readiness

Cloudflare Pages settings:

- Project: `market-pulse-ai`
- Root directory: `frontend`
- Build command: `npm run build`
- Build output directory: `dist`
- Production variable: `VITE_API_BASE_URL=https://market-pulse-ai-api.onrender.com`

## CORS

Production CORS should allow only:

- `https://market-pulse-ai.pages.dev`

Do not use wildcard origins in production.

## Migration Requirements

- No database migration is required.
- No authentication migration is required.
- No payment migration is required.
- No saved alert rule migration is required.
- No broker integration migration is required.

## Deployment Readiness Steps

1. Founder approves LP-1.
2. Merge release branch only after explicit approval.
3. Push `main`.
4. Redeploy Render backend.
5. Verify `/health`.
6. Verify `/api/news`, `/api/macro`, and `/api/subscription/features`.
7. Set or confirm Cloudflare `VITE_API_BASE_URL`.
8. Deploy Cloudflare Pages.
9. Run production browser smoke.
10. Create release tag only after production smoke passes.

## Decision

Ready for Founder Final Acceptance Test after validation passes. Not yet production-synchronized because deployment is intentionally blocked by the LP-1 instructions.
