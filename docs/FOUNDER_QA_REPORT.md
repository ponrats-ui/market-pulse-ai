# Founder QA Report

## Scope

This report covers the V1 Founder Production Release Candidate on branch feature/founder-production-final. The sprint stabilizes and completes the existing product direction without merge, deployment, push, or tag actions.

## Functional QA

| Area | Result | Notes |
| --- | --- | --- |
| Asset Search | Pass | TTB and AOT resolve to .BK symbols; RKLB returns no unsupported asset; Thai search for ทอง returns metals/ETF results. |
| Dashboard | Pass | Build and API smoke paths are healthy. |
| Compare | Pass | BTC-USD vs ETH-USD and NVDA vs AMD return HTTP 200. |
| Portfolio | Pass | Portfolio evaluation endpoint accepts holdings payload and returns HTTP 200. |
| News | Pass with limitation | Endpoint returns HTTP 200; unavailable provider data must remain transparent. |
| Calendar | Pass with limitation | Endpoint returns HTTP 200; live provider gaps are disclosed. |
| Risk | Pass | Risk endpoint returns HTTP 200. |
| Financials | Pass | Financial endpoint returns HTTP 200; non-equity assets should show not applicable when relevant. |
| Assistant | Pass | /api/assistant/ask returns HTTP 200 with conservative educational flow. |
| Relax Mode | Pass by config review | Optional YouTube embed source is configurable; no autoplay behavior is required. |

## Data Integrity QA

- No mock market values were added.
- Unsupported symbol RKLB is not returned by curated search.
- Search results are limited to the curated provider-ready universe.
- Config files were cleaned to UTF-8 Thai and English labels.

## Encoding QA

Command scan found only expected negative assertions in tests:

- backend/tests/test_analysis_engine.py asserts mojibake markers are absent from generated output.

No active mojibake was found in app source, frontend source, or configs during the scan.

## Build And Test QA

- Backend: 44 passed
- Frontend: production build passed
- Focused asset universe tests: 7 passed
- Smoke: all listed local endpoints returned 200

## Thai Summary

ผ่าน QA สำหรับ Founder Test โดยเน้นความถูกต้องของข้อมูลจริง การค้นหาสินทรัพย์แบบไม่เดาสุ่ม และการแสดงผลอย่างระมัดระวังสำหรับข้อมูลที่ยังไม่มี provider สด

## QA Decision

READY FOR FOUNDER TEST
