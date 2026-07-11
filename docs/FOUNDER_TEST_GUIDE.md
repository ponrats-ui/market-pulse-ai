# Founder Test Guide

## Setup

1. Start backend from D:\market-pulse-ai\backend.
2. Start frontend from D:\market-pulse-ai\frontend.
3. Open the local frontend URL shown by Vite.
4. Keep browser developer tools open and watch for console or network errors.

## Asset Search Checklist

Test these queries and confirm results are real supported assets or transparent unavailable states:

- NVDA
- AMD
- TSM
- PTT
- TTB
- AOT
- KBANK
- ทอง
- น้ำมัน
- QQQ
- TLT
- VNQ
- SOXX
- RKLB, expected: no supported asset result

## Dashboard Checklist

- Change category.
- Change industry/sector when available.
- Search within the selected universe.
- Select an asset and confirm price, source, timestamp, chart, risk, financials, news, and analysis update.
- Confirm unavailable data is labelled transparently and never shown as fake data.

## Compare Checklist

- NVDA vs AMD
- BTC-USD vs ETH-USD
- BTC-USD vs GLD
- QQQ vs TLT vs VNQ

Confirm comparison data loads without UI errors and missing metrics remain transparent.

## Portfolio Checklist

- Enter holdings.
- Confirm market value updates from quote data when available.
- Confirm cash/position/risk fields do not fabricate unavailable data.
- Confirm invalid or empty portfolio input is handled gracefully.

## News And Calendar Checklist

- News: NVDA, BTC-USD, PTT.BK
- Calendar: open economic calendar panel
- Confirm any unavailable provider data is clearly labelled.

## Assistant And AI Checklist

- Ask about NVDA risk.
- Ask about BTC-USD trend.
- Confirm the answer separates facts, interpretation, risks, action plan, and disclaimer.
- Confirm it avoids guaranteed predictions or direct buy/sell promises.

## Relax Mode Checklist

- Confirm music never autoplays.
- Open the music panel.
- Play only after explicit user action.
- Confirm mute, volume, close, and original YouTube link behavior.
- Confirm the panel does not block dashboard navigation.

## Responsive Checklist

Test desktop, tablet, and mobile widths:

- No overlapping cards.
- No broken navigation.
- Search remains keyboard accessible.
- Compact panels remain readable.

## Thai Summary

คู่มือนี้ใช้ตรวจรับจากมุมมองผู้ก่อตั้ง โดยเน้นว่าข้อมูลต้องไม่ปลอม, ระบบต้องไม่ค้าง, และทุกส่วนต้องอธิบายข้อจำกัดของข้อมูลอย่างชัดเจน
