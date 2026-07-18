# Data Provider Routing

## Routing Policy

Provider order is configurable through environment variables:

- `DATA_HUB_QUOTE_PROVIDERS`
- `DATA_HUB_HISTORY_PROVIDERS`
- `DATA_HUB_FUNDAMENTALS_PROVIDERS`
- `DATA_HUB_NEWS_PROVIDERS`
- `DATA_HUB_CALENDAR_PROVIDERS`

Default policy:

- Quote: yfinance
- History: yfinance
- Fundamentals: yfinance
- News: Yahoo Finance RSS / configured news aggregator path
- Calendar: configured calendar provider, currently transparent unavailable without credentials

## Fallback Rules

- Do not fabricate market data.
- Do not silently substitute unsupported symbols.
- Return transparent unavailable states with provider failure reasons.
- Preserve provider failures in `data_hub.provider_failures`.

## Cache TTL

The existing in-memory TTL cache is retained:

- `DATA_HUB_QUOTE_TTL_SECONDS`, default 60
- `DATA_HUB_HISTORY_TTL_SECONDS`, default 300
- `DATA_HUB_FUNDAMENTALS_TTL_SECONDS`, default 3600
- `DATA_HUB_NEWS_TTL_SECONDS`, default 900
- `DATA_HUB_ASSET_MASTER_TTL_SECONDS`, default 300

Redis or scheduled automation is intentionally out of scope for this sprint.

## Thai Summary

Provider Router เลือกแหล่งข้อมูลตามชนิดข้อมูลและสินทรัพย์ หาก provider ล้มเหลวหรือไม่มีข้อมูล ระบบต้องแสดงสถานะ unavailable อย่างโปร่งใส และไม่เติมค่าปลอม
