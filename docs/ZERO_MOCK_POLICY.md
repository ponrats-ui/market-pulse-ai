# Zero Mock Policy

## Table of Contents

- [Purpose](#purpose)
- [Policy](#policy)
- [Never Fabricate](#never-fabricate)
- [Unavailable Data](#unavailable-data)
- [Acceptable Test Data](#acceptable-test-data)
- [User Trust](#user-trust)

## Purpose

The Zero Mock Policy protects user trust.

Financial products can influence real decisions. Market Pulse AI must never present fake information as real market evidence.

## Policy

Production must use real provider data when available. If data is unavailable, the product must clearly display an unavailable state with a concise explanation.

The product should prefer an honest empty state over fabricated completeness.

## Never Fabricate

Market Pulse AI must never fabricate:

- Prices
- Charts
- News
- Scores
- Financial statements
- Indicators
- Recommendations

This applies to frontend UI, backend API responses, AI outputs, documentation examples presented as live behavior, and production deployments.

## Unavailable Data

If data is unavailable, display:

Data unavailable

The unavailable state should explain why when possible. Examples include provider unavailable, endpoint unavailable, stale data, missing financial statements, unsupported asset type, or insufficient evidence.

## Acceptable Test Data

Clearly labeled test fixtures may exist for automated tests. Test data must not appear as live production market data.

Mock data may be used only in isolated development or testing contexts where it cannot be mistaken for real provider output.

## User Trust

A transparent unavailable state builds more trust than a fabricated chart or invented recommendation.

Zero Mock is not only an engineering rule. It is a product promise.
