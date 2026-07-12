# Phase E Founder Test Guide

## Goal

Confirm that Premium architecture is prepared safely without changing the core product experience or sending real notifications.

## Local Setup

1. Run the backend.
2. Run the frontend.
3. Confirm the existing dashboard still loads normally.

## API Checklist

- `GET /api/subscription/features`
- `GET /api/premium/entitlements`
- `POST /api/premium/entitlements/check`
- `POST /api/alerts/evaluate`
- `POST /api/digests/build`

## Entitlement Checks

- Free users can access core market features.
- Free users cannot access premium-only alerts.
- Premium users can access premium convenience features.
- Disabled state blocks access.

## Alert Checks

- Price move rule triggers when threshold is crossed.
- Quiet hours suppress notifications.
- Duplicate rule evaluation does not create duplicate notifications.
- Delivery status remains `provider_unavailable`.
- No outbound message is sent.

## Digest Checks

- Morning brief can be generated.
- Evening wrap can be generated.
- Weekly portfolio summary can be generated.
- Generated digests show `sent: false`.

## Browser Walkthrough

- Dashboard
- Asset search
- Chart
- Risk
- Financials
- News
- Compare
- Portfolio
- Watchlist
- PIA Assistant
- Relax Mode
- Language switch

## Thai Summary

Founder Test สำหรับ Phase E ให้ตรวจว่าระบบ Premium/Alerts เป็นเพียงโครงสร้าง ยังไม่ส่งแจ้งเตือนจริง ไม่เปิดชำระเงิน และไม่กระทบการใช้งานตลาดหลักของผู้ใช้ฟรี.
