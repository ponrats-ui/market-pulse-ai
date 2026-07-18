# Founder Chart Engine V1

## Summary

Founder Chart Engine V1 adds a professional chart workspace under the asset overview without changing the core dashboard navigation. It uses real provider history from the existing backend API and never fabricates candles, prices, or chart history.

Thai summary: ระบบกราฟเวอร์ชันนี้เพิ่มพื้นที่วิเคราะห์กราฟแบบมืออาชีพ โดยใช้ข้อมูลจริงจากผู้ให้บริการเท่านั้น และแสดงสถานะไม่พร้อมใช้งานอย่างโปร่งใสเมื่อข้อมูลไม่เพียงพอ

## Architecture

- Frontend chart workspace: `frontend/src/ProfessionalChart.tsx`
- Frontend integration point: `frontend/src/main.tsx`
- Chart styling and responsive behavior: `frontend/src/styles.css`
- Backend history provider: `backend/app/providers/yfinance_provider.py`
- Backend technical indicators: `backend/app/services/technical.py`
- Regression tests: `backend/tests/test_chart_engine_ranges.py`, `backend/tests/test_rc3_contracts.py`

The chart component is lazy-loaded with `React.lazy` so the dashboard shell can render before the heavier chart workspace is loaded.

## Data Flow

1. The dashboard selects a symbol and timeframe.
2. The frontend calls:
   - `/api/assets/{symbol}/history?range={range}&interval={interval}`
   - `/api/technical/{symbol}?range={range}&interval={interval}`
3. The backend fetches real yfinance history through the provider abstraction.
4. The frontend renders candles, OHLC, area, line, volume, indicators, levels, and overlays from the returned provider data.

No fallback path creates synthetic historical prices.

## Supported Timeframes

- `1d`
- `5d`
- `1mo`
- `3mo`
- `6mo`
- `ytd`
- `1y`
- `3y`
- `5y`
- `max`

The `3y` timeframe uses yfinance date-window history because yfinance does not reliably support `period=3y`.

## Chart Modes

- Candlestick, default
- OHLC
- Area
- Line

## Indicators

Available overlays:

- EMA20
- EMA50
- EMA200
- SMA20
- SMA50
- SMA200
- Bollinger Bands
- VWAP
- Volume MA

Available side-panel metrics:

- RSI14
- MACD
- ATR

If a selected indicator has insufficient provider history, the chart omits that line instead of inventing values.

## Levels And Overlays

The workspace displays transparent educational overlays:

- Recent support
- Recent resistance
- 52-week high
- 52-week low
- Previous close
- PIA support/risk/target note as overlay language only
- Event overlay unavailable note when no live event provider exists

These overlays are not price predictions.

## Drawing Tools

Available local drawing tools:

- Trend line
- Horizontal line
- Rectangle
- Text
- Arrow
- Undo
- Redo
- Delete/reset

Drawings are local UI annotations only and do not alter provider data.

## Compare Overlay

Compare mode overlays normalized returns:

- US/global default: AAPL, MSFT, NVDA
- Thai default: PTT.BK, AOT.BK, KBANK.BK

Comparison history is loaded only when compare mode is enabled.

## Performance

- Professional chart code is lazy-loaded into its own Vite chunk.
- Existing backend history caching is reused.
- Compare histories are loaded only on demand.
- Stale compare history updates are ignored after component cleanup.
- Frontend production bundle completed without a bundle-size warning.

## Accessibility

- The SVG chart has an image role and descriptive label.
- Toolbar buttons expose active state through styling and accessible button semantics.
- Indicator toggles use `aria-pressed`.
- Focus-visible styling is available through shared button styles.
- Mobile toolbar remains reachable as a compact sticky control surface.

## Responsive Validation

- Desktop chart canvas height: 600px
- Mobile chart canvas height at 390px viewport: 380px
- Mobile horizontal overflow: none after grid containment fix
- Console errors: none from the app during chart checks

## API Smoke Results

All smoke requests returned HTTP 200 locally:

- `/health`
- `/api/assets/AAPL/history?range=1mo&interval=1d`
- `/api/assets/MSFT/history?range=1mo&interval=1d`
- `/api/assets/OKLO/history?range=1mo&interval=1d`
- `/api/assets/PTT.BK/history?range=1mo&interval=1d`
- `/api/assets/KBANK.BK/history?range=1mo&interval=1d`
- `/api/assets/BTC-USD/history?range=1mo&interval=1d`
- `/api/assets/GLD/history?range=1mo&interval=1d`
- `/api/assets/AAPL/history?range=3y&interval=1d`

The `AAPL 3y` smoke test returned 757 real daily points after the provider date-window fix.

## Validation Results

- Backend tests: `111 passed`
- Frontend build: passed
- Desktop browser check: PASS
- Mobile 390px browser check: PASS
- Chart interactions checked: 3Y timeframe, OHLC mode, Compare mode

## Known Limitations

- Event overlays remain hidden until a live event provider is connected.
- Drawing annotations are not persisted.
- Screenshot export serializes the current SVG into a local PNG download.
- Support and resistance are simple educational overlays derived from recent provider highs/lows.
- Compare presets are intentionally conservative and not user-configurable in this sprint.

