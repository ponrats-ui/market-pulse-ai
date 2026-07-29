# RC5A.1.1 Production Stability Report

## Summary

RC5A.1.1 is a production incident hotfix for Render restart loops and intermittent HTTP 502 responses affecting `/health` and `/api/opportunities/penny`.

Founder Acceptance remains PENDING.

## Root Cause

The FastAPI lifespan handler started the Penny Opportunity scheduler during application startup. The scheduler immediately executed `run_penny_scan_once`, which could perform provider work before any HTTP request.

That startup path violated the production startup policy:

- No full market scans during startup.
- No provider downloads during startup.
- `/health` must remain lightweight and independent from market providers.

RC5A.1 also hardened the penny engine path, but Data Hub and direct provider paths could still bypass the new provider symbol mapper. A direct or resolved request for a Thai foreign-board symbol such as `AOT-F.BK` could still reach Yahoo Finance outside the penny registry prefilter.

## Execution Graph

### Pre-Hotfix Startup Path

| Stage | File | Function | Caller | Callee | Purpose |
| --- | --- | --- | --- | --- | --- |
| Uvicorn startup | Runtime | `uvicorn app.main:app` | Render | FastAPI app import | Start ASGI app |
| FastAPI lifespan | `backend/app/main.py` | `lifespan` | FastAPI | `register_penny_opportunity_engine` | Register opportunity engine |
| FastAPI lifespan | `backend/app/main.py` | `lifespan` | FastAPI | `start_penny_opportunity_scheduler` | Start background scheduler |
| Scheduler | `backend/app/opportunities/scheduler.py` | `OpportunityScheduler.start` | Penny service | background thread `loop` | Run scan loop |
| Scheduler loop | `backend/app/opportunities/scheduler.py` | `loop` | background thread | `scan()` | Immediate first scan |
| Penny scan | `backend/app/services/penny_opportunities.py` | `run_penny_scan_once` | scheduler | `build_penny_opportunities` | Build snapshot |
| Candidate scan | `backend/app/services/penny_opportunities.py` | `build_penny_opportunities` | scan once | `_scan_quote_map`, `_evaluate_registry_asset` | Candidate provider work |
| Provider lookup | `backend/app/services/penny_opportunities.py` | `_scan_quote_map` | penny engine | `get_provider("yfinance")` | Select Yahoo provider |
| Yahoo batch | `backend/app/providers/yfinance_provider.py` | `get_scan_quotes` | penny engine | `yf.download` | Batch quote download |
| Yahoo per-symbol | `backend/app/providers/yfinance_provider.py` | `get_quote`, `get_history`, `get_financials` | provider router or penny engine | `yf.Ticker`, `ticker.history` | Live provider data |

### Post-Hotfix Startup Path

| Stage | File | Function | Caller | Callee | Purpose |
| --- | --- | --- | --- | --- | --- |
| Uvicorn startup | Runtime | `uvicorn app.main:app` | Render | FastAPI app import | Start ASGI app |
| FastAPI lifespan | `backend/app/main.py` | `lifespan` | FastAPI | `register_penny_opportunity_engine` | Register metadata only |
| HTTP health | `backend/app/main.py` | `health` | HTTP request | none | Return static health payload |

No Yahoo Finance call is reachable from startup or `/health` after the hotfix.

## Yahoo Entry Points

| Entry Point | File | Guard |
| --- | --- | --- |
| Data Hub quote/history/fundamentals | `backend/app/data_hub/provider_router.py` via `resolve_symbol` | `ProviderSymbolMapper` rejects unsupported Thai provider symbols before provider selection |
| Penny batch scan quotes | `backend/app/services/penny_opportunities.py` then `backend/app/providers/yfinance_provider.py` | Penny registry prefilter and provider final guard |
| Direct yfinance provider methods | `backend/app/providers/yfinance_provider.py` | `_provider_safe_symbol` rejects unsupported Thai foreign-board/special-board symbols before `yf.download`, `yf.Ticker`, or `ticker.history` |

## Crash Loop Analysis

The local repository proves the application previously started a provider-heavy scan in the lifespan path. This can explain Render instability because startup/background provider work may block resources, trigger Yahoo retry or delisted-symbol noise, and keep the process under pressure even while `/health` is otherwise lightweight.

The exact Render termination signal cannot be proven from local repository state alone. The most likely mechanisms are provider blocking, resource exhaustion, or process timeout caused by startup/background scan work. The hotfix removes that startup provider path entirely.

## Fix

- Removed automatic Penny Opportunity scheduler startup from FastAPI lifespan.
- Kept opportunity engine registration during startup.
- Added Data Hub provider symbol mapping before provider selection.
- Added final yfinance provider guards for quote, history, financials, and scan quote paths.
- Added tests proving startup and health do not call Yahoo.
- Added tests proving Thai foreign-board symbols do not reach provider calls.

## Validation

Required validation:

- Backend tests.
- Frontend build.
- Startup smoke.
- Health smoke.
- Direct production simulation that imports the app, enters lifespan, and verifies `/health`.

## Thai Summary

สาเหตุหลักคือระบบเริ่ม background scheduler สำหรับ Penny Opportunity ตอน FastAPI startup ทำให้มีโอกาสเรียก Yahoo Finance ก่อนหรือโดยไม่ต้องมี HTTP request การแก้ไขนี้ทำให้ startup ทำเฉพาะการลงทะเบียน metadata และไม่สแกนตลาดสด พร้อมเพิ่ม guard กลางเพื่อไม่ให้สัญลักษณ์หุ้นไทยกระดานต่างประเทศ เช่น `AOT-F.BK` ไปถึง Yahoo Finance
