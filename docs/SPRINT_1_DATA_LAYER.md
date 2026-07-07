# Sprint 1 Data Layer

Sprint 1 adds a real market data layer with normalized provider responses, in-memory caching, and frontend integration.

## Provider Abstraction

Providers implement `MarketDataProvider` in `backend/app/providers/base.py`.

Required provider methods:

- `get_quote(symbol)` returns a normalized quote.
- `get_history(symbol, range, interval)` returns normalized OHLCV history.
- `get_financials(symbol)` returns partial financial statement data where available.

The active provider is selected through `backend/app/providers/registry.py`. Sprint 1 uses yfinance.

## Cache TTL

The cache is implemented in `backend/app/services/cache.py`.

- Quote TTL: 60 seconds
- Historical TTL: 300 seconds
- Watchlist TTL: 300 seconds

Cache keys include provider, endpoint type, symbol, range, and interval where relevant.

## API Endpoints

- `GET /health`
- `GET /api/watchlist`
- `GET /api/assets/{symbol}`
- `GET /api/assets/{symbol}/history?range=1mo&interval=1d`
- `GET /api/dashboard`
- `GET /api/analysis/{symbol}`
- `GET /api/risk/{symbol}`
- `GET /api/financials/{symbol}`

Failed provider calls return structured `error` fields instead of breaking the whole response.

## Local Run Commands

```bash
cd backend
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m pytest
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

```bash
cd frontend
npm.cmd install
npm.cmd run build
```

## yfinance Limitations

- Data can be delayed, incomplete, revised, or temporarily unavailable.
- Some Thai market index symbols may vary by provider availability.
- yfinance is suitable for Sprint 1 prototyping, not a paid-market-data replacement.
- Production deployments should add request timeouts, retries, observability, and provider failover.

## Cloudflare Frontend Note

Cloudflare Pages serves the frontend only. Set `VITE_API_BASE_URL` to the deployed backend URL when the backend is available. If it is empty, the frontend uses mock data.

## Backend Deployment Note

FastAPI should be hosted separately from Cloudflare Pages, such as on Cloudflare Containers, Render, Fly.io, Railway, or a VM. Configure CORS for the production Pages domain.
