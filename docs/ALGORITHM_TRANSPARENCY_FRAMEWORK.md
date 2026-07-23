# Algorithm Transparency Framework

Market Pulse AI uses Glass Box Investment Intelligence: every active opportunity score must be explainable, versioned, and reproducible from structured evidence.

## Principles

- Evidence before score.
- Explanation beside score.
- Risk beside opportunity.
- Confidence separate from opportunity.
- Missing data remains visible.
- No score is enabled without an Algorithm Card.

## Required Algorithm Contract

Every enabled Opportunity Engine must provide:

- Algorithm identity and versions
- Objective and investment hypothesis
- Universe and eligibility methodology
- Active factor definitions and weights
- Factor rationale in Thai and English
- Risk model and risk rationale
- Score formula
- Confidence methodology
- Completeness methodology
- Ranking methodology
- Limitations and non-claims
- Change history and change impact

## Activation Rule

No Algorithm Card means no production engine activation. The backend validates the Penny Algorithm Definition before registering the Penny engine.

## Candidate Explanations

Candidate explanations are deterministic and derived from:

- Factor contributions
- Risk penalties
- Missing-data fields
- Data confidence
- Data completeness
- Ranking position and score gaps

No LLM call is used during hourly scans to explain deterministic calculations.
