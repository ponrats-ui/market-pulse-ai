# RC2D Founder Test Guide

## Scope

Use this checklist to test RC2D locally before any merge or production deployment. RC2D should improve daily investor workflows without fabricating financial data, news, macro events, or recommendations.

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

## 1. Asset Search

Search these terms and confirm relevant ranked results appear:

- `NVDA`
- `AMD`
- `TSM`
- `PTT`
- `ทอง`
- `น้ำมัน`
- `QQQ`
- `TLT`
- `VNQ`
- `SOXX`

Expected result: matching symbols appear quickly. If provider data is unavailable, the app should say unavailable rather than inventing values.

## 2. Compare

Test these comparisons:

- `NVDA` vs `AMD`
- `BTC-USD` vs `GLD`
- `QQQ` vs `TLT` vs `VNQ`

Check:

- Normalized performance
- Price
- Return
- Risk
- Volatility
- Correlation
- Market cap
- PE
- Sector
- Dividend
- AI opinion
- Recommendation

## 3. Portfolio

Test the simulated portfolio workflow:

- Set initial capital
- Add buy transaction
- Add sell transaction
- Check cash balance
- Check unrealized P/L
- Check realized P/L
- Check allocation
- Check risk score

Expected result: all calculations are local simulations. No broker integration should appear.

## 4. News

Test news and news impact for:

- `NVDA`
- `BTC-USD`
- `PTT.BK`

Check:

- Headline
- Summary
- Affected assets
- Impact direction
- Impact strength
- Expected duration
- Confidence
- Reasoning
- Cross-asset effects

Expected result: if no provider returns articles, the response clearly says unavailable. No simulated articles should appear.

## 5. API Smoke

Run these local API checks:

```text
GET /health
GET /api/assets/search?q=NVDA
GET /api/assets/search?q=ทอง
GET /api/compare?symbols=NVDA,AMD
POST /api/portfolio/evaluate
GET /api/news?symbol=NVDA
GET /api/analysis/NVDA
```

Minimal portfolio POST payload:

```json
{
  "holdings": [
    { "cashBalance": 1000 },
    { "symbol": "NVDA", "quantity": 2, "averageCost": 100 },
    {
      "transactions": [
        { "symbol": "NVDA", "side": "buy", "quantity": 2, "price": 100 },
        { "symbol": "NVDA", "side": "sell", "quantity": 1, "price": 125 }
      ]
    }
  ]
}
```

## Founder Decision

Pass RC2D locally only if:

- No fabricated data appears.
- Existing dashboard workflows still work.
- New RC2D fields are additive and backward-compatible.
- Known unavailable states are transparent.
