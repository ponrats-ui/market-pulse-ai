# Production Data Providers

## Purpose

Phase B connects production data providers through the Market Pulse Data Hub without adding UI modules or fabricating values.

## Provider Priority

- Quotes and history: yfinance compatibility adapter, configured fallback provider, transparent unavailable state.
- Fundamentals: yfinance compatibility adapter, configured fundamentals provider when added, partial response with field-level provenance.
- News: Yahoo Finance RSS, optional RSS URL, Finnhub, Alpha Vantage, NewsAPI, transparent unavailable state.
- Macro: FRED when configured, transparent unavailable state.
- Calendar: configured calendar provider, transparent unavailable state.
- Crypto sentiment: Alternative.me only when explicitly enabled, transparent unavailable state.

## Runtime Configuration

All provider credentials are read from environment variables. No secrets are committed.

## Thai Summary

Phase B ใช้ provider จริงผ่าน Data Hub และต้องแสดงสถานะ unavailable อย่างโปร่งใสเมื่อไม่มีข้อมูลหรือยังไม่ได้ตั้งค่า provider
