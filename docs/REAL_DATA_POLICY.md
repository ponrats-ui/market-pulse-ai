# Real Data Policy

Market Pulse AI must never fabricate financial data, news, sentiment, or AI evidence.

## Providers

- Yahoo Finance: configured for quotes, historical prices, and available fundamentals through `yfinance`.
- Finnhub: not configured.
- FRED: not configured.
- Alpha Vantage: not configured.
- News provider: not configured.
- Sentiment provider: not configured.
- Economic calendar provider: not configured.

## Display Rules

- If real provider data exists, display it with source and timestamp.
- If provider data is unavailable, display an unavailable state.
- If financial statements do not apply to an asset class, state that the asset does not publish corporate financial statements.
- If a provider fails, do not replace the result with generated market values.

## Remaining Limitations

- Static Cloudflare Pages deployments without `VITE_API_BASE_URL` cannot fetch live backend data.
- News, sentiment, and economic calendar integrations require provider selection and credentials.
- Technical support and resistance levels remain unavailable until calculated from historical prices.

## Thai Summary

Market Pulse AI ต้องใช้ข้อมูลจริงเท่านั้น หากยังไม่มีผู้ให้บริการข้อมูล ระบบต้องแสดงว่าไม่พร้อมใช้งาน ไม่สร้างราคา ข่าว sentiment หรือหลักฐานประกอบ AI ขึ้นเอง
