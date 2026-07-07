# Cloudflare Pages Deployment

The frontend is ready for Cloudflare Pages.

## Build Settings

- Framework preset: Vite
- Root directory: `frontend`
- Build command: `npm run build`
- Build output directory: `dist`
- Node version: current Cloudflare Pages LTS default or newer

## Environment Variables

Set this variable in Cloudflare Pages:

```bash
VITE_API_BASE_URL=https://your-backend.example.com
```

## Steps

1. Push the repository to GitHub.
2. Open Cloudflare Dashboard.
3. Go to Workers & Pages.
4. Create a Pages project from the GitHub repository.
5. Configure build settings above.
6. Add `VITE_API_BASE_URL`.
7. Deploy preview, verify the dashboard, then promote to production.

## Backend Note

Cloudflare Pages hosts the static frontend. The FastAPI backend needs separate hosting such as Cloudflare Containers, Render, Fly.io, Railway, or a VM. Keep CORS configured for your production frontend domain.
