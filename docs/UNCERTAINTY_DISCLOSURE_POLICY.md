# Uncertainty Disclosure Policy

## Purpose

Uncertainty Disclosure prevents the system from sounding more certain than the evidence supports.

## Principle

Uncertainty is product information, not a defect to hide.

Thai summary: ความไม่แน่นอนต้องแสดงอย่างตรงไปตรงมา ไม่สร้างความมั่นใจเกินหลักฐาน

## Implementation Rule

The platform must disclose:

- Missing evidence.
- Stale evidence.
- Conflicting evidence.
- Unsupported evidence.
- Provider failures.
- Incomplete financial periods.
- Insufficient historical coverage.
- Weak catalyst verification.
- Unknown risk status.
- Fallback use.

## Prohibited Behavior

- Using precise-looking scores to imply precise outcomes.
- Hiding small score gaps.
- Calling uncertain risk confirmed.
- Calling unavailable evidence neutral.
- Writing guaranteed or certain investment language.

## User-Facing Disclosure

Scores should use whole-number precision and explain that small differences may not be meaningful.

## Validation Requirement

Algorithms must publish uncertainty conditions and bilingual uncertainty statements before activation.

## Known Limitation

Current disclosure is evidence-status based. It does not quantify full model error or probabilistic forecast error.

## Future Governance Requirement

Future probability engines must disclose assumptions, conflict signals, and data-quality limitations alongside probabilities.
