# Cloudflare Pages Deployment

The frontend is ready for Cloudflare Pages. Sprint 1 still deploys the static frontend only; the FastAPI backend is deployed separately later.

## Cloudflare Pages Settings

- Framework preset: Vite
- Root directory: `frontend`
- Build command: `npm run build`
- Build output directory: `dist`
- Node version: current Cloudflare Pages LTS default or newer

## Environment Variables

For static-only deploys, leave this unset or empty. The frontend shows unavailable data states when it is empty or the API is unavailable.

```bash
VITE_API_BASE_URL=
```

For local backend testing:

```bash
VITE_API_BASE_URL=http://localhost:8000
```

When the backend is deployed later, update it to the production API URL:

```bash
VITE_API_BASE_URL=https://your-backend.example.com
```

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

Cloudflare Pages hosts the static frontend. The FastAPI backend needs separate hosting such as Cloudflare Containers, Render, Fly.io, Railway, or a VM. Keep CORS configured for your production frontend domain.
