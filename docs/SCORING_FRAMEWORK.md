# Scoring Framework

## Table of Contents

- [Purpose](#purpose)
- [Scoring Philosophy](#scoring-philosophy)
- [Opportunity Score](#opportunity-score)
- [Penny Opportunity Score](#penny-opportunity-score)
- [Catalyst Score](#catalyst-score)
- [Similarity Score](#similarity-score)
- [Risk Penalty](#risk-penalty)
- [Market Score](#market-score)
- [Market Adjusted Score](#market-adjusted-score)
- [Risk Score](#risk-score)
- [Confidence Score](#confidence-score)
- [Interpretation Standard](#interpretation-standard)

## Purpose

This document explains the scoring concepts used by Market Pulse AI.

Scores explain the market. They do not predict the future.

## Scoring Philosophy

Scores should help users quickly understand complex information. They should be deterministic where appropriate, explainable, and tied to evidence.

A score is useful only when users can understand what it means, what affects it, and what it does not mean.

## Opportunity Score

### Purpose

The Opportunity Score summarizes asset-level market signals into a single review indicator.

### Meaning

A higher score suggests stronger current evidence under the model. It does not mean guaranteed upside or a required buy decision.

### Interpretation

The score should be read with trend, momentum, volatility, risk, and available technical context.

### Philosophy

The Opportunity Score is a prioritization tool, not a prediction.

## Penny Opportunity Score

### Purpose

The Penny Opportunity Score is the RC2 ranking score for low-priced equities that may deserve deeper research.

### Meaning

It summarizes whether a low-priced asset has evidence of asymmetric opportunity after considering liquidity, fundamentals, growth, technical strength, verified catalyst availability, risk, and data confidence.

### Interpretation

A higher score does not mean the asset is safe or should be bought. It means the asset may deserve review under the penny opportunity framework.

### Philosophy

Penny stock is a category, not an investment thesis. Cheapness alone should never create a high score.

### Implementation Reference

The first production implementation is documented in `docs/PENNY_OPPORTUNITY_SCANNER_IMPLEMENTATION.md`, runs on the shared Opportunity Engine Framework, and uses methodology version `penny-opportunity-v1`.

RC5A evolves the Thailand-specific implementation into Thai Emerging Opportunities (Penny Stock) with methodology version `thai-emerging-opportunity-v1`. The default Thai universe uses `price <= 10.00 THB`, while supported configurable thresholds are `5.00`, `7.50`, `10.00`, `15.00`, or a custom value inside `5.00-15.00 THB`.

Price defines the universe. Evidence determines the opportunity. Price tier is disclosed for context but does not add positive score.

Top 5 means the five qualifying candidates with the highest final Penny Opportunity Scores from the complete supported scan universe. The final ranking score is the positive weighted factor score minus risk penalty, bounded between 0 and 100. Data Confidence and Data Completeness are qualification, explanation, and tie-breaking signals only; they are not added to the Opportunity Score.

Transparent Intelligence requires each displayed Penny score to reconcile from weighted factor contributions minus risk penalties. The score is accompanied by version metadata, missing evidence, confidence explanation, completeness explanation, and ranking rationale.

RC5A factor weights are Financial Intelligence `55%`, Business Intelligence `20%`, Liquidity `10%`, Technical Participation `5%`, Verified Catalyst Evidence `5%`, and Market Context `5%`. Risk penalties, confidence, and completeness remain separate.

## Catalyst Score

### Purpose

The Catalyst Score summarizes the quality and relevance of potential future catalysts.

### Meaning

It helps users understand whether identifiable events, policy shifts, products, contracts, approvals, industry cycles, or technology changes could affect the opportunity view.

### Interpretation

The score should be read with evidence quality and timing uncertainty. A possible catalyst with weak evidence should not create strong confidence.

### Philosophy

Catalysts must be evidence-supported. Hype is not a catalyst.

## Similarity Score

### Purpose

The Similarity Score is a future concept for comparing current companies with historical high-growth companies.

### Meaning

It may indicate whether a company shares measurable characteristics with historical multi-bagger companies, such as revenue acceleration, margin expansion, industry tailwind, innovation, execution, and competitive moat.

### Interpretation

Similarity does not predict the future. It helps users identify research questions.

### Philosophy

Historical patterns are useful only when limitations and differences are disclosed.

## Risk Penalty

### Purpose

Risk Penalty reduces opportunity quality when severe risks weaken the case.

### Meaning

It may reflect dilution, reverse splits, going concern warnings, excessive debt, negative cash flow, accounting issues, delisting risk, pump-and-dump characteristics, extremely low liquidity, or high spreads.

### Interpretation

An asset can have strong opportunity signals and still receive a lower final ranking because the risk penalty is severe.

### Philosophy

Risk is part of opportunity quality, not a separate footnote.

## Market Score

### Purpose

The Market Score summarizes broader market conditions relevant to the selected asset or market environment.

### Meaning

It helps users understand whether the broader environment is supportive, neutral, or risky.

### Interpretation

The Market Score should be read with macro context, index movement, currency, yields, volatility, and risk appetite where available.

### Philosophy

Market context matters. Good asset signals can weaken in poor market conditions.

## Market Adjusted Score

### Purpose

The Market Adjusted Score combines selected-asset evidence with relevant market context.

### Meaning

It helps prevent isolated asset analysis by incorporating the environment around the asset.

### Interpretation

A strong asset score with weak market context should be interpreted more cautiously than a strong asset score with supportive market context.

### Philosophy

Assets live inside markets. The score should reflect that relationship.

## Risk Score

### Purpose

The Risk Score summarizes potential downside, uncertainty, volatility, liquidity, and data limitations.

### Meaning

A higher risk score means the user should be more cautious, size positions carefully, or wait for stronger confirmation.

### Interpretation

Risk Score should be read with volatility, drawdown, data quality, event risk, and concentration.

### Philosophy

Risk is not a side note. It is part of every investment decision.

## Confidence Score

### Purpose

The Confidence Score indicates how much trust the system has in the available evidence.

### Meaning

Higher confidence means the evidence is more complete or consistent. Lower confidence means missing, stale, conflicting, or insufficient data.

### Interpretation

Low confidence should reduce the strength of any recommendation.

### Philosophy

Confidence should describe evidence quality, not emotional certainty.

Confidence is not expected return. Opportunity Score, Penny Opportunity Score, Catalyst Score, and Similarity Score must remain separate from Confidence.

## Interpretation Standard

Every score should explain:

- Purpose
- Meaning
- Evidence used
- What the score does not mean
- Missing data
- Risk considerations
- Confidence versus opportunity distinction

Scores should support investor judgment, not replace it.

## Trust Foundation Update

Scores must be interpreted as model outputs from declared evidence and declared weights. They must not be described as probability of profit, guaranteed return, investment quality, or personal suitability.

Confidence measures evidence reliability. Completeness measures evidence availability. Neither should be merged into the score meaning.
## Primary Corporate Evidence

For corporate assets, Financial Intelligence must be the largest single positive evidence domain. The default target is 55%, with a governed range of 45%-65%. Confidence and completeness remain separate from score construction.

## Business Intelligence Score

Business Intelligence is a secondary corporate evidence layer. It evaluates business quality, operating durability, business risk, and missing operational evidence using only available provider and Financial Intelligence fields.

The Business Intelligence Score remains separate from Financial Intelligence. It must not be merged into opportunity ranking weights until a Founder-approved methodology migration is versioned.

Current domains include business model quality, revenue model quality, competitive position context, pricing power evidence, capital allocation evidence, industry structure, cyclicality, regulatory risk, durability of growth, and business risk.

Unavailable evidence such as competitive advantage, customer concentration, supplier risk, management execution, and governance must remain unavailable when no verified provider evidence exists.
