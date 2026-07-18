# Founder Master Asset Search Fix

Date: 2026-07-15
Branch: `fix/master-asset-registry-search`

## Summary

The asset search blocker was caused by the frontend and backend depending on a small curated exchange seed instead of a broader searchable master registry. Symbols outside that seed, including `SPGI`, `RKLB`, and `SPCX`, could not appear in search even when Yahoo Finance could provide live data after symbol selection.

This fix introduces a master asset registry layer that keeps searchability separate from live provider availability. Search can now return verified registry assets while downstream quote, chart, risk, news, and financial sections continue to show real provider data or transparent unavailable states.

## Previous Behavior

- Search was limited to the curated records in `configs/exchange_master.json`.
- The curated source contained only 47 records.
- Valid securities outside the curated seed were treated as unsupported.
- The frontend could show no result for a valid ticker even though the backend provider could fetch the asset by canonical symbol.
- Browse category mapping did not align registry asset groups with the existing category IDs.

## Root Cause

`/api/assets/search` called the sector/asset universe service, which loaded assets through the Exchange Master seed. The seed's policy explicitly treated symbols outside the curated source as unsupported. The frontend then consumed this limited response and had no path to discover valid symbols absent from the seed.

The frontend category browser also used existing category IDs such as `global_stocks`, while registry records could be grouped by derived values such as `US`. That mismatch caused category browse counts to be empty even when the registry contained the assets.

## Fix Applied

- Added `backend/app/data_hub/master_asset_registry.py`.
- Added a verified offline source file at `data/exchange_sources/us_listed_verified.csv`.
- Merged the existing exchange seed with the verified source into a deduplicated registry.
- Updated symbol search, symbol resolution, capabilities, provider routing, and Data Hub status to use the master registry.
- Added `/api/master-asset-registry` for registry metadata.
- Updated `/api/assets/search` to support registry filters and larger safe limits.
- Updated frontend search behavior to use backend registry search only when the API exists, with explicit unavailable/error states.
- Updated frontend category mapping so registry records populate existing category IDs.
- Added tests covering exact ticker search, company-name search, Thai-name search, prefix search, deduplication, and unsupported-symbol behavior.

## Data Source

Primary registry inputs:

- `configs/exchange_master.json`
- `data/exchange_sources/us_listed_verified.csv`

Registry metadata observed locally:

- `version`: `master-registry-v1`
- `source`: `master_asset_registry`
- `coverage_status`: `partial_verified_registry`
- `search_coverage`: `partial_verified_us_thai_global_registry`
- `live_data_coverage`: `provider_dependent_partial`
- `record_count`: 141
- `searchable_count`: 141

Supported exchanges observed in metadata:

- Bond Yield
- COMEX
- Crypto
- FX
- Germany
- Hong Kong
- ICE
- Japan
- NASDAQ
- NYMEX
- NYSE
- NYSE American
- NYSE Arca
- SET
- US

## API Smoke Results

Local backend: `http://127.0.0.1:8000`

| Endpoint | Result |
| --- | --- |
| `/health` | PASS, HTTP 200 |
| `/api/assets/search?q=SPGI` | PASS, first result `SPGI` |
| `/api/assets/search?q=RKLB` | PASS, first result `RKLB` |
| `/api/assets/search?q=SPCX` | PASS, first result `SPCX` |
| `/api/assets/search?q=AAPL` | PASS, first result `AAPL` |
| `/api/assets/search?q=Apple` | PASS, first result `AAPL` |
| `/api/assets/search?q=TTB` | PASS, first result `TTB.BK` |
| `/api/assets/search?q=ทหารไทยธนชาต` | PASS, first result `TTB.BK` |
| `/api/assets/search?q=KBANK` | PASS, first result `KBANK.BK` |
| `/api/assets/search?q=ทอง` | PASS, first result `GC=F` |
| `/api/assets/search?q=ZZZNOTAREALMARKETPULSE` | PASS, zero results |
| `/api/assets/SPGI` | PASS, HTTP 200 |
| `/api/assets/RKLB` | PASS, HTTP 200 |
| `/api/compare?symbols=SPGI,RKLB` | PASS, HTTP 200 |
| `/api/news-impact/SPGI` | PASS, HTTP 200 |
| `/api/risk/RKLB` | PASS, HTTP 200 |
| `/api/financials/SPGI` | PASS, HTTP 200 |

## Browser Results

Local frontend: `http://127.0.0.1:5173`

| Query | Search Result | Selection | Dashboard Result |
| --- | --- | --- | --- |
| `SPGI` | PASS, `SPGI | S&P Global` | PASS, selected `SPGI` | PASS, live price, source `yfinance`, timestamp shown |
| `RKLB` | PASS, `RKLB | Rocket Lab USA` | PASS, selected `RKLB` | PASS, live price, source `yfinance`, timestamp shown |
| `SPCX` | PASS, `SPCX | AXS SPAC and New Issue ETF` | PASS, selected `SPCX` | PASS, provider data shown; provider profile naming may differ |
| `AAPL` | PASS, `AAPL | Apple` | PASS, selected `AAPL` | PASS, live price, source `yfinance`, timestamp shown |
| `Apple` | PASS, `AAPL | Apple` | PASS, selected `AAPL` | PASS, live price, source `yfinance`, timestamp shown |
| `TTB` | PASS, `TTB.BK | TMBThanachart Bank` | PASS, selected `TTB.BK` | PASS, live price, source `yfinance`, timestamp shown |
| `ทหารไทยธนชาต` | PASS, `TTB.BK | TMBThanachart Bank` | PASS, selected `TTB.BK` | PASS, live price, source `yfinance`, timestamp shown |
| `KBANK` | PASS, `KBANK.BK | Kasikornbank` | PASS, selected `KBANK.BK` | PASS, live price, source `yfinance`, timestamp shown |
| `ทอง` | PASS, `GC=F | Gold Futures` | PASS, selected `GC=F` | PASS, live price, source `yfinance`, timestamp shown |

Additional browser checks:

- Unsupported query `ZZZNOTAREALMARKETPULSE`: PASS, zero results and no stale result list.
- Clear search with keyboard: PASS, recent-search chips remain and browse rows return.
- Category `US stocks`: PASS, populated with 98 registry-backed assets.
- Sector filter `Semiconductor`: PASS, populated with 11 registry-backed rows.
- Browser console errors: PASS, no app console errors observed.

## Remaining Coverage Limitations

- The new source is a verified offline partial registry, not a full licensed exchange master.
- Live data remains provider-dependent. Searchability does not guarantee quote, chart, fundamentals, news, or risk availability.
- Some provider profile metadata can differ from registry metadata. Example: `SPCX` search metadata identifies the ETF, while yfinance profile text may differ.
- Full official exchange ingestion for SET, NYSE, NASDAQ, NYSE American, NYSE Arca, ETFs, ADRs, REITs, bonds, commodities, and FX should be handled in a later data-provider sprint.

## Decision

PASS for the Founder master asset registry search blocker.
