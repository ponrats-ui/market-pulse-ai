# 04 System Decisions

## Table of Contents

- [Purpose](#purpose)
- [Decision Record Format](#decision-record-format)
- [Cloudflare Pages](#cloudflare-pages)
- [Render](#render)
- [YFinance First](#yfinance-first)
- [Zero Mock](#zero-mock)
- [AI Committee](#ai-committee)
- [Modular Architecture](#modular-architecture)
- [UI Freeze](#ui-freeze)
- [Release Branch](#release-branch)
- [Provider Abstraction](#provider-abstraction)
- [Confidence Scoring](#confidence-scoring)
- [Fallback Policy](#fallback-policy)
- [Current State](#current-state)
- [Future Work](#future-work)
- [Known Limitations](#known-limitations)
- [Related Documents](#related-documents)

## Purpose

This document records why major engineering decisions were made. It prevents future maintainers from accidentally undoing product principles without understanding the trade-offs.

## Decision Record Format

Each decision includes:

- Decision
- Context
- Alternatives Considered
- Pros
- Cons
- Trade-offs
- Reason Chosen
- Date
- Impact
- Future Revisit Conditions

## Cloudflare Pages

Decision: use Cloudflare Pages for the frontend.

Context: the frontend is a static Vite app and should be cheap, fast, and easy to deploy.

Alternatives Considered: Render static site, Netlify, Vercel, self-hosting.

Pros: simple static hosting, global edge delivery, environment variables, GitHub integration.

Cons: backend must be deployed separately.

Trade-offs: split deployment adds configuration responsibility for `VITE_API_BASE_URL`.

Reason Chosen: the frontend is naturally static and Cloudflare Pages fits the deployment model.

Date: 2026-07.

Impact: production frontend depends on a correctly configured backend URL.

Future Revisit Conditions: revisit if the app becomes server-rendered or requires edge server logic.

## Render

Decision: use Render for the FastAPI backend.

Context: the backend needs Python, FastAPI, provider calls, and a health endpoint.

Alternatives Considered: Cloudflare Workers, Railway, Fly.io, VPS.

Pros: straightforward Python web service deployment and health checks.

Cons: cold starts and free-tier latency may occur.

Trade-offs: deployment simplicity is prioritized over lowest latency.

Reason Chosen: Render supports the current backend with minimal production ceremony.

Date: 2026-07.

Impact: `render.yaml` defines build, start, CORS, and health configuration.

Future Revisit Conditions: revisit if latency, scale, or provider workload exceeds Render fit.

## YFinance First

Decision: use yfinance as the first market-data provider.

Context: the product needs quotes, history, and some fundamentals without committing paid API keys.

Alternatives Considered: paid market-data APIs, broker APIs, scraping custom sources.

Pros: broad symbol coverage, easy Python integration, no committed secrets.

Cons: upstream behavior can be slow, incomplete, or rate-limited.

Trade-offs: broad early coverage is prioritized over institutional reliability.

Reason Chosen: yfinance supports the MVP and RC workflows while provider abstraction preserves future options.

Date: 2026-07.

Impact: transparent unavailable states are essential when yfinance fails.

Future Revisit Conditions: revisit before high-traffic production launch or premium alert delivery.

## Zero Mock

Decision: never show fabricated market data as production truth.

Context: financial products can influence real decisions.

Alternatives Considered: placeholder data for visual completeness, demo mode.

Pros: protects trust, reduces regulatory and ethical risk, keeps UI honest.

Cons: unavailable states can look less impressive than fake completeness.

Trade-offs: honesty is prioritized over visual fullness.

Reason Chosen: missing data is safer than false data.

Date: 2026-07.

Impact: frontend and backend must preserve nulls and unavailable reasons.

Future Revisit Conditions: do not revisit without explicit Founder approval.

## AI Committee

Decision: split AI interpretation into specialist roles.

Context: investment views are multi-factor and can conflict.

Alternatives Considered: one AI summary, pure quantitative score, no AI layer.

Pros: clearer reasoning, visible disagreement, better educational value.

Cons: more UI and contract complexity.

Trade-offs: explainability is prioritized over a single simple score.

Reason Chosen: committee structure reduces opaque AI authority.

Date: 2026-07.

Impact: each role should state evidence and missing data.

Future Revisit Conditions: revisit when adding real LLM orchestration or external research providers.

## Modular Architecture

Decision: separate services, providers, analysis engine, and frontend API client.

Context: the app grew from MVP dashboard to multi-surface research workspace.

Alternatives Considered: keep all logic in endpoints or frontend components.

Pros: testability, future provider support, clearer ownership.

Cons: more files and contracts.

Trade-offs: maintainability is prioritized over small-file minimalism.

Reason Chosen: modularity preserves release stability as features expand.

Date: 2026-07.

Impact: new business logic should not be embedded directly in route handlers.

Future Revisit Conditions: revisit package boundaries if mobile or desktop apps become active.

## UI Freeze

Decision: freeze the Founder-accepted UI before release candidate preparation.

Context: repeated visual work created a stable professional dashboard.

Alternatives Considered: continue redesigning during release prep.

Pros: reduces regression risk and gives validation a stable target.

Cons: minor design improvements must wait.

Trade-offs: release stability is prioritized over visual iteration.

Reason Chosen: release candidates require fixed acceptance surfaces.

Date: 2026-07-17.

Impact: future UI changes before release are bug fixes only.

Future Revisit Conditions: after v1.0 release or explicit Founder approval.

## Release Branch

Decision: create `release/v1.0.0-rc1` from accepted `develop`.

Context: release hardening should not destabilize `develop` or `main`.

Alternatives Considered: release directly from `develop`, merge to `main` first.

Pros: clear release audit trail, isolated documentation/version updates.

Cons: branch management overhead.

Trade-offs: traceability is prioritized over fewer branches.

Reason Chosen: release branches support Founder acceptance and rollback planning.

Date: 2026-07.

Impact: no deployment, tag, or main merge happens without approval.

Future Revisit Conditions: revisit after CI/CD maturity improves.

## Provider Abstraction

Decision: keep provider access behind adapters and routers.

Context: market-data providers differ in availability, schema, limits, and credentials.

Alternatives Considered: call yfinance directly from every service.

Pros: easier provider replacement, status reporting, normalized contracts.

Cons: extra abstraction for simple calls.

Trade-offs: future flexibility is prioritized over shortest implementation.

Reason Chosen: provider reliability is a known long-term risk.

Date: 2026-07.

Impact: services consume normalized responses where practical.

Future Revisit Conditions: expand with formal provider SLAs or paid providers.

## Confidence Scoring

Decision: show confidence and limitations instead of certainty.

Context: analysis can be incomplete or contradictory.

Alternatives Considered: hide confidence, show only recommendation, show precise probabilities without calibration.

Pros: encourages caution and evidence review.

Cons: confidence is currently heuristic.

Trade-offs: transparent uncertainty is prioritized over false precision.

Reason Chosen: users need to know how much evidence supports a view.

Date: 2026-07.

Impact: low-data responses should show low confidence.

Future Revisit Conditions: revisit after historical calibration work.

## Fallback Policy

Decision: fallback means unavailable, not fabricated replacement data.

Context: providers may fail, timeout, or return partial fields.

Alternatives Considered: generate placeholder values, cache forever, hide panels.

Pros: honest UI, safer compliance posture, easier debugging.

Cons: dashboard may show partial sections during outages.

Trade-offs: data integrity is prioritized over complete-looking UI.

Reason Chosen: transparent unavailability is central to the product.

Date: 2026-07.

Impact: frontend fallback objects use unavailable states.

Future Revisit Conditions: improve provider resilience without changing the no-fabrication rule.

## Current State

The current decisions support a production candidate that is honest, modular, and deployable without secrets in the frontend.

## Future Work

- add formal architecture decision records if the project grows
- add provider performance decision record after optimization
- add security decision record before authentication

## Known Limitations

- Some decisions are founder-led and intentionally conservative.
- Dates reflect project release period, not every commit date.

## Related Documents

- [01 Product Vision](01_PRODUCT_VISION.md)
- [02 System Architecture](02_SYSTEM_ARCHITECTURE.md)
- [05 Release Engineering](05_RELEASE_ENGINEERING.md)
- [06 Founder Bible](06_FOUNDER_BIBLE.md)
- [Founder UI Freeze Acceptance](FOUNDER-UI-FREEZE-ACCEPTANCE.md)
