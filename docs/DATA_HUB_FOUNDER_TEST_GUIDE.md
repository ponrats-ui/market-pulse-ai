# Data Hub Founder Test Guide

## Local Setup

Run backend and frontend as usual:

```bash
cd D:\market-pulse-ai\backend
.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000

cd D:\market-pulse-ai\frontend
npm.cmd run dev
```

## API Checks

Open or request:

- `/api/data-hub/status`
- `/api/data-hub/resolve?q=TTB`
- `/api/data-hub/resolve?q=TTB.BK`
- `/api/data-hub/resolve?q=KBANK`
- `/api/data-hub/resolve?q=AOT`
- `/api/data-hub/resolve?q=RKLB`
- `/api/data-hub/assets/TTB.BK/capabilities`
- `/api/compare?symbols=TTB,TTB.BK,RKLB`
- `POST /api/portfolio/evaluate` with both `TTB` and `TTB.BK`

## Browser Checks

- Search `TTB`, confirm `TTB.BK` result.
- Search `KBANK`, confirm `KBANK.BK`.
- Search `AOT`, confirm `AOT.BK`.
- Search `RKLB`, confirm no supported asset result.
- Compare `TTB` and `TTB.BK`, confirm one canonical comparison asset.
- Portfolio with `TTB` and `TTB.BK`, confirm one canonical position.
- Confirm no fake data appears when provider fields are unavailable.

## Ingestion Checks

Run:

```bash
python scripts/update_exchange_master.py --dry-run
python scripts/update_exchange_master.py --validate
```

Expected without source files: the script reports no verified sources found and does not modify `configs/exchange_master.json`.

## Thai Summary

ให้ทดสอบว่า Search, Compare และ Portfolio ใช้ canonical symbol เดียวกัน โดยเฉพาะ `TTB` และ `TTB.BK` ต้องไม่กลายเป็นสินทรัพย์คนละตัว
