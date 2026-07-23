# AI Confidence Model

## Table of Contents

- [Purpose](#purpose)
- [Confidence Is Not Expected Return](#confidence-is-not-expected-return)
- [What Confidence Measures](#what-confidence-measures)
- [Confidence Inputs](#confidence-inputs)
- [Low Confidence Behavior](#low-confidence-behavior)
- [Explainability Requirements](#explainability-requirements)

## Purpose

The AI Confidence Model defines how Market Pulse AI should communicate certainty and uncertainty in opportunity discovery and investment intelligence.

Confidence measures how reliable the available evidence is.

## Confidence Is Not Expected Return

Opportunity Score must not equal Confidence.

A high Opportunity Score may indicate strong signals, but Confidence asks whether the evidence is complete, consistent, recent, and trustworthy.

A high-upside idea can have low confidence. A stable company can have moderate opportunity but high confidence. These concepts must remain separate.

## What Confidence Measures

Confidence may conceptually measure:

- Data completeness
- Data freshness
- Provider reliability
- Signal agreement
- Signal conflict
- Historical coverage
- Fundamental availability
- News and catalyst evidence
- Risk evidence quality
- Model applicability to asset class

## Confidence Inputs

### Evidence Completeness

More complete evidence supports higher confidence.

### Evidence Consistency

Signals that agree across financial, technical, catalyst, narrative, and risk dimensions may support higher confidence.

### Evidence Freshness

Stale data should reduce confidence.

### Provider Quality

Provider outages, partial coverage, or conflicting sources should reduce confidence.

### Asset-Class Fit

The model must disclose when an evidence type does not apply to the selected asset class.

## Low Confidence Behavior

When confidence is low, the system should:

- Reduce recommendation strength
- Make missing data visible
- Avoid strong language
- Explain what evidence is needed
- Encourage further research
- Avoid implying certainty

## Explainability Requirements

Every confidence output should explain:

- Why confidence is high, medium, or low
- Which evidence is strong
- Which evidence is missing
- Which signals conflict
- Whether data is stale or provider-dependent
- What would increase or decrease confidence
