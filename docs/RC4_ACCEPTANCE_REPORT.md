# RC4 Acceptance Report

## Branch

`feature/rc4-pia-production-intelligence`

## Scope

RC4 productionizes the existing PIA experience without deploying, merging, pushing, or tagging.

## Completed

- Exchange-master architecture added through `configs/exchange_master.json` and backend loader service.
- Asset search now uses exchange-master metadata and returns ticker, company, exchange, sector, industry, country, currency, Thai alias, and source metadata.
- Existing APIs remain backward compatible.
- PIA branding remains active across header and footer.
- Technical chart supports multiple overlays, crosshair tooltip, brush zoom, and `YTD`/`MAX` timeframes.
- Fundamental analysis exposes additional provider-returned fields: PEG, cash, free cash flow, revenue growth, earnings growth, and intrinsic value status.
- Risk engine exposes probability, severity, evidence, mitigation, and trend per category.
- Compare engine continues to expose radar, correlation matrix, relative strength, and thesis fields.
- Paper portfolio exposes sector allocation, transaction history, analytics unavailable state, and live quote based valuation.
- Subscription architecture added through `configs/subscription_features.json` and `/api/subscription/features`; no payment gateway is implemented.
- PIA Relax Mode remains optional, configurable, non-blocking, and no-autoplay.

## Data Integrity

No fake prices, fake news, fabricated calendar events, or guaranteed investment recommendations were added.

## Known Limitations

- `configs/exchange_master.json` is an exchange-master seed, not a full licensed exchange feed.
- Full NYSE/NASDAQ/SET/MAI listings require a licensed provider or exchange-master sync job.
- Economic calendar remains transparent unavailable when no provider is configured.
- Thai news summaries require provider/translation integration and are not fabricated.
- Sharpe ratio, drawdown, and portfolio performance chart require persisted portfolio value history.

## Decision

READY FOR FOUNDER REVIEW based on local backend tests, frontend build, API smoke tests, and performance build check recorded in `docs/RC4_QA_REPORT.md`.
