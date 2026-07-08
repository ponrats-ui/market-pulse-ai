# Architecture

Market Pulse AI separates the frontend dashboard, backend API, provider integrations, configuration, and documentation.

## Current Layout

- `frontend`: React + Vite + TypeScript dashboard
- `backend`: FastAPI market data and analysis API
- `configs`: watchlist and shared configuration
- `docs`: architecture, deployment, and sprint documentation

## Future Workspace Direction

A future workspace migration can move toward:

```text
apps/
  web/
  mobile/
  desktop/
backend/
  app/
  api/
  services/
packages/
  api-contract/
  shared-types/
configs/
docs/
```

Sprint 2 does not move folders, so Cloudflare Pages and local commands remain stable.

## Frontend

- React + Vite + TypeScript
- TailwindCSS for styling
- Recharts for time-series visualization
- lucide-react for interface icons
- Thai/English i18n in `frontend/src/i18n`
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
4. Dashboard renders localized labels and Thai/English interpretation surfaces.
5. Failed assets return structured `error` fields so the UI can keep rendering.
## MVP Stabilization

The MVP keeps Cloudflare Pages static deployment functional by treating `VITE_API_BASE_URL` as optional. The frontend API client falls back to typed mock data after failed, slow, or unavailable backend requests. UI panels render empty states instead of blank sections, and source details are surfaced where available.

## Sprint 3 Research Terminal Architecture

Sprint 3 adds provider-ready research endpoints while preserving the Sprint 1 yfinance market data layer.

- Real quote/history data continues through `YFinanceProvider`.
- Comparison is built from cached quote and history data.
- AI Q&A lives in `backend/app/services/qa_assistant.py` and is rule-based for now.
- News impact uses `NewsProvider` and `MockNewsProvider` so future providers can be added without changing endpoint contracts.
- Calendar and sentiment are explicit placeholder services until provider integrations are selected.
