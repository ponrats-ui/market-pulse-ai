# RC5 Founder Test Guide

Date: 2026-07-10
Branch: feature/rc5-production-stabilization

## Local Setup

Backend:

```powershell
cd D:\market-pulse-ai\backend
.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Frontend:

```powershell
cd D:\market-pulse-ai\frontend
npm.cmd run dev -- --host 127.0.0.1
```

Open:

```text
http://127.0.0.1:5173
```

## Founder Walkthrough Checklist

Dashboard:

- Confirm BTC loads price, daily change, chart, source, and timestamp.
- Confirm technical indicators render without freezing.
- Confirm AI Committee, Risk, Financials, Sentiment, and News panels show either real data or transparent unavailable states.

Asset Search:

- Search `NVDA`.
- Search `ทอง`.
- Search `PTT`.
- Confirm keyboard navigation works with arrow keys and Enter.

Watchlist:

- Add selected asset.
- Open selected asset from watchlist.
- Remove selected asset.
- Check manual reorder buttons.

Compare:

- Open Compare.
- Confirm default `BTC-USD vs ETH-USD` does not error.
- Test `NVDA vs AMD`.
- Test `BTC-USD vs GLD`.

Paper Trading:

- Add one holding.
- Confirm market value, allocation, risk, diversification, and unavailable analytics messaging are clear.

News and Calendar:

- Open News Impact.
- Open Economic Calendar.
- Confirm missing provider data is transparent and not fabricated.

Assistant and Committee:

- Ask one question about the selected asset.
- Confirm the answer is cautious and does not guarantee returns.
- Confirm evidence and risk language are present.

PIA Relax Mode:

- Open PIA Relax Mode.
- Confirm music does not autoplay.
- Press play only if desired.
- Confirm close button hides the panel and investment data remains accessible.

Language:

- Switch between Thai and English.
- Confirm core UI labels update.
- Financial terms and product names may remain English.

## Acceptance Criteria

- No UI crash.
- No fresh browser console errors.
- No fabricated data.
- Backend tests pass.
- Frontend build passes.
- Local smoke endpoints return HTTP 200.

