# 17 Operations Runbook

## Table of Contents

- [Purpose](#purpose)
- [Startup](#startup)
- [Shutdown](#shutdown)
- [Deploy](#deploy)
- [Rollback](#rollback)
- [Health Checks](#health-checks)
- [Monitoring](#monitoring)
- [Logs](#logs)
- [Alerts](#alerts)
- [Provider Outage](#provider-outage)
- [Recovery Steps](#recovery-steps)
- [Current Production](#current-production)
- [Future Roadmap](#future-roadmap)
- [Known Limitations](#known-limitations)
- [Related Documents](#related-documents)

## Purpose

This runbook tells operators how to run, verify, and recover Market Pulse AI.

## Startup

Backend local:

```powershell
cd backend
.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Frontend local:

```powershell
cd frontend
npm run dev
```

## Shutdown

Stop local terminal processes with Ctrl+C or stop the process bound to ports 8000 and 5173.

Do not delete repository files as part of normal shutdown.

## Deploy

Deployment requires explicit approval.

Backend:

- Render root: `backend`
- build: `pip install -r requirements.txt`
- start: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- health: `/health`

Frontend:

- Cloudflare root: `frontend`
- build: `npm run build`
- output: `dist`
- env: `VITE_API_BASE_URL=<backend URL>`

## Rollback

Rollback steps:

1. Identify last known good backend and frontend deployment.
2. Restore backend service version or commit.
3. Restore Cloudflare Pages deployment.
4. Verify health and dashboard smoke.
5. Record incident.

## Health Checks

Minimum:

- `GET /health`
- frontend page loads
- `GET /api/assets/BTC-USD`
- `GET /api/assets/NVDA`
- `GET /api/assets/quotes?symbols=...`

## Monitoring

Current monitoring is manual and platform-provided.

Useful signals:

- Render service health
- Render logs
- Cloudflare deployment status
- browser console
- API response time
- provider unavailable rate

## Logs

Render logs should be used for backend startup and provider failures.

Frontend console should be checked for uncaught app errors and repeated API failures.

Do not paste secrets into logs or issue reports.

## Alerts

Current premium alert architecture is not active for outbound sending. Alert evaluation endpoints exist for local rule evaluation only.

Future operational alerts should monitor health, latency, provider outages, and failed deployments.

## Provider Outage

Provider outage response:

1. Confirm `/health` still passes.
2. Test a known quote endpoint.
3. Check response for unavailable or warning fields.
4. Confirm UI displays unavailable state.
5. Do not invent replacement data.

## Recovery Steps

For backend outage:

- check Render service
- inspect logs
- restart service if needed
- verify CORS and env vars

For frontend outage:

- check Cloudflare deployment
- verify build artifacts
- verify `VITE_API_BASE_URL`

For provider outage:

- document provider state
- wait or switch provider only through approved provider work

## Current Production

Operations are intentionally simple: Cloudflare static frontend plus Render backend.

## Future Roadmap

- production monitoring dashboard
- rate-limit alerts
- provider health page
- automated smoke tests

## Known Limitations

- No automated incident pager.
- No formal SLO.
- Provider outages may be outside project control.

## Related Documents

- [05 Release Engineering](05_RELEASE_ENGINEERING.md)
- [18 Incident Response](18_INCIDENT_RESPONSE.md)
- [19 Troubleshooting](19_TROUBLESHOOTING.md)

