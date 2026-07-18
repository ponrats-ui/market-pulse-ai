# 07 Glossary

## Table of Contents

- [Purpose](#purpose)
- [Financial Terms](#financial-terms)
- [Technical Indicators](#technical-indicators)
- [Architecture Terms](#architecture-terms)
- [Internal Module Names](#internal-module-names)
- [Provider Terms](#provider-terms)
- [AI Terms](#ai-terms)
- [Release Terms](#release-terms)
- [Git Terms](#git-terms)
- [Abbreviations](#abbreviations)
- [Current State](#current-state)
- [Future Work](#future-work)
- [Known Limitations](#known-limitations)
- [Related Documents](#related-documents)

## Purpose

This glossary gives contributors a shared vocabulary. Market Pulse AI spans finance, product, AI, frontend, backend, and release engineering, so common definitions reduce confusion.

## Financial Terms

Asset: anything the user can research, such as a stock, ETF, crypto asset, commodity, FX pair, index, or bond yield.

Equity: a stock or share representing ownership in a company.

ETF: exchange-traded fund.

Index: a benchmark that tracks a market or group of securities.

Commodity: a physical market asset such as gold, oil, natural gas, silver, copper, or platinum.

FX: foreign exchange.

Market Cap: market capitalization, usually share price multiplied by shares outstanding.

P/E: price-to-earnings ratio.

P/BV: price-to-book-value ratio.

Dividend Yield: dividend per share divided by price, where provider data exists.

EPS: earnings per share.

ROE: return on equity.

ROA: return on assets.

Gross Margin: gross profit divided by revenue.

Net Margin: net profit divided by revenue.

Debt to Equity: leverage ratio comparing debt and equity.

Free Cash Flow: cash generated after capital expenditures, where available.

Drawdown: decline from a previous peak.

Volatility: degree of price movement.

Liquidity: ease of buying or selling without large price impact.

## Technical Indicators

SMA: simple moving average.

EMA: exponential moving average.

RSI: relative strength index, a momentum oscillator.

MACD: moving average convergence divergence.

Bollinger Bands: bands around a moving average based on volatility.

ATR: average true range, a volatility measure.

VWAP: volume-weighted average price.

OHLCV: open, high, low, close, volume.

Support: heuristic level where buyers may appear. Not a prediction.

Resistance: heuristic level where sellers may appear. Not a prediction.

## Architecture Terms

Frontend: React application in `frontend/`.

Backend: FastAPI service in `backend/`.

API Layer: route definitions and request/response boundary.

Service Layer: backend business logic modules in `backend/app/services/`.

Provider Layer: adapters and registries that fetch external data.

Data Hub: backend abstraction for provider routing, asset contracts, symbol resolution, and provider health.

Config: JSON or deployment settings in `configs/`, `render.yaml`, and frontend environment variables.

Unavailable State: explicit response or UI state that says data is missing, disabled, stale, or not applicable.

## Internal Module Names

Chief Investment AI: compact summary view that aggregates evidence into cautious educational interpretation.

AI Committee: specialist role-based analysis layer.

Opportunity Scanner: dashboard surface ranking real-data research candidates.

Professional Chart: chart workspace with indicators and drawing tools.

Paper Trading: simulated portfolio and transaction workflow.

PIA: Personal Investment Assistant.

Relax Mode: optional embedded YouTube focus music feature.

Master Asset Registry: searchable registry for supported global and Thai assets.

## Provider Terms

yfinance: Python package used as the current primary Yahoo Finance compatibility provider.

Provider Adapter: code that converts upstream data into Market Pulse AI contracts.

Provider Registry: code that selects available providers.

Provider Health: status metadata showing whether a provider is available, unavailable, degraded, or not configured.

Source: origin label shown in API and UI responses.

Timestamp: time associated with provider data or response generation.

Stale: data that may be old or delayed.

## AI Terms

Evidence: data used to support an interpretation.

Interpretation: explanation of what evidence may mean.

Recommendation: cautious educational action label, not regulated financial advice.

Confidence: heuristic estimate of evidence strength.

Market Regime: broad state of market behavior used by analysis logic where available.

Adaptive Weights: configurable factor weights used by analysis profiles.

Limitations: missing data, weak evidence, provider gaps, or uncertainty disclosures.

## Release Terms

Release Candidate: a branch or build prepared for release validation.

UI Freeze: Founder-accepted UI state where only bug fixes are allowed.

Founder Acceptance: explicit approval that product behavior meets Founder expectations.

Production Acceptance: verification that deployed production works after release.

Rollback: restore production to the last known good state.

P0: release blocker.

P1: must fix before release deployment.

P2: accepted technical debt.

## Git Terms

Branch: named line of development.

Commit: saved repository change.

Merge: integration of one branch into another.

Tag: named release pointer.

Working Tree: current filesystem state of tracked and untracked files.

Untracked File: file not currently committed or staged.

Staged File: file prepared for commit.

## Abbreviations

AI: artificial intelligence.

API: application programming interface.

CORS: cross-origin resource sharing.

FX: foreign exchange.

MVP: minimum viable product.

PIA: Personal Investment Assistant.

QA: quality assurance.

RC: release candidate.

SLA: service-level agreement.

TTL: time to live.

UI: user interface.

UX: user experience.

Vite: frontend build tool.

## Current State

These terms describe the current release candidate and its established architecture.

## Future Work

Add terms when new modules become production behavior. Do not add aspirational features as if they already exist.

## Known Limitations

Some financial terms are simplified for contributor clarity. They are not formal financial education material.

## Related Documents

- [01 Product Vision](01_PRODUCT_VISION.md)
- [02 System Architecture](02_SYSTEM_ARCHITECTURE.md)
- [03 Algorithm Reference](03_ALGORITHM_REFERENCE.md)
- [05 Release Engineering](05_RELEASE_ENGINEERING.md)
