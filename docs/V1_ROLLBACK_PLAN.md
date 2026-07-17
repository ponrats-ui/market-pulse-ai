# V1 Rollback Plan

## Goal

Restore the last stable production state quickly if V1 deployment causes production failures.

## Backend Rollback

1. Open Render dashboard.
2. Select the Market Pulse AI backend service.
3. Roll back to the previous successful deploy.
4. Confirm `/health` returns HTTP 200.
5. Smoke test `/api/assets/BTC-USD`, `/api/analysis/BTC-USD`, `/api/risk/BTC-USD`, and `/api/calendar`.

## Frontend Rollback

1. Open Cloudflare Pages.
2. Select `market-pulse-ai`.
3. Promote the previous successful deployment.
4. Confirm `https://market-pulse-ai.pages.dev` returns HTTP 200.
5. Smoke test dashboard, asset search, chart, compare, portfolio, PIA Assistant, Relax Mode, and language switch.

## Git Rollback

If a code rollback is required after merge:

1. Create a hotfix branch from `main`.
2. Revert the problematic merge commit.
3. Run backend tests and frontend build.
4. Push the hotfix branch and open a review.
5. Deploy only after approval.

## Communication

- Mark the incident as production stability.
- Record affected URLs and timestamps.
- Record whether data was unavailable, stale, or incorrect.
- Confirm no fabricated values were shown.
