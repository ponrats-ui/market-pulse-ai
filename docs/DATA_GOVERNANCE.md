# Data Governance

## Table of Contents

- [Purpose](#purpose)
- [Accepted Data Providers](#accepted-data-providers)
- [Data Freshness](#data-freshness)
- [Validation](#validation)
- [Normalization](#normalization)
- [Error Handling](#error-handling)
- [Fallback Strategy](#fallback-strategy)
- [Missing Data Policy](#missing-data-policy)
- [Caching Philosophy](#caching-philosophy)
- [Data Quality Monitoring](#data-quality-monitoring)
- [Single Source of Truth](#single-source-of-truth)
- [Production Data Rules](#production-data-rules)

## Purpose

Data governance protects trust in Market Pulse AI. The product must clearly distinguish real provider data, unavailable data, stale data, partial data, and derived analysis.

## Accepted Data Providers

Accepted providers should be documented, attributable, and appropriate for the data domain.

Examples of provider categories:

- Market price providers
- Historical chart providers
- Fundamental data providers
- News providers
- Macro and economic data providers
- Reference-data providers

Provider use should remain transparent to users where it affects interpretation.

## Data Freshness

Data should include timestamps whenever possible.

The product should disclose stale or delayed data when the freshness of data can materially affect interpretation.

## Validation

Data should be checked for presence, format, reasonableness, source, timestamp, and applicability.

Invalid data should not be promoted into confident analysis.

## Normalization

Provider-specific data should be normalized into product-level concepts such as symbol, name, price, currency, timestamp, source, confidence, status, and unavailable reason.

Normalization supports consistency across markets and providers.

## Error Handling

Data errors should be transparent and controlled. The product should avoid silent failure when the user needs to know why information is unavailable.

Errors should be communicated in user-safe language without exposing sensitive internal details.

## Fallback Strategy

Fallbacks should preserve honesty.

A fallback may try another provider, use a stale-but-labeled value, or show unavailable. A fallback must not fabricate data.

## Missing Data Policy

Missing data should be shown as unavailable, not invented.

The UI should explain missing data when possible, such as provider unavailable, unsupported asset type, endpoint unavailable, or insufficient evidence.

## Caching Philosophy

Caching should improve performance and provider stability without misleading users.

Cached data should preserve timestamp and freshness context. Stale data should be identified when relevant.

## Data Quality Monitoring

Future governance should monitor:

- Provider availability
- Response latency
- Error rates
- Stale data frequency
- Missing fields
- Symbol mapping failures
- Unexpected value ranges

## Single Source of Truth

Each data domain should have a clear source of truth. Derived UI displays should not create competing interpretations of the same field.

## Production Data Rules

Production must follow:

- No fabricated data
- Clear provider attribution
- Clear unavailable states
- Clear timestamps where available
- No hidden mock fallback
- No fake charts, scores, news, or recommendations
