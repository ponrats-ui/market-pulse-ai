# Architecture

Market Pulse AI separates the frontend dashboard, backend API, provider integrations, configuration, and documentation.

## Frontend

- React + Vite + TypeScript
- TailwindCSS for styling
- Recharts for time-series visualization
- lucide-react for interface icons
- Uses backend data when `VITE_API_BASE_URL` is set
- Falls back to mock data when the API is unavailable or the env var is empty

## Backend

- FastAPI application in `backend/app/main.py`
- Provider contract in `backend/app/providers/base.py`
- Provider registry in `backend/app/providers/registry.py`
- yfinance implementation in `backend/app/providers/yfinance_provider.py`
- TTL cache in `backend/app/services/cache.py`
- Conservative analysis services in `backend/app/services`

## Data Flow

1. Frontend loads `/api/watchlist` or local mock watchlist.
2. User selects category and asset.
3. Frontend requests quote, history, AI analysis, risk, and financials.
4. Backend retrieves normalized yfinance data through the provider abstraction.
5. Quote, history, and watchlist responses are cached with short TTLs.
6. Failed assets return structured `error` fields so the UI can keep rendering.

## Extension Points

- Add new providers by implementing `MarketDataProvider`.
- Add provider failover in `registry.py`.
- Add persistent caching or edge caching for production.
- Add backend deployment through Cloudflare Containers, Render, Fly.io, Railway, or container hosting.
