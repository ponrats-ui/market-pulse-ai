# FS-100 Founder Test Guide

## Setup

1. Start backend:
   `cd D:\market-pulse-ai\backend`
   `.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000`

2. Start frontend:
   `cd D:\market-pulse-ai\frontend`
   `npm.cmd run dev -- --host 127.0.0.1`

3. Open:
   `http://127.0.0.1:5173`

## Search Checklist

- AAPL
- OKLO
- RKLB
- SPGI
- KKP
- BBL
- KBANK
- PTT
- AOT
- ธนาคารกรุงเทพ
- กสิกรไทย
- ปตท
- ทอง

Expected: exact ticker/name/Thai alias search returns canonical assets, and selecting an asset updates dashboard, chart, financials, risk, news, and assistant context.

## Dashboard Checklist

- Confirm asset logo or fallback.
- Confirm symbol, company/asset name, provider, timestamp, and price data.
- Confirm Professional Chart is directly under Asset Overview.
- Confirm chart range and mode controls still work.
- Confirm Today’s Opportunities separates US and Thai groups.
- Confirm Market Mood renders even if some metrics are unavailable.
- Confirm News has internal scroll and original links.

## Compare Checklist

- Add AAPL and MSFT.
- Search and add KKP.
- Try adding KKP.BK after KKP and confirm duplicate canonical symbols are blocked.
- Remove every compared asset and confirm empty state is clear.

## Assistant Checklist

- Select BTC-USD, AAPL, OKLO, PTT.BK, GLD.
- Open Assistant after each asset.
- Confirm suggested prompts change and do not show fixed Bitcoin wording for non-Bitcoin assets.

## Portfolio Checklist

- Set initial cash.
- Search and select AAPL.
- Submit buy.
- Submit second buy.
- Submit partial sell.
- Confirm cash, market value, realized P/L, unrealized P/L, allocation, and transaction history.
- Test TTB and TTB.BK as one canonical simulated position.
- Reset portfolio.

## Mobile Checklist

- Set viewport to 390x844.
- Confirm no horizontal overflow.
- Confirm search remains usable.
- Confirm chart height is 380px.
- Confirm tables scroll internally.

