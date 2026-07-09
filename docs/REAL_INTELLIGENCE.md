# Real Intelligence Providers

## Purpose

RC2C replaces placeholder intelligence surfaces with provider abstractions that can return real-world data when configured and transparent unavailable states when not configured.

Thai summary: RC2C ไม่สร้างข่าว เหตุการณ์ หรือข้อมูลเศรษฐกิจปลอม หากยังไม่ได้ตั้งค่าผู้ให้บริการ ระบบจะแสดงสถานะ unavailable พร้อมเหตุผลอย่างโปร่งใส

## Providers

### News

Provider abstraction lives in `backend/app/providers/news`.

Supported provider classes:

- Yahoo Finance News RSS
- Generic RSS
- Finnhub News
- Alpha Vantage News
- NewsAPI

Runtime behavior:

- Providers are tried through `NewsAggregator`.
- Unconfigured providers are skipped.
- The first configured provider that returns articles wins.
- If no provider returns articles, the API returns an empty list with provider status and unavailable reason.

Configuration:

- `ENABLE_YAHOO_FINANCE_NEWS=true` enables Yahoo Finance RSS.
- `NEWS_RSS_URL=` enables a custom RSS feed. Use `{query}` as the query placeholder.
- `FINNHUB_API_KEY=`
- `ALPHAVANTAGE_API_KEY=`
- `NEWSAPI_KEY=`

API:

- `GET /api/news?symbol=NVDA&limit=10`
- `GET /api/news-impact/{symbol}`

## News Classification

Every returned article is classified from provider-returned article text only.

Current categories:

- Earnings
- Guidance
- M&A
- Dividend
- Product Launch
- AI
- Semiconductor
- Energy
- Defense
- Healthcare
- Government
- Macroeconomics
- Central Bank
- Supply Chain
- Regulation
- Geopolitics

Impact fields:

- Immediate Impact
- Short-Term Impact
- Long-Term Impact
- Direction: Bullish, Neutral, or Bearish
- Affected Assets
- Affected Sector
- Importance
- Confidence
- Evidence

If evidence is insufficient, classification remains neutral or unavailable.

## Economic Calendar

Provider abstraction lives in `backend/app/providers/calendar`.

Current provider shell:

- TradingEconomics

Only high-impact event types should be returned:

- FOMC
- CPI
- PPI
- NFP
- ECB
- BOJ
- BOE
- GDP
- Rate Decision

If no provider is configured, `/api/calendar` returns an empty event list and an unavailable reason.

## Fear & Greed

Provider abstraction lives in `backend/app/providers/sentiment`.

Current behavior:

- `GET /api/sentiment/{symbol}` returns unavailable status unless a real provider is configured later.
- The system never estimates Fear & Greed.

## Macro Data

Provider abstraction lives in `backend/app/providers/macro`.

Planned supported indicators:

- FRED
- US Rates
- Inflation
- Unemployment
- Yield Curve
- Dollar Index
- Oil
- Gold
- VIX

Current endpoint:

- `GET /api/macro`

If no macro provider is configured, the endpoint returns an unavailable status and the supported indicator list.

## Company Events

Provider abstraction lives in `backend/app/providers/company_events`.

Planned event types:

- Earnings
- Dividend
- Split
- Guidance
- Buyback
- Insider
- M&A
- SEC Filing

Current endpoint:

- `GET /api/company-events/{symbol}`

If no provider is configured, the endpoint returns an unavailable status and no events.

## Fallback

News uses ordered fallback. Other provider categories currently expose a single provider shell and transparent unavailable status.

Provider responses include:

- Provider
- Timestamp
- Cache Age
- Confidence
- Unavailable Reason
- Provider Configured

## Caching

Real intelligence endpoints use the shared TTL cache.

Current TTL:

- `INTELLIGENCE_TTL_SECONDS = 900`

This keeps provider calls bounded and prepares the backend for provider rate limits.

## Rate Limits

Provider adapters should respect each provider's published limits. API keys must never be committed to git. Providers should prefer cache hits, backoff on failures, and return unavailable status instead of retry loops that could exhaust quota.

## API Compatibility

Existing endpoints remain available:

- `/api/news-impact/{symbol}`
- `/api/calendar`
- `/api/sentiment/{symbol}`
- `/api/analysis/{symbol}`

New endpoints:

- `/api/news`
- `/api/macro`
- `/api/company-events/{symbol}`

`/api/analysis/{symbol}` now includes `real_intelligence` provider status for news, calendar, sentiment, macro, and company events.

## Limitations

- API transports for paid-key providers are intentionally not activated until credentials and provider terms are configured.
- News classification is rule-based and conservative.
- Macro, company events, and Fear & Greed currently return transparent unavailable payloads.
- No fabricated news, calendar, sentiment, macro, or company event data is returned.
