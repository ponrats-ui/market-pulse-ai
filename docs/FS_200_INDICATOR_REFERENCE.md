# FS-200 Indicator Reference

## Moving Averages

- SMA: arithmetic mean of the last `n` real close values.
- EMA: exponential moving average seeded by the first complete SMA window.
- Lines are hidden until enough real closes exist.

## RSI

- Default period: 14.
- Uses gains and losses from real close-to-close changes.
- Reference levels: 30 and 70.
- RSI alone is not treated as a buy/sell signal.

## MACD

- Defaults: 12 / 26 / 9.
- MACD line: EMA12 minus EMA26.
- Signal line: EMA9 of MACD line.
- Histogram: MACD line minus signal line.

## Bollinger Bands

- Default period: 20.
- Default deviation: 2 standard deviations.
- Uses real close prices.

## ATR

- Default period: 14.
- True range uses high-low, high-previous close, and low-previous close.
- Labeled as volatility evidence.

## VWAP

- Uses typical price and volume.
- Intraday VWAP is preferred.
- If volume or intraday support is unavailable, VWAP is marked unavailable rather than fabricated.

## Volume MA

- Default period: 20.
- Uses real volume only.

