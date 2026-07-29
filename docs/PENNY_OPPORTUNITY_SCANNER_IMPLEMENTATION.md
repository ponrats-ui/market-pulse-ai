# Penny Opportunity Scanner Implementation

## Purpose

The Penny Opportunity Scanner adds an evidence-first discovery path for low-priced equities. It is designed to identify candidates that may deserve further research, not to recommend buying or selling.

Penny stock is treated as a category, not an investment thesis. Low price alone cannot create a high ranking.

## Architecture

The scanner is the first registered engine on the shared Opportunity Engine Framework documented in `docs/OPPORTUNITY_ENGINE_FRAMEWORK.md`.

It remains exposed through:

`GET /api/opportunities/penny?market=&limit=&language=`

Top 5 means the five qualifying candidates with the highest final Penny Opportunity Scores from the provider-safe bounded scan universe.

The Penny Opportunity universe is rescanned and reranked by an explicit bounded snapshot producer. Production may run the producer manually from Render Shell or through a future scheduler, but public user requests must only read the latest published snapshot.

The implementation is intentionally memory-conscious:

- It starts from lightweight Master Asset Registry metadata.
- It scans a provider-safe bounded TH/US lightweight equity universe before final ranking.
- It processes registry candidates in bounded batches and releases intermediate provider quote maps after each batch.
- It normalizes provider symbols before market data calls.
- It excludes unsupported Thai foreign-board or special-board variants before provider calls.
- It fetches quote data before history or news.
- It skips expensive history calls for candidates that fail cheap hard filters.
- It keeps only compact scoring and evidence payloads in the response.

## Classification Policy

Policies are versioned through `thai-emerging-policy-v1` with configuration version `thai-emerging-config-v1`.

Thailand:

- Thai Emerging Opportunities default universe: price less than or equal to `10.00 THB`.
- Configurable threshold: `5.00`, `7.50`, `10.00`, `15.00`, or a custom value from `5.00` to `15.00 THB`.
- Price tiers: Micro Penny, Classic Penny, Thai Emerging, and Extended Emerging.

United States:

- Penny stock: price below 5 USD.
- Low-priced small cap: price above or equal to 5 USD and less than or equal to 10 USD.

Thresholds and factor weights are centralized in the Penny engine definition rather than scattered through the application.

Price defines the universe. Evidence determines the opportunity.

## Eligibility Rules

Every candidate is evaluated with real provider-returned data where available. The scanner verifies:

- Equity asset class.
- Supported market.
- Provider symbol.
- Valid current price.
- Market-aware price classification.
- Trading history availability.
- Liquidity.
- Data freshness.
- Provider attribution.

Unsupported or unavailable conditions are surfaced as `UNKNOWN` where data is absent.

## Hard Disqualification Rules

A candidate cannot enter the Top 5 when confirmed evidence shows:

- Invalid or missing price.
- Price outside the market policy.
- Non-equity instrument.
- Insufficient trading history.
- Insufficient liquidity.
- Data completeness below the configured minimum.
- Confirmed critical risk flag.

The scanner does not infer severe risk from missing data alone.

## Scoring Factors

The Penny Opportunity Score is a bounded 0-100 heuristic. It combines:

- Financial Intelligence score.
- Business Intelligence score.
- Liquidity score.
- Technical and momentum score.
- Catalyst evidence score when a live provider supplies verified evidence.
- Market context score.
- Risk penalty.

The score is not a probability of profit, expected return, or multi-bagger prediction.

RC5A uses the target evidence mix documented in the Product Bible: Financial Intelligence `55%`, Business Intelligence `20%`, liquidity `10%`, technical participation `5%`, catalyst evidence `5%`, and market context `5%`. Risk penalties remain separate.

Final ranking sorts by `penny_opportunity_score DESC`. Tie-breakers are deterministic and applied only when final scores match:

1. `data_confidence DESC`
2. `data_completeness DESC`
3. `liquidity_score DESC`
4. lower `risk_penalty`
5. `symbol ASC`

Data Confidence and Data Completeness are not added to the Penny Opportunity Score.

## Hourly Scan Snapshot

The backend owns snapshot publication through the RC5A.2 producer command documented in `docs/RC5A2_PENNY_SNAPSHOT_PRODUCER.md`. The browser only polls for the latest published snapshot and does not trigger a full market scan.

The current Render configuration runs a single `uvicorn app.main:app --host 0.0.0.0 --port $PORT` process. Under that topology the in-process scheduler has one active owner per service instance and uses an execution lock to prevent overlapping scans. If deployment later adds multiple workers or replicas, this scheduler should move to an external cron-protected refresh endpoint or a dedicated worker.

Each completed scan publishes a compact persisted snapshot containing scan timing, engine metadata, methodology version, score version, policy version, config version, qualification funnel counts, Top 5 items, provider status, limitations, duration, memory diagnostics, batch diagnostics, and status.

If a new scan fails, the API keeps serving the latest successful snapshot, marks it `stale`, and includes the failed scan timestamp and failure stage. If no successful snapshot exists yet, the endpoint returns `not_ready`, `scan_in_progress`, or `failed` instead of triggering a synchronous full-universe scan inside the user request.

Custom threshold requests such as `max_price=7.5` are served from the latest snapshot and filtered transparently. If the requested threshold is above the latest published scan threshold, the response is marked `partial` and discloses that extended candidates require a future scheduled bounded scan.

## Provider Symbol Mapping

