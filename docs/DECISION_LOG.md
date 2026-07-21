# Decision Log

## Table of Contents

- [Purpose](#purpose)
- [Decision Format](#decision-format)
- [ADR-001: Explainable AI](#adr-001-explainable-ai)
- [ADR-002: Zero Mock Policy](#adr-002-zero-mock-policy)
- [ADR-003: Market Adjusted Score](#adr-003-market-adjusted-score)
- [ADR-004: Chief Investment AI](#adr-004-chief-investment-ai)
- [ADR-005: AI Committee](#adr-005-ai-committee)
- [ADR-006: Global Market Vision](#adr-006-global-market-vision)
- [ADR-007: Cross-Market Intelligence](#adr-007-cross-market-intelligence)

## Purpose

This document records architecture and product-governance decisions for Market Pulse AI.

## Decision Format

Each decision should include:

- Date
- Context
- Decision
- Alternatives
- Reason
- Expected Impact

## ADR-001: Explainable AI

### Date

2026-07-21

### Context

Financial AI outputs can influence user decisions. Unexplained recommendations reduce trust and can create false confidence.

### Decision

Market Pulse AI will prioritize Explainable AI as a core product principle.

### Alternatives

- Black-box recommendation model
- Signal-only product
- Raw data dashboard without AI explanation

### Reason

Users need to understand why an output exists before relying on it.

### Expected Impact

The product will emphasize evidence, confidence, missing data, and limitations in AI outputs.

## ADR-002: Zero Mock Policy

### Date

2026-07-21

### Context

Fabricated financial data can mislead users and damage trust.

### Decision

Production must never present fabricated data as real.

### Alternatives

- Use mock data when providers fail
- Use demo values for visual completeness
- Hide unavailable states

### Reason

Honest unavailability is safer than false completeness.

### Expected Impact

The product will show transparent unavailable states when data is missing.

## ADR-003: Market Adjusted Score

### Date

2026-07-21

### Context

Asset-level signals can be misleading when broader market conditions are ignored.

### Decision

Market Pulse AI will support market-adjusted interpretation that combines asset evidence with relevant market context.

### Alternatives

- Use asset-only scoring
- Use market-only scoring
- Show separate scores without synthesis

### Reason

Assets live inside broader markets, sectors, currencies, and macro environments.

### Expected Impact

Users receive more contextual analysis and a clearer explanation of market influence.

## ADR-004: Chief Investment AI

### Date

2026-07-21

### Context

Users need a concise synthesis of complex evidence.

### Decision

Market Pulse AI will provide a Chief Investment AI view that aggregates evidence cautiously.

### Alternatives

- Only display raw data
- Only display specialist opinions
- Provide direct trade calls

### Reason

A synthesis layer helps users understand the overall view while preserving evidence and limitations.

### Expected Impact

Users get a clearer summary without treating it as guaranteed advice.

## ADR-005: AI Committee

### Date

2026-07-21

### Context

Investment analysis requires multiple perspectives.

### Decision

Market Pulse AI will use an AI Committee concept to separate technical, fundamental, macro, news, risk, and chief perspectives.

### Alternatives

- Single AI voice
- Pure scoring system
- Manual-only interpretation

### Reason

Distinct perspectives reduce one-dimensional conclusions.

### Expected Impact

Users can see agreement, disagreement, confidence, and missing data across viewpoints.

## ADR-006: Global Market Vision

### Date

2026-07-21

### Context

Investors increasingly evaluate assets across countries, currencies, sectors, and asset classes.

### Decision

Market Pulse AI will use a global-first product vision.

### Alternatives

- Thailand-only platform
- US-only platform
- Single-asset-class platform

### Reason

Long-term investor workflows are global and multi-asset.

### Expected Impact

Architecture and documentation should remain flexible for global market expansion.

## ADR-007: Cross-Market Intelligence

### Date

2026-07-21

### Context

Assets are affected by related markets such as commodities, currencies, yields, indices, and macro variables.

### Decision

Market Pulse AI will treat cross-market intelligence as a long-term strategic capability.

### Alternatives

- Analyze assets independently
- Add only static category labels
- Depend only on price charts

### Reason

Cross-market context can improve explanation quality and risk awareness.

### Expected Impact

Future analysis should explain relevant market relationships where evidence exists.
