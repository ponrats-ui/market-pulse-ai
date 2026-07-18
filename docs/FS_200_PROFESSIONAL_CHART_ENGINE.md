# FS-200 Professional Chart Engine

## Summary

FS-200 hardens the Market Pulse AI professional chart workspace while preserving the FS-100 platform. The chart consumes canonical symbols and real normalized provider history. It separates raw candles, calculated indicators, user drawings, PIA overlays, and event layers.

Thai summary: FS-200 ทำให้กราฟมืออาชีพมีโครงสร้างชัดเจน ใช้ข้อมูลจริงเท่านั้น และแยกชั้นข้อมูลตลาดดิบ อินดิเคเตอร์ การวาดของผู้ใช้ และ PIA overlay ออกจากกัน

## Chart Library

Selected approach: custom React SVG chart, supported by existing React/Vite stack.

Installed chart library inspection:

- `recharts` is already installed and used elsewhere.
- `recharts` does not provide first-class candlestick/OHLC tooling.
- No additional chart library was added to avoid overlapping dependencies and bundle growth.

License impact: no new chart dependency or license obligation was introduced.

## Supported Chart Types

- Candlestick
- OHLC bar
- Area
- Line

Default remains candlestick.

## Supported Ranges

- 1D
- 5D
- 1M
- 3M
- 6M
- YTD
- 1Y
- 3Y
- 5Y
- MAX

`3Y` uses a yfinance date-window request because yfinance does not reliably support `period=3y`.

## Supported Indicators

- EMA 20, 50, 200
- SMA 20, 50, 200
- RSI 14
- MACD 12/26/9
- Bollinger Bands 20/2
- ATR 14
- VWAP where provider data supports meaningful calculation
- Volume MA 20

Indicators are calculated only from real price/volume history.

## Partial Status

- Drawing tools: PARTIAL. Horizontal line, trend line, rectangle, text, arrow, undo, redo, and clear are available as local UI annotations. Persistence by symbol/timeframe is not complete in this sprint.
- Event layer: PARTIAL. Layer is modular and transparent but hidden until real event provider data exists.
- PIA overlays: PARTIAL. Overlay policy and UI layer are present; no target/stop levels are generated when evidence is insufficient.

