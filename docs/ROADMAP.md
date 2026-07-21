# Roadmap

## Table of Contents

- [Roadmap Purpose](#roadmap-purpose)
- [Completed](#completed)
- [Current](#current)
- [Future](#future)
- [After Version 1](#after-version-1)
- [Development Principles](#development-principles)
- [Definition of Progress](#definition-of-progress)

## Roadmap Purpose

This roadmap defines the long-term product direction for Market Pulse AI. It should guide future prompts, commits, reviews, and release decisions without locking the team into obsolete sprint details.

The roadmap is intentionally phase-based. Each phase should improve reliability, explainability, usability, or production readiness without compromising the Zero Mock Policy.

## Completed

### Phase A: Engineering Foundation

Focus: establish the technical base for a production-capable investment intelligence product.

Completed outcomes:

- React, Vite, TypeScript frontend foundation.
- FastAPI backend foundation.
- Provider abstraction for real market data.
- Cloudflare Pages frontend deployment path.
- Render backend deployment path.
- Git and documentation workflow.
- Zero Mock policy established as a product rule.

### Phase B: UI Polish RC1

Focus: make the dashboard feel credible, readable, and production-quality.

Completed outcomes:

- Professional dashboard visual direction.
- Thai-first localization improvements.
- Company logo support with safe fallbacks.
- Knowledge Center and explainability surfaces.
- Opportunity Score explanations.
- Market Mood and market context improvements.
- Responsive dashboard polish.
- Founder UI freeze and Phase B checkpoint.

## Current

### Phase C: UX & Explainability

Focus: improve how users understand scores, AI reasoning, market context, and selected-asset analysis.

Current priorities:

- Clearer explanation for Market and Asset Assessment.
- Better compact presentation without losing information.
- Safer visual hierarchy for executive decision support.
- Consistent contextual explanations for AI and scoring.
- Continued production verification after each UI polish prompt.

## Future

### Phase D: Production Hardening

Focus: improve release confidence and operational safety.

Expected outcomes:

- Stronger error handling.
- Provider timeout and degradation policy review.
- Performance audits.
- Accessibility audits.
- Security and dependency audits.
- Production smoke-test discipline.

### Phase E: Founder Acceptance Test

Focus: final founder review before release candidate status.

Expected outcomes:

- Full walkthrough of every major workflow.
- Production-only verification.
- Console and network validation.
- Responsive validation.
- Known limitations review.

### Phase F: Release Candidate

Focus: prepare a controlled release candidate.

Expected outcomes:

- Release notes.
- Rollback plan.
- Deployment checklist.
- Version confirmation.
- Final release decision.

### Phase G: Public Beta

Focus: expose the product to broader real-user feedback while preserving safety.

Expected outcomes:

- Feedback collection workflow.
- Issue triage process.
- Monitoring and operational review.
- Documentation for early users.

### Phase H: Version 1.0

Focus: first stable public production release.

Expected outcomes:

- Stable production frontend and backend.
- Public documentation.
- Clear legal and educational disclaimers.
- Known limitations documented.
- Founder-approved release tag.

## After Version 1

Long-term product expansion areas:

- **Portfolio Intelligence:** portfolio risk, concentration, allocation, performance, and educational coaching.
- **Alert System:** intelligent alerts, morning briefs, evening wraps, and saved monitoring rules.
- **Cross-Market Intelligence:** relationships between assets, sectors, macro variables, commodities, currencies, and yields.
- **Macro Intelligence:** central bank, inflation, currency, liquidity, and economic regime context.
- **Personal AI:** user-specific research preferences, portfolio-aware summaries, and explainable watchlist monitoring.
- **Strategy Lab:** educational scenario analysis, hypothesis testing, and transparent rules-based research workflows.

## Development Principles

Future roadmap work should follow this operating rhythm:

```text
One Prompt
↓
One Commit
↓
One Deploy
↓
Founder Review
↓
Approve
```

Each phase must preserve:

- Zero Mock Policy.
- Production as Source of Truth.
- Explainability above complexity.
- No black-box AI where transparent reasoning is possible.
- No release approval based on localhost alone.

## Definition of Progress

A roadmap item is complete only when:

- The implementation or documentation is committed.
- The change is validated in the appropriate environment.
- Production behavior is verified when the task affects production UI or behavior.
- Known limitations are documented honestly.
- The founder can review the result without hidden assumptions.
