# V1 Release Checklist

## Branch

- Release branch: `release/v1-production-candidate`
- Source branch: `feature/phase-e-premium-foundation`
- Founder approval for Phases A-E: granted

## Release Freeze

- New features: none
- UI redesign: none
- Architecture expansion: none
- Scope: release hardening, validation, security, performance, accessibility, documentation

## Required Gates

- Backend tests: PASS, 84 passed
- Frontend build: PASS
- Frontend dependency audit: PASS, `npm audit --audit-level=moderate` found 0 vulnerabilities
- Backend dependency consistency: PASS, `pip check` found no broken requirements
- Backend vulnerability audit: NOT RUN, `pip-audit` is not installed locally
- Secret scan: PASS, no committed secrets found
- Cloudflare config: PASS, `frontend/wrangler.toml` uses `market-pulse-ai` and `dist`
- Render config: PASS, `render.yaml` defines backend root, build, start command, and `/health`
- Local API smoke: PASS
- Production API smoke: PARTIAL, current production backend is behind the release branch
- Browser desktop review: PASS
- Browser mobile review: PASS

## Security Checklist

- No secrets in Git: PASS
- Strict production CORS: PASS, Render config uses `https://market-pulse-ai.pages.dev`
- Input validation: PASS for FastAPI query bounds and Pydantic request bodies; deeper per-field validation remains future hardening
- Safe URLs: PASS after tightening custom YouTube embed URL handling
- Safe YouTube embedding: PASS, no autoplay before explicit Play and postMessage target is restricted to embed origin
- Unsafe HTML: PASS, no `dangerouslySetInnerHTML` found
- Provider keys: PASS, keys are environment variable names only
- Secure error responses: PARTIAL, public APIs still return transparent provider-unavailable payloads but no centralized error envelope
- Rate-limit strategy: DOCUMENTED in support and rollback docs, not implemented in app code

## Performance Checklist

- Frontend bundle: PASS, build artifacts generated without bundle warning
- Lazy/code splitting: PASS, current chunks separate React, charts, icons, and app code
- Cache policy: PASS, backend has service TTL cache
- Provider request limits: PARTIAL, caching exists but no formal external rate limiter
- Render cold start: KNOWN LIMITATION
- Mobile responsiveness: PASS in 390px browser review

## Legal And Product Language

- Educational disclaimer: PASS
- Risk disclosure: PASS
- Privacy policy: NOT PRESENT as a dedicated document
- Terms of use: NOT PRESENT as a dedicated document
- Provider attribution: PARTIAL, yfinance/Yahoo Finance source is surfaced in data payloads
- MIT/open-source notices: PASS
- PIA trademark language: PASS, uses PIA(tm)-style text and does not use registered mark

## Decision

NOT READY TO MERGE.

The release branch is locally stable, but production is not yet aligned with the branch and dedicated Privacy Policy and Terms of Use documents are missing for public launch readiness.
