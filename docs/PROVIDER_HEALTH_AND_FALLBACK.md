# Provider Health And Fallback

## Health States

- `healthy`: provider is configured and returned usable data.
- `degraded`: provider is configured but failed or returned an error.
- `rate_limited`: provider failed with rate-limit wording.
- `unavailable`: provider is not configured or cannot be used.

## Tracked Fields

- configured
- healthy
- degraded
- last_success
- last_failure
- response_time_ms
- cache_usage
- failure_reason

## Fallback Rules

Provider fallback must never invent replacement values. If all providers fail, the API returns a transparent unavailable or partial response with reason metadata.

## Thai Summary

ระบบติดตามสุขภาพ provider เพื่อรู้ว่า provider ใดพร้อมใช้งาน ล้มเหลว หรือถูกจำกัด rate และต้องไม่เติมข้อมูลปลอมระหว่าง fallback
