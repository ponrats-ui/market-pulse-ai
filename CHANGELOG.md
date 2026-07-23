# Changelog

All notable changes to Market Pulse AI will be documented in this file.

The format is inspired by Keep a Changelog, and this project uses human-readable release notes.

## [Unreleased]

### Added

- Asset Intelligence layer with explicit classification, corporate Financial Intelligence profile, special-profile boundaries, reusable Financial Intelligence report, methodology endpoint, and Financial Intelligence API.
- Financial Intelligence backend engine with formula registry, evidence normalization, score, confidence, completeness, risk signals, cache metadata, and version metadata.
- Penny Opportunity v2 migration using Financial Intelligence as the largest positive evidence domain at 55% weight.
- Trust Foundation layer with backend trust policy contracts, evidence integrity metadata, uncertainty disclosure, algorithm neutrality validation, conflict-of-interest safeguards, ranking integrity validation, decision-boundary disclosure, and frontend trust disclosure for Penny Opportunities.
- Transparent Intelligence framework with Penny Algorithm Definition, activation validation, score reconciliation, ranking explanation, and Why Not snapshot explanations.
- Penny algorithm endpoints for methodology, candidate score explanation, and Why Not analysis.
- Explainable Penny Opportunity Scanner for Thailand and United States low-priced equity discovery across the complete supported lightweight registry universe.
- `GET /api/opportunities/penny` endpoint with hourly backend scan snapshots, market-aware classification, risk penalties, data confidence, missing-data disclosure, and provider attribution.
- Penny Opportunities UI section inside Today's Opportunities with a visible Thai/English risk warning and full-card selected-asset navigation.
- Shared Opportunity Engine Framework with reusable engine contracts, registry, deterministic ranking, scheduler shell, and atomic snapshot store for future opportunity categories.
- Penny UI score breakdown panel with Algorithm Lab, factor contributions, risk penalty reconciliation, missing evidence, and rank rationale.

### Documentation

- Added Financial Intelligence, Asset Intelligence, model registry, scoring, normalization, formula, risk, confidence, API, UI, governance, and Penny migration documentation.
- Added trust governance documents for Trust Foundation, Algorithm Neutrality, Evidence Integrity, Uncertainty Disclosure, Ranking Integrity, Conflict of Interest, Decision Boundary, and Intellectual Honesty.
- Added `docs/OPPORTUNITY_ENGINE_FRAMEWORK.md` and `docs/PENNY_OPPORTUNITY_SCANNER_IMPLEMENTATION.md`, then linked the framework and scanner across roadmap, product bible, AI architecture, scoring, and explainability docs.
- Added Algorithm Transparency, Algorithm Lab, Why This, Why Not, Algorithm Governance, and Penny Algorithm documentation.

## [1.0.0-rc1] - 2026-07-18

### Added

- Release candidate readiness checklist for production merge review.
- Production audit coverage for Cloudflare Pages, Render, CI, environment variables, secrets, zero-mock behavior, API smoke, browser regression, and rollback readiness.
- Founder UI freeze, documentation freeze, and engineering handbook knowledge base from the accepted release branch.
- Professional dashboard experience with global asset search, watchlist, opportunities, Professional Chart, PIA analysis, risk, fundamentals, news impact, compare, paper portfolio, assistant, calendar, and optional PIA Relax Mode.

### Changed

- Aligned frontend package metadata, About dialog, backend API metadata, `/health`, and Render deployment documentation to version `1.0.0-rc1`.
- Confirmed production frontend configuration resolves to the Render backend URL on Cloudflare Pages when no safe runtime override is configured.
- Confirmed unavailable states remain transparent when a provider does not return live data.

### Security

- Verified no committed secrets, provider keys, access tokens, private keys, or payment credentials were found in the audited code and configuration paths.
- Confirmed Render CORS production configuration is restricted to `https://market-pulse-ai.pages.dev`.
- Confirmed YouTube audio is embedded only through source URLs and is not downloaded, restreamed, or stored.

### Validation

- Frontend build passed with Vite production output.
- Backend test suite passed with 113 tests.
- Local API smoke passed for release endpoints, including dashboard, quote, history, search, compare, portfolio, news, macro, premium, alert, and digest routes.
- Browser regression passed on desktop and 390px mobile viewport with no current console errors after clean reload.

### Changed

- Stabilized MVP API fallback behavior and cache age reporting.
- Improved dashboard empty states, source transparency, accessibility affordances, and portfolio input validation.
- Cleaned AI and unavailable-state wording in English and Thai.
- Added regression coverage for cache age reporting.
- Documented Cloudflare Pages production API environment variable setup.
- Made backend CORS origins configurable through `CORS_ALLOWED_ORIGINS`.

### Added

- RC2 professional investment platform foundation with real-data asset search, live quote batch evaluation, portfolio valuation, and enhanced comparison metrics.
- MIT license and open-source governance documents.
- Founder and project identity documentation.
- Application footer identity and About dialog.
- Render backend deployment configuration and deployment guide.
- GitHub Actions CI for backend tests and frontend build validation.
- Backend environment variable examples for production deployment.

## Sprint 2

### Added

- Thai and English localization.
- AI Investment Committee dashboard.
- Chief Investment AI summary card.
- Improved financial, news, and sentiment panels.

## Sprint 1

### Added

- Normalized yfinance market data layer.
- Provider registry and in-memory TTL cache.
- Quote, history, dashboard, analysis, risk, and financial endpoints.

## Sprint 0

### Added

- Initial React + Vite + TypeScript frontend.
- Initial FastAPI backend.
- Cloudflare Pages-ready frontend foundation.

## Thai Summary

ไฟล์นี้ใช้บันทึกการเปลี่ยนแปลงสำคัญของ Market Pulse AI เพื่อให้ผู้ใช้และผู้ร่วมพัฒนาเห็นพัฒนาการของโครงการอย่างโปร่งใส

## Sprint 3

### Added

- Real-data asset comparison endpoint and UI.
- Timeframe selector for historical chart data.
- Rule-based AI Q&A assistant.
- Portfolio analyzer with localStorage.
- Economic calendar provider-not-configured endpoint.
- News impact provider interface.
- Sentiment provider-not-configured endpoint.

## Real Data Sprint

### Changed

- Removed generated frontend market values and generated chart curves.
- Replaced unavailable news, calendar, sentiment, and frontend static fallback data with explicit unavailable states.
- Removed invented provider headlines and sentiment scores.
- Added real data policy and audit documentation.
