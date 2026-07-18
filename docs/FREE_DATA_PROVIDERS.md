# Free Data Providers

## Data Honesty Policy

Market Pulse AI must never fabricate news, economic events, sentiment, macro data, company events, or market data. If a provider is unavailable, unconfigured, rate-limited, or fails, the API returns an empty data set with provider status and an unavailable reason.

## Provider Matrix

| Area | Provider | Key Required | Status | Use |
| --- | --- | --- | --- | --- |
| Prices | Yahoo Finance via yfinance | No | Integrated | Quotes and historical prices |
| News | Yahoo Finance RSS | No | Integrated, controlled by `ENABLE_YAHOO_FINANCE_NEWS` | Symbol-aware headline RSS |
| News | Generic RSS | No | Integrated when `NEWS_RSS_URL` is set | Trusted finance RSS feeds |
| News | Finnhub | Yes, `FINNHUB_API_KEY` | Shell | Company news/provider fallback |
| News | Alpha Vantage News | Yes, `ALPHA_VANTAGE_API_KEY` | Shell | News/provider fallback |
| News | NewsAPI | Yes, `NEWSAPI_KEY` | Shell | News/provider fallback |
| Macro | FRED | Yes, `FRED_API_KEY` | Small implementation | FEDFUNDS, CPI, unemployment, 10Y, 2Y |
| Calendar | TradingEconomics | Yes, `TRADING_ECONOMICS_KEY` | Shell | High-impact macro events |
| Sentiment | Alternative.me Fear & Greed | No | Opt-in implementation | Crypto Fear & Greed |
| Company Events | Finnhub | Yes, `FINNHUB_API_KEY` | Shell | Earnings/dividend/splits/future events |

## Fallback Strategy

News provider order:

1. Yahoo Finance RSS
2. Generic RSS
3. Finnhub
4. Alpha Vantage News
5. NewsAPI
6. Unavailable state

Macro, calendar, sentiment, and company events return provider-specific unavailable states until configured providers are enabled.

## Rate Limit Risks

- Free API keys can be rate-limited or throttled.
- RSS feeds can change format without notice.
- Network failures must not trigger fabricated fallback data.
- Cache TTL should be respected before retrying providers.

Current intelligence cache TTL: `900` seconds.

## Environment Variables

```env
FINNHUB_API_KEY=
ALPHA_VANTAGE_API_KEY=
FRED_API_KEY=
NEWSAPI_KEY=
TRADING_ECONOMICS_KEY=
NEWS_RSS_URL=
ENABLE_YAHOO_FINANCE_NEWS=true
ENABLE_ALTERNATIVE_ME_FEAR_GREED=false
```

Do not commit real keys.
