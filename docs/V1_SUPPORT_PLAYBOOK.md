# V1 Support Playbook

## First Response

1. Confirm whether the issue is frontend, backend, provider, or browser-specific.
2. Ask for the URL, asset symbol, timestamp, and browser/device.
3. Do not ask users for API keys, passwords, or private financial data.

## Health Checks

- Frontend: `https://market-pulse-ai.pages.dev`
- Backend health: `https://market-pulse-ai-api.onrender.com/health`
- BTC quote: `/api/assets/BTC-USD`
- BTC analysis: `/api/analysis/BTC-USD`
- News: `/api/news?symbol=NVDA`
- Macro: `/api/macro`

## Common Issues

- Provider unavailable: verify the UI displays transparent unavailable states.
- Render cold start: retry after service wakes.
- CORS error: verify `CORS_ALLOWED_ORIGINS` matches the Cloudflare Pages URL.
- Stale data: check payload timestamp and provider source.
- Relax Mode stream unavailable: verify the source permits embedding.

## Escalation

Escalate immediately if:

- The app fabricates prices, charts, news, or analysis.
- The app displays guaranteed investment advice.
- Secrets or provider keys appear in logs.
- Production returns 5xx errors on core endpoints.

## Rate-Limit Strategy

Current mitigation relies on backend cache TTLs and transparent unavailable states. A formal rate limiter should be added before high-traffic launch.
