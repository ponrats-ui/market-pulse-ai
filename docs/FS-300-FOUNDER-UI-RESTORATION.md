# FS-300 Founder UI Restoration

## Summary

FS-300 restores the dashboard toward a professional investment terminal layout without changing backend contracts, data providers, or investment logic.

The implementation keeps the existing Market Pulse AI modules intact and reorganizes the dashboard into a dense three-column research workspace:

- Left rail: asset search, sector browser, and watchlist.
- Center workspace: opportunities, price strip, professional chart, chief investment view, AI committee, and financial analysis.
- Right rail: news, sentiment, quick assistant, risk, and data notice.

## Scope

Changed:

- Dashboard layout composition in `frontend/src/main.tsx`.
- Header and navigation density in `frontend/src/main.tsx`.
- Added a compact dashboard quick assistant panel that reuses the existing assistant question and ask flow.
- Added FS-300 CSS overrides in `frontend/src/styles.css`.

Unchanged:

- Backend API contracts.
- Data provider behavior.
- Master Asset Registry.
- Chart engine data model.
- Compare, portfolio, watchlist, search, language switching, and existing feature routes.
- Deployment configuration.

## Visual Direction

The restored interface uses a compact market-terminal structure:

- Reduced hero/header height.
- Wider central chart workspace.
- Sticky left and right rails on desktop.
- More compact cards, buttons, labels, and controls.
- News, risk, sentiment, and assistant tools kept visible in the right rail.
- Mobile layout avoids horizontal overflow and keeps the asset selector compact enough for the research workspace to begin in the first screen.

## Responsive Verification

Browser metrics were captured against the local running app at `http://127.0.0.1:5173`.

| Viewport | Result |
| --- | --- |
| 1920 x 1080 | PASS: three-column terminal grid, no horizontal overflow, chart visible in first viewport. |
| 1536 x 864 | PASS: three-column terminal grid, no horizontal overflow, chart visible in first viewport. |
| 1366 x 768 | PASS: no horizontal overflow; chart panel header visible in first viewport with chart body continuing below fold. |
| 390 x 844 | PASS: no horizontal overflow; compact selector and opportunities visible in first viewport; chart appears after opportunity section. |

## Validation Results

- Frontend build: PASS.
- Backend tests: PASS, 113 tests passed.
- API smoke: PASS.
  - `GET /health`
  - `GET /api/assets/search?q=NVDA`
  - `GET /api/assets/NVDA`
  - `GET /api/assets/NVDA/history?range=1mo&interval=1d`
  - `GET /api/analysis/NVDA`
- Mojibake marker scan: PASS for modified frontend files.
- Browser console errors from the app: PASS, none observed during local verification.

## Visual Comparison Limitation

The Founder-approved mockup and reference screenshots referenced in the prompt were not available on this Windows filesystem. The requested paths under `/mnt/data` and matching attachment lookups were not present locally.

Because the approved mockup image could not be inspected, this report cannot honestly certify exact 95% visual fidelity. The implementation follows the written FS-300 direction and verifies the running UI through viewport metrics instead.

Screenshot file export was also blocked by the browser runtime with a filesystem permission error in an earlier verification attempt. Browser viewport metrics were captured instead.

## Acceptance Matrix

| Requirement | Status | Notes |
| --- | --- | --- |
| Restore professional terminal dashboard | PASS | Dashboard now uses a dense three-column terminal grid. |
| Make chart primary | PASS | Professional chart moved directly after opportunities and price strip in the center workspace. |
| Keep search/watchlist visible | PASS | Asset selector and watchlist remain in the left rail. |
| Keep news/risk/assistant accessible | PASS | Right rail includes news, sentiment, quick assistant, risk, and data notice. |
| Preserve existing functionality | PASS | No backend/API contracts changed; build and API smoke pass. |
| Responsive layout | PASS | Desktop, laptop, tablet-width, and mobile metrics show no horizontal overflow. |
| Thai/English safety | PASS | Modified files passed mojibake marker scan. |
| Exact mockup fidelity | PARTIAL | Mockup file was unavailable on this machine. |
| Saved screenshot artifacts | PARTIAL | Browser runtime could not write screenshot files; metrics were captured instead. |

## Known Limitations

- The mobile dashboard still prioritizes asset selection first, so the full chart body is below the first viewport on small phones.
- Exact pixel fidelity to the Founder mockup remains unverified until the image is available in the local workspace.
- The quick assistant panel reuses existing assistant behavior and does not introduce new assistant capabilities.

## Decision

READY FOR FOUNDER REVIEW, with visual fidelity marked PARTIAL because the approved mockup image was unavailable for direct comparison.
