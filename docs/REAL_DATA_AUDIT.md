# Real Data Audit

## Summary

- Generated frontend market values removed: 9 exported fallback objects/functions.
- Generated chart curves removed: 2 generated series.
- Invented news/calendar/sentiment backend outputs removed: 3 endpoints.
- Real providers connected: 1 (`yfinance` through Yahoo Finance).

## Replacements

| File | Old source | New source | Remaining limitations |
| --- | --- | --- | --- |
| Previous frontend generated-data module | Generated frontend prices, charts, analysis, news, sentiment, and calendar data | `frontend/src/data/unavailableData.ts` with explicit unavailable states | Static frontend needs `VITE_API_BASE_URL` for live backend data |
| `frontend/src/lib/api.ts` | Generated fallback payloads on API failure | Unavailable fallback payloads on API failure | Backend URL must be configured for live data |
| `backend/app/services/calendar.py` | Curated future event list | Provider-not-configured response | Economic calendar provider not selected |
| `backend/app/services/sentiment.py` | Generated sentiment score | Provider-not-configured response | Sentiment provider not selected |
| `backend/app/main.py` news endpoint | Invented headline provider | Provider-not-configured response | News provider not selected |
| `backend/app/providers/yfinance_provider.py` | Text for unavailable financial trends | `None` for values not returned by provider | Statement history normalization remains future work |
| `backend/app/services/analysis.py` | Text implying unavailable technical levels existed | Explicit unavailable support/resistance state | Technical level calculation remains future work |
| `frontend/src/main.tsx` | UI fallbacks that implied values or generated sources | Unavailable states and source labels | Portfolio needs batch quotes for all holdings |

## Verification Targets

- Production UI must not display banned generated-data labels.
- Charts must render only real historical points from the backend.
- News, sentiment, and calendar sections must show provider-not-configured until real integrations exist.

## Thai Summary

รอบนี้ลบข้อมูลที่สร้างขึ้นเองออกจาก UI และ backend แล้วเปลี่ยนเป็นสถานะไม่พร้อมใช้งานอย่างชัดเจน ข้อมูลราคาจริงและกราฟจริงยังมาจาก Yahoo Finance ผ่าน backend เมื่อเชื่อมต่อได้
