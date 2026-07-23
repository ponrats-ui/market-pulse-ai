# Penny Opportunity Algorithm

## Purpose

The Penny Opportunity Algorithm discovers low-priced equities supported by evidence of financial survivability, growth, liquidity, market participation, and verified catalysts. Material risks are deducted transparently.

Low share price alone is not evidence of investment opportunity.

## Hypothesis

A low-priced security may deserve further research only when multiple independent evidence groups agree.

## Active Factors

- Liquidity
- Financial Health
- Growth
- Technical Strength
- Catalyst Evidence
- Market Context

Weights are sourced from the active Penny engine configuration and exposed by `GET /api/opportunities/penny/algorithm`.

## Score Formula

Weighted positive factor contributions minus evidence-supported risk penalties, bounded 0-100.

The score is not probability of profit, expected return, buy probability, or prediction confidence.

## Ranking

Primary rank is final Penny Opportunity Score descending. Tie-breakers are data confidence, data completeness, liquidity score, lower risk penalty, and symbol.

## Missing Data

Missing data reduces confidence or completeness. It is not replaced with synthetic values.

## Non-Claims

- Not a buy or sell recommendation.
- Does not predict future returns.
- High rank does not guarantee price appreciation.
- Provider data may be delayed, incomplete, or incorrect.

## Trust Foundation

The Penny Opportunity Algorithm now publishes `trust-policy-v1` with:

- Evidence integrity metadata.
- Algorithm neutrality declarations.
- Uncertainty disclosure.
- Conflict-of-interest safeguards.
- Ranking integrity policy.
- Decision-boundary disclosure.

The Penny Opportunity Score is a ranking heuristic over available evidence. It is not a probability of profit, not a personal suitability score, and not a buy or sell recommendation.
