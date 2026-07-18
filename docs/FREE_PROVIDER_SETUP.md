# Free Provider Setup

## Environment Variables

Add credentials only in local or deployment environment settings:

```env
FRED_API_KEY=
FINNHUB_API_KEY=
ALPHA_VANTAGE_API_KEY=
NEWSAPI_KEY=
TRADING_ECONOMICS_KEY=
NEWS_RSS_URL=
ENABLE_YAHOO_FINANCE_NEWS=true
ENABLE_ALTERNATIVE_ME_FEAR_GREED=false
```

## Notes

- yfinance requires no API key but can be delayed, throttled, or incomplete.
- Yahoo Finance RSS can be enabled without credentials through `ENABLE_YAHOO_FINANCE_NEWS=true`.
- Alternative.me sentiment is opt-in through `ENABLE_ALTERNATIVE_ME_FEAR_GREED=true`.
- Trading Economics transport remains unavailable until a reliable integration is enabled.

## Thai Summary

ใส่ API keys เฉพาะใน environment ของเครื่องหรือระบบ deploy เท่านั้น ห้าม commit keys จริงลง git
