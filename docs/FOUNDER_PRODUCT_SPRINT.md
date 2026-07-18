# Founder Product Sprint - Investment Experience Upgrade

Date: 2026-07-16
Branch: feature/founder-investment-experience
Status: READY WITH DOCUMENTED PARTIALS

## Summary

This sprint completed the Founder Investment Experience Upgrade without adding broker integrations or fabricated values. The implementation keeps all price, comparison, portfolio, and screener calculations tied to backend/provider data. Unavailable fields are displayed transparently.

## Completed Items

- Compare now uses the Master Asset Registry search endpoint.
- Compare supports ranked autocomplete, canonical symbols, Thai names, company-name search, duplicate prevention, add/remove, and a clear unsupported state.
- Default BTC-USD / ETH-USD compare presets were removed.
- Paper Trading now uses Master Asset Registry search for order entry.
- Paper Trading supports reset, buy, repeated buy, partial sell, merged positions, average cost, cash balance, realized P/L, unrealized P/L, daily P/L, market value, allocation, country allocation, sector allocation, transaction history, and transparent unavailable states.
- Today’s Opportunities uses a bounded liquid universe instead of scanning arbitrary registry rows.
- Watchlist signal chips remain evidence-based and show neutral/no-signal states when evidence is insufficient.
- Context-aware PIA prompt helper is connected to selected symbol and quote metadata.
- Dividend yield is displayed when the provider returns it; unavailable dividend fields are not fabricated.

## Screener Coverage

PASS / PARTIAL: Today’s Opportunities is intentionally a bounded liquid scan, not a full-market scan.

US/global liquid universe:
AAPL, MSFT, NVDA, AMD, TSM, SPY, QQQ, TLT, VNQ, SOXX, GLD, SLV

Thai liquid universe:
PTT.BK, AOT.BK, SCB.BK, KBANK.BK, TTB.BK, CPALL.BK, DELTA.BK, ADVANC.BK

The backend quote smoke test returned HTTP 200 for the full bounded universe. Results are ranked only from provider-returned quote/fundamental fields; no unavailable technical factors are fabricated.

## Compare Browser Results

PASS:

- Opened Compare screen.
- Added AAPL from Master Asset Registry search.
- Added MSFT from Master Asset Registry search.
- Removed AAPL.
- Added KKP.BK from Master Asset Registry search with Thai name visible.
- Confirmed table updated with NVDA, AMD, MSFT, and KKP.BK.
- Confirmed KKP duplicate search result is disabled as “Already added”.

## Paper Trading Browser Results

PASS:

- Reset portfolio.
- Set initial cash during workflow.
- Bought AAPL twice.
- Confirmed one merged AAPL position with quantity 5 and average cost 112.
- Sold 2 AAPL.
- Confirmed remaining AAPL quantity 3.
- Confirmed cash increased and realized P/L displayed.
- Added KKP.BK from Master Asset Registry search.
- Confirmed asset, sector, and country allocations updated.
- Confirmed no NaN remains in transaction history.

PARTIAL:

- Transaction-backed portfolio state persisted after refresh, but the separate Initial Cash input resets to its default value. This should be persisted in a future portfolio settings pass.
- Performance chart remains unavailable until portfolio history snapshots are persisted.
- Win rate remains unavailable until enough closed-trade data exists.

## Context-Aware PIA Prompt Results

PASS:

- BTC-USD produced crypto-specific prompts about volatility, invalidation, and risk plan.
- AAPL produced technology/growth-specific prompts about valuation, momentum, and peers.

PARTIAL:

- Browser automation did not reliably complete the full prompt sweep for OKLO, PTT.BK, and GLD before commit. The helper logic includes explicit branches for Thai equities, crypto, commodities, energy, technology, and default assets, but the remaining symbols should be manually retested in the Founder walkthrough.

## Dividend Availability

PARTIAL:

- Dividend yield is displayed where quote/financial provider data exposes it.
- Dividend per share, ex-date, payment date, payout ratio, and historical dividend trend are not fabricated and remain unavailable unless provider data supplies them.

## Watchlist Signal Evidence

PASS:

Signals are derived from live quote fields only:

- Trend strong: daily change >= 3%.
- High risk: daily change <= -3%.
- Breakout watch: price near provider high.
- Liquidity active: volume >= 1,000,000.
- Dividend factor: provider dividend yield > 0.
- No strong signal from latest data: shown when evidence is insufficient.

## Validation Results

PASS:

- Backend tests: 102 passed.
- Frontend build: passed.
- API smoke: health, search, Thai search, quotes, compare, news, analysis, and portfolio evaluate returned HTTP 200.
- Desktop browser: dashboard, opportunities, compare, and paper trading critical workflow passed.
- Mobile browser: 390 x 844 dashboard loaded with no horizontal overflow.
- Malformed text scan: no matches in founder sprint files for the checked patterns.

PARTIAL:

- Browser console included earlier dev-session logs from prior tabs and navigation aborts. The actual product issue found was the opportunity screener requesting overly broad symbols; it was corrected to a bounded liquid universe and frontend timeout was raised to 20 seconds.

## PASS / PARTIAL / FAIL

PASS:

- Compare autocomplete critical workflow.
- Paper Trading critical workflow.
- Frontend build.
- Backend tests.
- API smoke tests.
- Desktop critical workflow.
- Mobile no critical layout failure.
- No NaN/fabricated transaction values.

PARTIAL:

- Full-market opportunity scan is intentionally limited to a liquid universe.
- Dividend details beyond yield depend on provider availability.
- Full five-symbol context prompt browser sweep needs manual Founder retest for OKLO, PTT.BK, and GLD.
- Initial Cash input persistence after refresh is incomplete.

FAIL:

- None blocking for the committed MVP critical workflows.

## Remaining Limitations

- Persist Initial Cash separately from transaction history.
- Add portfolio performance snapshot persistence before enabling a performance chart.
- Add closed-trade analytics before showing win rate.
- Add richer dividend provider fields before displaying ex-date/payment/payout/history.
- Add automated browser tests for context-aware prompt switching across asset classes.
