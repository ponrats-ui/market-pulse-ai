# Founder 12 Fix Matrix

Branch: `feature/founder-production-final`  
Scope: corrective Founder feedback sprint. No merge, deploy, push, or tag performed.

| Item | Founder requirement | Files changed | API used | Browser verification | Status | Remaining limitation |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | Supported asset universe: TTB/KBANK/AOT resolve, RKLB returns no result, no tiny seed claim | `configs/exchange_master.json`, `backend/app/services/asset_universe.py`, `backend/app/providers/yfinance_provider.py`, `scripts/update_exchange_master.py` | `/api/assets/search` | Dashboard search: `TTB` resolved to `TTB.BK`; `RKLB` returned no visible supported result | PARTIAL | Full S&P 500, Nasdaq-100, and complete SET constituents require verified constituent source files. Ingestion script added; current universe remains curated/provider-ready. |
| 2 | Asset Center order: Category, Industry, Search, Asset; industry filters search | `frontend/src/main.tsx` | `/api/sectors`, `/api/assets/search` | Labels rendered in exact order: Category, Sector Browser, Search global asset, Asset. Banking filter showed SCB/KBANK/TTB; TTB autocomplete appeared. | PASS | Label uses "Sector Browser" in English UI, equivalent to Industry selector. |
| 3 | Important News headline links and Open original article control | `backend/app/services/news.py`, `frontend/src/main.tsx`, `frontend/src/types/market.ts` | `/api/news-impact/{symbol}` | Dashboard and News page showed clickable headlines plus visible `Open original article` links with source names preserved. | PASS | Depends on provider article URL availability. |
| 4 | Dashboard whitespace uses desktop width; mobile intact | `frontend/src/main.tsx` | N/A | Desktop used expanded container and wider news area; mobile 390px check showed no horizontal overflow. | PASS | No pixel-perfect design pass beyond browser checks. |
| 5 | Chief Investment AI actionable cautious recommendation | `frontend/src/main.tsx` | `/api/risk/{symbol}`, `/api/assets/{symbol}` | TTB.BK showed Recommendation, Confidence, Supporting reasons, Risks, Conditions to change, and disclaimer. | PASS | Rule-based from existing evidence, not a predictive model. |
| 6 | Fundamental data depth for equities | `backend/app/providers/yfinance_provider.py`, `backend/app/services/financials.py`, `frontend/src/main.tsx` | `/api/financials/AAPL`, `/api/financials/NVDA`, `/api/financials/TTB.BK` | Browser financial panel exposes revenue, profit, cash flow, balance sheet, margin, valuation, and growth rows. API smoke returned 200 for all three. | PARTIAL | AAPL/NVDA return deeper yfinance data when available. TTB.BK has provider gaps for some statement fields; unavailable fields stay transparent. |
| 7 | Single asset master across modules for TTB.BK | `configs/exchange_master.json`, `configs/watchlist.json`, `backend/app/providers/yfinance_provider.py`, `frontend/src/main.tsx` | Dashboard, compare, portfolio, news, financials, risk, assistant, watchlist endpoints | TTB.BK selected on dashboard; watchlist favorite worked; risk/news/financial/analysis smoke returned 200; assistant used selected asset. | PASS | Compare browser pass used default table visibly; TTB compare endpoint verified by API smoke. |
| 8 | AI Assistant structured output | `backend/app/services/qa_assistant.py`, `frontend/src/main.tsx` | `/api/assistant/ask` | Assistant response visibly included Overview, Positive/Negative factors, Risk, PIA recommendation, Confidence, Evidence used, Missing data, and follow-up questions. | PASS | The assistant is evidence-synthesis only, not a generative investment advisor. |
| 9 | True paper trading simulator | `backend/app/services/portfolio.py`, `backend/tests/test_portfolio.py`, `frontend/src/main.tsx`, `frontend/src/types/market.ts` | `/api/portfolio/evaluate` | Browser workflow: buy AAPL twice, sell 1; one AAPL row, quantity 3, average cost 110, cash 690, realized P/L 20, transaction count 3. | PASS | Performance chart, Sharpe, drawdown require persisted portfolio history. |
| 10 | Economic calendar real provider or transparent unavailable state | Existing provider path retained | `/api/calendar` | Calendar screen rendered transparent unavailable/provider configuration state. | PARTIAL | `TRADING_ECONOMICS_KEY` or another live calendar provider is required; no fabricated events were added. |
| 11 | Asset-specific news impact | `backend/app/services/news.py`, `frontend/src/main.tsx`, `frontend/src/types/market.ts` | `/api/news-impact/AAPL`, `/api/news-impact/NVDA`, `/api/news-impact/BTC-USD`, `/api/news-impact/TTB.BK` | News page for TTB.BK showed related TMBThanachart articles, clickable headlines, source, impact, sentiment, and Open original article controls. API smoke returned 200 for requested symbols. | PASS | Duplicate clustering is basic provider/classifier grouping, not full semantic clustering. |
| 12 | PIA Relax Mode custom URL and no autoplay | `frontend/src/main.tsx`, `frontend/src/types/market.ts`, `configs/relax_streams.json` | N/A | Browser: panel opened, no iframe before Play, pasted required YouTube URL, saved preference, iframe appeared after Play, Open YouTube source used required URL. | PASS | If YouTube blocks embedding, app shows transparent embed-unavailable message. |

## Validation Summary

- Frontend build: PASS
- Backend tests: PASS, 45 passed
- API smoke: PASS, all tested endpoints returned HTTP 200
- Browser verification: PASS/PARTIAL as listed
- Mojibake scan: PASS for active app/config source; only negative test assertions mention mojibake markers.

## Production Blockers

- Item 1 remains PARTIAL until verified full constituent data files are ingested.
- Item 10 remains PARTIAL until a live economic calendar provider is configured.
- Item 6 remains PARTIAL for TTB.BK where yfinance does not return equivalent statement fields.
