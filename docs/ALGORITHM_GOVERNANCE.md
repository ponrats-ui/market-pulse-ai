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
