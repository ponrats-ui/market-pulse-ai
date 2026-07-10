# RC3 Production Sync Plan

## Rule

Do not merge, deploy, push, or tag RC3 until Founder approval is explicit.

## Safe Steps

1. Run RC3 Founder Test locally.
2. Confirm backend tests, frontend build, integration smoke, and performance checks pass.
3. Founder approves RC3.
4. Merge `feature/rc3-founder-production-intelligence` into `main`.
5. Push `main`.
6. Redeploy backend on Render.
7. Verify backend production endpoints:
   - `/health`
   - `/api/assets/search?q=NVDA`
   - `/api/sectors`
   - `/api/technical/NVDA`
   - `/api/analysis/NVDA`
   - `/api/news?symbol=NVDA`
   - `/api/calendar`
8. Build frontend.
9. Deploy Cloudflare Pages.
10. Smoke test production website.
11. Create a release tag only after production verification.

## Suggested Tag

```text
v0.8.0-rc3-founder-production-intelligence
```

## Production Smoke Checklist

- Universal Search
- Autocomplete
- Sector Browser
- Dashboard
- Technical Indicators
- AI Committee
- Fundamental Analysis
- Risk Engine
- News Impact
- Economic Calendar
- Paper Portfolio
- Watchlist
- Compare
- AI Assistant
- Language Switch

## Rollback

If production smoke fails, do not tag. Redeploy the previous stable `main` commit and document failed endpoint, browser console output, and timestamp.
