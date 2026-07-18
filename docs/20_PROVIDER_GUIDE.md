# 20 Provider Guide

## Table of Contents

- [Purpose](#purpose)
- [Provider Principles](#provider-principles)
- [Current Provider](#current-provider)
- [Future Providers](#future-providers)
- [Selection Rules](#selection-rules)
- [Fallback Rules](#fallback-rules)
- [Timeout Rules](#timeout-rules)
- [Data Quality Validation](#data-quality-validation)
- [Current Production](#current-production)
- [Future Roadmap](#future-roadmap)
- [Known Limitations](#known-limitations)
- [Related Documents](#related-documents)

## Purpose

This guide explains how provider data enters Market Pulse AI and how to add or operate providers safely.

## Provider Principles

- provider data must be attributed
- missing data stays unavailable
- secrets stay server-side
- provider failures are not hidden
- no fake fallback values
- provider limits must be respected

## Current Provider

Current primary provider: yfinance/Yahoo Finance compatibility path.

Used for:

- quotes
- history
- available fundamentals
- market-condition proxy symbols
- sparklines through history

Why: broad coverage, low setup cost, no committed API keys.

## Future Providers

Future provider categories:

- macro data, such as FRED
- company news, such as RSS or approved APIs
- economic calendar
- sentiment
- premium alerts
- licensed market data

Future providers must be added behind interfaces or registries, not directly in UI components.

## Selection Rules

Provider selection should consider:

- asset class
- symbol support
- credentials
- provider health
- response quality
- rate limits
- cache status

Current implementation uses yfinance first for market data and provider registries for optional categories.

## Fallback Rules

Fallback rules:

1. Try configured provider.
2. Return normalized data if available.
3. If unavailable, return unavailable status and reason.
4. Do not fabricate replacement values.
5. Preserve nulls.

## Timeout Rules

Ordinary frontend API timeout is shorter than batch quote timeout.

Batch quote has a dedicated longer timeout because provider latency is known and accepted.

Future timeout changes must be tested against refresh behavior and provider limits.

## Data Quality Validation

Validate:

- symbol
- timestamp
- numeric fields
- empty history
- missing close prices
- stale fields
- provider warnings

Invalid or missing data should become unavailable, partial, stale, or warning state.

## Current Production

Market data is yfinance-first. Optional provider surfaces may exist but return unavailable when not configured.

## Future Roadmap

- formal provider health dashboard
- provider priority configuration
- rate limiting and backoff
- paid provider integration if approved
- provider contract tests

## Known Limitations

- yfinance is not an institutional SLA provider.
- Some symbols may fail or be delayed.
- Optional providers need credentials and product review.

## Related Documents

- [10 API Reference](10_API_REFERENCE.md)
- [13 State Management](13_STATE_MANAGEMENT.md)
- [16 Performance Guide](16_PERFORMANCE_GUIDE.md)
- [Real Data Policy](REAL_DATA_POLICY.md)

