# FS-200 Known Limitations

## Drawing Tools

Drawing tools are PARTIAL. Local drawing annotations work for the visible chart session, but robust persistence by canonical symbol and timeframe is not complete.

## Event Layer

Corporate and market event markers are PARTIAL. The layer exists, but markers remain hidden until a real dated event provider is connected.

## PIA Overlay

PIA overlay policy is implemented as a separate analysis layer. Potential support/risk/target zones are not generated unless evidence is available. No guaranteed target or stop-loss levels are shown.

## Intraday Data

Intraday history depends on yfinance support for the asset and interval. The app does not synthesize intraday candles from daily candles.

## Chart Library

The project continues to use the custom SVG chart engine rather than adding a dedicated candlestick library. This preserves bundle size and avoids dependency overlap, but advanced native pan/zoom remains limited.

