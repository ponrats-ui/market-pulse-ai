# Market Pulse AI

Market Pulse AI is a production-ready financial intelligence dashboard foundation for tracking crypto, Thai stocks, global stocks, indices, energy, precious metals, and FX/macro assets. Users can select an asset category and asset to view price data, chart context, cautious AI analysis, risk analysis, financial statement analysis when applicable, and news placeholders.

> This is not financial advice. Market Pulse AI provides educational information and conservative analysis only.

## Features

- React + Vite + TypeScript frontend
- TailwindCSS dark market-terminal interface
- Recharts line chart
- lucide-react icons
- FastAPI backend
- Provider abstraction with yfinance-first implementation
- Watchlist, asset price, AI analysis, risk, and financial statement endpoints
- Cloudflare Pages-ready frontend build
- GitHub-ready repository structure

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

### Frontend

```bash
cd frontend
npm install
npm run dev
npm run build
```

The frontend expects `VITE_API_BASE_URL`. If unset, it defaults to `http://127.0.0.1:8000`.

## GitHub Workflow

```bash
git status
git add .
git commit -m "chore: initialize market pulse ai foundation"
git branch -M main
git remote add origin https://github.com/<owner>/market-pulse-ai.git
git push -u origin main
```

## Cloudflare Pages Deployment

1. Push the repository to GitHub.
2. In Cloudflare Dashboard, create a Pages project from the GitHub repository.
3. Set the root directory to `frontend`.
4. Build command: `npm run build`.
5. Build output directory: `dist`.
6. Add `VITE_API_BASE_URL` pointing to the deployed backend API.
7. Deploy.

## Risk Disclaimer

Market Pulse AI does not provide investment, tax, legal, or financial advice. All analysis is probabilistic, educational, and may be incomplete or incorrect. Users should verify data independently, define risk limits, and consult licensed professionals before making financial decisions.
