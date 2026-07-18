# 09 Engineering Handbook

## Table of Contents

- [Purpose](#purpose)
- [System Overview](#system-overview)
- [Repository Structure](#repository-structure)
- [Folder Responsibilities](#folder-responsibilities)
- [Naming Conventions](#naming-conventions)
- [Module Ownership](#module-ownership)
- [Coding Philosophy](#coding-philosophy)
- [Extension Guidelines](#extension-guidelines)
- [Dependency Map](#dependency-map)
- [Request Journey](#request-journey)
- [Current Production](#current-production)
- [Future Roadmap](#future-roadmap)
- [Known Limitations](#known-limitations)
- [Related Documents](#related-documents)

## Purpose

This handbook is the first document a new engineer should read. It explains how Market Pulse AI works, where code lives, how modules relate, and why the system is designed around real data, cautious analysis, and transparent unavailable states.

## System Overview

Market Pulse AI is a split frontend/backend investment research workspace.

- Frontend: React, Vite, TypeScript, TailwindCSS, Recharts, lucide-react.
- Backend: FastAPI, Python, Pydantic, yfinance-first provider abstraction.
- Deployment: Cloudflare Pages for static frontend, Render for backend.
- Data policy: use provider data when available; never fabricate production market values.

Why: a split architecture keeps the UI inexpensive to host, keeps provider logic server-side, and lets future providers be added without rewriting the dashboard.

## Repository Structure

```text
frontend/      React/Vite dashboard
backend/       FastAPI backend and tests
configs/       Product and analysis configuration
data/          Exchange source files and generated registries
docs/          Product, architecture, release, and engineering documentation
scripts/       Local utility scripts
.github/       CI workflow
render.yaml    Render backend deployment configuration
README.md      Project entry point
```

## Folder Responsibilities

`frontend/src/main.tsx`: main application shell and dashboard screens.

`frontend/src/lib/api.ts`: frontend API client, timeout behavior, backend URL resolution, unavailable fallbacks.

`frontend/src/types/market.ts`: TypeScript response contracts used by the UI.

`frontend/src/features/chart/`: professional chart engine, indicators, overlays, and toolbar.

`backend/app/main.py`: FastAPI app, endpoint wiring, CORS configuration, and cache access functions.

`backend/app/services/`: business logic for analysis, technicals, portfolio, compare, financials, news, sentiment, macro, calendar, and cache.

`backend/app/analysis_engine/`: adaptive analysis components, evidence, confidence, risk, probability, thesis, and profile loading.

`backend/app/data_hub/`: symbol resolution, provider routing, master registry, capabilities, and provider status.

`backend/app/providers/`: provider contracts and provider implementations or registries.

`backend/tests/`: pytest coverage.

## Naming Conventions

- Python modules use `snake_case`.
- TypeScript functions use `lowerCamelCase`.
- React components use `PascalCase`.
- Documentation freeze docs use numeric prefixes.
- Release branches use `release/<version>`.
- Feature and fix branches use `feature/<name>` and `fix/<name>`.

## Module Ownership

Frontend app shell: dashboard orchestration, navigation, local state, user interactions.

Frontend API client: endpoint paths, request timeout, cancellation behavior, unavailable fallback contracts.

Backend API layer: route shape and request validation.

Backend services: business decisions and calculations.

Provider layer: upstream data retrieval, normalization, unavailable reasons.

Analysis engine: evidence assembly, heuristic reasoning, confidence, risk, and thesis outputs.

Docs: release memory and founder intent.

## Coding Philosophy

Keep changes small, honest, and testable.

The code should:

- preserve real-data boundaries
- report unavailable data clearly
- avoid hiding provider failures
- separate route wiring from business logic
- avoid broad refactors during release branches
- keep UI freeze intact unless fixing a verified bug

## Extension Guidelines

When adding a provider:

1. Add provider behind an existing interface or registry.
2. Normalize response fields.
3. Include source, timestamp, status, and unavailable reason.
4. Add tests for success and provider-unavailable behavior.
5. Document provider limits in [20 Provider Guide](20_PROVIDER_GUIDE.md).

When adding a dashboard surface:

1. Confirm it uses real data or transparent unavailable state.
2. Add TypeScript contracts.
3. Add backend tests if endpoint behavior changes.
4. Add browser validation if UI changes.
5. Update documentation.

## Dependency Map

```text
React UI
  -> frontend API client
  -> FastAPI route
  -> service module
  -> data hub or provider adapter
  -> yfinance or configured provider

Analysis services
  -> quote/history/fundamentals
  -> analysis_engine modules
  -> conservative response contracts
```

## Request Journey

```text
User action
  -> React state update
  -> api.ts request
  -> FastAPI endpoint
  -> service layer
  -> cache lookup
  -> provider call if needed
  -> normalized payload
  -> UI renders data or unavailable state
```

## Current Production

The current release branch contains the Founder-approved UI freeze, documentation freeze v1.0, real-data provider policy, and engineering handbook sprint.

## Future Roadmap

- formal shared API contracts
- provider performance work
- rate limiting
- richer observability
- cloud sync after privacy/auth design

## Known Limitations

- yfinance can be slow or unavailable.
- Batch quote can take about 25-31 seconds locally.
- Optional providers require credentials and may return unavailable states.
- No real brokerage connection exists.

## Related Documents

- [02 System Architecture](02_SYSTEM_ARCHITECTURE.md)
- [03 Algorithm Reference](03_ALGORITHM_REFERENCE.md)
- [10 API Reference](10_API_REFERENCE.md)
- [11 Data Model](11_DATA_MODEL.md)
- [20 Provider Guide](20_PROVIDER_GUIDE.md)

