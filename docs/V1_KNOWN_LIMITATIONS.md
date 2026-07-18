# V1 Known Limitations

## Production Alignment

Current production is behind the release branch. `/api/news`, `/api/macro`, and `/api/subscription/features` returned 404 during Phase F production smoke testing.

## Legal Documents

Dedicated Privacy Policy and Terms of Use documents are not present. These should exist before public launch.

## Backend Dependency Audit

`pip-audit` is not installed locally. Backend dependency review used `pip check` and outdated package review, but not a vulnerability database scan.

## Rate Limiting

Provider cache TTLs reduce repeated requests, but there is no formal application-level rate limiter yet.

## Render Cold Start

Render free or low-resource services may experience cold-start latency. This should be measured after production deployment.

## Provider Availability

Market data depends on configured providers and yfinance availability. Unavailable provider data should remain transparent and must not be fabricated.

## Premium And Alerts

Premium, alerts, digests, and notification channels are architecture-only. Payments and outbound notifications are disabled.

## Portfolio

Portfolio tools are simulated only. They are educational and are not connected to real brokers.
