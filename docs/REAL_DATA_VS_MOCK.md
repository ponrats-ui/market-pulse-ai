# Real Data vs Mock Data

## Real Data Now

- Quote price: yfinance
- Historical prices: yfinance
- OHLC chart fields: yfinance history
- Volume: yfinance when available
- Market cap: yfinance when available
- Financial statement basics: yfinance when available
- Asset comparison: real quote and history endpoints

## Mock or Placeholder Now

- News impact: mock provider until a news source is configured
- Economic calendar: curated placeholder events
- Fear & Greed and market sentiment: mock sentiment service
- AI Q&A: rule-based response, no paid AI API

## Why Mock Data Remains

Some services require paid credentials, rate-limited keys, or licensing review. Sprint 3 creates provider interfaces without committing secrets.

## Thai Summary

ข้อมูลราคา กราฟย้อนหลัง และการเปรียบเทียบสินทรัพย์ใช้ข้อมูลจริงจาก backend เมื่อเชื่อมต่อได้ ส่วนข่าว ปฏิทินเศรษฐกิจ sentiment และ AI Q&A ยังเป็น mock หรือ rule-based เพื่อหลีกเลี่ยงการใช้ API key แบบเสียเงิน
