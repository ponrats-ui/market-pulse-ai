# RC2D Production Sync Plan

## Rule

Do not merge, deploy, push, or tag RC2D until the Founder explicitly approves the local RC2D founder test.

## Safe Production Steps

1. Founder approves RC2D locally.
2. Merge feature branch into `main`.
3. Push `main` to GitHub.
4. Render auto-deploys backend, or manually redeploy backend from Render.
5. Build frontend:

```powershell
cd D:\market-pulse-ai\frontend
npm.cmd run build
```

6. Deploy Cloudflare Pages frontend.
7. Smoke test production.
8. Create Git tag only after successful production verification.

Recommended tag:

```text
v0.7.0-rc2d-founder-test
```

## Backend Production Smoke

Verify HTTP 200:

```text
/health
/api/analysis/BTC-USD
/api/news
/api/macro
```

## Frontend Production Smoke

Verify:

- Asset Search
- Dashboard
- AI Analysis
- News
- Risk
- Financial Analysis
- Portfolio
- Watchlist
- Compare
- Language Switch

## Deployment Report

After production verification, create:

```text
docs/RC2D_DEPLOYMENT_REPORT.md
```

Include:

- Deployment URLs
- Git commit
- Git tag
- Production version
- Backend health
- Frontend build
- Smoke test results
- Known issues

## Rollback

If production smoke fails:

- Do not tag.
- Revert or redeploy the previous stable main commit.
- Record the failed endpoint, response, and timestamp.
