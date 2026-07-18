# 08 Contributing

## Table of Contents

- [Purpose](#purpose)
- [Repository Setup](#repository-setup)
- [Coding Standards](#coding-standards)
- [Naming Conventions](#naming-conventions)
- [Commit Message Conventions](#commit-message-conventions)
- [Branch Naming](#branch-naming)
- [Review Expectations](#review-expectations)
- [Testing Expectations](#testing-expectations)
- [Documentation Expectations](#documentation-expectations)
- [Release Workflow](#release-workflow)
- [Current State](#current-state)
- [Future Work](#future-work)
- [Known Limitations](#known-limitations)
- [Related Documents](#related-documents)

## Purpose

This document explains how contributors should work on Market Pulse AI. It complements the root [Contributing](../CONTRIBUTING.md) file with project-specific engineering and release guidance.

## Repository Setup

Backend:

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
.\.venv\Scripts\python.exe -m pytest
```

Frontend:

```powershell
cd frontend
npm install
npm run build
```

Local integration:

```powershell
cd frontend
copy .env.example .env.local
```

Set `VITE_API_BASE_URL=http://127.0.0.1:8000` for local backend integration.

## Coding Standards

General:

- keep changes scoped
- prefer existing patterns
- avoid unrelated refactors
- preserve transparent unavailable states
- do not introduce fake production data
- keep error handling explicit

Frontend:

- use TypeScript types from `frontend/src/types`
- keep UI behavior responsive
- preserve Thai/English labels
- use accessible labels for controls
- avoid silent API failure paths

Backend:

- keep route handlers thin
- place business logic in services
- normalize provider responses
- include source and unavailable metadata where practical
- add focused pytest coverage for behavior changes

## Naming Conventions

Branches:

- `feature/<short-name>`
- `fix/<short-name>`
- `release/<version>`
- `hotfix/<short-name>`

Files:

- docs use clear numbered or topic-based names
- backend modules use snake_case
- frontend components use PascalCase where component files are separated
- utility functions use descriptive lowerCamelCase in TypeScript

## Commit Message Conventions

Preferred format:

```text
type(scope): short summary
```

Examples:

- `feat(portfolio): introduce PIA portfolio intelligence`
- `fix(frontend): consume production backend correctly`
- `docs: add documentation freeze v1.0 knowledge base`
- `chore(release): prepare v1.0.0-rc1`

Use direct, honest summaries. Do not combine unrelated changes in one commit.

## Branch Naming

Use release branches only for release hardening.

Examples:

- `release/v1.0.0-rc1`
- `fix/fs-300b1-batch-quote-abort`
- `feature/phase-e-premium-foundation`

Do not merge to `main`, push, deploy, or tag without explicit approval.

## Review Expectations

Reviewers should check:

- correctness
- data integrity
- no fabricated market data
- conservative AI wording
- CORS and environment safety
- mobile behavior
- tests
- documentation updates
- release impact

For release branches, treat visual changes and feature additions as suspicious unless explicitly approved.

## Testing Expectations

Minimum backend validation:

```powershell
cd backend
.\.venv\Scripts\python.exe -m pytest
```

Minimum frontend validation:

```powershell
cd frontend
npm run build
```

Browser validation is required for UI-affecting work.

API smoke should cover:

- `/health`
- `/api/watchlist`
- quote endpoint
- history endpoint
- asset search
- batch quotes
- analysis and risk where relevant

## Documentation Expectations

Update documentation when changing:

- architecture
- provider behavior
- release process
- product policy
- AI wording policy
- deployment configuration
- known limitations

Docs must distinguish current production behavior from future planned behavior.

## Release Workflow

1. Complete feature/fix work on scoped branch.
2. Validate locally.
3. Receive Founder acceptance where required.
4. Merge accepted work into `develop`.
5. Create release branch from accepted `develop`.
6. Perform release audit and documentation.
7. Merge to `main` only after explicit Founder approval.
8. Deploy only after approval.
9. Tag only after production verification.

## Current State

The current release candidate branch is `release/v1.0.0-rc1`. UI Freeze is accepted, and documentation-only work is permitted in this freeze sprint.

## Future Work

- add linting and formatting standards
- expand CI to include security and dependency audits
- document PR templates
- add automated release checklist tooling

## Known Limitations

- The project currently relies on manual Founder approval gates.
- Frontend tests may be limited; browser validation fills some gaps.
- Provider availability can affect local smoke tests.

## Related Documents

- [01 Product Vision](01_PRODUCT_VISION.md)
- [02 System Architecture](02_SYSTEM_ARCHITECTURE.md)
- [04 System Decisions](04_SYSTEM_DECISIONS.md)
- [05 Release Engineering](05_RELEASE_ENGINEERING.md)
- [07 Glossary](07_GLOSSARY.md)
- [Root Contributing Guide](../CONTRIBUTING.md)
