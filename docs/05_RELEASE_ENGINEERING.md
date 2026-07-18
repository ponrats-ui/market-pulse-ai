# 05 Release Engineering

## Table of Contents

- [Purpose](#purpose)
- [Release Philosophy](#release-philosophy)
- [Git Flow](#git-flow)
- [Branch Strategy](#branch-strategy)
- [Release Branch](#release-branch)
- [Hotfix Flow](#hotfix-flow)
- [Rollback](#rollback)
- [Versioning](#versioning)
- [Deployment](#deployment)
- [Cloudflare Pages](#cloudflare-pages)
- [Render](#render)
- [Release Checklist](#release-checklist)
- [Regression Checklist](#regression-checklist)
- [Founder Acceptance](#founder-acceptance)
- [Production Acceptance](#production-acceptance)
- [Emergency Patch Process](#emergency-patch-process)
- [Current State](#current-state)
- [Future Work](#future-work)
- [Known Limitations](#known-limitations)
- [Related Documents](#related-documents)

## Purpose

This document preserves the release process for Market Pulse AI. It explains what to do before a public release and why each step exists.

## Release Philosophy

Market Pulse AI releases must be boring, traceable, and honest.

Release work should not add features. It should:

- validate the accepted product
- document known limitations
- prevent secrets from entering Git
- keep production behind verified code
- separate Founder approval from deployment execution

## Git Flow

Current flow:

```text
feature/* or fix/*
  -> develop
  -> release/*
  -> main after explicit Founder approval
```

Rules:

- Do not rewrite accepted history.
- Do not squash accepted Founder chains unless requested before acceptance.
- Do not push, deploy, merge, or tag without explicit approval.
- Use explicit `git add` paths.
- Never stage `RC2D_WIP_PATCH.diff`.

## Branch Strategy

`main`:

- production lineage
- protected from unapproved release work

`develop`:

- accepted integration branch
- receives Founder-approved chains

`release/v1.0.0-rc1`:

- release candidate preparation
- documentation, versioning, audit, and blocker fixes only

Feature/fix branches:

- scoped implementation work
- merged into `develop` after acceptance

## Release Branch

Create release branches only from accepted `develop`.

Example:

```powershell
git checkout develop
git checkout -b release/v1.0.0-rc1
```

Why this exists:

- isolates release documentation and version changes
- keeps `develop` stable after acceptance
- avoids accidental production merge

## Hotfix Flow

Hotfixes should be narrow.

Recommended flow:

```text
main
  -> hotfix/<issue>
  -> validation
  -> main after approval
  -> back-merge to develop if needed
```

Hotfixes must include:

- verified root cause
- smallest possible code change
- focused test
- release note
- rollback note

## Rollback

Rollback means returning production to the last known good deployment and documenting why.

Rollback steps:

1. Identify failing release commit.
2. Confirm last good frontend and backend versions.
3. Redeploy previous Render service version or commit.
4. Redeploy previous Cloudflare Pages deployment.
5. Verify `/health` and dashboard smoke tests.
6. Record incident notes.

See [V1 Rollback Plan](V1_ROLLBACK_PLAN.md).

## Versioning

Market Pulse AI should use semantic versioning:

- `MAJOR.MINOR.PATCH`
- release candidates use `-rcN`

Examples:

- `1.0.0-rc1`
- `1.0.0`
- `1.0.1`

Version fields should stay consistent where established:

- frontend package metadata
- backend FastAPI version and health response
- changelog
- About dialog if present

Do not invent new versioning systems without a decision record.

## Deployment

Deployment is not automatic unless explicitly approved.

Production deployment order:

1. Merge approved release branch into `main`.
2. Push `main`.
3. Deploy or redeploy Render backend.
4. Deploy or redeploy Cloudflare frontend.
5. Run production smoke tests.
6. Create release tag only after production verification.

## Cloudflare Pages

Expected settings:

- Framework preset: Vite
- Root directory: `frontend`
- Build command: `npm run build`
- Build output directory: `dist`
- Production variable: `VITE_API_BASE_URL=<Render backend URL>`

Cloudflare should not contain backend secrets. The frontend API URL is public configuration.

## Render

Expected settings:

- Root directory: `backend`
- Runtime: Python
- Build command: `pip install -r requirements.txt`
- Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- Health check: `/health`
- `APP_ENV=production`
- `CORS_ALLOWED_ORIGINS=https://market-pulse-ai.pages.dev`

## Release Checklist

- branch created from accepted `develop`
- working tree clean except allowed untracked files
- frontend build passes
- backend tests pass
- API smoke passes
- browser desktop smoke passes
- browser mobile smoke passes
- console has no uncaught app errors
- zero-mock audit passes
- secret audit passes
- production config audit passes
- release documentation updated
- changelog updated
- version fields consistent

## Regression Checklist

Core surfaces:

- dashboard
- asset search
- watchlist
- Opportunities
- professional chart
- Chief AI
- AI Committee
- risk
- financials
- news impact
- sentiment
- calendar
- compare
- paper portfolio
- Relax Mode
- language switch

Refresh requirements:

- perform three independent refreshes
- wait for primary dashboard requests
- confirm Opportunities renders
- confirm chart renders
- confirm no new Opportunity AbortError

## Founder Acceptance

Founder acceptance confirms product behavior, UI quality, documentation clarity, and known limitations.

Founder acceptance is required before:

- merge to `main`
- production deployment
- release tag

## Production Acceptance

Production acceptance confirms deployed behavior, not local behavior.

Required checks:

- production frontend loads
- production backend health is 200
- real data appears when provider returns it
- missing provider data is transparent
- no production console errors
- mobile layout remains usable

## Emergency Patch Process

Emergency patches are allowed only for critical production defects.

Process:

1. Identify P0 issue.
2. Create hotfix branch.
3. Make smallest safe fix.
4. Run targeted and full validation where practical.
5. Get Founder approval.
6. Deploy.
7. Document incident and follow-up.

## Current State

Release candidate work is performed on `release/v1.0.0-rc1`. The UI Freeze is accepted. Production deployment is still a separate approved action.

## Future Work

- add automated release checklist script
- add dependency audit to CI
- add production smoke automation
- add deployment status documentation

## Known Limitations

- Production deployment still requires manual approval.
- Browser validation can depend on local provider timing.
- Batch quote performance is accepted technical debt for the current release.

## Related Documents

- [04 System Decisions](04_SYSTEM_DECISIONS.md)
- [Founder UI Freeze Acceptance](FOUNDER-UI-FREEZE-ACCEPTANCE.md)
- [V1 Release Checklist](V1_RELEASE_CHECKLIST.md)
- [V1 Rollback Plan](V1_ROLLBACK_PLAN.md)
- [Deployment Cloudflare](DEPLOYMENT_CLOUDFLARE.md)
- [Deploy Backend Render](DEPLOY_BACKEND_RENDER.md)
