# RC3 QA Report

## Branch

`feature/rc3-founder-production-intelligence`

## Validation Status

Passed local RC3 validation.

## Backend Tests

Passed.

```text
36 passed in 1.14s
```

## Frontend Build

Passed.

```text
npm.cmd run build
```

Vite built successfully with manual chunks:

- `react`
- `charts`
- `icons`
- app `index`

No chunk-size warning was reported.

## API Smoke

Passed against local backend:

```text
http://127.0.0.1:8000
```

| Endpoint | Method | Result |
| --- | --- | --- |
| `/health` | GET | HTTP 200 |
| `/api/assets/search?q=NVDA` | GET | HTTP 200 |
| `/api/assets/search?q=ทอง` | GET | HTTP 200 |
| `/api/sectors` | GET | HTTP 200 |
| `/api/technical/NVDA` | GET | HTTP 200 |
| `/api/compare?symbols=NVDA,AMD` | GET | HTTP 200 |
| `/api/news?symbol=NVDA&limit=5` | GET | HTTP 200 |
| `/api/calendar` | GET | HTTP 200 |
| `/api/analysis/NVDA` | GET | HTTP 200 |
| `/api/risk/NVDA` | GET | HTTP 200 |
| `/api/financials/NVDA` | GET | HTTP 200 |
| `/api/portfolio/evaluate` | POST | HTTP 200 |

PowerShell displayed the decoded Thai query text with console mojibake, but the endpoint returned gold-related assets successfully.

## Performance Check

Passed build-level check. Vite manual chunks were added for React, Recharts, and lucide-react. The build completed without the previous large single-chunk warning.

## Risks

- The curated asset universe is not a complete global exchange master.
- Real economic calendar events require a configured provider.
- Real Thai news translation requires a configured translation or multilingual news provider.
- Paper trading remains local simulation and does not place broker orders.
- FX conversion is transparent unavailable until a provider is configured.

## Decision

READY FOR FOUNDER TEST
