# AI Architecture

## Table of Contents

- [Purpose](#purpose)
- [Logical Architecture](#logical-architecture)
- [Opportunity Discovery Architecture](#opportunity-discovery-architecture)
- [Stage Responsibilities](#stage-responsibilities)
- [AI Committee Model](#ai-committee-model)
- [Architecture Principles](#architecture-principles)

## Purpose

This document describes the logical AI architecture of Market Pulse AI at an architecture level. It does not define implementation details.

The purpose of the AI architecture is to transform real market evidence into explainable, cautious, educational analysis.

## Logical Architecture

The long-term logical flow is:

Market Data -> Validation -> Normalization -> Feature Engineering -> Opportunity Score -> Market Context -> Market Adjusted Score -> Risk Analysis -> Chief Investment AI -> Investment Committee -> Recommendation -> Explanation

## Opportunity Discovery Architecture

The long-term AI Opportunity Discovery flow is:

Asset Universe
-> Eligibility Filter
-> Financial Engine
-> Technical Engine
-> Catalyst Engine
-> Narrative AI
-> Risk Penalty Engine
-> Multi-Bagger Similarity
-> Opportunity Ranking
-> Explainable AI
-> Dashboard

This architecture supports discovery rather than simple ranking. Its purpose is to identify assets that deserve deeper research because financial, technical, catalyst, narrative, risk, and confidence evidence may be aligning.

The discovery engine must preserve the separation between:

- Opportunity strength
- Risk penalty
- Catalyst evidence
- Similarity evidence
- Confidence
- Educational recommendation

Opportunity discovery must never become a black-box signal.

## Stage Responsibilities

### Market Data

Collect available data from configured providers, including prices, history, fundamentals, news, macro context, and market indicators.

### Validation

Check whether data is present, fresh, usable, and internally reasonable. Invalid or missing data must not be converted into artificial confidence.

### Normalization

Convert provider-specific data into consistent product-level concepts such as symbol, price, currency, timestamp, source, confidence, and unavailable reason.

### Feature Engineering

Transform validated data into interpretable signals such as momentum, volatility, trend, relative strength, valuation context, and risk indicators.

### Opportunity Score

Summarize asset-level evidence into an explainable score that helps users identify assets worth reviewing.

### Catalyst Engine

Evaluate potential future catalysts such as new products, government policy, contracts, mergers and acquisitions, approvals, expansion, technology shifts, industry cycles, and supply chain changes.

Catalyst evidence must be sourced or clearly marked unavailable.

### Narrative AI

Evaluate whether an asset is connected to a credible market narrative. Narrative AI should identify themes, but it must not promote hype without measurable evidence.

### Risk Penalty Engine

Apply negative adjustments when risks materially weaken the opportunity case, including dilution, going concern warnings, excessive debt, negative cash flow, accounting concerns, delisting risk, pump-and-dump characteristics, very low liquidity, or high spreads.

### Multi-Bagger Similarity

Compare current companies with historical high-growth companies using measurable characteristics such as revenue acceleration, margin expansion, industry tailwinds, market creation, capital efficiency, innovation, execution, and competitive moat.

Similarity is not prediction. It is a research signal.

### Opportunity Ranking

Prioritize assets for research based on opportunity strength, evidence quality, risk penalty, catalyst relevance, similarity, and confidence.

### Market Context

Evaluate broader market conditions that may affect the selected asset, including index direction, sector context, macro variables, currency, yields, and risk appetite.

### Market Adjusted Score

Combine asset-level evidence with relevant market context to avoid analyzing the asset in isolation.

### Risk Analysis

Identify downside, volatility, concentration, liquidity, event risk, missing data, and uncertainty.

### Chief Investment AI

Aggregate available evidence into a cautious educational view with supporting reasons, risks, limitations, and conditions that could change the conclusion.

### Investment Committee

Provide multiple analytical viewpoints, such as technical, fundamental, macro, news, risk, and chief investment perspectives.

### Recommendation

Return cautious educational actions rather than guaranteed predictions. Recommendations should be supported by evidence and confidence levels.

### Explanation

Explain why the output exists, what evidence was used, what is missing, what risks matter, and what the user may monitor next.

## AI Committee Model

The committee model should prevent one-dimensional analysis. Each member should contribute a distinct perspective and disclose confidence and missing data.

Committee output should reveal agreement, disagreement, and uncertainty.

## Architecture Principles

- Evidence before opinion.
- Probability over prediction.
- Explain uncertainty.
- Never fabricate missing evidence.
- Keep recommendations educational.
- Human decides.
- Discover opportunities through evidence, not hype.
- Keep Opportunity Score separate from Confidence.
