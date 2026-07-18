# 01 Product Vision

## Table of Contents

- [Purpose](#purpose)
- [Product Vision](#product-vision)
- [Mission](#mission)
- [Target Users](#target-users)
- [Product Principles](#product-principles)
- [Zero Mock Philosophy](#zero-mock-philosophy)
- [Real Data Policy](#real-data-policy)
- [User Experience Goals](#user-experience-goals)
- [Design Philosophy](#design-philosophy)
- [Competitive Position](#competitive-position)
- [Current State](#current-state)
- [Future Work](#future-work)
- [Known Limitations](#known-limitations)
- [Long-Term Roadmap](#long-term-roadmap)
- [Related Documents](#related-documents)

## Purpose

This document preserves the business and product intent behind Market Pulse AI. It explains what the product is meant to do, why it exists, and which principles must remain stable as the codebase evolves.

## Product Vision

Market Pulse AI is a Thai-first, bilingual investment research workspace for people who want real market context without hype. The product combines live provider data, conservative interpretation, portfolio awareness, and transparent unavailable states in one professional dashboard.

The long-term vision is to become a trusted personal investment assistant that helps users understand markets, compare assets, monitor risk, and prepare better questions before making their own decisions.

## Mission

The mission is to make market research clearer, calmer, and more disciplined for everyday investors.

Market Pulse AI should:

- show real data when available
- explain what the data means
- disclose uncertainty and missing evidence
- separate facts from interpretation
- never promise returns
- help the user decide what to monitor next

## Target Users

Primary users:

- Thai retail investors who follow Thai and global assets
- bilingual users who move between Thai and English terminology
- long-term investors who want a daily market terminal
- self-directed learners who need explanation, not promotion
- users who want to compare assets across equities, crypto, ETFs, commodities, FX, and indices

Secondary users:

- contributors maintaining the project
- educators demonstrating market-data workflows
- founders and operators reviewing release quality

## Product Principles

1. Evidence before opinion.
2. Probability over prediction.
3. Transparency over hype.
4. Professional over flashy.
5. Real data over generated filler.
6. User control over automation.
7. Education over advice.
8. Local clarity before global scale.

These principles are non-negotiable. They are expanded in [06 Founder Bible](06_FOUNDER_BIBLE.md).

## Zero Mock Philosophy

Market Pulse AI must not display fake market data as if it were real. A missing price, missing chart, missing news item, or missing provider response must be shown as unavailable, stale, partial, or not applicable.

Mock values may exist only in isolated tests or fixtures where they are clearly test data. Production UI and API responses must not invent prices, chart candles, headlines, economic events, sentiment scores, or AI evidence.

This rule exists because financial interfaces can influence real decisions. False confidence is more harmful than an honest empty state.

## Real Data Policy

Current real-data policy:

- Yahoo Finance through `yfinance` is the main provider for quotes, history, and available fundamentals.
- Optional providers may be configured later through environment variables.
- Provider failures produce transparent unavailable states.
- AI and analysis modules use available evidence and disclose limitations.
- Frontend static deployment may show unavailable states if no backend URL is configured.

See [Real Data Policy](REAL_DATA_POLICY.md) and [Data Provider Attribution](DATA_PROVIDER_ATTRIBUTION.md).

## User Experience Goals

The user experience should feel like a professional market terminal that is approachable for a first-time investor.

Goals:

- important market information visible immediately
- predictable navigation
- readable dark theme
- clear source and timestamp labels
- transparent unavailable messaging
- responsive desktop and mobile layout
- conservative investment wording
- compact controls that do not hide critical data
- optional wellbeing features that never block investment workflows

## Design Philosophy

The design is intentionally dense, structured, and work-focused. It should support scanning, comparison, and repeated daily use.

Market Pulse AI should avoid:

- promotional landing-page patterns inside the app
- oversized decorative cards
- vague AI excitement language
- hidden data provenance
- fake confidence

The UI freeze acceptance for the current release is recorded in [Founder UI Freeze Acceptance](FOUNDER-UI-FREEZE-ACCEPTANCE.md).

## Competitive Position

Market Pulse AI is not trying to replace a broker, terminal, or licensed adviser.

It competes on:

- Thai-first bilingual clarity
- transparent unavailable states
- open-source governance
- conservative AI interpretation
- cross-asset research workflow
- low-cost deployment model
- founder-led product discipline

## Current State

The current release candidate includes:

- React and Vite frontend
- FastAPI backend
- yfinance-first provider abstraction
- global asset search and master registry
- dashboard with quote, chart, watchlist, Opportunities, Chief AI, AI Committee, risk, financials, news impact, sentiment, calendar, compare, paper portfolio, and Relax Mode surfaces
- local simulated portfolio workflows
- Cloudflare Pages frontend readiness
- Render backend readiness
- open-source governance documents

## Future Work

Future work should expand capability only after preserving the current discipline.

Examples:

- provider performance optimization
- additional licensed or free providers
- persistent cloud sync
- production alert delivery
- improved calendar, macro, and sentiment providers
- stronger observability and rate limiting
- formal accessibility review

## Known Limitations

- Provider availability depends on upstream services and network access.
- Local batch quote requests may be slow.
- Some optional providers are intentionally unavailable until configured.
- Paper trading is simulated and does not connect to brokers.
- AI analysis is educational and may be incomplete.

## Long-Term Roadmap

Version 1.x:

- stabilize production release
- preserve UI freeze
- improve documentation and release process
- harden provider error handling

Version 2.x:

- improve provider reliability and performance
- expand personal portfolio coaching
- add opt-in premium monitoring and alerts
- improve analytics explainability

Version 3.x:

- institutional-grade audit trails
- richer data-provider governance
- advanced scenario analysis where evidence supports it
- team or adviser workflows if product direction justifies them

## Related Documents

- [02 System Architecture](02_SYSTEM_ARCHITECTURE.md)
- [03 Algorithm Reference](03_ALGORITHM_REFERENCE.md)
- [04 System Decisions](04_SYSTEM_DECISIONS.md)
- [05 Release Engineering](05_RELEASE_ENGINEERING.md)
- [06 Founder Bible](06_FOUNDER_BIBLE.md)
- [07 Glossary](07_GLOSSARY.md)
- [08 Contributing](08_CONTRIBUTING.md)
