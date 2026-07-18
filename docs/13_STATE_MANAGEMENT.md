# 13 State Management

## Table of Contents

- [Purpose](#purpose)
- [Frontend State](#frontend-state)
- [Backend State](#backend-state)
- [Caching](#caching)
- [Loading](#loading)
- [Retry](#retry)
- [Abort Lifecycle](#abort-lifecycle)
- [Provider Fallback](#provider-fallback)
- [Error Handling](#error-handling)
- [Data Refresh](#data-refresh)
- [Current Production](#current-production)
- [Future Roadmap](#future-roadmap)
- [Known Limitations](#known-limitations)
- [Related Documents](#related-documents)

## Purpose

This document explains how state moves through Market Pulse AI and why local state, backend cache, request cancellation, and unavailable payloads are used.

## Frontend State

Frontend state is React state plus localStorage.

Examples:

- selected asset
- selected section
- language
- search query and results
- watchlist
- recent searches
- portfolio simulation
- comparison symbols
- Relax Mode preference
- loading and error states

Why: the current product has no login or cloud sync. Local state keeps the app private and simple.

## Backend State

Backend state is intentionally minimal.

Current backend state:

- in-memory TTL cache
- provider status metadata
- loaded configuration files

No persistent user account, real brokerage data, or private portfolio database exists.

## Caching

Backend cache lives in `backend/app/services/cache.py`.

Cached areas include:

- watchlist
- quote
- history
- fundamentals

Why: provider calls can be slow or rate-limited. TTL cache reduces repeated calls while keeping data freshness visible through metadata.

## Loading

Frontend loading states should:

- show progress or skeletons
- avoid blocking navigation
- avoid showing fake values
- let already loaded sections remain readable

## Retry

Current production does not implement aggressive retry loops. This is intentional to avoid provider abuse and duplicated requests.

Future retry logic should include:

- bounded attempts
- backoff
- provider rate-limit awareness
- clear user-visible unavailable state after failure

## Abort Lifecycle

Frontend requests use `AbortController` for timeout and cancellation.

Important rules:

- canceled requests are not treated as data failures when superseded
- batch quote has a dedicated longer timeout
- request timeout must not produce fake fallback values
- repeated refresh should not accumulate stale active requests

The FS-300B.1 fix stabilized the batch quote abort lifecycle.

## Provider Fallback

Fallback means unavailable or partial response. It does not mean generated market data.

Provider fallback should include:

- source
- status
- warnings
- unavailable reason
- timestamp where available

## Error Handling

Frontend:

- logs helpful diagnostics for API failures
- renders unavailable states
- avoids crashing the full dashboard

Backend:

- uses validation constraints on query parameters
- returns controlled provider-unavailable payloads where possible
- keeps route handlers thin

## Data Refresh

Refresh behavior:

- selected asset changes trigger quote/history/analysis/risk/financials refresh
- Opportunities uses batch quote refresh
- watchlist and sparklines refresh from configured endpoints
- language changes do not refetch market data

## Current Production

The current state model is local-first, provider-backed, and cache-aware. It is sufficient for a public informational MVP without user accounts.

## Future Roadmap

- cloud sync after authentication and privacy model
- request observability
- provider-level backoff
- optional refresh intervals with user control

## Known Limitations

- LocalStorage can be cleared by browser settings.
- In-memory backend cache resets on process restart.
- No distributed cache exists.

## Related Documents

- [09 Engineering Handbook](09_ENGINEERING_HANDBOOK.md)
- [12 Sequence Diagrams](12_SEQUENCE_DIAGRAMS.md)
- [16 Performance Guide](16_PERFORMANCE_GUIDE.md)
- [20 Provider Guide](20_PROVIDER_GUIDE.md)

