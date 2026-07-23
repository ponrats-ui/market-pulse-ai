# Evidence Integrity Policy

## Purpose

Evidence Integrity ensures that every score can be traced to visible data, status, provider, and transformation context.

## Principle

Evidence must be auditable. Missing evidence must remain missing.

Thai summary: หลักฐานทุกชิ้นต้องตรวจสอบที่มาได้ และข้อมูลที่ขาดต้องแสดงว่าไม่พร้อมใช้งาน

## Implementation Rule

Evidence records should include:

- Evidence ID.
- Evidence type.
- Provider.
- Source timestamp.
- Retrieval timestamp.
- Freshness status.
- Availability status.
- Verification status.
- Supported factor.
- Candidate symbol.
- Transformation summary.
- Data limitations.

## Prohibited Behavior

- Treating inferred evidence as verified fact.
- Hiding provider failures.
- Hiding stale data.
- Collapsing conflicting evidence into a false single conclusion.
- Fabricating values to improve completeness.

## User-Facing Disclosure

When evidence is partial, stale, unsupported, unavailable, or failed, the UI should show that limitation directly.

## Validation Requirement

Algorithm validation must require evidence metadata fields and allowed evidence statuses.

## Known Limitation

Not every provider returns source timestamps. When a provider timestamp is unavailable, retrieval timestamp and provider limitation must remain visible.

## Future Governance Requirement

New providers must document freshness, verification limits, and failure behavior before being used in production scoring.
