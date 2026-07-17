# FS-300B.1 Batch Quote Abort Lifecycle Fix

## Reproduced Symptom

After a normal browser refresh, the dashboard could log repeated errors like:

- `AbortError: signal is aborted without reason`
- `Market Pulse API request failed for /api/assets/quotes?symbols=...`
- `Failed to load opportunity scan`

When this happened, Today's Opportunities showed `Not enough real data to rank opportunities` even though single-asset quote endpoints still worked.

## Verified Root Cause

The batch quote request used the same 20 second timeout as small single-resource requests.

Direct timing of the local batch endpoint showed:

- Endpoint: `GET /api/assets/quotes?symbols=AAPL,MSFT,NVDA,AMD,TSM,SPY,QQQ,TLT,VNQ,SOXX,GLD,SLV,PTT.BK,AOT.BK,SCB.BK,KBANK.BK,TTB.BK,CPALL.BK,DELTA.BK,ADVANC.BK`
- Result: HTTP 200
- Duration: about 25.8 seconds
- Items: 20
- Source: `yfinance`

Because the frontend timeout was 20 seconds, the frontend aborted a valid but slow batch quote request. The catch path then logged the abort as a real API failure, and the opportunity scan did not complete.

## Files Changed

- `frontend/src/lib/api.ts`
- `frontend/src/main.tsx`
- `docs/FS-300B1-BATCH-QUOTE-ABORT-FIX.md`

## Fix Applied

### API Request Classification

`frontend/src/lib/api.ts` now distinguishes:

- Intentional cancellation: throws `ApiRequestCanceledError` without logging as a Market Pulse API failure.
- Real timeout: logs `Market Pulse API request timed out...` and throws a timeout-specific error.
- Network/backend failure: preserves existing API failure logging.
- Unexpected error: preserves diagnostics.

### Batch Quote Timeout

Batch quote requests now use a dedicated timeout:

- Normal request timeout: `20,000 ms`
- Batch quotes timeout: `120,000 ms`

The timeout protection remains in place; it was not removed.

### Effect-Owned Request Lifecycle

`frontend/src/main.tsx` now gives the opportunity scan and watchlist quote loaders their own `AbortController`.

Cleanup aborts only the request created by that effect invocation. Intentional cleanup cancellation is ignored by callers and does not show as a dashboard failure.

The opportunity scan also avoids overlapping batch quote requests by skipping a new scan while one is already in flight.

## StrictMode Behavior

React development remounts or normal unmount cleanup can cancel an in-flight request. That cancellation is now treated as intentional and is not logged as an application error.

The subsequent active request uses a fresh `AbortController` and can complete normally.

## Browser Validation

Local browser validation was run at `http://127.0.0.1:5173`.

After increasing the batch timeout to 120 seconds:

| Refresh | Result |
| --- | --- |
| Refresh 1 | 10 opportunity cards rendered; no opportunity AbortError observed. |
| Refresh 2 | 10 opportunity cards rendered; no opportunity AbortError observed. |
| Refresh 3 | 10 opportunity cards rendered; no opportunity AbortError observed. |

Observed opportunity scan completion times in the final browser run were about 8-10 seconds because provider/cache state was warm.

## Network Evidence

Direct endpoint evidence:

- Batch quote endpoint returned HTTP 200.
- Response contained 20 items.
- Provider source was `yfinance`.
- Cold/local direct request duration was about 25.8 seconds, which exceeded the old 20 second timeout and justified a dedicated batch timeout.

The browser automation environment did not expose reliable resource timing entries for the cross-origin API request, so Network-tab evidence is based on direct endpoint timing plus rendered opportunity-card completion.

## Console Result

Final browser validation showed no new repeated `AbortError` for the opportunity scan.

Limitation: the browser automation log retained older timeout entries from the earlier failed 60 second validation attempt and could not be cleared by the tool. Those retained entries referenced the previous `60000ms` timeout and were not produced by the final 120 second validation.

## Regression Tests

No frontend unit test framework is currently configured in `frontend/package.json`; it has build, dev, and preview scripts only. Therefore, no focused frontend unit tests were added in this micro patch.

Manual/runtime validation covered:

- Fresh request does not inherit an aborted signal.
- Effect cleanup cancellation is ignored as intentional.
- Batch quote scan completes after refresh.
- Real timeout handling remains explicit.

## Remaining Limitations

- Very slow provider conditions can still hit the 120 second batch timeout and will be reported as a real timeout.
- Browser console-log clearing could not be controlled through the automation API, so the final report distinguishes current validation from retained historical tool logs.

## Acceptance

PASS for the targeted FS-300B.1 issue.

The original repeated `AbortError` path is removed, batch quotes use a request-appropriate timeout, and three final browser refreshes rendered opportunity cards successfully.
