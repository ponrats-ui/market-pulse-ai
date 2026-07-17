# Founder Polish 04: Logos and 7-Day Sparklines

## Summary

Founder Polish 04 adds compact asset identity and real 7-day trend context to Today's Opportunities and Watchlist.

Status: PASS

## Architecture

- Backend exposes one batch endpoint: `GET /api/assets/sparklines?symbols=AAPL,MSFT,NVDA`.
- The endpoint reuses the existing cached history path through `get_cached_history(symbol, "1mo", "1d")`.
- The frontend requests sparklines once for deduplicated symbols used by visible Today's Opportunities rows and the user Watchlist.
- The same sparkline map is reused by both sections.

## Logo Source Policy

- Logos are never downloaded, bundled, scraped, or committed into the repository.
- Quote responses now support backward-compatible logo metadata fields:
  - `logo_url`
  - `icon_url`
  - `provider_logo_url`
  - `logo_provider`
  - `logo_available`
- If yfinance returns a provider logo URL, the frontend may render it remotely.
- If no provider logo is returned, the frontend renders a deterministic fallback avatar.

## Fallback Behavior

- Fallback avatars use ticker initials such as `AA`, `NV`, `OK`, `PT`, or `BT`.
- Background color is deterministic from the symbol, not random.
- Fallbacks include accessible labels such as `AAPL fallback logo`.
- No emoji is used as the only identity marker.

## Sparkline Data Source

- Sparkline points come from provider-returned historical close prices only.
- No generated, simulated, or fabricated points are created.
- The endpoint returns the latest available 5-7 close points where possible.
- If fewer than five close points are available, the response keeps the real points and sets `unavailable_reason`.
- If no history exists, `points` remains empty and the frontend shows `N/A`.

## Caching Strategy

- Sparkline data reuses the existing historical cache TTL: `HISTORICAL_TTL_SECONDS`.
- Current default TTL is 300 seconds unless overridden by environment configuration.
- Quote logo metadata reuses the existing quote cache path.

## Batch Request Strategy

- The frontend deduplicates symbols before requesting sparklines.
- The request includes only visible opportunity rows plus watchlist symbols.
- This avoids a render-time N+1 pattern and avoids loading every opportunity candidate's history.
- Browser `performance.getEntriesByType()` was unavailable in the in-app browser runtime, so request count was verified by code path and API smoke rather than resource timing.

## API Smoke Results

PASS:

- `/health` returned HTTP 200.
- `/api/assets/sparklines?symbols=AAPL,MSFT,NVDA,OKLO,AAPL` returned HTTP 200 and deduped to `AAPL,MSFT,NVDA,OKLO`.
- `/api/assets/sparklines?symbols=PTT.BK,CPALL.BK,KBANK.BK,AOT.BK` returned HTTP 200 with 7 points per symbol.
- `/api/assets/sparklines?symbols=AAPL,OKLO,KKP.BK,BTC-USD,GLD` returned HTTP 200 with 7 points per symbol.

Sample verified directions:

- AAPL positive, up 5.42%.
- MSFT positive, up 1.75%.
- NVDA positive, up 7.91%.
- OKLO negative, down 4.61%.
- TSM negative, down 3.03%.
- PTT.BK positive, up 5.44%.
- CPALL.BK positive, up 1.08%.
- KBANK.BK positive, up 3.07%.
- AOT.BK positive, up 2.80%.
- BTC-USD negative, down 0.24%.
- GLD negative, down 1.36%.

## Browser Results

Desktop PASS:

- Today's Opportunities rendered 10 compact rows.
- Watchlist rendered logo/fallback and sparkline rows.
- 11 logo/fallback elements rendered.
- 11 sparklines rendered.
- Positive, negative, and flat sparkline states rendered.
- No horizontal overflow.
- No app console errors.

Mobile 390 x 844 PASS:

- No horizontal overflow.
- 10 opportunity rows rendered.
- Watchlist row rendered.
- 11 logo/fallback elements rendered.
- 11 sparklines rendered.
- Sparkline accessible labels rendered, for example `AAPL 7-day trend positive, up 5.42 percent`.
- No app console errors.

## Performance Notes

- Initial broad sparkline loading was narrowed during validation to visible opportunity symbols plus watchlist symbols.
- This keeps the batch request compact and reduces provider pressure.
- The endpoint still performs provider history retrieval through the existing cached history layer.

## PASS / PARTIAL / FAIL

PASS:

- Today's Opportunities shows professional fallback avatars and real 7-day sparklines.
- Watchlist shows fallback avatars and real 7-day sparklines.
- Sparkline direction matches provider-returned data from the batch endpoint.
- Batch loading is used.
- Missing data remains transparent with `N/A` and `unavailable_reason`.
- Desktop and mobile layouts pass.
- Backend tests pass.
- Frontend build passes.

PARTIAL:

- Real company logos depend on provider-returned logo URLs. In the current local yfinance smoke, fallback avatars were used for visible rows.
- Browser network resource timing was not exposed by the in-app browser runtime; request strategy was verified by code inspection and API smoke.

FAIL:

- None.

## Remaining Limitations

- yfinance may not provide logo URLs for many assets; fallback avatars are expected behavior.
- Sparkline availability depends on provider historical data and market calendar.
- Backend batch endpoint is cached but still sequentially resolves uncached history internally; future provider adapters may support true upstream batch history retrieval.
