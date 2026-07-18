# 02 System Architecture

## Table of Contents

- [Purpose](#purpose)
- [Architecture Overview](#architecture-overview)
- [Frontend](#frontend)
- [Backend](#backend)
- [API Layer](#api-layer)
- [Business Logic](#business-logic)
- [Analysis Engine](#analysis-engine)
- [Provider Layer](#provider-layer)
- [Deployment Model](#deployment-model)
- [State Management](#state-management)
- [Directory Structure](#directory-structure)
- [Request Flow](#request-flow)
- [Data Flow](#data-flow)
- [Error Flow](#error-flow)
- [Startup Flow](#startup-flow)
- [Module Dependency Map](#module-dependency-map)
- [Current State](#current-state)
- [Future Work](#future-work)
- [Known Limitations](#known-limitations)
- [Related Documents](#related-documents)

## Purpose

This document explains how Market Pulse AI is assembled and why the system is separated into frontend, backend, provider, and documentation layers. It is the long-term map for engineers joining the project.

## Architecture Overview

Market Pulse AI uses a split deployment model:

- Cloudflare Pages serves the static frontend.
- Render runs the FastAPI backend.
- The backend talks to market-data providers.
- The frontend never stores provider secrets.
- Missing or failed provider data is returned as unavailable instead of fabricated.

```text
User Browser
  -> Cloudflare Pages static frontend
  -> Render FastAPI backend
  -> Provider layer
  -> yfinance and optional future providers
```

This split keeps the frontend cheap and cacheable while keeping provider access, CORS, and server-side logic behind the backend.

## Frontend

Location: `frontend/`

Primary technologies:

- React
- Vite
- TypeScript
- TailwindCSS
- Recharts
- lucide-react

Responsibilities:

- render the research workspace
- handle Thai/English UI state
- call backend API through `VITE_API_BASE_URL`
- show loading, unavailable, stale, and source states
- preserve local preferences such as watchlist, language, portfolio simulation, and Relax Mode settings

Why it was designed this way:

- Vite keeps build and Cloudflare Pages deployment simple.
- TypeScript protects API contract usage.
- Local state is appropriate while the product has no authentication or cloud sync.

## Backend

Location: `backend/app/`

Primary technologies:

- FastAPI
- Python
- Pydantic
- yfinance
- pytest

Responsibilities:

- expose API endpoints
- normalize provider data
- calculate analysis, risk, technical, compare, portfolio, and intelligence responses
- enforce transparent unavailable states
- centralize provider access
- provide CORS-controlled production access

Why it was designed this way:

- FastAPI is simple to deploy on Render.
- Python fits market data and analysis workflows.
- Keeping analysis server-side reduces frontend complexity and avoids leaking future provider credentials.

## API Layer

Primary file: `backend/app/main.py`

Core endpoint families:

- `/health`
- `/api/watchlist`
- `/api/assets/...`
- `/api/assets/search`
- `/api/assets/quotes`
- `/api/analysis/{symbol}`
- `/api/risk/{symbol}`
- `/api/financials/{symbol}`
- `/api/technical/{symbol}`
- `/api/compare`
- `/api/portfolio/evaluate`
- `/api/calendar`
- `/api/news-impact/{symbol}`
- `/api/sentiment/{symbol}`
- `/api/assistant/ask`

The API layer should remain thin. Business logic belongs in services, provider routers, or analysis modules.

## Business Logic

Location: `backend/app/services/`

Service modules hold domain behavior:

- `analysis.py`
- `asset_universe.py`
- `comparison.py`
- `financials.py`
- `portfolio.py`
- `technical.py`
- `news.py`
- `sentiment.py`
- `calendar.py`
- `cache.py`

Why this split exists:

- endpoints stay readable
- tests can target services directly
- provider fallbacks remain consistent
- future providers can be added without rewriting UI surfaces

## Analysis Engine

Location: `backend/app/analysis_engine/`

The analysis engine turns evidence into cautious educational interpretation. It includes:

- asset class detection
- adaptive weights
- confidence calculation
- evidence assembly
- probability view
- recommendation policy
- risk engine
- investment thesis
- market regime handling

The engine must not claim certainty. Its outputs must include evidence, limitations, and disclaimers.

## Provider Layer

Key locations:

- `backend/app/providers/`
- `backend/app/data_hub/`
- `backend/app/data_hub/providers/`

Provider responsibilities:

- normalize quotes
- normalize history
- expose provider status
- report unavailable reasons
- keep provider-specific details out of UI components

Yahoo Finance through `yfinance` is the current primary provider. Other provider shells and registries exist for future expansion, but they must return unavailable states unless configured with real credentials.

## Deployment Model

Frontend:

- Cloudflare Pages
- root directory: `frontend`
- build command: `npm run build`
- output directory: `dist`
- environment variable: `VITE_API_BASE_URL`

Backend:

- Render web service
- root directory: `backend`
- build command: `pip install -r requirements.txt`
- start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- health check: `/health`
- CORS: `CORS_ALLOWED_ORIGINS`

## State Management

Current frontend state uses React state and localStorage.

Current localStorage-backed areas include:

- language preference
- user watchlist
- recent searches
- paper portfolio
- Relax Mode preference

Why local state is used:

- no authentication exists yet
- paper portfolio is simulated
- privacy and simplicity are more important than cloud sync in the current release

Future cloud sync should be added behind explicit user accounts and privacy rules.

## Directory Structure

Current layout:

```text
frontend/
backend/
configs/
docs/
scripts/
data/
.github/
README.md
```

Important configuration:

- `configs/watchlist.json`
- `configs/exchange_master.json`
- `configs/analysis_profiles.json`
- `configs/subscription_features.json`
- `configs/relax_streams.json`
- `render.yaml`
- `frontend/wrangler.toml`

## Request Flow

```text
User selects asset
  -> React state updates selected symbol
  -> frontend API client builds backend URLs
  -> FastAPI endpoint receives request
  -> service resolves canonical symbol
  -> provider router fetches or reuses cached data
  -> service normalizes response
  -> frontend renders data, source, timestamp, or unavailable state
```

## Data Flow

```text
Provider raw response
  -> provider adapter
  -> normalized contract
  -> service calculation
  -> API response
  -> typed frontend model
  -> dashboard panel
```

## Error Flow

```text
Provider unavailable or timeout
  -> provider reports reason
  -> service returns partial or unavailable response
  -> frontend logs development diagnostic where appropriate
  -> UI shows transparent unavailable state
```

The frontend must not replace failed API data with fake market data.

## Startup Flow

Backend:

```text
Render starts uvicorn
  -> FastAPI app loads
  -> CORS origins are read from environment
  -> endpoints become available
  -> Render health check calls /health
```

Frontend:

```text
Cloudflare serves static files
  -> React app loads
  -> API base URL is resolved
  -> dashboard requests initial data
  -> unavailable states render if backend is not reachable
```

## Module Dependency Map

```text
frontend/src/main.tsx
  -> frontend/src/lib/api.ts
  -> frontend/src/types/market.ts
  -> backend/app/main.py
  -> backend/app/services/*
  -> backend/app/data_hub/*
  -> backend/app/providers/*
  -> external providers

backend/app/services/analysis.py
  -> backend/app/analysis_engine/*
  -> provider and data hub evidence
```

## Current State

The architecture supports production deployment, local testing, transparent unavailable states, and release-branch validation. It is intentionally modular but still compact enough for a small project.

## Future Work

- add rate limiting
- improve provider observability
- separate API contracts into shared package if multi-app support becomes real
- add cloud sync only after privacy and auth decisions
- add provider performance optimization outside UI freeze scope

## Known Limitations

- The local batch quote provider path can be slow.
- Some optional providers are not configured.
- No real broker integration exists.
- No authentication or user cloud storage exists.

## Related Documents

- [01 Product Vision](01_PRODUCT_VISION.md)
- [03 Algorithm Reference](03_ALGORITHM_REFERENCE.md)
- [04 System Decisions](04_SYSTEM_DECISIONS.md)
- [05 Release Engineering](05_RELEASE_ENGINEERING.md)
- [Real Data Policy](REAL_DATA_POLICY.md)
- [Provider Health and Fallback](PROVIDER_HEALTH_AND_FALLBACK.md)
