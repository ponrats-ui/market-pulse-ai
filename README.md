# Market Pulse AI

Market Pulse AI is a Thai-first bilingual financial intelligence dashboard for tracking crypto, Thai stocks, global stocks, indices, energy, precious metals, and FX/macro assets. Users can select an asset category and asset to view real market data, chart context, AI investment committee analysis, risk analysis, financial statement analysis when applicable, and clear unavailable states for sections that do not yet have a configured provider.

> This is not financial advice. Market Pulse AI provides educational information and conservative analysis only.

## Project Identity

- Created by: **Ponrat Saripan**
- Repository: [https://github.com/ponrats-ui/market-pulse-ai](https://github.com/ponrats-ui/market-pulse-ai)
- License: [MIT License](LICENSE)

Thai summary: Market Pulse AI สร้างโดย **Ponrat Saripan** และเผยแพร่เป็น open-source ภายใต้สัญญาอนุญาต MIT

## Features

- React + Vite + TypeScript frontend
- TailwindCSS dark market-terminal interface
- Thai and English localization with instant language switching
- Language preference stored in localStorage
- Chief Investment AI summary card
- Five-specialist AI Investment Committee
- Grouped financial statement cards with color indicators
- Fear & Greed / market sentiment widget
- News impact unavailable-state panel until a provider is configured
- Recharts line chart
- lucide-react icons
- FastAPI backend
- yfinance-first provider abstraction
- Normalized quote and historical price responses
- In-memory TTL cache for quote, history, and watchlist data
- Empty-state UI for Cloudflare Pages static deployments
- Explicit unavailable responses when frontend API URL is empty or unavailable

## Local Setup

### Backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
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

The frontend uses `VITE_API_BASE_URL`. If it is empty or unavailable, the UI displays unavailable states rather than fabricated market data.

Create `frontend/.env.local` for local backend integration:

```bash
VITE_API_BASE_URL=http://127.0.0.1:8000
```

## Production Deployment

Market Pulse AI uses a split production architecture:

- Cloudflare Pages serves the static Vite frontend from `frontend/dist`.
- Render runs the FastAPI backend from `backend`.
- The frontend connects to the backend through `VITE_API_BASE_URL`.
- The backend allows only configured CORS origins.

### Render Backend

Render can use the repository `render.yaml` file.

- Root directory: `backend`
- Build command: `pip install -r requirements.txt`
- Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- Health check path: `/health`

Backend environment variables:

```bash
APP_ENV=production
LOG_LEVEL=info
CORS_ALLOWED_ORIGINS=https://market-pulse-ai.pages.dev
```

See [Render backend deployment](docs/DEPLOY_BACKEND_RENDER.md).

## Cloudflare Pages Deployment

1. Push the repository to GitHub.
2. In Cloudflare Dashboard, open the Pages project.
3. Root directory: `frontend`.
4. Build command: `npm run build`.
5. Build output directory: `dist`.
6. Set `VITE_API_BASE_URL=https://YOUR_BACKEND_URL` for production backend data, or leave it empty only for static unavailable states.
7. Deploy.

Cloudflare Pages environment variable:

```bash
VITE_API_BASE_URL=https://YOUR_BACKEND_URL
```

After changing this value, redeploy the frontend.

## Open Source Governance

- [Authors](AUTHORS.md)
- [Contributing](CONTRIBUTING.md)
- [Code of Conduct](CODE_OF_CONDUCT.md)
- [Security Policy](SECURITY.md)
- [Vision](VISION.md)
- [Changelog](CHANGELOG.md)

## Sprint Documentation

- [Sprint 1 Data Layer](docs/SPRINT_1_DATA_LAYER.md)
- [Sprint 2 Localization](docs/SPRINT_2_LOCALIZATION.md)
- [AI Investment Committee](docs/AI_COMMITTEE.md)
- [MVP Stabilization](docs/MVP_STABILIZATION.md)

## Documentation Index

- [01 Product Vision](docs/01_PRODUCT_VISION.md)
- [02 System Architecture](docs/02_SYSTEM_ARCHITECTURE.md)
- [03 Algorithm Reference](docs/03_ALGORITHM_REFERENCE.md)
- [04 System Decisions](docs/04_SYSTEM_DECISIONS.md)
- [05 Release Engineering](docs/05_RELEASE_ENGINEERING.md)
- [06 Founder Bible](docs/06_FOUNDER_BIBLE.md)
- [07 Glossary](docs/07_GLOSSARY.md)
- [08 Contributing](docs/08_CONTRIBUTING.md)
- [09 Engineering Handbook](docs/09_ENGINEERING_HANDBOOK.md)
- [10 API Reference](docs/10_API_REFERENCE.md)
- [11 Data Model](docs/11_DATA_MODEL.md)
- [12 Sequence Diagrams](docs/12_SEQUENCE_DIAGRAMS.md)
- [13 State Management](docs/13_STATE_MANAGEMENT.md)
- [14 Testing Strategy](docs/14_TESTING_STRATEGY.md)
- [15 Security Model](docs/15_SECURITY_MODEL.md)
- [16 Performance Guide](docs/16_PERFORMANCE_GUIDE.md)
- [17 Operations Runbook](docs/17_OPERATIONS_RUNBOOK.md)
- [18 Incident Response](docs/18_INCIDENT_RESPONSE.md)
- [19 Troubleshooting](docs/19_TROUBLESHOOTING.md)
- [20 Provider Guide](docs/20_PROVIDER_GUIDE.md)
- [21 Version History](docs/21_VERSION_HISTORY.md)
- [22 Architecture Decision Records](docs/22_ARCHITECTURE_DECISION_RECORDS.md)

## Risk Disclaimer

Market Pulse AI does not provide investment, tax, legal, or financial advice. All analysis is probabilistic, educational, and may be incomplete or incorrect. Users should verify data independently, define risk limits, and consult licensed professionals before making financial decisions.

## Sprint 3 Research Terminal

Sprint 3 adds real-data research terminal features:

- Timeframe-based price chart using backend historical OHLCV data.
- Real asset comparison using quote and history endpoints.
- Rule-based AI Q&A assistant using quote, risk, and analysis context.
- LocalStorage portfolio analyzer.
- Economic calendar unavailable endpoint until a provider is configured.
- News impact provider interface with a provider-not-configured response.
- Sentiment unavailable endpoint until a provider is configured.

New endpoints:

- `GET /api/compare?symbols=BTC-USD,ETH-USD`
- `POST /api/assistant/ask`
- `GET /api/calendar`
- `GET /api/news-impact/{symbol}`
- `GET /api/sentiment/{symbol}`

See [Sprint 3 Research Terminal](docs/SPRINT_3_RESEARCH_TERMINAL.md) and [Real Data Policy](docs/REAL_DATA_POLICY.md).
