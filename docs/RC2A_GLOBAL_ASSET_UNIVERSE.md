# RC2A Global Asset Universe

## Overview

RC2A expands Market Pulse AI from a fixed MVP selector into a professional research workspace that can discover, track, and compare a broader global asset universe using real provider data.

Thai summary: RC2A ทำให้ระบบค้นหาสินทรัพย์ได้กว้างขึ้น เพิ่ม watchlist ของผู้ใช้ และเพิ่ม compare mode โดยยังใช้ข้อมูลจริงจาก backend เท่านั้น

## Architecture

- Frontend search calls `GET /api/assets/search` only after a debounced user query.
- The asset universe lives behind `backend/app/services/asset_universe.py`.
- Quotes, history, risk, analysis, and comparison still flow through the backend API and the yfinance provider abstraction.
- User watchlist, recent searches, and favorites are persisted locally in browser storage.
- Compare mode requests only the selected 2-5 symbols through `GET /api/compare`.

## Search Strategy

- Search supports symbol, company name, Thai name where available, asset type, market, and keywords.
- Ranking favors exact symbol matches, then symbol prefixes, then text matches, then lightweight subsequence fuzzy matches.
- Results are limited server-side to keep responses small.
- The frontend debounces search input and does not preload the full universe into memory.

## Supported Exchanges and Asset Classes

- Thailand: SET and SET index symbols supported by Yahoo Finance.
- US stocks: NYSE and NASDAQ examples.
- ETFs: broad index and commodity ETF examples.
- Crypto: major USD pairs supported by Yahoo Finance.
- Commodities: futures symbols supported by Yahoo Finance.
- Forex: Yahoo Finance FX pairs.
- Major indices: US, Japan, Hong Kong, Germany, and Thailand.
- Bond yields: US 10Y Treasury yield through Yahoo Finance.

## Data Policy

- No mock market values are used for RC2A surfaces.
- If a provider does not return a field, the UI shows `Unavailable`.
- AI and risk summaries are derived from backend-returned quote/history inputs and remain conservative.
- Financial metrics such as market cap, PE, and sector are displayed only when yfinance returns them.

## Known Limitations

- The initial universe is curated and intentionally limited; it is not yet a full exchange master database.
- Thai company names are available only for selected high-usage symbols.
- Yahoo Finance coverage varies by asset class, exchange, and trading session.
- Reordering and favorites persist per browser/device only.
- Compare mode supports symbol entry; full compare-search suggestions are planned for RC2B.

## RC2B Candidates

- Server-backed user accounts and synced watchlists.
- Exchange master symbol ingestion with paging.
- Provider-level symbol lookup API integration.
- Compare-mode searchable picker reuse.
- Watchlist import/export.
