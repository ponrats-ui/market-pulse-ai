# Cloudflare Pages Deployment

The frontend is ready for Cloudflare Pages. Sprint 0 deploys the static frontend only and can safely use mock data while the FastAPI backend is deployed separately later.

## Cloudflare Pages Settings

- Framework preset: Vite
- Root directory: `frontend`
- Build command: `npm run build`
- Build output directory: `dist`
- Node version: current Cloudflare Pages LTS default or newer

## Environment Variables

For Sprint 0, leave this unset or set it to a local/mock placeholder. The frontend falls back to mock data if the API is unavailable.

```bash
VITE_API_BASE_URL=
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

## Dashboard Deploy

1. Push the repository to GitHub.
2. Open Cloudflare Dashboard.
3. Go to Workers & Pages.
4. Create a Pages project from the GitHub repository.
5. Configure the Pages settings above.
6. Leave `VITE_API_BASE_URL` unset for Sprint 0, or set it to a local/mock placeholder.
7. Deploy preview, verify the dashboard, then promote to production.

## Backend Note

Cloudflare Pages hosts the static frontend. The FastAPI backend needs separate hosting such as Cloudflare Containers, Render, Fly.io, Railway, or a VM. Keep CORS configured for your production frontend domain.
