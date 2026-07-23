# Opportunity Engine Framework

## Purpose

The Opportunity Engine Framework is the reusable foundation for Market Pulse AI opportunity discovery categories.

It separates shared scan infrastructure from engine-specific methodology so future engines can reuse scheduling, locking, snapshot publication, ranking, confidence, completeness, and API delivery without rebuilding the platform.

The first registered production engine is:

- `penny-opportunity`

Future engines such as Dividend, Value, Growth, Momentum, ETF, Crypto, Hidden Gem, AI Picks, and Global Opportunities must plug into the same lifecycle before production activation.

## Engine Lifecycle

Every opportunity engine follows the same conceptual lifecycle:

1. Provider data
2. Universe discovery
3. Cheap pre-filter
4. Eligibility evaluation
5. Bounded candidate shortlist
6. Rich data acquisition
7. Factor scoring
8. Risk evaluation
9. Final score
10. Data confidence and completeness
11. Deterministic ranking
12. Immutable snapshot
13. API delivery
14. Web and mobile rendering

The orchestrator and shared contracts must not contain Penny-specific price thresholds, warning text, or factor assumptions.

## Shared Responsibilities

Shared infrastructure owns:

- Engine definitions
- Engine registry
- Ranking helpers
- Snapshot storage
- Atomic snapshot publication
- Failure fallback
- Scheduler shell
- Overlap prevention
- Version metadata exposure
- Compact API metadata
- Testable contracts

## Engine-Specific Responsibilities

Each engine owns:

- Universe policy
- Supported markets
- Eligibility rules
- Factor weights
- Factor scoring methodology
- Risk policy
- Score thresholds
- Completeness thresholds
- Confidence thresholds
- Warning text
- Explanations
- Category-specific API item fields

## Engine Definition

Each engine exposes an `OpportunityEngineDefinition` with:

- `engine_id`
- `category`
- `display_name`
- `methodology_version`
- `score_version`
- `policy_version`
- `config_version`
- `supported_markets`
- `schedule_frequency_minutes`
- `maximum_results`
- `shortlist_limit`
- `minimum_score`
- `minimum_confidence`
- `minimum_completeness`
- `freshness_policy`
- `factor_weights`
- `risk_policy`
- `tie_breaker_policy`

For RC1, only `penny-opportunity` is enabled.

## Registry

The registry provides:

- `register_engine()`
- `get_engine()`
- `get_engine_definition()`
- `list_enabled_engines()`

Unknown engines fail safely with a `KeyError`. Future engines must register a runtime only after their methodology, transparency, tests, and API contract are complete.

## Scheduler

The shared scheduler starts one daemon thread per enabled engine and prevents duplicate scheduler threads for the same engine ID.

The Penny engine runs every 60 minutes. The browser never triggers a full universe scan. The browser only fetches the latest compact snapshot.

## Current Deployment Safety

The current Render command runs one `uvicorn app.main:app --host 0.0.0.0 --port $PORT` process. Under this topology, the in-process scheduler has one active owner for the service instance and an engine-specific execution lock prevents overlapping Penny scans.

If the backend later uses multiple workers, multiple instances, or horizontal scaling, the scheduler must move to a dedicated worker, Render cron job, or protected external trigger backed by a shared lock.

## Snapshot Architecture

Snapshots are stored in a shared in-memory `OpportunitySnapshotStore`.

Current storage decision:

- In-memory storage is acceptable for the current single-instance backend.
- Loss on restart is acceptable because the API can regenerate the snapshot.
- The limitation is documented and should be upgraded before multi-instance deployment.

Upgrade path:

- Existing database if provisioned.
- Redis or another shared cache if already approved.
- File-backed JSON only if runtime filesystem behavior is explicitly validated.

## Atomic Publication

The engine builds a complete snapshot first. The store publishes a deep copy only after scan, scoring, ranking, and serialization have succeeded.

When a scan fails:

- The previous successful snapshot remains available.
- Failure metadata is recorded separately.
- The response can be marked `partial` or stale.
- Empty fabricated replacement results are never generated.

## Concurrency Control

The Penny engine uses a non-blocking execution lock. If a scan is already active:

- A second scan does not start.
- The latest valid snapshot continues to be served.
- If no successful snapshot exists, the API returns `running` or `unavailable` honestly.

## Ranking

Shared ranking supports deterministic score-first ordering. Penny ranking uses:

1. `penny_opportunity_score DESC`
2. `data_confidence DESC`
3. `data_completeness DESC`
4. `liquidity_score DESC`
5. `risk_penalty ASC`
6. `symbol ASC`

Confidence and completeness are not added to the final score.

## API Delivery

`GET /api/opportunities/penny` is preserved.

The response now includes both legacy fields and shared engine metadata:

- `engine`
- `scan.snapshot_id`
- `scan.scan_started_at`
- `scan.scan_completed_at`
- `scan.last_successful_scan_at`
- `scan.next_scan_at`
- `scan.frequency_minutes`
- `qualification.prefiltered_count`
- `qualification.result_count`

## Frontend Delivery

The frontend reads the latest snapshot and displays:

- Last scanned
- Next scan
- Scans every hour
- Universe scanned
- Qualified candidates
- Data may be stale

Frontend polling must never initiate a full market scan.

## Resource Strategy

The framework protects server resources through:

- One hourly scan per enabled engine
- One shared snapshot for all users
- No per-user universe scans
- Quote-first filtering
- Bounded concurrency
- Compact snapshots
- Candidate-level failure isolation
- No raw provider payload retention in API responses

## Observability

Snapshots and provider status expose:

- Engine ID
- Snapshot ID
- Scan start and completion
- Scan duration
- Universe size
- Eligible and qualified counts
- Failed candidate count
- Provider failures
- Skipped overlapping scans
- Failure stage

Logs and responses must not include secrets, tokens, or raw provider payloads.

## Known Limitations

- In-memory snapshots are not shared across multiple backend instances.
- The initial scheduler is safe only for the current single-process Render topology.
- Batch quote availability depends on Yahoo Finance provider behavior.
- Catalyst quality remains limited by currently configured providers.

## Future Engine Onboarding

To add a future engine:

1. Create the engine policy and version identifiers.
2. Define supported markets and universe discovery.
3. Define eligibility rules.
4. Define factor scorers and weights.
5. Define risk policy and penalties.
6. Define confidence and completeness thresholds.
7. Register the engine runtime.
8. Add or map an API route.
9. Add frontend category rendering.
10. Add engine tests, snapshot tests, and API tests.
11. Enable scheduler entry after validation.

No future engine should be enabled without an Algorithm Card and explainability coverage.

## Transparent Intelligence

Every enabled engine must also pass Algorithm Transparency validation. The Penny engine validates its Algorithm Definition before registration. If objective, hypothesis, factor labels, factor rationale, version metadata, limitations, non-claims, or factor-weight consistency are missing, the engine must not activate.

Reference documents:

- `docs/ALGORITHM_TRANSPARENCY_FRAMEWORK.md`
- `docs/ALGORITHM_LAB.md`
- `docs/WHY_THIS_EXPLANATION.md`
- `docs/WHY_NOT_EXPLANATION.md`
- `docs/ALGORITHM_GOVERNANCE.md`
