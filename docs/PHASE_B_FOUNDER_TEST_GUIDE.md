# Phase B Founder Test Guide

## Local Validation

```bash
cd D:\market-pulse-ai\backend
.\.venv\Scripts\python.exe -m pytest

cd D:\market-pulse-ai\frontend
npm.cmd run build
```

## Provider Smoke

- `GET /api/data-hub/status`
- `GET /api/financials/NVDA`
- `GET /api/news?symbol=NVDA&limit=5`
- `GET /api/macro`
- `GET /api/calendar`
- `GET /api/sentiment/BTC-USD`

## Failure Simulation

- Leave `FINNHUB_API_KEY`, `ALPHA_VANTAGE_API_KEY`, `NEWSAPI_KEY`, `FRED_API_KEY`, and `TRADING_ECONOMICS_KEY` empty.
- Confirm unavailable states are explicit and no fake articles, events, fundamentals, or sentiment scores are generated.

## Thai Summary

ทดสอบโดยไม่ใส่ API keys ก่อน เพื่อยืนยันว่าระบบแสดง unavailable อย่างตรงไปตรงมาและไม่สร้างข้อมูลปลอม
