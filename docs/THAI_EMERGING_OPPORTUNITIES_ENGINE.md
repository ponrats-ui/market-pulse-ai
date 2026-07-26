# Thai Emerging Opportunities Engine

## Purpose

Thai Emerging Opportunities (Penny Stock) is the Thailand-specific opportunity engine for lower-priced equities.

The engine is not designed to find the cheapest shares. It is designed to find Thai listed companies whose available financial quality, business quality, liquidity, market participation, and risk evidence may justify deeper research.

## Core Principle

Price defines the universe.

Evidence determines the opportunity.

Low share price is not a positive score factor and does not imply quality, value, turnaround, or future performance.

## Thai Penny Universe

The default Thai scanning universe is:

- Market: Thailand
- Asset type: operating-company equity
- Maximum share price: `10.00 THB`
- Methodology: `Thai Emerging Opportunity`
- Version: `thai-emerging-opportunity-v1`

## Configurable Thresholds

Supported Thai maximum share price values:

- `5.00 THB`
- `7.50 THB`
- `10.00 THB` default
- `15.00 THB`
- Custom value between `5.00 THB` and `15.00 THB`

The active threshold is exposed in every scan under `universe` and `qualification.active_thresholds`.

## Price Tiers

| Tier | Range | Meaning |
| --- | --- | --- |
| Micro Penny | `0.01-2.00 THB` | Very high-risk lower-price universe |
| Classic Penny | `2.00-5.00 THB` | Traditional penny-style universe |
| Thai Emerging | `5.00-10.00 THB` | Default core Thai emerging opportunity range |
| Extended Emerging | `10.00-15.00 THB` | Optional extended universe when enabled |

Price tier is context only. It does not add opportunity score.

## Universe Filter

The filter sequence is:

1. Master Asset Registry
2. Thailand market classification
3. Operating-company equity classification
4. Active maximum share price threshold
5. Trading history requirement
6. Liquidity requirement
7. Financial Intelligence
8. Business Intelligence
9. Technical participation
10. Catalyst evidence where available
11. Risk penalties
12. Deterministic ranking

## Evidence Layers

RC5A consumes both:

- Financial Intelligence: primary positive evidence layer, `55%`
- Business Intelligence: secondary evidence layer, `20%`

Remaining positive factor weights:

- Liquidity: `10%`
- Technical participation: `5%`
- Verified catalyst evidence: `5%`
- Market context: `5%`

Risk penalties remain separate. Confidence and completeness remain separate.

## Turnaround Detection

Turnaround detection requires supportive evidence across financial quality, business quality, and growth. The engine does not classify a company as a turnaround because its share price is low.

## Value Trap Detection

Value trap detection is triggered when low price is accompanied by weak financial evidence, weak business evidence, or failed liquidity evidence.

When detected, the engine adds an explicit `value_trap_evidence` risk penalty.

## Emerging Quality Detection

Emerging quality detection requires supportive Financial Intelligence, supportive Business Intelligence, and acceptable liquidity.

This category is evidence-based. It is not caused by being in the `5.00-10.00 THB` tier.

## Explainable Opportunity Score

Each candidate exposes:

- Price tier
- Active universe filter
- Financial Intelligence report
- Business Intelligence report
- Opportunity setup
- Factor scores
- Factor contributions
- Risk penalties
- Missing evidence
- Confidence explanation
- Completeness explanation
- Score explanation

## API

Default:

```text
GET /api/opportunities/penny?market=TH
```

Custom Thai threshold:

```text
GET /api/opportunities/penny?market=TH&max_price=7.5
```

Methodology:

```text
GET /api/opportunities/penny/algorithm
```

## Limitations

Provider coverage can be incomplete or unavailable. Missing financial, business, catalyst, or liquidity data reduces confidence and completeness instead of being fabricated.

The score is a research ranking, not investment advice, not a forecast, and not a guarantee.
