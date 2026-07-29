# RC5A.1 Production Diagnostics

## Incident

Production Render health checks were reachable, but the Thai Emerging Opportunities endpoint could return HTTP 502 under load:

```text
GET /api/opportunities/penny?market=TH
```

Provider logs showed many Yahoo Finance requests for Thai foreign-board symbols such as `ACAP-F.BK`, `ABM-F.BK`, and `88TH-F.BK`. Yahoo Finance often reports these as unavailable or possibly delisted.

## Root Cause

The RC5A scanner trusted registry `provider_symbols["yfinance"]` directly. That allowed foreign-board and special-board Thai symbols to enter the default Thai common-share universe and reach Yahoo Finance.

The scanner also had two production lifecycle risks:

- The scheduled scan starts during FastAPI lifespan startup and can be expensive on a cold Render instance.
- `GET /api/opportunities/penny` performed a synchronous live scan when `max_price` was supplied.

Together, invalid provider symbols plus unbounded provider work could exceed production request or cold-start limits.

## Hotfix

RC5A.1 hardens the pipeline:

- Added a reusable Data Hub provider symbol mapper.
- Normalized Thai common shares to Yahoo Finance `.BK` symbols.
- Excluded `-F` foreign-board and special-board symbols before provider calls.
- Added scan symbol limits, provider batch limits, and scan deadline diagnostics.
- Made the public endpoint snapshot-first for default and custom threshold requests.
- Returned transparent statuses such as `not_ready`, `scan_in_progress`, `partial`, and `stale` instead of starting unbounded request-time scans.

## Status Semantics

| Status | Meaning |
| --- | --- |
| `ok` | Snapshot is available and current enough for display. |
| `partial` | Snapshot is available but some provider work failed, timed out, or the requested threshold exceeds the latest published scan threshold. |
| `stale` | Reserved for future explicit stale-only response handling. |
| `not_ready` | No successful snapshot exists and the endpoint will not run a full live scan inside the request. |
| `provider_unavailable` | Reserved for provider outage classification when no snapshot exists. |
| `scan_in_progress` | Initial or scheduled scan is running and no successful snapshot exists yet. |

## Production Verification Targets

- `GET /health`
- `GET /api/opportunities/penny?market=TH`
- `GET /api/opportunities/penny?market=TH&max_price=7.5`
- `GET /api/opportunities/penny/algorithm`

The endpoint may return an empty `items` array when no snapshot exists. That is acceptable only when the response explicitly states why and does not fabricate candidates.

## Thai Summary

ปัญหาเกิดจาก engine ส่งสัญลักษณ์หุ้นไทยบางประเภท เช่น `-F` ไปยัง Yahoo Finance ทั้งที่ไม่ใช่หุ้นสามัญในจักรวาล Thai Emerging Opportunities เริ่มต้น การแก้ไขนี้เพิ่มชั้น map symbol กลาง ตัดสัญลักษณ์ที่ไม่รองรับก่อนเรียก provider จำกัดขนาดงานสแกน และทำให้ API อ่าน snapshot เป็นหลักแทนการสแกนสดใน request ของผู้ใช้
