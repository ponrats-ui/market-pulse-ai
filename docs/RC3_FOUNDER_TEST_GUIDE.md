# RC3 Founder Test Guide

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

## Checklist

### Universal Search

Search and select:

- `Apple`
- `AAPL`
- `NVIDIA`
- `NVDA`
- `Tesla`
- `TSLA`
- `ทอง`
- `Gold`
- `Bitcoin`
- `BTC`
- `CPALL`
- `PTT`
- `TLT`
- `VOO`
- `QQQ`
- `SPY`
- `SOXX`
- `VNQ`

Expected: suggestions appear while typing, with symbol, name, market, sector, and Thai aliases when available.

### Sector Browser

Test:

- Technology
- Semiconductor
- AI
- Banking
- Energy
- REIT
- ETF
- Crypto Layer1
- Gold
- Oil

Expected: choosing a sector shows curated assets and selecting one updates the global selected asset.

### Technical Analysis

For `NVDA`, `BTC-USD`, `PTT.BK`, and `GLD`, toggle:

- EMA20
- EMA50
- EMA200
- SMA50
- SMA200
- RSI14
- MACD
- Volume
- ATR
- VWAP
- Bollinger Bands

Expected: indicators use real historical prices. If history is unavailable, the panel must say unavailable.

### Compare Engine V3

Test:

- `NVDA` vs `AMD`
- `BTC-USD` vs `GLD`
- `QQQ` vs `TLT` vs `VNQ`
- Semiconductor sector assets

Expected: table includes price, performance, volatility, market cap, PE, sector, AI summary, and real-data limitations.

### News Impact

Test:

- `NVDA`
- `BTC-USD`
- `PTT.BK`

Expected: only provider-returned news appears. No fake articles. Missing news clearly says unavailable.

### Economic Calendar

Open Economic Calendar.

Expected: real provider events appear only if configured. Without a provider, the unavailable state must be explicit.

### AI Committee

Check:

- Technical Analyst
- Fundamental Analyst
- Macro Economist
- News Analyst
- Risk Manager
- Chief Investment AI

Expected: each view explains evidence, confidence, missing information, and limitations. No guaranteed buy/sell wording.

### Fundamental Analysis

Test:

- `NVDA`
- `AAPL`
- `PTT.BK`
- `BTC-USD`
- `GLD`

Expected: stocks show provider-returned financials when available. Non-stocks explain that statements are not applicable and show alternative fundamentals.

### Risk Engine

Check category risks:

- Volatility
- Liquidity
- Gap Risk
- Interest Rate
- Macro
- Correlation
- Currency
- Concentration
- Tail Risk
- Headline Risk

Expected: each category has score, probability, severity, evidence, and mitigation.

### Paper Portfolio

Test:

- Cash balance
- Buy transaction
- Sell transaction
- Average cost
- Market value
- Unrealized P/L
- Realized P/L
- Allocation
- Risk score

Expected: calculations use live quotes when backend is available. FX conversion remains unavailable until a provider is configured.

### Translation

Switch Thai and English.

Expected: key investor-facing text is bilingual. Tickers, company names, and standard financial terms may remain English.

## API Smoke

```text
GET /health
GET /api/assets/search?q=NVDA
GET /api/assets/search?q=ทอง
GET /api/sectors
GET /api/technical/NVDA
GET /api/compare?symbols=NVDA,AMD
POST /api/portfolio/evaluate
GET /api/news?symbol=NVDA
GET /api/calendar
GET /api/analysis/NVDA
GET /api/risk/NVDA
GET /api/financials/NVDA
```

## Founder Decision

Pass only if no fake data appears and unavailable provider states are transparent.
