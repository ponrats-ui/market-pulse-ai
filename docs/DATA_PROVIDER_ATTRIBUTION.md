# Data Provider Attribution

Market Pulse AI uses provider abstractions so data sources can evolve over time. Data availability depends on provider configuration and provider limits.

## Current Providers

Primary market data:

- Yahoo Finance through `yfinance`

Prepared optional providers:

- Finnhub
- Alpha Vantage
- FRED
- NewsAPI
- Trading Economics
- RSS feeds
- Alternative.me Fear and Greed Index

Hosting and platform providers:

- Cloudflare Pages for frontend hosting
- Render for backend hosting
- YouTube for optional Relax Mode embeds

## Provider Limitations

Providers may return delayed, incomplete, rate-limited, stale, or unavailable data. Market Pulse AI must display transparent unavailable states instead of fabricated values.

## Delayed Data

Some quotes, prices, fundamentals, index values, macro values, or news items may be delayed. Users should confirm real-time market information with official exchanges, brokers, or paid professional data providers.

## Incomplete Fundamentals

Financial statement analysis may be incomplete for some assets. Crypto, commodities, indices, FX, macro instruments, and bond yields do not have traditional company financial statements.

## Economic Calendar Limitations

Economic calendar data may be static, provider-limited, or unavailable unless a supported provider is configured. Calendar events should be verified with official central bank, government, or exchange sources.

## News Limitations

News availability depends on configured providers and source permissions. News impact analysis may be unavailable or limited when no live provider is configured. Market Pulse AI does not fabricate news items.

## Attribution Display

The application should show source, timestamp, provider status, unavailable reasons, and disclaimers where applicable.

## Thai Summary

ข้อมูลตลาดมาจากผู้ให้บริการภายนอก เช่น Yahoo Finance ผ่าน yfinance และ provider อื่นที่อาจตั้งค่าในอนาคต ข้อมูลอาจล่าช้า ไม่ครบถ้วน หรือไม่พร้อมใช้งาน ระบบต้องแสดงสถานะ unavailable อย่างโปร่งใสและไม่สร้างข้อมูลปลอม.
