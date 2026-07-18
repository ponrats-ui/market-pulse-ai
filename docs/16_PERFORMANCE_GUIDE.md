# 16 Performance Guide

## Table of Contents

- [Purpose](#purpose)
- [Current Performance](#current-performance)
- [Known Bottlenecks](#known-bottlenecks)
- [Provider Latency](#provider-latency)
- [Rendering Cost](#rendering-cost)
- [Bundle Size](#bundle-size)
- [Known Technical Debt](#known-technical-debt)
- [Future Optimization Roadmap](#future-optimization-roadmap)
- [Current Production](#current-production)
- [Future Roadmap](#future-roadmap)
- [Known Limitations](#known-limitations)
- [Related Documents](#related-documents)

## Purpose

This document records performance expectations and known bottlenecks without changing the system during documentation freeze.

## Current Performance

The frontend uses Vite code splitting. The professional chart is lazy-loaded. Backend provider calls use in-memory TTL caching.

Expected local behavior:

- ordinary endpoints should respond quickly when provider/cache is healthy
- chart history depends on provider response
- batch quote may be much slower than single quote

## Known Bottlenecks

The largest accepted bottleneck is batch quote latency. Local batch quote requests can take about 25-31 seconds for a broad symbol set.

This is accepted technical debt for correctness. It must not be optimized during documentation-only or UI-freeze tasks.

## Provider Latency

Provider latency comes from:

- yfinance upstream response time
- symbol count
- cache misses
- network conditions
- market hours and data availability

Provider failures should produce controlled unavailable states.

## Rendering Cost

Rendering cost comes from:

- dense dashboard layout
- Opportunity cards
- chart SVG and overlays
- watchlist rows and sparklines
- compare and portfolio tables

Current design favors professional density. Avoid adding expensive effects during release freeze.

## Bundle Size

The frontend build uses manual chunks for React, Recharts, lucide icons, vendor code, and chart chunks.

Performance checks should record:

- largest JavaScript bundle
- chart chunk size
- build warnings
- sourcemap behavior

## Known Technical Debt

- slow batch quote provider path
- no formal provider concurrency control
- no backend distributed cache
- no automated frontend performance budget
- no production observability dashboard

## Future Optimization Roadmap

Future work may include:

- provider batching strategy
- concurrency limits
- cache warmup
- server-side opportunity scoring
- stale-while-revalidate behavior
- frontend virtualization for large lists
- production monitoring

These are future tasks and not current release behavior.

## Current Production

Current production readiness prioritizes correctness and transparent data over speed. Slow data is preferable to fake data.

## Future Roadmap

See [20 Provider Guide](20_PROVIDER_GUIDE.md) for provider-level future work and [05 Release Engineering](05_RELEASE_ENGINEERING.md) for release validation.

## Known Limitations

- Render cold starts may affect first response.
- Provider slowness can delay dashboard completion.
- No service-level objective is formally defined.

## Related Documents

- [13 State Management](13_STATE_MANAGEMENT.md)
- [17 Operations Runbook](17_OPERATIONS_RUNBOOK.md)
- [20 Provider Guide](20_PROVIDER_GUIDE.md)

