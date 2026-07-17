# Founder US Master Asset Registry

Date: 2026-07-15
Branch: `fix/us-master-registry`

## Summary

The US master asset registry has been expanded from a small verified subset to a scalable exchange-directory based registry. The search engine was already functional; the blocker was incomplete source coverage.

## Root Cause

The previous `data/exchange_sources/us_listed_verified.csv` contained only `97` records. It was a verified launch subset, not a broad US listed security master. Because the runtime registry merged that small CSV with the curated seed, valid US listed securities such as `OKLO`, `IONQ`, `SMR`, and `NNE` were absent.

## Source

Generated source:

- `data/exchange_sources/us_listed_verified.csv`
- `data/exchange_sources/us_listed_verified.meta.json`

Fetch utility:

- `scripts/fetch_us_master_registry.py`

Public sources used:

- Nasdaq Trader listed symbols: `https://www.nasdaqtrader.com/dynamic/SymDir/nasdaqlisted.txt`
- Nasdaq Trader other listed symbols: `https://www.nasdaqtrader.com/dynamic/SymDir/otherlisted.txt`
- Nasdaq screener metadata: `https://api.nasdaq.com/api/screener/stocks?tableonly=true&limit=10000&offset=0&download=true`

## Coverage

Raw records inspected: `13052`

Included US records: `11729`

Runtime master registry total records: `13577`

Runtime searchable records: `13577`

Exchange counts:

- NASDAQ: `4832`
- NYSE Arca: `2680`
- NYSE: `2398`
- Cboe BZX: `1545`
- NYSE American: `274`

Asset type counts:

- Stock: `5721`
- ETF: `5541`
- Preferred stock: `382`
- Closed-end fund: `36`
- ADR: `27`
- REIT: `22`

## Sector Counts

Sector browser counts observed through the backend:

- ETF: `5536`
- Finance: `1404`
- Consumer Discretionary: `1082`
- Health Care: `1027`
- Technology: `726`
- Industrials: `595`
- Real Estate: `285`
- Energy: `175`
- Utilities: `170`
- Consumer Staples: `143`
- Basic Materials: `135`
- Telecommunications: `97`
- Unclassified: `775`

Technology now contains hundreds of securities instead of the previous approximately `98` records.

## Search Examples

Verified exact search results:

- `OKLO` -> `OKLO`, NYSE, Utilities
- `RKLB` -> `RKLB`, NASDAQ, Industrials
- `IONQ` -> `IONQ`, NYSE, Technology
- `PLTR` -> `PLTR`, NASDAQ, Technology
- `SOFI` -> `SOFI`, NASDAQ, Finance
- `SMR` -> `SMR`, NYSE, Industrials
- `NNE` -> `NNE`, NASDAQ, Utilities
- `AMD` -> `AMD`, NASDAQ, Semiconductor
- `TSLA` -> `TSLA`, NASDAQ, Consumer
- `NVDA` -> `NVDA`, NASDAQ, Semiconductor
- `MSFT` -> `MSFT`, NASDAQ, Technology
- `META` -> `META`, NASDAQ, Technology
- `AMZN` -> `AMZN`, NASDAQ, Consumer
- `GOOGL` -> `GOOGL`, NASDAQ, Technology
- `AAPL` -> `AAPL`, NASDAQ, Technology
- `SPGI` -> `SPGI`, NYSE, Finance
- `SPCX` -> `SPCX`, NASDAQ, Technology
- `BRK.B` -> `BRK.B`, NYSE, provider symbol `BRK-B`
- `V` -> `V`, NYSE, Consumer Discretionary
- `MA` -> `MA`, NYSE, Consumer Discretionary
- `JPM` -> `JPM`, NYSE, Finance
- `GS` -> `GS`, NYSE, Finance

## API Payload

`/api/assets/search` returns the registry fields needed by the frontend:

- canonical symbol
- display symbol
- provider symbol
- company name
- aliases
- exchange
- country
- currency
- sector
- industry
- asset class
- security type
- enabled/searchable flags
- coverage source/status
- data capability fields

## Browser Results

Local frontend: `http://127.0.0.1:5173`

Local backend: `http://127.0.0.1:8000`

Observed:

- US Stocks count: `6130`
- Technology count: `726`
- Health Care count: `1027`
- Energy count: `175`
- Search `OKLO`: first result `OKLO`, dashboard updated with live provider data
- Search `RKLB`: first result `RKLB`, dashboard updated with live provider data
- Search `PLTR`: first result `PLTR`, dashboard updated with live provider data
- Search `IONQ`: first result `IONQ`, dashboard updated with live provider data
- Selected dashboards showed `yfinance` source and no unavailable state near the selected asset
- Captured application console errors: none

## Validation

Completed:

- Focused backend tests: `25 passed`
- Full backend tests: `102 passed`
- Frontend build: passed
- API smoke: passed for `OKLO`, `RKLB`, `PLTR`, `IONQ`, `SMR`, `NNE`, and `BRK.B`
- Registry validation: passed
- US-only update dry run: passed without writing config files

## Known Limitations

- This is a public-source verified registry, not a paid exchange-licensed security master.
- Live quote, history, fundamentals, and news remain provider dependent.
- Nasdaq screener sector/industry enrichment can be temporarily unavailable; the generator supports a local cache for reproducible enrichment when the upstream endpoint is flaky.
- Some securities remain `Unclassified` when sector metadata is unavailable.
- Warrants, rights, units, test issues, and duplicate symbols are intentionally excluded.

## Decision

PASS for the Founder US master asset registry expansion.
