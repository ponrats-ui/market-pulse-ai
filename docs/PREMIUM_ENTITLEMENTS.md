# Premium Entitlements

Phase E introduces a centralized entitlement architecture for future subscription states.

## Supported States

- `free`
- `premium`
- `admin`
- `disabled`

## Rules

- Core market information remains enabled for free users.
- Premium-only convenience features require `premium` or `admin`.
- `disabled` blocks all features, including core features.
- Unknown features are denied by default.
- Payment status is always reported as disabled in Phase E.

## Backend Contracts

- `GET /api/premium/entitlements`
- `POST /api/premium/entitlements/check`
- `GET /api/subscription/features`

The application should call the entitlement service rather than hardcoding plan checks throughout UI or business logic.

## Thai Summary

ระบบสิทธิ์ถูกออกแบบให้รวมศูนย์ เพื่อให้เพิ่ม Premium ได้ในอนาคตโดยไม่กระจายเงื่อนไขไปทั่วโค้ด สถานะ `disabled` จะปิดการเข้าถึงทั้งหมด และ Phase E ยังไม่เปิดรับชำระเงิน.
