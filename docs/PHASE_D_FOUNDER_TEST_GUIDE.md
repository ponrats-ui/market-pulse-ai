# Phase D Founder Test Guide

## Backend Checks

Run:

```bash
cd D:\market-pulse-ai\backend
.\.venv\Scripts\python.exe -m pytest
```

## Frontend Build

Run:

```bash
cd D:\market-pulse-ai\frontend
npm.cmd run build
```

## Portfolio API Smoke

POST `/api/portfolio/evaluate` with:

- repeated buys
- partial sell
- sell all
- insufficient cash
- insufficient shares
- `TTB` and `TTB.BK` aliases
- stale quote provider simulation if testing through unit tests

## Browser Review

- Open Portfolio.
- Confirm simulated values render.
- Confirm no broker language or real-account implication appears.
- Confirm no console errors.

## Thai Summary

ให้ทดสอบพอร์ตจำลองทั้งซื้อซ้ำ ขายบางส่วน ขายทั้งหมด เงินไม่พอ หุ้นไม่พอ และ alias ของสัญลักษณ์ เพื่อยืนยันว่า accounting ถูกต้อง
