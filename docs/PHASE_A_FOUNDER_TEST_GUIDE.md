# Phase A Founder Test Guide

## Local Setup

Run backend:

```bash
cd D:\market-pulse-ai\backend
.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Run frontend:

```bash
cd D:\market-pulse-ai\frontend
npm.cmd run dev
```

Open:

```text
http://127.0.0.1:5173
```

## API Smoke Checklist

- `GET /health`
- `GET /api/data-hub/status`
- `GET /api/data-hub/resolve?q=TTB`
- `GET /api/data-hub/resolve?q=TTB.BK`
- `GET /api/data-hub/resolve?q=KBANK`
- `GET /api/data-hub/resolve?q=AOT`
- `GET /api/data-hub/resolve?q=RKLB`
- `GET /api/data-hub/assets/TTB.BK/capabilities`
- `GET /api/data-hub/universe/metadata`
- `GET /api/assets/search?q=TTB`
- `GET /api/compare?symbols=TTB,TTB.BK,RKLB`
- `GET /api/news?symbol=TTB&limit=5`
- `GET /api/analysis/TTB`
- `GET /api/risk/TTB`
- `POST /api/portfolio/evaluate` with both `TTB` and `TTB.BK`

## Browser Checklist

- Search `TTB`; confirm it resolves to `TTB.BK` when visible under the current filters.
- Search `KBANK`; confirm it resolves to `KBANK.BK`.
- Search `AOT`; confirm it resolves to `AOT.BK`.
- Search `RKLB`; confirm it is not shown as a supported asset.
- Compare `TTB` and `TTB.BK`; confirm only one canonical comparison asset is evaluated.
- Portfolio with `TTB` and `TTB.BK`; confirm one canonical position.
- Confirm Dashboard, Watchlist, News, Fundamentals, Risk, AI Committee, and PIA Assistant do not fabricate unavailable data.
- Confirm browser console has no current errors.

## Ingestion Checklist

Run:

```bash
python scripts/update_exchange_master.py --dry-run
python scripts/update_exchange_master.py --validate
```

Expected without source files: the script reports that no verified sources were found and does not modify `configs/exchange_master.json`.

## Thai Summary

ให้ตรวจว่า `TTB`, `TTB.BK`, `KBANK`, และ `AOT` ใช้ canonical symbol ถูกต้องทุกโมดูล และ `RKLB` ยังไม่ถูกแสดงเป็นสินทรัพย์ที่รองรับจนกว่าจะเพิ่มเข้าจักรวาลข้อมูลอย่างถูกต้อง
