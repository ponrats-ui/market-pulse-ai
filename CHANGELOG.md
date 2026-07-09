# Changelog

All notable changes to Market Pulse AI will be documented in this file.

The format is inspired by Keep a Changelog, and this project uses human-readable release notes.

## [Unreleased]

### Changed

- Stabilized MVP API fallback behavior and cache age reporting.
- Improved dashboard empty states, source transparency, accessibility affordances, and portfolio input validation.
- Cleaned AI and unavailable-state wording in English and Thai.
- Added regression coverage for cache age reporting.
- Documented Cloudflare Pages production API environment variable setup.
- Made backend CORS origins configurable through `CORS_ALLOWED_ORIGINS`.

### Added

- RC2 professional investment platform foundation with real-data asset search, live quote batch evaluation, portfolio valuation, and enhanced comparison metrics.
- MIT license and open-source governance documents.
- Founder and project identity documentation.
- Application footer identity and About dialog.
- Render backend deployment configuration and deployment guide.
- GitHub Actions CI for backend tests and frontend build validation.
- Backend environment variable examples for production deployment.

## Sprint 2

### Added

- Thai and English localization.
- AI Investment Committee dashboard.
- Chief Investment AI summary card.
- Improved financial, news, and sentiment panels.

## Sprint 1

### Added

- Normalized yfinance market data layer.
- Provider registry and in-memory TTL cache.
- Quote, history, dashboard, analysis, risk, and financial endpoints.

## Sprint 0

### Added

- Initial React + Vite + TypeScript frontend.
- Initial FastAPI backend.
- Cloudflare Pages-ready frontend foundation.

## Thai Summary

ไฟล์นี้ใช้บันทึกการเปลี่ยนแปลงสำคัญของ Market Pulse AI เพื่อให้ผู้ใช้และผู้ร่วมพัฒนาเห็นพัฒนาการของโครงการอย่างโปร่งใส

## Sprint 3

### Added

- Real-data asset comparison endpoint and UI.
- Timeframe selector for historical chart data.
- Rule-based AI Q&A assistant.
- Portfolio analyzer with localStorage.
- Economic calendar provider-not-configured endpoint.
- News impact provider interface.
- Sentiment provider-not-configured endpoint.

## Real Data Sprint

### Changed

- Removed generated frontend market values and generated chart curves.
- Replaced unavailable news, calendar, sentiment, and frontend static fallback data with explicit unavailable states.
- Removed invented provider headlines and sentiment scores.
- Added real data policy and audit documentation.
