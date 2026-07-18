# V1 Deployment Report

## Deployment Status

No merge, push, deploy, or tag was executed in Phase F.

## Production URLs Reviewed

- Frontend: `https://market-pulse-ai.pages.dev`
- Backend: `https://market-pulse-ai-api.onrender.com`
- Health: `https://market-pulse-ai-api.onrender.com/health`

## Local Validation

- Backend tests: PASS, 84 passed
- Frontend build: PASS
- Local API smoke: PASS
- Desktop browser review: PASS
- Mobile browser review: PASS

## Production Smoke

Current production frontend returned HTTP 200.

Current production backend results:

- `/health`: 200
- `/api/assets/search?q=NVDA`: 200
- `/api/assets/BTC-USD`: 200
- `/api/assets/BTC-USD/history?range=1mo&interval=1d`: 200
- `/api/analysis/BTC-USD`: 200
- `/api/risk/BTC-USD`: 200
- `/api/financials/NVDA`: 200
- `/api/compare?symbols=NVDA,AMD`: 200
- `/api/calendar`: 200
- `/api/news?symbol=NVDA`: 404 on current production
- `/api/macro`: 404 on current production
- `/api/subscription/features`: 404 on current production

## Interpretation

The release branch serves the missing endpoints locally, but current production has not been deployed from this branch. Because deployment is explicitly forbidden until Founder approval after Phase F, production remains behind the release candidate.

## Required Deployment Sequence After Approval

1. Merge `release/v1-production-candidate` into `main`.
2. Push `main`.
3. Redeploy Render backend.
4. Confirm Render environment variables.
5. Build and deploy Cloudflare Pages frontend.
6. Run production smoke tests again.
7. Create tag `v1.0.0-rc1` only after smoke passes.
