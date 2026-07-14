# Founder Final Fix 01

Date: 2026-07-14
Branch: release/v1-launch-patch-1
Scope: Only the four Founder final fix items were addressed. No merge, push, deploy, or tag was performed.

## 1. Asset Center Supported Universe

Status: PASS

Action taken:
- Asset categories now derive from the canonical Exchange Master/Data Hub sector payload instead of the older limited watchlist seed.
- Category asset dropdown shows the full supported category universe, while the industry browser continues to filter by the selected category.
- Thai aliases were added for the verified Thai and commodity searches.

Verification:
- Browser category selector showed 10 categories: US Stocks, Thailand, Crypto, ETF, Indices, Commodities, Forex, Bonds, Sector ETF, REIT.
- US Stocks showed AAPL, AMD, AMZN, GOOGL, META, MSFT, NVDA, TSLA, TSM.
- Thailand showed ADVANC.BK, AOT.BK, CPALL.BK, DELTA.BK, KBANK.BK, PTT.BK, SCB.BK, TTB.BK.
- Crypto showed BTC-USD, ETH-USD, SOL-USD, XRP-USD.
- ETF showed GLD, QQQ, SLV, SPY, VOO, VTI.
- Commodities showed BZ=F, CL=F, GC=F, HG=F, NG=F, SI=F.

Required assets checked:
AAPL, MSFT, GOOGL, META, NVDA, TTB.BK, KBANK.BK, AOT.BK, BTC-USD, GLD.

## 2. Global Asset Search

Status: PASS

Action taken:
- Search results are no longer filtered by the currently selected industry.
- Search selection uses the canonical symbol and updates the global selected asset, category, and dependent dashboard modules.
- Unsupported searches now show a clear no-result state without mixing in recent searches.

Verification:
- AAPL returned and selected AAPL.
- Apple returned and selected AAPL.
- TTB returned and selected TTB.BK.
- ทหารไทยธนชาต returned and selected TTB.BK.
- ทอง returned gold-related assets: GLD and GC=F, with HG=F also matching the broader metals universe.
- UNSUPPORTEDXYZ returned zero result buttons and showed the no-result state.
- Browser-visible Thai text rendered correctly with no mojibake.

## 3. Market Condition Panel

Status: PASS

Action taken:
- Added a real backend market-condition endpoint using yfinance-backed proxy symbols.
- Frontend sentiment panel now renders market proxy evidence rather than relying on a single unavailable sentiment result.
- Partial provider unavailability is isolated per metric and does not make the whole panel useless.

Verification:
- API smoke test returned 8 market proxies: ^VIX, ^GSPC, ^SET.BK, USDTHB=X, GC=F, CL=F, BTC-USD, ^TNX.
- Browser showed VIX, S&P 500, SET Index, USD/THB, Gold, WTI Oil, Bitcoin, and US 10Y.
- Browser showed Thai market state text, including เป็นกลาง / ระมัดระวัง language where applicable.
- Browser showed yfinance/Yahoo provider attribution and timestamps.
- Browser console errors: none.

## 4. Relax Mode

Status: PASS

Action taken:
- Relax Mode now supports expanded, minimized, and closed states.
- No iframe is created before explicit Play, preventing autoplay behavior.
- Minimized mini-player includes stream title, Play/Pause, Mute, Expand, and Close controls.
- Preference model persists selected stream, custom URL, volume, mute, and minimized state.
- Mobile mini-player styling was constrained to stay inside the viewport.

Verification:
- Opening Relax Mode created zero iframes before Play.
- Minimize changed the panel to the relax-panel-minimized state with zero iframes before Play.
- Expand restored the full panel.
- Pressing Play created one iframe only after explicit user action.
- Close removed the panel and removed the iframe.
- Mobile viewport check at 390 x 844 showed compact mini-player width within viewport and no horizontal overflow.

## Validation Summary

Frontend build: PASS
Backend tests: PASS, 84 passed
API smoke: PASS
Browser verification: PASS for all four issues
Browser console errors: none
Mojibake check: PASS for browser-visible text in the verified workflows

## Remaining Notes

- The Exchange Master is still a curated seed universe with documented partial coverage, not a full licensed exchange master.
- The browser automation environment printed external Statsig transport errors from the Codex shell/browser tooling; the application page console itself reported no errors.
