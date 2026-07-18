# 18 Incident Response

## Table of Contents

- [Purpose](#purpose)
- [Incident Principles](#incident-principles)
- [Provider Down](#provider-down)
- [API Outage](#api-outage)
- [Slow Response](#slow-response)
- [Frontend Failure](#frontend-failure)
- [Render Outage](#render-outage)
- [Cloudflare Outage](#cloudflare-outage)
- [Broken Deployment](#broken-deployment)
- [Regression](#regression)
- [Emergency Hotfix](#emergency-hotfix)
- [Current Production](#current-production)
- [Future Roadmap](#future-roadmap)
- [Known Limitations](#known-limitations)
- [Related Documents](#related-documents)

## Purpose

This document explains how to respond when production or release validation fails.

## Incident Principles

- protect users first
- do not hide uncertainty
- do not fabricate data
- make the smallest safe fix
- document the root cause
- preserve evidence
- get Founder approval for release actions

## Provider Down

Symptoms:

- quote/history endpoints show unavailable fields
- dashboard shows unavailable states
- batch quote is slow or partial

Response:

1. Verify `/health`.
2. Test single quote and history.
3. Check provider status payloads.
4. Confirm UI remains honest.
5. Document provider outage.

## API Outage

Symptoms:

- `/health` fails
- frontend network errors
- Render service unavailable

Response:

1. Inspect Render logs.
2. Confirm environment variables.
3. Restart service if appropriate.
4. Roll back only after identifying deployment-related failure.

## Slow Response

Symptoms:

- batch quote takes 25-31 seconds or more
- dashboard takes time to complete Opportunities

Response:

1. Confirm request eventually returns.
2. Confirm frontend timeout is not exceeded.
3. Do not optimize during release freeze unless it is a P0/P1 blocker.
4. Document as technical debt if accepted.

## Frontend Failure

Symptoms:

- blank page
- Vite overlay
- uncaught console error
- broken navigation

Response:

1. Reproduce locally.
2. Run `npm run build`.
3. Inspect recent UI changes.
4. Fix only verified blocker.

## Render Outage

Response:

- check Render status and service logs
- validate health endpoint
- redeploy previous backend only after approval

## Cloudflare Outage

Response:

- check Cloudflare deployment status
- verify static build artifacts
- verify environment variables
- roll back previous Pages deployment after approval

## Broken Deployment

Response:

1. Stop additional deployments.
2. Identify frontend or backend side.
3. Compare deployed commit to last known good commit.
4. Roll back if production is unusable.
5. Create incident note.

## Regression

Response:

- classify P0/P1/P2
- reproduce with exact steps
- identify commit range
- fix smallest affected area
- add test where practical

## Emergency Hotfix

Emergency hotfix steps:

1. Create hotfix branch.
2. Apply smallest fix.
3. Run targeted and full validation where practical.
4. Get approval.
5. Deploy.
6. Back-merge if needed.

## Current Production

Incident response is manual. The current system relies on platform health, logs, and smoke tests.

## Future Roadmap

- incident template
- monitoring alerts
- synthetic smoke tests
- provider outage dashboard

## Known Limitations

- No automated pager.
- No external monitoring service is documented as active.

## Related Documents

- [17 Operations Runbook](17_OPERATIONS_RUNBOOK.md)
- [19 Troubleshooting](19_TROUBLESHOOTING.md)
- [05 Release Engineering](05_RELEASE_ENGINEERING.md)

