# Cloudflare Pages Deployment

The frontend is ready for Cloudflare Pages. Sprint 1 still deploys the static frontend only; the FastAPI backend is deployed separately later.

## Cloudflare Pages Settings

- Framework preset: Vite
- Root directory: `frontend`
- Build command: `npm run build`
- Build output directory: `dist`
- Node version: current Cloudflare Pages LTS default or newer

## Environment Variables

For production with a deployed backend, set this in **Cloudflare Pages > Settings > Environment variables**:

```bash
VITE_API_BASE_URL=https://YOUR_BACKEND_URL
```

For local backend testing:

```bash
VITE_API_BASE_URL=http://127.0.0.1:8000
```

For static-only preview deploys, leave this unset or empty. The frontend shows unavailable data states when it is empty or the API is unavailable.

Use separate production and preview values if Cloudflare Pages uses different backend services.

Do not commit secrets or private API keys. This variable should only contain the public backend base URL.

## Wrangler Deploy

From the frontend directory:

```bash
npm install
npm run build
npx wrangler pages deploy dist --project-name market-pulse-ai
```

If Wrangler asks for authentication, run:

```bash
npx wrangler login
```

## Backend Note

Cloudflare Pages hosts the static frontend. The FastAPI backend is prepared for Render using `render.yaml`. Keep `CORS_ALLOWED_ORIGINS` configured for the production Pages domain and any future custom domains.
