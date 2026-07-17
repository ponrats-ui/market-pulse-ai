# FS-200 Founder Test Guide

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

## Asset Verification

Verify chart load and no stale previous-symbol data:

- AAPL
- MSFT
- OKLO
- RKLB
- PTT.BK
- KBANK.BK
- BTC-USD
- GLD

## Chart Flow 1

1. Select AAPL.
2. Confirm Professional Chart is under Asset Overview.
3. Select 1Y.
4. Enable EMA20 and EMA50.
5. Enable RSI.
6. Enable MACD.
7. Hover candles.
8. Enter fullscreen.
9. Exit fullscreen.
10. Export PNG.

## Chart Flow 2

1. Select PTT.BK.
2. Confirm THB context.
3. Enable Volume MA.
4. Enable Bollinger Bands.
5. Confirm no fabricated event markers.

## Chart Flow 3

1. Select BTC-USD.
2. Select 1M.
3. Enable ATR.
4. Confirm crypto history is treated as provider-returned history.

## Chart Flow 4

1. Enable compare.
2. Confirm normalized percentage return labels.
3. Disable compare.
4. Confirm base chart remains intact.

