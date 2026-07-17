# Founder Thai Master Asset Registry

Date: 2026-07-15
Branch: `fix/thai-master-registry`

## Summary

The Thai master asset registry blocker is fixed by using a verified SET/mai listing source instead of maintaining a small curated Thai list. Search now supports ordinary Thai stocks, foreign/preferred share classes, ETFs, property funds, REITs, infrastructure funds, and fund-like listed securities while still keeping live-data availability transparent.

Thai summary: ระบบค้นหาหุ้นไทยถูกปรับให้ใช้แหล่งข้อมูล SET/mai ที่ตรวจสอบได้จริง ไม่ใช่รายการตัวอย่างขนาดเล็ก และยังแสดงสถานะข้อมูลอย่างโปร่งใสเมื่อ provider บางส่วนไม่พร้อมใช้งาน

## Root Cause

The previous registry merged only the curated exchange seed and the verified US source. Thai coverage therefore missed many ordinary SET/mai symbols and did not have a reproducible Thai source file equivalent to the US listed source. Some Thai aliases also depended on generated names, which caused ambiguous Thai-name ranking for common user queries.

## Data Source

Source: Stock Exchange of Thailand public stock list API

Endpoint used by the fetch utility:

`https://www.set.or.th/api/set/stock/list?lang=en`

Generated files:

- `data/exchange_sources/thai_listed_verified.csv`
- `data/exchange_sources/thai_listed_verified.meta.json`

Refresh utility:

- `scripts/fetch_thai_master_registry.py`

Maintenance utility:

- `scripts/update_exchange_master.py --market thailand --dry-run --diff`

## Coverage

Raw SET records fetched: `3859`

Included verified records: `1827`

Exchange counts:

- SET: `1371`
- mai: `456`

Included security types:

- `S`: ordinary/common shares, `931`
- `F`: foreign share classes, `865`
- `L`: ETFs, `13`
- `P`: preferred shares, `8`
- `Q`: preferred foreign/share classes, `8`
- `U`: fund-like listed securities, `2`

Excluded security types:

- `V`: derivative warrants, `1482`
- `W`: warrants, `88`
- `X`: depositary receipts, `462`

Master registry total records: `1960`

Searchable records: `1960`

Thai Stocks browser count observed locally: `1829`

The browser count is higher than the verified Thai source count because existing Thai index seed records are also grouped under Thai stocks.

## API Shape

Thai search results now include:

- `symbol`
- `canonical_symbol`
- `display_symbol`
- `label`
- `company_name`
- `company_name_en`
- `company_name_th`
- `short_name_en`
- `short_name_th`
- `thai_name`
- `asset_class`
- `asset_type`
- `security_type`
- `exchange`
- `market`
- `sector`
- `industry`
- `country`
- `currency`
- `aliases`
- `provider_symbols`
- `data_capabilities`
- `live_data_capability`
- `quote_capability`
- `history_capability`
- `fundamentals_capability`
- `news_capability`
- `coverage_source`
- `coverage_status`

## Verified Ticker Search

These Founder-required tickers resolve to canonical ordinary `.BK` symbols first:

`KKP`, `BBL`, `KTB`, `SCB`, `KBANK`, `BAY`, `TISCO`, `TTB`, `AOT`, `CPALL`, `CPF`, `HMPRO`, `GLOBAL`, `CRC`, `BJC`, `MINT`, `CENTEL`, `ADVANC`, `TRUE`, `COM7`, `PTT`, `PTTEP`, `TOP`, `BCP`, `OR`, `GPSC`, `GULF`, `BGRIM`, `EA`, `DELTA`, `HANA`, `KCE`, `BDMS`, `BH`, `CHG`, `BCH`, `AAV`, `BA`, `BTS`, `SCC`, `SCGP`, `IVL`, `PTTGC`, `TU`, `CBG`, `OSP`

## Verified Thai Search

These Thai-name searches resolve to the expected ordinary `.BK` symbols first:

- `เกียรตินาคินภัทร` -> `KKP.BK`
- `ธนาคารกรุงเทพ` -> `BBL.BK`
- `กรุงไทย` -> `KTB.BK`
- `ไทยพาณิชย์` -> `SCB.BK`
- `กสิกรไทย` -> `KBANK.BK`
- `ทหารไทยธนชาต` -> `TTB.BK`
- `ปตท` -> `PTT.BK`
- `ปตท.สผ.` -> `PTTEP.BK`
- `ซีพีออลล์` -> `CPALL.BK`
- `แอดวานซ์` -> `ADVANC.BK`
- `ท่าอากาศยานไทย` -> `AOT.BK`
- `กรุงเทพดุสิตเวชการ` -> `BDMS.BK`
- `โรงพยาบาลบำรุงราษฎร์` -> `BH.BK`
- `ปูนซิเมนต์ไทย` -> `SCC.BK`

## Validation

Registry validation checks:

- duplicate canonical symbols
- duplicate provider symbols that point to different canonical assets
- malformed required fields
- invalid Thai `.BK` provider mapping
- invalid Thai exchange/currency mapping
- invalid asset class/security type mapping
- searchable records without canonical symbols
- mojibaked Thai text

Latest validation:

- Focused asset universe tests: `15 passed`
- Full backend tests: `98 passed`
- Frontend build: passed
- API smoke: passed for required ticker and Thai-name searches
- Registry validation: passed in focused tests
- Duplicate canonical symbols: none
- Duplicate provider mappings: none
- Invalid Thai provider mappings: none
- Broken Thai names detected in runtime registry: none

## Browser Verification

Local frontend: `http://127.0.0.1:5173`

Local backend: `http://127.0.0.1:8000`

Observed after final validation:

- Thai Stocks category count: `1829`
- Asset list count: `1829`
- Banking count: `24`
- Commerce count: `66`
- Energy & Utilities count: `121`
- Healthcare Services count: `58`
- Information & Communication Technology count: `79`
- Required ticker and Thai-name searches ranked ordinary `.BK` symbols first
- `KKP` browser selection updated the dashboard with real price data, `yfinance` source, and no unavailable state near the selected asset
- Mobile viewport `390x844`: search input visible and no horizontal overflow
- Application console errors: none observed

## Legal And Usage Notes

This project uses the SET public listing endpoint only as a security master reference for search and symbol mapping. It does not claim licensed redistribution of exchange market data. Live quote, news, fundamentals, and portfolio data remain provider-dependent and must continue to show transparent unavailable states when a provider cannot supply data.

## Known Limitations

- The registry is a verified launch source, not a paid exchange-licensed security master.
- Live data coverage can still vary by yfinance/Yahoo Finance availability.
- Some Thai names are ambiguous because multiple companies share common Thai words; curated Founder aliases are prioritized only where needed.
- Derivative warrants, warrants, and depositary receipts are intentionally excluded from this phase.

## Decision

PASS for the Founder Thai master asset registry blocker, subject to final backend, frontend, API, and browser validation in this sprint.
