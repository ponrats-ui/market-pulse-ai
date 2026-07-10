# PIA Phase 1 QA

## Branch

`feature/pia-founder-experience`

## Backend Tests

Passed.

```text
36 passed in 1.09s
```

## Frontend Build

Passed.

```text
npm.cmd run build
```

Build completed without the Vite large bundle warning.

## Smoke Tests

Local backend:

```text
http://127.0.0.1:8000
```

| Endpoint | Method | Result |
| --- | --- | --- |
| `/health` | GET | HTTP 200 |
| `/api/assets/NVDA/history?range=ytd&interval=1d` | GET | HTTP 200 |
| `/api/assets/NVDA/history?range=max&interval=1d` | GET | HTTP 200 |
| `/api/technical/NVDA?range=1y&interval=1d` | GET | HTTP 200 |
| `/api/compare?symbols=NVDA,AMD,TSM` | GET | HTTP 200 |
| `/api/news?symbol=NVDA&limit=5` | GET | HTTP 200 |
| `/api/calendar` | GET | HTTP 200 |
| `/api/portfolio/evaluate` | POST | HTTP 200 |
| `/api/assistant/ask` | POST | HTTP 200 |

PowerShell displayed Thai response text with console mojibake, but the API returned successful UTF-8 JSON.

## Performance

- Code splitting remains active.
- Build output remains below Vite warning thresholds.
- PIA Relax Mode iframe is created only after explicit Play.

## Accessibility

- Header music button has an accessible label.
- Relax Mode controls use buttons, range input, close control, and source link.
- Chart controls use `aria-pressed`.
- Watchlist reorder buttons include ARIA labels.

## Known Limitations

- Drag and drop is architecture-ready through manual reorder controls, not full pointer drag/drop.
- Economic calendar still returns transparent unavailable state when no provider is configured.
- News Thai summaries require provider/translation support and are not fabricated.
- Paper trading remains a local simulator and does not connect to brokers.

## Decision

READY FOR FOUNDER WALKTHROUGH.
