# Trust Foundation

## Purpose

Market Pulse AI must earn user trust through evidence, neutrality, and intellectual honesty. Trust is not a visual claim; it is a product contract enforced through algorithm metadata, API responses, user-facing disclosure, tests, and documentation.

## Principle

The platform provides research support. It does not decide for the user, promise outcomes, or present rankings as personal financial advice.

Thai summary: ระบบช่วยวิเคราะห์เพื่อการศึกษา ไม่ตัดสินใจแทนผู้ใช้ และไม่รับประกันผลตอบแทน

## Implementation Rule

Every opportunity engine must expose a trust policy version, evidence requirements, neutrality declarations, uncertainty rules, conflict-of-interest rules, ranking integrity rules, provider limitations, and a decision boundary.

The Penny Opportunity Scanner currently exposes `trust-policy-v1`.

## Prohibited Behavior

- Hiding missing or failed evidence.
- Labeling scores as probability of profit.
- Allowing advertising, sponsorship, affiliate relationships, popularity, user engagement, developer preference, or Founder preference to affect rankings.
- Presenting AI output as a command to buy or sell.
- Replacing unavailable data with fabricated values.

## User-Facing Disclosure

User-facing panels must state that scores are evidence-based heuristics, not recommendations or guarantees. Where compact space is needed, use the compact trust disclosure from the API rather than inventing new language.

## Validation Requirement

Backend validation must fail if a supported algorithm lacks a trust disclosure or if any commercial, engagement, popularity, or editorial influence is declared active.

Frontend builds must continue to show trust disclosure without changing scoring logic.

## Known Limitation

Trust metadata currently applies first to the Penny Opportunity Scanner. Future opportunity engines must adopt the same contract before production activation.

## Future Governance Requirement

Every scoring, ranking, provider, or AI-output change must update the relevant trust document and tests before release.
