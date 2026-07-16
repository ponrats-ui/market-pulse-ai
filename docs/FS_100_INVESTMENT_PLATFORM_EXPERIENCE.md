# FS-100 Investment Platform Experience

## Overview

FS-100 stabilizes the Founder-approved investment platform experience around the existing Professional Chart Engine. The sprint focuses on coherent canonical asset flow, real-data transparency, workflow consistency, and regression protection.

Thai summary: FS-100 ทำให้ประสบการณ์ใช้งาน Market Pulse AI เชื่อมต่อกันเป็นแพลตฟอร์มวิเคราะห์การลงทุนเดียว โดยยึดข้อมูลจริงและแสดงข้อจำกัดของผู้ให้บริการอย่างโปร่งใส

## Modules Covered

- Master Asset Registry and canonical symbol resolver
- Asset Center and global search
- Dashboard asset overview
- Professional Chart Engine V1
- Today's Opportunities
- Market Mood
- Important News
- Financial Analysis and dividends
- Compare
- Context-aware PIA Assistant
- Professional Paper Trading
- Watchlist Intelligence
- Logos and seven-day sparklines

## Key Implementation Notes

- Canonical symbol resolution now scores exact canonical/display/Thai-name matches above generic aliases. This prevents broad aliases such as `ปตท` from resolving to related but unintended securities.
- Compare chips can be removed down to an empty state, and compare search still blocks duplicate canonical symbols.
- PIA Assistant no longer initializes with a fixed Bitcoin question. Suggested prompts remain selected-asset aware.
- Today's Opportunities score bands follow the FS-100 thresholds:
  - 90-100: Strong Candidate
  - 80-89: Positive Watch
  - 70-79: Watch
  - 60-69: Neutral
  - Below 60: Weak / Avoid
- Watchlist signals now render only when real quote evidence exists.

## Data Providers

- Quotes, history, financials, technicals, sparklines, compare, market mood, and news use the existing backend provider abstraction.
- Current production provider path remains yfinance/Yahoo Finance-backed where available.
- Missing provider data is surfaced as unavailable, partial, stale, or not applicable rather than being fabricated.

## Request And Cache Strategy

- Search uses the Master Asset Registry and does not collapse to the legacy seed list during normal operation.
- Today’s Opportunities uses a bounded liquid universe and refreshes at most every 30 minutes.
- Quote requests are batched for watchlist/opportunity surfaces.
- Sparklines are requested with deduplicated symbols from visible opportunities and watchlist.
- Professional Chart history is requested by selected symbol and range; compare overlays load only when enabled.
- Backend cache keys include canonical symbol, range, and interval for history requests.

## Chart Regression

Professional Chart Engine remains directly under the asset overview. Browser validation confirmed:

- Desktop chart height: 600px
- Mobile chart height at 390px viewport: 380px
- Real yfinance source visible
- No horizontal overflow
- No app console errors

