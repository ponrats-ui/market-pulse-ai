# RC1 Release Checklist

Release: `1.0.0-rc1`  
Branch: `release/v1.0.0-rc1`  
Audit date: 2026-07-18  
Decision: `READY TO MERGE`

## Scope

This checklist records the FS-RC-100 Release Candidate Readiness and Production Audit for Market Pulse AI. It is an audit and release-hardening pass only. No features, UI redesign, provider expansion, or algorithm changes were introduced.

## Prerequisites

- FS-300 UI Freeze: PASS
- FS-DOC-100 Documentation Freeze: PASS
- FS-DOC-200 Engineering Handbook and Knowledge Base: PASS
- `RC2D_WIP_PATCH.diff`: left untouched and untracked

## Version Consistency

Expected version: `1.0.0-rc1`

Updated established version locations:

- `frontend/package.json`
- `frontend/package-lock.json`
- `backend/app/main.py`
- `frontend/src/main.tsx`
- `docs/DEPLOY_BACKEND_RENDER.md`

Result: PASS

## Production Configuration Audit

Frontend:

- Cloudflare Pages project: `market-pulse-ai`
- Build output directory: `dist`
- Production API base URL: `https://market-pulse-ai-api.onrender.com`
- Local loopback API values are guarded from leaking into production Pages host behavior.

Backend:

- Render service root: `backend`
- Build command: `pip install -r requirements.txt`
- Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- Health check path: `/health`
- Production CORS: `https://market-pulse-ai.pages.dev`

Result: PASS

## Security Audit

Secret scan findings:

- No committed API keys, private keys, access tokens, passwords, payment secrets, or service account blobs were found in audited source/config paths.
- Hits were limited to policy text, package metadata, environment variable names, and token-related code terminology.

Security posture:

- CORS is strict in `render.yaml` for production.
- Local development origins remain available through development configuration.
- YouTube embed behavior uses official embed/source URLs and does not store audio.
- Error handling avoids exposing secrets.

Result: PASS

## Zero-Mock Audit

Visible app text and source scans were checked for fake/demo/mock data risks.

Result:

- No fabricated prices, charts, AI outputs, news, or provider values were found.
- The only visible fabricated-data wording observed was a transparency notice: "No markers are fabricated."
- Provider-unavailable states remain explicit.

Result: PASS

## Validation Results

Frontend build:

- Command: `npm.cmd run build`
- Result: PASS
- Build time: 1.91s
- Largest chunks:
  - `react-Dmf4ZWtR.js`: 182.15 kB, gzip 57.34 kB
  - `index-BIw2QQb4.js`: 111.60 kB, gzip 31.57 kB
  - `ProfessionalChart-261JJRu8.js`: 16.21 kB, gzip 5.78 kB

Backend tests:

- Command: `.\.venv\Scripts\python.exe -m pytest --basetemp D:\market-pulse-ai\backend\.tmp-pytest-rc1`
- Result: PASS
- Tests: 113 passed

## API Smoke Results

All tested local endpoints returned HTTP 200.

Key endpoints:

- `/health`: 200, version `1.0.0-rc1`
- `/api/watchlist`: 200
- `/api/assets/search?q=NVDA&limit=5`: 200
- `/api/exchange-master`: 200
- `/api/master-asset-registry`: 200
- `/api/data-hub/status`: 200
- `/api/assets/quotes?symbols=...`: 200
- `/api/assets/BTC-USD`: 200
- `/api/assets/BTC-USD/history?range=1mo&interval=1d`: 200
- `/api/assets/NVDA`: 200
- `/api/assets/NVDA/history?range=1mo&interval=1d`: 200
- `/api/dashboard`: 200
- `/api/compare?symbols=NVDA,AMD`: 200
- `/api/calendar`: 200
- `/api/news?symbol=NVDA&limit=5`: 200
- `/api/news-impact/NVDA`: 200
- `/api/sentiment/BTC-USD`: 200
- `/api/macro`: 200
- `/api/market-condition`: 200
- `/api/analysis/NVDA`: 200
- `/api/risk/NVDA`: 200
- `/api/financials/NVDA`: 200
- `/api/assistant/ask`: 200
- `/api/portfolio/evaluate`: 200
- `/api/premium/entitlements/check`: 200
- `/api/alerts/evaluate`: 200
- `/api/digests/build`: 200

Performance notes:

- `/api/dashboard` took approximately 23.4s locally.
- `/api/sectors` returned a large payload and took approximately 14.0s locally.
- Broad batch quotes returned 200 and took approximately 6.9s locally in this run.
- These are P2 performance debt items, not RC1 merge blockers.

Result: PASS with P2 performance notes

## Browser Regression

Desktop:

- Dashboard loads: PASS
- Professional Chart renders: PASS
- Opportunities render as 10 real cards after each completed load: PASS
- Three refreshes completed successfully: PASS
- No horizontal overflow: PASS
- Chief AI compact view present: PASS
- Committee disclosures present: PASS
- Risk disclosure present: PASS
- Asset search returns `NVDA`: PASS
- Language switch Thai to English: PASS
- Compare route/view visible: PASS
- Portfolio route/view visible: PASS
- PIA Relax Mode remains optional and does not autoplay: PASS
- Clean reload console errors: PASS

Mobile:

- Viewport: 390 x 844
- No horizontal overflow: PASS
- Professional Chart fits viewport: PASS
- Navigation remains visible: PASS
- Relax panel does not block the full app: PASS
- Clean mobile console errors: PASS

Note: A stale local paper-portfolio state in the browser emitted a transient fetch error before the simulated portfolio was reset. The same backend payload returned HTTP 200, and a clean reload after reset produced no console errors. This is recorded as non-blocking local test-state noise.

Result: PASS

## P0/P1/P2 Findings

P0:

- None.

P1:

- Version inconsistency across frontend, backend, health response, About dialog, and deployment documentation.
- Status: FIXED.

P2:

- Local dashboard aggregation can take more than 20 seconds.
- `/api/sectors` payload is large and slow locally.
- Some optional provider-backed sections correctly display unavailable states until live provider configuration exists.
- Browser sessions with stale local portfolio state may show transient development console noise until the simulated portfolio is reset.

## Cloudflare Readiness

- Vite build passes.
- `frontend/wrangler.toml` uses `pages_build_output_dir = "dist"`.
- Production API base URL behavior is compatible with `market-pulse-ai.pages.dev`.
- No secrets are committed for frontend deployment.

Result: PASS

## Render Readiness

- `render.yaml` is present and production-oriented.
- Health endpoint returns `1.0.0-rc1` locally.
- Render CORS config is strict for Cloudflare Pages.
- Backend tests pass.

Result: PASS

## GitHub Readiness

- CI workflow runs backend tests and frontend build.
- Open-source governance and documentation are present from previous accepted work.
- `RC2D_WIP_PATCH.diff` remains untracked and must not be committed.

Result: PASS

## Rollback Checklist

If RC1 merge causes a production issue:

1. Stop deployment promotion.
2. Revert the RC1 merge commit on `main`.
3. Redeploy the last known good Render backend.
4. Redeploy the last known good Cloudflare Pages frontend.
5. Re-run `/health`, quote, dashboard, search, compare, portfolio, news, analysis, and mobile smoke tests.
6. Document the incident and corrective action before attempting a new RC.

## Merge Readiness Decision

Decision: `READY TO MERGE`

Conditions:

- Do not push, deploy, or tag until Founder approval is explicitly granted.
- Preserve `RC2D_WIP_PATCH.diff` as untracked.
- Treat P2 performance items as post-RC technical debt.
