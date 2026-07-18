# FS-200 Chart Architecture

## Frontend Structure

```text
frontend/src/features/chart/
  ProfessionalChart.tsx
  ChartToolbar.tsx
  ChartLegend.tsx
  ChartTooltip.tsx
  ChartIndicatorPanel.tsx
  ChartDrawingLayer.tsx
  ChartEventLayer.tsx
  ChartPiaOverlay.tsx
  chartTypes.ts
  chartUtils.ts
  indicators/
    ema.ts
    sma.ts
    rsi.ts
    macd.ts
    bollinger.ts
    atr.ts
    vwap.ts
    volumeMa.ts
```

## Layers

1. Raw provider data: normalized candles from `/api/assets/{symbol}/history`.
2. Calculated technical indicators: backend technical series and frontend formula references.
3. User drawings: local annotation layer.
4. PIA analytical overlays: clearly labeled as analysis, not market data.
5. Events: hidden until real event provider data exists.

## History Contract

History responses include:

- `symbol`
- `interval`
- `range`
- `timezone`
- `currency`
- `provider`
- `requested_at`
- `data_timestamp`
- `cache_age_seconds`
- `stale`
- `unavailable_reason`
- `candles`
- backward-compatible `points`

Each candle includes:

- `timestamp`
- `time`
- `open`
- `high`
- `low`
- `close`
- `adjusted_close`
- `volume`

Invalid candles are skipped with `skipped_candles` reasons.

## Cache And Request Strategy

- Initial chart: quote, history, technical analysis. History and technical share the same selected symbol/range/interval.
- Changing timeframe: one new history request and one technical request.
- Toggling indicators: no new history request.
- Adding compare overlay: compare histories are requested only when compare is enabled.
- Fullscreen: no new data request; current state is preserved.

## Error Strategy

The chart renders transparent unavailable states for missing history, insufficient indicator history, unsupported intraday data, and event provider absence. It does not fabricate candles, indicators, events, or levels.
