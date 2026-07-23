# Algorithm Governance

Market Pulse AI algorithms are governed by versioned definitions and validation.

## Version Fields

- `methodology_version`
- `score_version`
- `policy_version`
- `config_version`

## Change Policy

Every scoring or methodology change must update:

- Algorithm definition
- Algorithm changelog
- Scoring framework
- Relevant tests
- User-facing explanation when meaning changes

## Activation Validation

An engine cannot register if required transparency metadata is missing or if documented factor weights drift from active scoring configuration.

## Trust Foundation Update

Algorithm governance now requires trust review before production activation. Any scoring or ranking change must validate:

- Neutrality exclusions.
- Evidence metadata.
- Uncertainty disclosure.
- Conflict-of-interest boundaries.
- Ranking integrity.
- Decision-boundary language.
## Financial Intelligence Governance

Any scoring change that changes the role or weight of Financial Intelligence must update `docs/PRIMARY_EVIDENCE_POLICY.md`, `docs/FINANCIAL_SCORING_FRAMEWORK.md`, and the affected algorithm documentation.
