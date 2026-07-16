# FS-100 Known Limitations

## Provider Coverage

- yfinance/Yahoo coverage is not complete for every searchable asset.
- A searchable asset can have partial quote, history, financial, dividend, or news coverage.
- The UI must keep showing unsupported, unavailable, partial, or stale states transparently.

## Financials And Dividends

- Dividend payment dates, ex-dividend dates, payout ratios, and historical dividend trends may be unavailable for some assets.
- Non-company assets correctly show financial statement analysis as not applicable.
- Financial Health scoring uses available normalized fields only.

## News

- News depends on upstream provider feed availability.
- The app preserves original provider links and does not fabricate summaries when provider data is missing.

## Opportunities

- Today's Opportunities uses a bounded liquid universe for US and Thai markets.
- Full-market scans are intentionally avoided to protect performance and provider limits.
- Scores do not award unavailable factors.

## Portfolio

- Paper Trading is simulated only.
- Manual execution prices are user-entered.
- Portfolio historical performance, Sharpe ratio, max drawdown, and correlation require persisted portfolio history and remain unavailable when unsupported.

## Professional Chart

- Chart event overlays remain hidden until a live event provider exists.
- Drawing annotations are local UI state and are not persisted.
- Support/resistance overlays are educational calculations from provider data, not predictions.

