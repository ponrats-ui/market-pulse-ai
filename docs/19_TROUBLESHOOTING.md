# 19 Troubleshooting

## Table of Contents

- [Purpose](#purpose)
- [Timeouts](#timeouts)
- [AbortError](#aborterror)
- [CORS](#cors)
- [Build Failures](#build-failures)
- [Dependency Conflicts](#dependency-conflicts)
- [Provider Unavailable](#provider-unavailable)
- [Frontend Shows Unavailable](#frontend-shows-unavailable)
- [Chart Does Not Render](#chart-does-not-render)
- [Portfolio Looks Wrong](#portfolio-looks-wrong)
- [Current Production](#current-production)
- [Future Roadmap](#future-roadmap)
- [Known Limitations](#known-limitations)
- [Related Documents](#related-documents)

## Purpose

This document maps common symptoms to likely causes, diagnosis, resolution, and verification.

## Timeouts

Symptoms: slow dashboard, API request timeout, missing Opportunity cards.

Root Causes: provider latency, batch quote cache miss, network issue.

Diagnosis:

- test `/api/assets/quotes`
- compare single quote speed
- check browser console

Resolution:

- wait for provider if under accepted timeout
- document provider slowness
- do not add retries during release freeze

Verification: batch quote returns HTTP 200 and UI renders cards or unavailable state.

## AbortError

Symptoms: console shows aborted request or Opportunity scan fails.

Root Causes: user refresh, request cancellation, old lifecycle bug.

Diagnosis:

- refresh three times
- check whether new AbortError appears after completed load
- inspect batch quote timing

Resolution: only fix if repeated app error occurs after current lifecycle fix.

Verification: Opportunities renders after refresh without new repeated AbortError.

## CORS

Symptoms: browser blocks API calls.

Root Causes: missing `CORS_ALLOWED_ORIGINS`, wrong Cloudflare domain, backend in production rejecting origin.

Diagnosis:

- inspect browser network error
- check Render env vars
- call `/health` directly

Resolution: set exact Cloudflare origin in Render.

Verification: frontend can call backend endpoints.

## Build Failures

Symptoms: `npm run build` fails.

Root Causes: TypeScript error, missing dependency, syntax error.

Diagnosis:

- run frontend build locally
- inspect first fatal error

Resolution: fix only the failing source line or dependency mismatch.

Verification: build passes.

## Dependency Conflicts

Symptoms: install failure or lockfile mismatch.

Root Causes: Node version mismatch, package-lock drift, registry issue.

Diagnosis:

- compare CI Node version
- inspect `frontend/package-lock.json`

Resolution: use documented install command and avoid unrelated dependency upgrades.

Verification: install and build pass.

## Provider Unavailable

Symptoms: null price, empty news, no calendar events.

Root Causes: provider not configured, upstream failure, unsupported symbol.

Diagnosis:

- inspect response source/status
- check provider environment variables

Resolution: show unavailable state; configure provider only through approved provider work.

Verification: no fake data appears.

## Frontend Shows Unavailable

Symptoms: UI unavailable while backend works.

Root Causes: missing `VITE_API_BASE_URL`, wrong API URL, CORS, production localhost build.

Diagnosis:

- inspect browser network requests
- verify Cloudflare env var
- check `frontend/src/lib/api.ts` resolution behavior

Resolution: set correct API base URL and redeploy frontend.

Verification: quote, source, timestamp, and chart appear.

## Chart Does Not Render

Symptoms: empty chart panel.

Root Causes: no history points, provider failure, JavaScript error.

Diagnosis:

- call history endpoint
- call technical endpoint
- inspect `.pro-chart-svg`

Resolution: fix provider data path or display unavailable state.

Verification: chart renders with provider source or shows transparent unavailable message.

## Portfolio Looks Wrong

Symptoms: unexpected P/L, cash, or allocation.

Root Causes: invalid transaction, stale quote, insufficient shares, unsupported symbol.

Diagnosis:

- inspect transaction history
- inspect portfolio evaluation response
- check quote for each holding

Resolution: correct input or backend validation bug.

Verification: repeated buys, partial sells, sell all, and reset behave as expected.

## Current Production

Troubleshooting relies on local builds, backend tests, API smoke, browser console, and platform logs.

## Future Roadmap

- add troubleshooting scripts
- add health dashboard
- add automated smoke checks

## Known Limitations

- Provider outages may be intermittent.
- Some browser console logs can contain stale messages from previous sessions.

## Related Documents

- [17 Operations Runbook](17_OPERATIONS_RUNBOOK.md)
- [18 Incident Response](18_INCIDENT_RESPONSE.md)
- [20 Provider Guide](20_PROVIDER_GUIDE.md)

