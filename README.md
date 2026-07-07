# Market Pulse AI

Market Pulse AI is a financial intelligence dashboard foundation for tracking crypto, Thai stocks, global stocks, indices, energy, precious metals, and FX/macro assets. Users can select an asset category and asset to view price data, chart context, cautious AI analysis, risk analysis, financial statement analysis when applicable, and news placeholders.

> This is not financial advice. Market Pulse AI provides educational information and conservative analysis only.

## Features

- React + Vite + TypeScript frontend
- TailwindCSS dark market-terminal interface
- Recharts line chart
- lucide-react icons
- FastAPI backend
- yfinance-first provider abstraction
- Normalized quote and historical price responses
- In-memory TTL cache for quote, history, and watchlist data
- Watchlist, asset quote, asset history, dashboard, AI analysis, risk, and financial statement endpoints
- Cloudflare Pages-ready frontend build
- Mock fallback when frontend API URL is empty or unavailable

## Local Setup

### Backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Health check:

```bash
curl http://127.0.0.1:8000/health
```

Run tests:

```bash
.venv\Scripts\python.exe -m pytest
```

### Backend Endpoints

- `GET /health`
- `GET /api/watchlist`
- `GET /api/assets/{symbol}`
- `GET /api/assets/{symbol}/history?range=1mo&interval=1d`
- `GET /api/dashboard`
- `GET /api/analysis/{symbol}`
- `GET /api/risk/{symbol}`
- `GET /api/financials/{symbol}`

### Frontend

```bash
cd frontend
npm install
npm run dev
npm run build
```

The frontend uses `VITE_API_BASE_URL`. If it is empty or unavailable, it falls back to mock data.

Create `frontend/.env.local` for local backend integration:

```bash
VITE_API_BASE_URL=http://localhost:8000
```

## GitHub Workflow

```bash
git status
git add .
git commit -m "feat(data): add real market data layer"
git push
```

## Cloudflare Pages Deployment

1. Push the repository to GitHub.
2. In Cloudflare Dashboard, create or open the Pages project.
3. Set the root directory to `frontend`.
4. Build command: `npm run build`.
5. Build output directory: `dist`.
6. Leave `VITE_API_BASE_URL` empty for static mock fallback, or set it to the deployed backend API URL later.
7. Deploy.

See [docs/DEPLOYMENT_CLOUDFLARE.md](docs/DEPLOYMENT_CLOUDFLARE.md) for details.

## Risk Disclaimer

Market Pulse AI does not provide investment, tax, legal, or financial advice. All analysis is probabilistic, educational, and may be incomplete or incorrect. Users should verify data independently, define risk limits, and consult licensed professionals before making financial decisions.
