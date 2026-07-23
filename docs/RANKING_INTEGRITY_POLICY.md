# Ranking Integrity Policy

## Purpose

Ranking Integrity protects users from hidden rank manipulation.

## Principle

If a ranked list is shown, users should know the declared ranking inputs and what cannot influence the order.

Thai summary: ลำดับผลลัพธ์ต้องอธิบายได้ และต้องไม่ถูกปรับด้วยเหตุผลที่ซ่อนอยู่

## Implementation Rule

The Penny Opportunity Scanner ranking policy is:

1. `penny_opportunity_score DESC`
2. `data_confidence DESC`
3. `data_completeness DESC`
4. `liquidity_score DESC`
5. `risk_penalty ASC`
6. `symbol ASC`

Manual overrides are not implemented.

## Prohibited Behavior

- Paid placement.
- Manual reordering without disclosure.
- Suppressing negative evidence.
- Hiding risk penalties.
- Ranking by popularity, clicks, watchlists, or social engagement.

## User-Facing Disclosure

Rank explanations must state that rank does not imply suitability or a buy recommendation.

## Validation Requirement

Backend validation must fail if declared ranking inputs diverge from the active ranking policy.

## Known Limitation

Current ranking integrity validation is strict for the Penny scanner. Future engines need explicit engine-specific ranking policies.

## Future Governance Requirement

Any future manual override capability must preserve the original algorithmic rank and disclose actor, timestamp, reason, and authorization.
