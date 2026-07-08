# Deploy Backend to Render

This guide deploys only the FastAPI backend. The frontend remains on Cloudflare Pages.

## Prerequisites

- GitHub repository connected to Render
- Render account
- Backend code in `backend`
- Frontend already deployed or ready for Cloudflare Pages

## Create Render Service

1. Open Render Dashboard.
2. Select **New Web Service**.
3. Connect the GitHub repository.
4. Choose the Market Pulse AI repository.
5. Set the root directory to `backend`.

## Build Command

```bash
pip install -r requirements.txt
```

## Start Command

```bash
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

Render provides `PORT` at runtime. Do not hardcode a production port.

## Environment Variables

Use non-secret deployment values:

```bash
APP_ENV=production
LOG_LEVEL=info
CORS_ALLOWED_ORIGINS=https://market-pulse-ai.pages.dev
```

For preview or custom domains, add origins as a comma-separated list:

```bash
CORS_ALLOWED_ORIGINS=https://market-pulse-ai.pages.dev,https://your-custom-domain.com
```

Do not use wildcard origins in production. Do not commit secrets.

## Health Check URL

After deployment, verify:

```text
https://YOUR_RENDER_SERVICE.onrender.com/health
```

Expected JSON:

```json
{
  "status": "ok",
  "service": "market-pulse-ai",
  "version": "0.3.0"
}
```

## Connect Cloudflare Pages

In Cloudflare Pages, configure:

```bash
VITE_API_BASE_URL=https://YOUR_RENDER_SERVICE.onrender.com
```

Redeploy the frontend after changing the variable.

## Common Troubleshooting

- `CORS error`: Add the exact frontend origin to `CORS_ALLOWED_ORIGINS`.
- `Application failed to start`: Confirm the Render root directory is `backend`.
- `Port binding error`: Confirm the start command uses `$PORT`.
- `Market data unavailable`: Check yfinance availability and backend logs.
- `Frontend still shows unavailable data`: Confirm `VITE_API_BASE_URL` is set in Cloudflare Pages and the frontend has been redeployed.

## Rollback Steps

1. In Render, open the backend service.
2. Select a previous successful deploy.
3. Redeploy that version.
4. Verify `/health`.
5. If the backend URL changes, update `VITE_API_BASE_URL` in Cloudflare Pages and redeploy the frontend.
