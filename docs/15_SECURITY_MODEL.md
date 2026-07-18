# 15 Security Model

## Table of Contents

- [Purpose](#purpose)
- [Threat Model](#threat-model)
- [Secrets](#secrets)
- [Environment Variables](#environment-variables)
- [Authentication Assumptions](#authentication-assumptions)
- [Input Validation](#input-validation)
- [Dependency Updates](#dependency-updates)
- [CORS](#cors)
- [API Exposure](#api-exposure)
- [Client-Side Risks](#client-side-risks)
- [Zero Secret Policy](#zero-secret-policy)
- [Current Production](#current-production)
- [Future Roadmap](#future-roadmap)
- [Known Limitations](#known-limitations)
- [Related Documents](#related-documents)

## Purpose

This document defines the current security model and the assumptions behind it. Market Pulse AI is public educational software, not an authenticated brokerage or private financial account system.

## Threat Model

Primary risks:

- leaked provider credentials
- permissive CORS in production
- unsafe user-provided URLs
- dependency vulnerabilities
- provider abuse or rate exhaustion
- fake or misleading financial data
- accidental storage of private user data

Out of scope for current production:

- real brokerage authentication
- bank credentials
- payment activation
- private cloud portfolio storage

## Secrets

Secrets must never be committed to Git.

Examples:

- API keys
- provider tokens
- service-account files
- passwords
- private keys
- paid data-provider credentials

## Environment Variables

Frontend:

- `VITE_API_BASE_URL` is public configuration, not a secret.

Backend:

- `APP_ENV`
- `LOG_LEVEL`
- `PORT`
- `CORS_ALLOWED_ORIGINS`
- optional provider keys such as `FRED_API_KEY`, `FINNHUB_API_KEY`, `NEWSAPI_KEY`, and `TRADING_ECONOMICS_KEY`

Provider keys belong only in deployment environments or local ignored `.env` files.

## Authentication Assumptions

Current production has no user authentication. The app exposes public educational endpoints and local-only simulated portfolio state.

Future authentication is required before:

- cloud portfolio sync
- private alert settings
- payment activation
- user-specific notification delivery

## Input Validation

FastAPI query constraints exist for several endpoints, such as limits on search, sectors, news, and batch quotes.

Required approach:

- bound list sizes
- validate numeric ranges
- canonicalize symbols through registry where practical
- reject or sanitize unsafe URLs
- never treat client input as provider credentials

## Dependency Updates

Dependencies should be reviewed before release and updated deliberately.

Current CI installs:

- Python backend requirements
- frontend npm packages

Future CI should include dependency audit and lockfile review.

## CORS

Production CORS must be explicit. Wildcard origins are filtered out in production configuration.

Expected production origin:

- `https://market-pulse-ai.pages.dev`

Local origins are allowed only in development.

## API Exposure

Current APIs are public and educational. They should not expose secrets, server paths, stack traces, or private user data.

Provider unavailable payloads are acceptable; secret values are not.

## Client-Side Risks

Client-side code can be inspected by anyone.

Rules:

- do not embed provider keys
- do not store private personal financial data
- do not store brokerage credentials
- keep YouTube embedding limited to official embed/watch URLs

## Zero Secret Policy

If a secret is found in Git:

1. Stop work.
2. Do not repeat the secret in reports.
3. Identify file path and variable name only.
4. Rotate the secret outside Git.
5. Remove it from history using an approved procedure.

## Current Production

The current system uses public endpoints, CORS allowlists, environment variables, ignored `.env` files, and transparent no-secret docs.

## Future Roadmap

- rate limiting
- dependency audit in CI
- stronger response error envelope
- authentication and authorization design
- security headers review

## Known Limitations

- No formal rate limiter is active.
- No authentication exists.
- Public endpoints depend on provider availability.

## Related Documents

- [05 Release Engineering](05_RELEASE_ENGINEERING.md)
- [18 Incident Response](18_INCIDENT_RESPONSE.md)
- [20 Provider Guide](20_PROVIDER_GUIDE.md)
- [Security Policy](../SECURITY.md)

