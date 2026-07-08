# API Provider Roadmap

## Market Data

Current provider: yfinance.

Future options:

- Polygon.io
- Twelve Data
- Alpha Vantage
- Finnhub
- Exchange-native APIs

## News

Provider interface added in Sprint 3:

- `backend/app/providers/news_base.py`
- future news provider implementation file

Future options:

- Finnhub
- NewsAPI
- Alpha Vantage News
- GDELT
- RSS feeds

## Economic Calendar

Future options:

- Trading Economics
- Financial Modeling Prep
- Nasdaq calendar feeds
- Curated official central bank and statistics-office RSS feeds

## AI

Sprint 3 uses rule-based Q&A. A future LLM provider should be isolated behind a service interface and must preserve disclaimers, uncertainty, and risk controls.

## Thai Summary

Sprint 3 วางโครงสร้าง provider สำหรับข้อมูลข่าวและ AI ในอนาคต โดยยังไม่ใส่ API key หรือบริการเสียเงินลงใน repository
