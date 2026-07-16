# FS-100 Browser Results

## Environment

- Frontend: `http://127.0.0.1:5173`
- Backend: `http://127.0.0.1:8000`
- Browser: in-app browser
- API base: `VITE_API_BASE_URL=http://127.0.0.1:8000`

## Desktop

PASS.

- Asset Center rendered.
- Today's Opportunities rendered.
- Market Mood rendered.
- Important News rendered with internal scroll.
- Watchlist seven-day sparkline rendered.
- Professional Chart rendered SVG from yfinance.
- Chart height: 600px.
- Horizontal overflow: none.
- App console errors: none.

## Search And Dashboard

PASS.

- Search for `AAPL` returned Master Asset Registry rows.
- Selecting AAPL updated dashboard data.
- AAPL chart continued to show yfinance source.
- Financial Health panel appeared for company asset.

## Assistant

PASS.

- AAPL suggested prompts referenced AAPL context.
- Suggested prompts did not include BTC or Bitcoin.
- Initial assistant textarea uses neutral selected-asset wording.

## Compare

PASS.

- Compare section rendered.
- Remove buttons are enabled.
- Duplicate canonical assets are blocked.
- Empty compare state is supported.

## Portfolio

PASS.

- Paper Trading section rendered.
- Simulated AAPL buy accepted.
- Simulated partial sell accepted.
- Transaction history updated.
- Realized P/L and unrealized P/L surfaces rendered.
- No broker integration disclosure visible.

## News

PASS.

- News panel used internal vertical scroll.
- Sticky header rendered.
- Five original source links were available.
- Links preserve provider URL and open in a new tab with `target="_blank"`.

## Mobile 390x844

PASS.

- No horizontal overflow.
- Search visible.
- Professional Chart rendered.
- Chart height: 380px.
- yfinance source visible.
- Opportunities, news, and watchlist sparkline rendered.
- App console errors: none.

