# RC5 QA Report

Date: 2026-07-10
Branch: feature/rc5-production-stabilization

## Test Results

Backend:

```text
43 passed in 1.14s
```

Frontend:

```text
npm.cmd run build
✓ built in 1.04s
No Vite bundle warning observed.
```

Smoke endpoints:

```text
/health                                      200
/api/assets/search?q=NVDA                    200
/api/assets/search?q=ทอง                     200
/api/sectors                                 200
/api/compare?symbols=BTC-USD,ETH-USD         200
/api/compare?symbols=NVDA,AMD                200
/api/risk/NVDA                               200
/api/financials/NVDA                         200
/api/news-impact/NVDA                        200
/api/calendar                                200
/api/subscription/features                   200
```

Browser smoke:

```text
Market Pulse AI rendered.
Dashboard, Compare, Portfolio, and PIA Relax Mode were visible.
Market data status showed ready.
Fresh console error count: 0.
```

## Issues Fixed

### High: Default crypto compare endpoint returned 500

File: `backend/app/services/comparison.py`

Reason: Radar chart calculations subtracted `None` from `100` when PE or volatility values were unavailable, which is normal for crypto assets.

Fix: Added nullable inverse scaling so unavailable metrics remain transparent `null` values instead of crashing the endpoint.

Regression: `backend/tests/test_compare.py` now covers crypto-like missing valuation fields.

### Medium: Mojibaked fallback Thai text

File: `backend/app/services/asset_universe.py`

Reason: The fallback asset universe still contained corrupted Thai strings in Thai names and aliases.

Fix: Replaced corrupted Thai with valid UTF-8 Thai labels and search aliases.

### Low: Remaining English-only UI labels

File: `frontend/src/main.tsx`

Reason: Some existing panels still had hardcoded English labels in controls, empty states, and footer text.

Fix: Reused the existing local label structure to make search, watchlist, compare, assistant, portfolio, Relax Mode, and footer labels language-aware.

## Known Limitations

- Browser validation used local development servers, not production Cloudflare/Render.
- Some financial terms intentionally remain English, including Ticker, PE, PB, Market Cap, Cash, Currency, 1D, 1W, 1M, YTD, and PIA product naming.
- Provider unavailable states remain transparent and may show unavailable values when Yahoo Finance or configured providers do not return a field.
- `RC2D_WIP_PATCH.diff` remains untracked and untouched.

## Decision

READY FOR FOUNDER WALKTHROUGH

