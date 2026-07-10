# RC4 Founder Test Guide

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

## Founder Walkthrough

1. Confirm PIA branding: `Market Pulse AI`, `Personal Investment Assistant (PIA)`, and `Powered by PIA™`.
2. Search assets by ticker, English name, Thai term, sector, exchange, and alias:
   - `NVDA`
   - `NVIDIA`
   - `ทอง`
   - `น้ำมัน`
   - `กสิกร`
   - `NASDAQ`
   - `Semiconductor`
   - `SET`
3. Confirm search suggestions show exchange, sector, country, and currency.
4. Confirm Dashboard updates globally when changing selected asset.
5. Test Watchlist favorite, sort, pin/reorder controls, and remove.
6. Test chart indicators, crosshair tooltip, brush zoom, `YTD`, and `MAX`.
7. Review AI Committee for evidence, reasoning, confidence, vote, pros, cons, and Chief AI summary.
8. Review Fundamental Analysis and confirm unavailable metrics remain transparent.
9. Review Risk Engine and confirm each risk has evidence, probability, severity, mitigation, and trend.
10. Use Compare with `NVDA,AMD,TSM`; confirm radar, correlation matrix, relative strength, and thesis.
11. Use AI Assistant suggested prompts and conversation memory.
12. Add a Paper Trading holding and confirm market value, cash, allocation, sector allocation, transaction count, risk, and unavailable analytics explanation.
13. Open Economic Calendar and confirm only provider-backed or transparent unavailable data is shown.
14. Open News Impact and confirm original provider data only.
15. Open PIA Relax Mode and confirm no autoplay.

## API Smoke

```text
GET /health
GET /api/exchange-master
GET /api/assets/search?q=ทอง
GET /api/sectors
GET /api/technical/NVDA?range=1y&interval=1d
GET /api/compare?symbols=NVDA,AMD,TSM
GET /api/risk/NVDA
GET /api/financials/NVDA
GET /api/subscription/features
POST /api/portfolio/evaluate
POST /api/assistant/ask
```

## Pass Criteria

- No fake data.
- No placeholder values masquerading as real.
- No autoplay.
- No deployment, merge, push, or tag.
- Backend tests and frontend build pass.
