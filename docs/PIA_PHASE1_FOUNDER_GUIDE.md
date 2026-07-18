# PIA Phase 1 Founder Guide

## Local Setup

Backend:

```powershell
cd D:\market-pulse-ai\backend
.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Frontend:

```powershell
cd D:\market-pulse-ai\frontend
npm.cmd run dev
```

Open:

```text
http://127.0.0.1:5173
```

## Walkthrough

1. Confirm header says `Market Pulse AI`, `Personal Investment Assistant (PIA)`, and `Powered by PIA™`.
2. In Asset Center, confirm Category appears above Search.
3. Search `NVDA`, `ทอง`, `PTT`, `QQQ`, and `TLT`.
4. Add an asset to Watchlist, sort by symbol and daily percent, then switch to manual reorder.
5. Open the chart and test `YTD`, `MAX`, indicator toggles, tooltip crosshair, and brush zoom.
6. Review AI Committee and confirm each card shows vote, evidence, confidence, pros, cons, and reasoning.
7. Review Fundamental Analysis in Thai and confirm unavailable values are not replaced with fake data.
8. Review Risk Engine and confirm probability, severity, evidence, mitigation, historical context, and risk trend appear.
9. Open Compare and confirm radar chart, correlation matrix, relative strength, and thesis summary.
10. Open AI Assistant, use a suggested prompt, and confirm conversation history and follow-up questions appear.
11. Open Portfolio, add a holding, and confirm market value, cash, daily return, total return, allocation pie, sector allocation, realized P/L, risk, and diversification.
12. Open Economic Calendar and confirm provider-backed events appear only when available.
13. Open News Impact and confirm no fake articles appear.
14. Open PIA Relax Mode, confirm it does not autoplay, press Play manually, test pause, mute, volume, source link, and close.

## Pass Criteria

- No fake data.
- No autoplay.
- No blocked investment workflow.
- Thai labels are clear for core investor flows.
- Build and backend tests pass.
- Bundle warning remains gone.
