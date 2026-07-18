# 14 Testing Strategy

## Table of Contents

- [Purpose](#purpose)
- [Testing Philosophy](#testing-philosophy)
- [Unit Testing](#unit-testing)
- [Integration Testing](#integration-testing)
- [Regression Testing](#regression-testing)
- [Browser Testing](#browser-testing)
- [Acceptance Testing](#acceptance-testing)
- [Release Testing](#release-testing)
- [CI Expectations](#ci-expectations)
- [Coverage Philosophy](#coverage-philosophy)
- [Current Production](#current-production)
- [Future Roadmap](#future-roadmap)
- [Known Limitations](#known-limitations)
- [Related Documents](#related-documents)

## Purpose

This document describes how Market Pulse AI should be tested and why validation must focus on real data, unavailable states, and release safety.

## Testing Philosophy

Tests should protect:

- data integrity
- no-fabrication policy
- provider unavailable behavior
- API contracts
- portfolio math
- analysis wording and confidence behavior
- dashboard regression surfaces

## Unit Testing

Backend unit tests live in `backend/tests/`.

Examples:

- analysis engine tests
- portfolio math tests
- cache tests
- provider routing tests
- comparison tests
- premium alert foundation tests

Command:

```powershell
cd backend
.\.venv\Scripts\python.exe -m pytest
```

## Integration Testing

Integration tests should exercise routes and service boundaries together.

Important endpoints:

- `/health`
- `/api/assets/{symbol}`
- `/api/assets/{symbol}/history`
- `/api/assets/search`
- `/api/assets/quotes`
- `/api/compare`
- `/api/portfolio/evaluate`
- `/api/analysis/{symbol}`
- `/api/risk/{symbol}`

## Regression Testing

Regression testing protects Founder-accepted behavior.

Regression areas:

- UI freeze dashboard layout
- batch quote abort lifecycle
- zero-mock behavior
- provider unavailable states
- Thai/English switch
- chart rendering

## Browser Testing

Browser tests should verify:

- dashboard loads
- no horizontal overflow
- Opportunities renders real cards
- Professional Chart renders
- disclosures open
- navigation works
- language switch works
- console has no uncaught app errors

Manual browser tests are still important because the product is a dense dashboard.

## Acceptance Testing

Founder acceptance is product-level validation. It confirms:

- visible workflows make sense
- data is honest
- UI is production-quality
- known limitations are acceptable

## Release Testing

Release testing includes:

- frontend build
- backend tests
- API smoke
- desktop browser pass
- mobile browser pass
- three-refresh console validation
- production configuration audit
- secret audit
- zero-mock audit

## CI Expectations

Current CI:

- backend tests on Python 3.12
- frontend build on Node 22

CI should fail on:

- backend test failure
- frontend build failure
- dependency installation failure

## Coverage Philosophy

Coverage should scale with risk. Critical financial math, provider fallback, analysis contracts, and release blockers need tests before broad UI polish.

## Current Production

The backend has substantial pytest coverage. Frontend validation relies on TypeScript build and browser smoke checks.

## Future Roadmap

- add frontend unit tests
- add automated Playwright regression
- add dependency audit
- add markdown lint
- add generated API contract validation

## Known Limitations

- No formal frontend test suite is documented as active.
- Browser checks are partly manual/tool-assisted.
- Provider behavior can vary by network and upstream availability.

## Related Documents

- [05 Release Engineering](05_RELEASE_ENGINEERING.md)
- [10 API Reference](10_API_REFERENCE.md)
- [17 Operations Runbook](17_OPERATIONS_RUNBOOK.md)
