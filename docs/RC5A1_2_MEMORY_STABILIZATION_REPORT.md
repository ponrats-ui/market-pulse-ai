# RC5A.1.2 Production Memory Stabilization Report

## Incident

Render Events confirmed the production backend exceeded the 512 MB memory limit:

```text
Ran out of memory (used over 512MB) while running your code.
```

This report documents the memory investigation and hotfix for RC5A.1.2.

Founder Acceptance remains PENDING.

## Memory Allocation Report Before Changes

Measured on Windows using process working set and pagefile counters in fresh Python processes.

| Scenario | RSS | Pagefile / Private Allocation | Notes |
| --- | ---: | ---: | --- |
| Fresh Python process | 14.9 MB | 8.0 MB | Baseline |
| `import app.main` | 115.6 MB | 572.0 MB | Eager provider import path loaded heavy provider stack |
| FastAPI lifespan + `/health` | 116.1 MB | 572.3 MB | Same as import; no provider calls, but provider libraries already loaded |
| Master registry load | 41.8 MB | 34.0 MB | 13,577 registry assets |
| Search after registry load | 41.9 MB | 35.1 MB | Registry is not the largest startup allocation |
| Penny snapshot with no scan | 115.5 MB | 571.7 MB | Import path dominated memory |
| Bounded fake 160-candidate scan | 120.3 MB | 576.5 MB | Stub provider scan; still dominated by eager provider imports |

## Root Cause of Memory Growth

The largest confirmed startup allocation was eager loading of the Yahoo provider stack:

```text
app.main
-> app.data_hub.provider_router
-> app.providers.registry
-> app.providers.yfinance_provider
-> import pandas
-> import yfinance
```

This happened even when the application only needed startup, `/health`, or snapshot-first unavailable responses. The heavy provider libraries were loaded before any real market-data request.

Secondary memory pressure risks:

- `TTLCache` had no maximum entry cap, so repeated quote/history/fundamental requests could accumulate until TTL expiry.
- Snapshot storage uses defensive deep copies. This preserves immutability but can temporarily duplicate snapshot payloads during publish and read. Current Top 5 snapshot size is small, so this was not the primary Render memory trigger.
- Full master registry loading stores 13,577 assets, but measured RSS was much lower than eager provider imports.

## Execution Path Classification

### Startup

Post RC5A.1.1 startup no longer runs full scans, but before RC5A.1.2 it still imported provider libraries eagerly through module imports.

### Background Scan

Automatic startup scanning was removed in RC5A.1.1. Manual or future scheduled scans remain bounded by symbol limit, provider batch limit, worker cap, and deadline.

### Request Handling

Market-data requests still load provider libraries when they actually need Yahoo Finance. This preserves behavior while avoiding provider memory cost for health, metadata, and snapshot-first endpoints.

### Snapshot Generation

Snapshot generation remains bounded and snapshot-first. It does not run from startup or `/health`.

## Hotfix

- Made `pandas` and `yfinance` lazy-loaded in `backend/app/providers/yfinance_provider.py`.
- Kept the public yfinance provider API unchanged.
- Replaced `pandas.isna` in scalar parsing with lightweight `math.isnan` conversion.
- Added a bounded maximum entry count to `TTLCache`.
- Added regression tests proving `app.main` import does not load `pandas` or `yfinance`.
- Added regression tests proving cache entries evict when the configured bound is exceeded.

## Memory Allocation Report After Changes

| Scenario | RSS | Pagefile / Private Allocation | Notes |
| --- | ---: | ---: | --- |
| Fresh Python process | 14.9 MB | 8.0 MB | Baseline |
| `import app.main` | 49.9 MB | 38.9 MB | `pandas` and `yfinance` not loaded |
| FastAPI lifespan + `/health` | 52.6 MB | 40.9 MB | Startup remains lightweight |
| Master registry load | 41.8 MB | 34.3 MB | Unchanged, acceptable |
| Search after registry load | 41.7 MB | 33.9 MB | Unchanged, acceptable |
| Penny snapshot with no scan | 50.0 MB | 38.8 MB | Snapshot-first endpoint avoids provider imports |
| Bounded fake 160-candidate scan | 54.6 MB | 43.4 MB | Stub provider scan avoids provider imports |

## Before / After

| Path | Before RSS | After RSS | Before Pagefile | After Pagefile |
| --- | ---: | ---: | ---: | ---: |
| `import app.main` | 115.6 MB | 49.9 MB | 572.0 MB | 38.9 MB |
| FastAPI lifespan + `/health` | 116.1 MB | 52.6 MB | 572.3 MB | 40.9 MB |
| Penny snapshot with no scan | 115.5 MB | 50.0 MB | 571.7 MB | 38.8 MB |

## Remaining Memory Notes

Real Yahoo Finance requests will still load `pandas` and `yfinance` at first use. That is expected and preserves product behavior. The important production change is that health, startup, registry metadata, and snapshot-first opportunity responses no longer pay that memory cost.

Future provider-performance work may move live provider requests to a separate worker or external job queue, but that is outside this hotfix.

## Thai Summary

สาเหตุหลักของ memory growth คือ backend import `pandas` และ `yfinance` ตั้งแต่เริ่มโหลด `app.main` แม้ยังไม่ได้เรียกข้อมูลตลาดจริง การแก้ไขนี้เปลี่ยนให้โหลด provider library แบบ lazy เฉพาะตอนมี request ที่ต้องใช้ Yahoo Finance และเพิ่มขนาดสูงสุดให้ cache เพื่อลดการสะสมข้อมูลใน memory
