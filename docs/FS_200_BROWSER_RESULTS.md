# FS-200 Browser Results

## Status

PARTIAL PASS. The professional chart workspace rendered and interacted correctly in desktop and mobile layouts. During final live smoke, Yahoo Finance intermittently returned provider-unavailable responses from the local environment, so real-candle browser rendering was verified only when provider history was available earlier in the sprint. The chart correctly showed transparent unavailable states when the provider returned no history.

## Desktop Verification

- Viewport: 1280 x 720.
- Chart shell: PASS.
- Chart SVG: PASS when history is available.
- Chart height: PASS, 600 px.
- Legend: PASS.
- yfinance/Yahoo attribution: PASS.
- Toolbar controls: PASS for 1D, 5D, 1M, 3M, 6M, YTD, 1Y, 3Y, 5Y, MAX, Candlestick, OHLC, Line, Area, Compare, Fullscreen, Reset View, and Export PNG.
- Compare overlay: PASS, Compare label appeared and the base chart remained intact.
- Fullscreen fallback: PASS.
- Escape exits fullscreen: PASS after corrective check.
- Reset View: PASS.
- Horizontal overflow: PASS, no page-level overflow detected.
- App console errors: PASS, no application console errors detected. Browser runtime Statsig network warnings were outside the app page.

## Mobile Verification

- Viewport: 390 x 844.
- Chart shell: PASS.
- Chart height: PASS, 380 px.
- Toolbar availability: PASS.
- Legend: PASS.
- Horizontal overflow: PASS.
- Transparent unavailable state: PASS when provider history was unavailable.
- App console errors: PASS, no application console errors detected.

## API Smoke

Direct backend history function checks returned normalized yfinance candles for:

- AAPL
- MSFT
- OKLO
- RKLB
- PTT.BK
- KBANK.BK
- BTC-USD
- GLD

Later HTTP smoke attempts encountered intermittent provider-unavailable responses from yfinance in the local environment. The backend returned transparent unavailable metadata rather than fabricated candles. This is not a chart-rendering regression, but it remains a provider availability limitation for Founder testing.

## PASS Items

- Modular chart workspace loaded lazily.
- Normalized history contract exposed candles and metadata.
- Chart toolbar rendered required ranges and chart modes.
- Compare overlay was toggleable and labeled.
- Fullscreen fallback preserved chart state.
- Escape exited fullscreen.
- Mobile layout did not overflow.
- Provider-unavailable state did not crash the dashboard.

## PARTIAL Items

- Live browser verification with real candles: PARTIAL because yfinance became unavailable during final HTTP/browser smoke.
- Drawing tools: PARTIAL. Horizontal and trend-line style drawing support exists, but rectangle, text note, arrow, delete, undo/redo, and clear-drawing flows need deeper browser verification before claiming full support.
- Event layer: PARTIAL. The UI layer is present and transparent, but no live corporate/event provider is connected.
- PIA overlay: PARTIAL. The overlay is visually separated and labeled as educational analysis; richer evidence-based zones require future provider-backed calculations.

## FAIL Items

- None from deterministic build/test validation.