The scanner uses the Data Hub provider symbol mapper documented in `docs/PROVIDER_SYMBOL_MAPPING.md`.

Thai common shares are normalized to Yahoo Finance `.BK` symbols:

- `AOT` -> `AOT.BK`
- `AOT.BK` -> `AOT.BK`
- `PTT` -> `PTT.BK`
- `PTT.BK` -> `PTT.BK`

Foreign-board variants are excluded before provider calls:

- `AOT-F` -> excluded
- `AOT-F.BK` -> excluded
- `ACAP-F.BK` -> excluded

The exclusion is recorded as scanner diagnostics, not as provider failure.

## Scan Safety

Production scans are bounded by:

- `PENNY_SCAN_MAX_SYMBOLS`
- `PENNY_SCAN_MAX_PROVIDER_BATCH`
- `PENNY_SCAN_DEADLINE_SECONDS`
- `PENNY_SCAN_MAX_WORKERS`
- a scan execution lock
- persisted file-backed snapshots under `OPPORTUNITY_SNAPSHOT_DIR`

The `/health` endpoint does not trigger provider work. The user-facing penny endpoint serves published snapshots and transparent unavailable states.

## Risk Penalty

Risk flags are explicit and structured. Each risk includes:

- Code.
- Severity.
- Status.
- Penalty.
- Evidence.
- Timestamp.
- Thai and English explanation.

Critical confirmed risks disqualify candidates. Lower-severity risks reduce the final score.

## Data Confidence

Data Confidence is separate from Penny Opportunity Score. It measures how much reliable evidence was available to support the ranking.

Missing fundamentals, missing verified catalysts, short history, stale timestamps, and unknown risk checks reduce confidence.

## Missing Data Behavior

Missing data is never replaced with synthetic, average, simulated, placeholder, or fabricated values. The frontend displays missing data and unavailable catalyst evidence directly on each card.

## API Contract

The endpoint returns:

- `status`
- `category`
- `methodology_version`
- `score_version`
- `engine`
- `policy_version`
- `configuration_version`
- `generated_at`
- `scan`
- `markets`
- `universe`
- `warning`
- `qualification`
- `items`
- `limitations`
- `provider_status`
- `disclaimer`

Each item contains rank, symbol, market, exchange, currency, classification, price, scores, risk flags, missing data, catalyst evidence, explanation, timestamp, and provider attribution.

Transparent Intelligence endpoints:

- `GET /api/opportunities/penny/algorithm` returns the cacheable Penny Algorithm Card.
- `GET /api/opportunities/penny/explain/{symbol}` returns snapshot-derived score reconciliation and ranking explanation.
- `GET /api/opportunities/penny/why-not/{symbol}` returns snapshot-derived exclusion status without starting a scan.

Candidate explanations include raw positive score, factor contributions, total risk penalty, final score reconciliation, confidence explanation, completeness explanation, and ranking explanation.

## UI Behavior

The frontend adds a Penny Opportunities section inside the existing Today's Opportunities area. Cards are fully clickable and use the existing selected-asset state path:

1. Select asset.
2. Scroll to Selected Asset.
3. Refresh quote, chart, AI, risk, financials, sentiment, and news panels.
4. Show loading states instead of stale previous-asset data.

The warning is visible without opening a tooltip.

The UI displays backend scan metadata: Last scanned, Next scan, Scans every hour, Universe scanned, Qualified candidates, and Data may be stale.

## Provider Limitations

The first implementation uses the current provider stack. Verified catalysts are only shown when a configured provider returns real news or event evidence. If no live catalyst provider is available, the UI says so.

## Testing

Backend coverage includes classification, scoring boundaries, missing data, risk penalties, deterministic ranking, provider failure isolation, endpoint wiring, and memory-sensitive shortlist behavior.

Frontend validation is performed through TypeScript production build and browser review.

## Known Limitations

- The methodology is an initial transparent ranking heuristic, not a statistically validated investment model.
- Candidate pools are intentionally bounded to protect production memory.
- Catalyst scoring remains limited until stronger live event providers are configured.
- Fewer than five results may appear when fewer candidates pass quality and risk filters.

## Future Validation

Future work should validate the methodology against historical outcomes, add stronger provider-backed filings and events, and document any scoring changes in `docs/SCORING_FRAMEWORK.md`.

## Founder Verification Checklist

Founder Acceptance remains pending. Only the Founder may mark these items as PASS.

Desktop:

- [ ] Penny Opportunities category is visible.
- [ ] Important warning is visible.
- [ ] Results use real data.
- [ ] No fabricated catalyst is shown.
- [ ] Scores have explanations.
- [ ] Risks are displayed beside opportunities.
- [ ] Missing data is explicit.
- [ ] Full card is clickable.
- [ ] Selected asset updates correctly.
- [ ] Dependent panels do not show stale data.
- [ ] Fewer than five qualifying results is handled honestly.

Mobile:

- [ ] Same candidate universe as desktop.
- [ ] No clipping or hidden cards.
- [ ] Warning remains readable.
- [ ] Touch interaction works.
- [ ] Asset selection updates all panels.
- [ ] Loading states prevent stale information.
- [ ] Thai and English layouts remain usable.

Production:

- [ ] Endpoint responds successfully.
- [ ] Memory remains below service limit.
- [ ] No restart during founder test.
- [ ] Provider failures degrade gracefully.
- [ ] Logs contain no secrets.
- [ ] Results expose timestamps and attribution.
