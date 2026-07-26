# Business Intelligence Engine

## Purpose

The Business Intelligence Engine evaluates the quality and durability of an operating business using available evidence.

Financial Intelligence answers: what do the reported numbers show?

Business Intelligence answers: why might those numbers be sustainable, improving, weakening, or vulnerable?

## Scope

RC5 introduces Business Intelligence as a separate evidence layer for operating companies. It does not replace Financial Intelligence and it does not change opportunity ranking weights.

The first implementation exposes:

- `GET /api/intelligence/business/{symbol}`
- `GET /api/intelligence/business/methodology`

## Evidence Standard

The engine uses only available provider fields and Financial Intelligence output. Missing operational evidence remains unavailable.

The engine must not fabricate:

- Competitive advantage
- Market share
- Customer loyalty
- Pricing power
- Management quality
- Governance quality
- Supplier dependency
- Customer concentration

## Output Contract

The report includes:

- `business_intelligence_score`
- `business_quality_score`
- `business_risk`
- `business_evidence`
- `missing_business_evidence`
- `business_confidence`
- `business_completeness`
- `limitations`
- `evidence_based_narrative`
- `financial_intelligence_reference`
- `versions`

## Relationship to Financial Intelligence

Financial Intelligence remains the primary corporate evidence layer. Business Intelligence is a secondary interpretation layer that explains operating durability and vulnerability.

Business Intelligence is not merged into opportunity scoring until a Founder-approved methodology migration is versioned.

## Asset Boundaries

The engine is applicable to operating companies. It returns transparent `not_applicable` or `unsupported` states for assets that require different evidence models, including funds, crypto, commodities, indices, and sector-specific financial institutions.

## Versioning

Current versions:

- Methodology: `business-intelligence-v1`
- Scoring: `business-scoring-v1`
- Policy: `business-policy-v1`
- Evidence: `business-evidence-v1`

## Limitations

Business Intelligence is limited by provider field coverage. A low score, high score, or unavailable state is not investment advice.

