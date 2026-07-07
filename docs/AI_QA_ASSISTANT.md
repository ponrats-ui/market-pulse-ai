# AI Q&A Assistant

Sprint 3 adds a rule-based AI assistant endpoint.

## Endpoint

`POST /api/assistant/ask`

Request:

```json
{
  "question": "BTC ตอนนี้เสี่ยงไหม",
  "selected_symbol": "BTC-USD",
  "language": "th"
}
```

## Behavior

- Uses real quote, risk, and analysis data when available.
- Separates facts from interpretation in the answer text.
- Explains uncertainty and risk.
- Does not call paid AI APIs.

## Future LLM Plan

A future provider can be added behind the service boundary, with prompt safety checks and no secrets committed to git.

## Thai Summary

AI Q&A ตอนนี้เป็น rule-based และใช้ข้อมูล quote/risk/analysis จาก backend เมื่อมีข้อมูลจริง พร้อมย้ำความไม่แน่นอนและความเสี่ยงเสมอ
