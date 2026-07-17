# RC4 Production Plan

## Rule

Do not merge, deploy, push, or tag until the Founder explicitly approves RC4.

## Safe Production Sync

1. Founder completes local RC4 walkthrough.
2. Backend tests pass.
3. Frontend build passes.
4. API smoke passes.
5. Founder approves merge.
6. Merge RC4 into `main`.
7. Push `main`.
8. Redeploy backend on Render.
9. Deploy frontend on Cloudflare Pages.
10. Smoke production.
11. Create a release tag only after production verification.

## Production Smoke URLs

- `/health`
- `/api/exchange-master`
- `/api/assets/search?q=NVDA`
- `/api/assets/search?q=ทอง`
- `/api/technical/NVDA`
- `/api/compare?symbols=NVDA,AMD`
- `/api/risk/NVDA`
- `/api/subscription/features`

## Rollback

If production smoke fails, do not tag. Redeploy the previous stable `main` commit and document the failing endpoint, response, and timestamp.
