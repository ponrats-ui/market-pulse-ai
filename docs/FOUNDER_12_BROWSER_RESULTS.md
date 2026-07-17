# Founder 12 Browser Results

Browser route used: `http://127.0.0.1:5173/`  
Backend route used: `http://127.0.0.1:8000`  
Viewport checks: desktop default and mobile `390x844`.

| Item | Route / screen | Exact interaction | Expected result | Actual result | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Dashboard / Asset Console | Selected Banking sector, typed `TTB`; searched `RKLB` | TTB appears as supported `TTB.BK`; RKLB has no supported result | TTB.BK appeared with Thai name and SET metadata; RKLB did not show Rocket Lab/support result | PARTIAL |
| 2 | Dashboard / Asset Console | Read visible labels and typed in search | Order is Category, Industry, Search, Asset; search autocompletes and sector filters | Visible labels were Category, Sector Browser, Search global asset, Asset; Banking showed SCB.BK, KBANK.BK, TTB.BK; TTB autocomplete appeared | PASS |
| 3 | Dashboard / News Monitor and News Impact screen | Inspected visible news cards and links | Headline clickable; Open original article visible; source and URL preserved | Multiple article headlines and `Open original article` links had original article URLs and source labels | PASS |
| 4 | Dashboard desktop and mobile | Checked desktop rendering and set viewport to `390x844` | No excessive blank middle space; mobile no broken overflow | Desktop used widened content area; mobile had no horizontal overflow and dashboard controls stayed visible | PASS |
| 5 | Dashboard / Chief Investment AI | Selected `TTB.BK` | One cautious actionable recommendation with confidence, reasons, risks, conditions, disclaimer | TTB.BK showed `Hold`, Medium confidence, supporting reasons, risks, conditions to change, and educational disclaimer | PASS |
| 6 | Dashboard / Financial Statements | Selected `TTB.BK`; API smoke checked AAPL, NVDA, TTB.BK | Deeper real financial rows visible where provider data exists | Financial panel displayed deeper categories; APIs returned 200; TTB.BK still had yfinance field gaps for some metrics | PARTIAL |
| 7 | Dashboard, Watchlist, Compare, Portfolio, News, Financials, Risk, Assistant | Selected/favorited `TTB.BK`; smoke-tested downstream APIs | Same asset works consistently across modules | TTB.BK dashboard, watchlist, news, risk, financials, analysis, assistant APIs worked; compare endpoint returned 200 | PASS |
| 8 | AI Assistant screen | Asked `TTB.BK risk overview with evidence` | Structured answer includes Overview, positives, negatives, risk, PIA recommendation, confidence, evidence, missing data, follow-ups | Response visibly contained Overview, PIA recommendation, Evidence used, Missing data, Suggested follow-up questions | PASS |
| 9 | Portfolio screen | Reset; buy AAPL 2 @ 100; buy AAPL 2 @ 120; sell AAPL 1 @ 130 | Single AAPL row, quantity 3, average cost 110, cash 690, realized P/L 20, history 3 | Browser showed one AAPL row, quantity 3, average cost 110, cash 690, realized P/L 20, transaction count/history 3 | PASS |
| 10 | Economic Calendar screen | Opened Economic Calendar | Real provider events or transparent unavailable state | Calendar showed transparent provider/unavailable state; no fabricated events | PARTIAL |
| 11 | News Impact screen | Selected TTB.BK then opened News Impact; API smoke checked AAPL, NVDA, BTC-USD, TTB.BK | News tied to selected asset; clickable headline; impact/sentiment visible | TTB.BK/TMBThanachart articles appeared with clickable headline, Open original article, impact, sentiment, source | PASS |
| 12 | Header / PIA Relax Mode | Opened Relax Mode; pasted required URL; saved; pressed Play | No autoplay; embed appears only after Play; Open YouTube source works | No iframe before Play; after Play iframe src used `-DfHaOYeaqk` embed with list; Open YouTube source pointed to required URL | PASS |

## API Smoke Results

All returned HTTP 200:

- `/health`
- `/api/assets/search?q=TTB`
- `/api/assets/search?q=KBANK`
- `/api/assets/search?q=AOT`
- `/api/assets/search?q=RKLB`
- `/api/assets/search?q=ทอง`
- `/api/watchlist`
- `/api/sectors`
- `/api/assets/TTB.BK`
- `/api/compare?symbols=TTB.BK,AAPL`
- `/api/risk/TTB.BK`
- `/api/financials/AAPL`
- `/api/financials/NVDA`
- `/api/financials/TTB.BK`
- `/api/news-impact/AAPL`
- `/api/news-impact/NVDA`
- `/api/news-impact/BTC-USD`
- `/api/news-impact/TTB.BK`
- `/api/calendar`
- `/api/analysis/TTB.BK`
- `POST /api/portfolio/evaluate`
- `POST /api/assistant/ask`

## Console And Build Notes

- Initial browser pass exposed a Vite dev-server filesystem overlay for `configs/relax_streams.json`; fixed with a narrow `server.fs.allow` setting in `frontend/vite.config.ts`.
- Final browser route `http://127.0.0.1:5173/` rendered without Vite overlay.
- Old console errors from an earlier 5173 attempt remained in browser log history, but the final route rendered live yfinance data and API smoke passed.
