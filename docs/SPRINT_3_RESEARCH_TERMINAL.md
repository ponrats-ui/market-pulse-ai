# Sprint 3 Research Terminal

Sprint 3 upgrades Market Pulse AI into an interactive research terminal that uses real upstream market data where available and explicit unavailable states where credentials or paid APIs are normally required.

## Real Data Features

- Quotes from the yfinance provider.
- Historical OHLCV data from `/api/assets/{symbol}/history`.
- Chart timeframe selector using backend history ranges.
- Asset comparison using real quotes and historical close prices.
- Financial statement basics where yfinance exposes them.
- Portfolio valuation uses real quote data when the selected holding matches the active quote.

## Provider-Not-Configured Features

- AI Q&A response is rule-based and does not call a paid LLM.
- News impact returns provider-not-configured until a real provider is added.
- Economic calendar returns provider-not-configured until a real provider is added.
- Fear & Greed / market sentiment returns unavailable until a real provider is added.

## New Endpoints

- `GET /api/compare?symbols=BTC-USD,ETH-USD`
- `POST /api/assistant/ask`
- `GET /api/calendar`
- `GET /api/news-impact/{symbol}`
- `GET /api/sentiment/{symbol}`

## Safety

All research output must remain cautious and educational. The app must not present fixed outcomes or direct investment instructions.
