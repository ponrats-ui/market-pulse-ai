# 22 Architecture Decision Records

## Table of Contents

- [Purpose](#purpose)
- [ADR Format](#adr-format)
- [ADR-001 Cloudflare Pages Frontend](#adr-001-cloudflare-pages-frontend)
- [ADR-002 Render Backend](#adr-002-render-backend)
- [ADR-003 yfinance First Provider](#adr-003-yfinance-first-provider)
- [ADR-004 Zero Mock Policy](#adr-004-zero-mock-policy)
- [ADR-005 AI Committee Pattern](#adr-005-ai-committee-pattern)
- [ADR-006 Provider Abstraction](#adr-006-provider-abstraction)
- [ADR-007 UI Freeze](#adr-007-ui-freeze)
- [ADR-008 Release Branch](#adr-008-release-branch)
- [Current Production](#current-production)
- [Future Roadmap](#future-roadmap)
- [Known Limitations](#known-limitations)
- [Related Documents](#related-documents)

## Purpose

This document converts major project decisions into ADR format. It complements [04 System Decisions](04_SYSTEM_DECISIONS.md).

## ADR Format

Each ADR includes:

- Status
- Context
- Decision
- Consequences
- Alternatives
- Review Criteria
- Future Revisit Conditions

## ADR-001 Cloudflare Pages Frontend

Status: Accepted.

Context: the frontend is a static Vite app.

Decision: deploy frontend through Cloudflare Pages.

Consequences: frontend needs `VITE_API_BASE_URL` to reach backend.

Alternatives: Vercel, Netlify, Render static site.

Review Criteria: app remains static and build output is `dist`.

Future Revisit Conditions: server-rendering or edge backend requirements.

## ADR-002 Render Backend

Status: Accepted.

Context: backend is FastAPI/Python and needs provider calls.

Decision: deploy backend on Render using `render.yaml`.

Consequences: simple deployment, possible cold starts.

Alternatives: Fly.io, Railway, VPS, Cloudflare Workers.

Review Criteria: health endpoint passes and provider calls fit platform limits.

Future Revisit Conditions: latency or scaling requirements exceed Render fit.

## ADR-003 yfinance First Provider

Status: Accepted.

Context: broad market data is needed without committed secrets.

Decision: use yfinance as current primary quote/history/fundamental provider.

Consequences: good coverage but variable performance.

Alternatives: paid APIs, broker APIs, custom scraping.

Review Criteria: real data appears and unavailable states are transparent.

Future Revisit Conditions: provider reliability blocks production or premium features.

## ADR-004 Zero Mock Policy

Status: Accepted and non-negotiable.

Context: fake financial data can mislead users.

Decision: production must not fabricate prices, charts, news, sentiment, calendar events, or AI evidence.

Consequences: UI may show unavailable states.

Alternatives: demo data or placeholder values.

Review Criteria: release audits find no fake production data.

Future Revisit Conditions: none without explicit Founder approval.

## ADR-005 AI Committee Pattern

Status: Accepted.

Context: investment interpretation is multi-factor.

Decision: use specialist views and Chief AI aggregation.

Consequences: more explainable but more complex.

Alternatives: single AI score, no AI, purely technical score.

Review Criteria: each view separates evidence, interpretation, risk, and limitations.

Future Revisit Conditions: introduction of real LLM orchestration.

## ADR-006 Provider Abstraction

Status: Accepted.

Context: providers differ in schema, credentials, coverage, and reliability.

Decision: keep providers behind adapters, registries, and data hub contracts.

Consequences: more files, easier future provider replacement.

Alternatives: direct yfinance calls throughout services.

Review Criteria: services receive normalized data and unavailable reasons.

Future Revisit Conditions: shared provider package or paid provider rollout.

## ADR-007 UI Freeze

Status: Accepted.

Context: Founder accepted the UI restoration chain.

Decision: freeze UI for release candidate work.

Consequences: only bug fixes allowed before release.

Alternatives: continue visual iteration.

Review Criteria: release validation passes without redesign.

Future Revisit Conditions: post-release design sprint or explicit Founder approval.

## ADR-008 Release Branch

Status: Accepted.

Context: release prep must not destabilize `develop` or `main`.

Decision: create `release/v1.0.0-rc1` from accepted `develop`.

Consequences: release documentation and versioning are isolated.

Alternatives: release from `develop` directly or merge to `main` first.

Review Criteria: branch source matches accepted develop HEAD.

Future Revisit Conditions: mature automated release process.

## Current Production

These ADRs reflect the current release-candidate architecture and founder-approved constraints.

## Future Roadmap

- add ADRs for authentication
- add ADRs for paid providers
- add ADRs for cloud sync
- add ADRs for monitoring and rate limiting

## Known Limitations

- ADRs summarize decisions already made; not every historical trade-off is fully recorded.

## Related Documents

- [04 System Decisions](04_SYSTEM_DECISIONS.md)
- [05 Release Engineering](05_RELEASE_ENGINEERING.md)
- [20 Provider Guide](20_PROVIDER_GUIDE.md)
