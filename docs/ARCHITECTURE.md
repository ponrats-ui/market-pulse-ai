# Architecture

Market Pulse AI separates the frontend dashboard, backend API, provider integrations, configuration, and documentation.

## Frontend

- React + Vite + TypeScript
- TailwindCSS for styling
- Recharts for time-series visualization
- lucide-react for interface icons
- Mock fallback data if backend calls fail

## Backend

- FastAPI application in `backend/app/main.py`
- Provider contract in `backend/app/providers/base.py`
- yfinance implementation in `backend/app/providers/yfinance_provider.py`
- Conservative analysis services in `backend/app/services`

## Data Flow

1. Frontend loads the watchlist.
2. User selects category and asset.
3. Frontend requests asset price, AI analysis, risk, and financials.
4. Backend attempts yfinance data.
5. If provider data fails, backend returns safe mock fallback for price context.
6. Frontend also has mock fallback for offline Sprint 0 development.

## Extension Points

- Add new providers by implementing `MarketDataProvider`.
- Add caching between API and provider layers.
- Add backend deployment through Cloudflare Workers, Render, Fly.io, Railway, or container hosting.
