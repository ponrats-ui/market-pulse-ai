# 03 Algorithm Reference

## Table of Contents

- [Purpose](#purpose)
- [Reference Template](#reference-template)
- [Chief Investment AI](#chief-investment-ai)
- [Opportunity Scanner](#opportunity-scanner)
- [Technical Analysis](#technical-analysis)
- [Fundamental Analysis](#fundamental-analysis)
- [Financial Health](#financial-health)
- [Risk Analysis](#risk-analysis)
- [AI Committee](#ai-committee)
- [Portfolio Analytics](#portfolio-analytics)
- [Compare Engine](#compare-engine)
- [Watchlist Ranking](#watchlist-ranking)
- [Paper Trading](#paper-trading)
- [Economic Calendar](#economic-calendar)
- [Confidence Score](#confidence-score)
- [Provider Selection](#provider-selection)
- [Data Quality Validation](#data-quality-validation)
- [Zero Mock Enforcement](#zero-mock-enforcement)
- [Current State](#current-state)
- [Future Work](#future-work)
- [Known Limitations](#known-limitations)
- [Related Documents](#related-documents)

## Purpose

This document is the engineering reference for Market Pulse AI analysis behavior. It describes what each module does and why it was designed that way. Where formulas are heuristic, they are explicitly described as heuristic.

## Reference Template

Each module follows this template:

- Purpose
- Business Objective
- Inputs
- Outputs
- Data Sources
- Indicators
- Formula
- Weights
- Thresholds
- Decision Rules
- Confidence Calculation
- Fallback Rules
- Edge Cases
- Known Limitations
- Future Improvements

## Chief Investment AI

Purpose: produce a cautious educational view that summarizes price, risk, and available analysis evidence.

Business Objective: help the user understand the current setup without issuing guaranteed investment advice.

Inputs:

- quote response
- risk response
- analysis response where available
- market regime and asset class metadata

Outputs:

- recommendation wording
- confidence
- supporting reasons
- risks
- limitations
- disclaimer

Data Sources: backend analysis services and provider-backed quote/risk evidence.

Indicators: price change, risk score, volatility level, available fundamentals, evidence completeness.

Formula: current implementation uses rule-based and heuristic aggregation. It is not a predictive model.

Weights: configured through analysis profiles where adaptive analysis is used. See `configs/analysis_profiles.json`.

Thresholds: risk score thresholds are used to change cautious wording, such as reducing urgency when risk is high.

Decision Rules:

- high risk pushes the output toward caution
- positive price movement alone is not enough for a strong conclusion
- missing evidence lowers confidence
- disclaimer must always remain visible

Confidence Calculation: confidence is based on evidence availability and signal consistency.

Fallback Rules: if evidence is missing, return a low-confidence unavailable or wait-for-data view.

Edge Cases:

- non-stock assets do not have corporate financial statements
- stale or partial quote data reduces confidence

Known Limitations: not a licensed adviser and not a price predictor.

Future Improvements: richer evidence scoring and provider reliability weighting.

## Opportunity Scanner

Purpose: rank visible market opportunities from real quote and metadata fields.

Business Objective: help users find assets worth further research without claiming they are buys.

Inputs:

- batch quotes
- asset metadata
- price change fields
- optional sparkline history

Outputs:

- opportunity cards
- scores
- reasons
- source and timestamp
- unavailable factors

Data Sources: provider-backed quote batch endpoint and master asset registry.

Indicators: daily change, availability of price, market cap, valuation fields where applicable, data freshness.

Formula: heuristic scoring from available quote and metadata fields.

Weights: current weights are implementation heuristics in the frontend opportunity calculation path.

Thresholds: score bands map to cautious labels such as watch, wait, or caution.

Decision Rules:

- no provider data means no real opportunity score
- unavailable factors must remain visible or traceable
- score is a research prompt, not a recommendation

Confidence Calculation: implicit through unavailable factors and available fields.

Fallback Rules: failed batch quote returns unavailable items, not generated cards.

Edge Cases: provider latency can delay cards.

Known Limitations: local batch quote can take about 25-31 seconds.

Future Improvements: server-side ranking, provider performance optimization, and richer liquidity checks.

## Technical Analysis

Purpose: calculate technical indicators from real historical price data.

Business Objective: explain trend, momentum, volatility, and chart structure using provider history.

Inputs:

- historical OHLCV data
- selected range and interval

Outputs:

- indicator values
- technical source
- chart overlays
- unavailable message if insufficient history exists

Data Sources: yfinance-backed history endpoint.

Indicators: SMA, EMA, RSI, MACD, Bollinger Bands, ATR, VWAP, volume moving average where data exists.

Formula: standard indicator formulas implemented in `frontend/src/features/chart/indicators` and backend technical services. VWAP and volume indicators require volume data.

Weights: no global investment weight is assigned by the chart module itself.

Thresholds: standard technical thresholds may inform display, but current chart output is descriptive.

Decision Rules:

- insufficient data produces unavailable state
- no event markers are shown without dated provider events

Confidence Calculation: based on data sufficiency and source availability.

Fallback Rules: no fabricated candles, levels, or events.

Edge Cases: missing volume, market holidays, stale provider data.

Known Limitations: support/resistance overlays are educational and heuristic.

Future Improvements: server-side indicator consistency and validated event overlays.

## Fundamental Analysis

Purpose: interpret provider-returned corporate fundamentals when applicable.

Business Objective: help users assess quality, profitability, valuation, and balance sheet context.

Inputs:

- provider financial/fundamental fields
- asset class

Outputs:

- applicable status
- facts
- interpretation
- risks
- cautious action plan

Data Sources: yfinance fundamentals where available.

Indicators: revenue, net profit, margins, debt to equity, cash flow quality, ROE, ROA, EPS, P/E, P/BV, dividend yield.

Formula: descriptive and heuristic. It does not calculate intrinsic value.

Weights: no fixed production valuation model is claimed.

Thresholds: valuation and leverage flags are cautious heuristics only.

Decision Rules:

- stocks may show financial statement analysis
- crypto, commodities, FX, and indices show not-applicable explanation
- missing metrics remain unavailable

Confidence Calculation: depends on metric availability and applicability.

Fallback Rules: no generated financial statements.

Edge Cases: incomplete provider fields, non-corporate assets.

Known Limitations: multi-year trend depth depends on provider availability.

Future Improvements: verified statement history and normalized accounting periods.

## Financial Health

Purpose: summarize available corporate fundamentals into a compact health view.

Business Objective: make financial quality easier to scan.

Inputs: available financial metrics from the financial statement response.

Outputs: health label, metric cards, risks, action plan.

Data Sources: financial analysis service.

Indicators: same as Fundamental Analysis.

Formula: current frontend health score is a heuristic derived from available metrics. It is not a formal credit or equity rating.

Weights: equal or simple heuristic treatment of available metrics.

Thresholds: health labels such as weak, average, good, and excellent.

Decision Rules: unavailable metrics do not become zero unless explicitly defined by provider.

Confidence Calculation: lower when fewer metrics exist.

Fallback Rules: not-applicable panel for non-statement assets.

Edge Cases: negative values, missing valuation, sparse fundamentals.

Known Limitations: label is educational and should not be used alone.

Future Improvements: audited scoring model with documented metric weights.

## Risk Analysis

Purpose: identify downside, volatility, liquidity, event, concentration, and data-quality risks.

Business Objective: make risk visible before users act.

Inputs:

- quote
- history
- asset class
- analysis evidence

Outputs:

- risk score
- risk categories
- main risks
- risk controls
- facts
- interpretation
- disclaimer

Data Sources: provider data and analysis engine modules.

Indicators: volatility, price movement, drawdown where available, provider completeness.

Formula: heuristic risk scoring. It is not a Value-at-Risk model.

Weights: loaded through adaptive analysis configuration where applicable.

Thresholds: scores near 7 or higher are treated as high risk.

Decision Rules:

- high volatility increases caution
- missing data increases uncertainty
- risk controls must be practical and conservative

Confidence Calculation: confidence drops when history or quote data is missing.

Fallback Rules: unavailable risk response if evidence is insufficient.

Edge Cases: crypto volatility, stale markets, thin data.

Known Limitations: no broker-specific liquidity or order-book depth.

Future Improvements: richer downside analytics and stress scenarios.

## AI Committee

Purpose: split analysis into specialist views.

Business Objective: prevent a single opaque AI opinion from hiding disagreement.

Inputs:

- quote
- risk
- financials
- analysis metadata

Outputs:

- technical analyst view
- fundamental analyst view
- macro economist view where data exists
- news analyst view where data exists
- risk manager view
- committee summary

Data Sources: current provider-backed responses and transparent unavailable modules.

Indicators: role-specific evidence.

Formula: rule-based assembly of specialist views.

Weights: committee aggregation can use configurable profile weights in adaptive analysis.

Thresholds: confidence and risk thresholds affect wording.

Decision Rules: each role must separate evidence from interpretation.

Confidence Calculation: role confidence depends on role-specific data availability.

Fallback Rules: missing provider roles must state unavailable evidence.

Edge Cases: conflicting signals across roles.

Known Limitations: no live LLM provider is required in the current implementation.

Future Improvements: richer structured committee contracts and audit trail.

## Portfolio Analytics

Purpose: evaluate simulated holdings using live quote data when available.

Business Objective: help users understand concentration, allocation, and simulated profit/loss.

Inputs:

- holdings or transactions
- initial cash
- current quote data

Outputs:

- cash balance
- market value
- realized and unrealized P/L
- allocation
- risk and diversification fields
- stale/unavailable quote notes

Data Sources: backend quote batch and portfolio service.

Indicators: position weight, daily P/L, concentration, sector/country allocation where metadata exists.

Formula: standard accounting calculations for quantity, cost, proceeds, cash, market value, and P/L.

Weights: diversification and risk are heuristic.

Thresholds: concentration thresholds identify high single-position dependency.

Decision Rules:

- insufficient cash blocks buys
- insufficient shares blocks sells
- stale quote remains visible

Confidence Calculation: higher when quotes and metadata are available.

Fallback Rules: positions without live quote show transparent unavailable status.

Edge Cases: partial sells, repeated buys, alias deduplication.

Known Limitations: simulated only; no broker connection.

Future Improvements: persisted history, FX conversion, and cloud sync.

## Compare Engine

Purpose: compare 2-5 assets using real quote, history, and metadata where available.

Business Objective: support relative research rather than isolated asset review.

Inputs: selected symbols.

Outputs:

- comparison table
- performance fields
- radar metrics
- correlation matrix where history exists
- summary

Data Sources: quote and history providers.

Indicators: price, 1D, 1W, 1M, YTD, volatility, market cap, P/E, sector.

Formula: percentage performance and heuristic radar metrics.

Weights: no recommendation weight is claimed.

Thresholds: null is preserved where valuation or volatility fields are unavailable.

Decision Rules: compare only canonical symbols and do not invent missing metrics.

Confidence Calculation: based on data completeness.

Fallback Rules: unavailable compare response if backend is not reachable.

Edge Cases: crypto assets without P/E or ROE, missing history.

Known Limitations: provider history length may differ per asset.

Future Improvements: normalized currency handling and richer factor comparison.

## Watchlist Ranking

Purpose: let users maintain and scan tracked assets.

Business Objective: make daily monitoring faster.

Inputs: user watchlist, provider quotes, local sort mode.

Outputs: rows with price, daily change, sparkline, source state.

Data Sources: local watchlist and quote/sparkline endpoints.

Indicators: latest price, daily percent change, seven-day sparkline where available.

Formula: sorting is user-driven or simple by available fields.

Weights: none.

Thresholds: none beyond unavailable handling.

Decision Rules: user-controlled list should not be replaced by defaults after customization.

Confidence Calculation: source and stale fields indicate reliability.

Fallback Rules: unavailable quote row if provider fails.

Edge Cases: deleted assets, invalid symbols, provider timeouts.

Known Limitations: local persistence only.

Future Improvements: cloud sync and alert linkage.

## Paper Trading

Purpose: simulate trading operations without connecting to real brokers.

Business Objective: help users learn position math and portfolio effects.

Inputs: initial cash, buy and sell transactions, quantity, price, symbol.

Outputs: transaction history, realized P/L, cash, holdings, current valuation.

Data Sources: user-entered transactions and live quote refresh.

Indicators: average cost, market value, realized/unrealized P/L.

Formula: standard average-cost accounting.

Weights: none.

Thresholds: validation prevents negative cash or selling more than held.

Decision Rules: all money remains simulated.

Confidence Calculation: quote reliability affects current valuation only.

Fallback Rules: unavailable current price if provider fails.

Edge Cases: repeated buys, partial sells, sell all, reset.

Known Limitations: no tax, fees, slippage, or broker execution.

Future Improvements: fees, FX, and persisted portfolio history.

## Economic Calendar

Purpose: expose economic event information only when a real provider is configured.

Business Objective: remind users that macro events can affect assets.

Inputs: provider credentials and provider response.

Outputs: calendar events or transparent unavailable response.

Data Sources: provider registry, currently unavailable unless configured.

Indicators: event title, date, country, importance where provider supplies it.

Formula: none.

Weights: none.

Thresholds: none.

Decision Rules: no fake events.

Confidence Calculation: provider availability and event metadata completeness.

Fallback Rules: provider-not-configured response.

Edge Cases: missing credentials, provider outages.

Known Limitations: no default live calendar provider in the current release.

Future Improvements: configured provider integration and event impact mapping.

## Confidence Score

Purpose: communicate how much evidence supports a view.

Business Objective: reduce overconfidence.

Inputs: evidence availability, signal consistency, provider completeness.

Outputs: confidence labels or scores.

Data Sources: analysis engine evidence.

Indicators: missing fields, conflicts, source quality.

Formula: heuristic confidence calculation.

Weights: profile-dependent where configured.

Thresholds: low, medium, high confidence bands.

Decision Rules: missing data lowers confidence.

Fallback Rules: low confidence when evidence is insufficient.

Edge Cases: strong price move but weak fundamentals, or conflicting committee views.

Known Limitations: not statistically calibrated.

Future Improvements: historical validation and calibration.

## Provider Selection

Purpose: choose available real data providers without leaking provider details to the UI.

Business Objective: support future provider growth.

Inputs: provider registry, environment variables, asset symbol, provider health.

Outputs: normalized provider response or unavailable status.

Data Sources: yfinance and optional provider registries.

Formula: ordered provider selection and explicit unavailable state.

Weights: provider priority is configuration and registry driven.

Thresholds: timeout and availability status affect response.

Fallback Rules: do not fabricate after provider failure.

Known Limitations: yfinance is the primary production provider.

Future Improvements: rate limits, provider SLAs, and paid provider support.

## Data Quality Validation

Purpose: prevent bad provider data from becoming confident product output.

Business Objective: protect users from misleading displays.

Inputs: normalized provider fields.

Outputs: stale, partial, unavailable, or valid state.

Rules:

- preserve nulls
- include source
- include timestamp where available
- mark stale or unavailable data
- do not coerce missing data into real values

Future Improvements: stricter schema validation and provider audits.

## Zero Mock Enforcement

Purpose: keep production honest.

Business Objective: maintain trust.

Rules:

- no fake prices
- no fabricated charts
- no invented headlines
- no fake sentiment scores
- no generated economic calendar events
- no AI evidence without data

Tests may use fixtures, but production code must label unavailable data transparently.

## Current State

The current implementation is mostly rule-based and heuristic. It is designed for explainability, not predictive certainty.

## Future Work

Future algorithms must document formulas, evidence, thresholds, and validation before being treated as production behavior.

## Known Limitations

- Heuristics are not predictive models.
- Confidence is not statistically calibrated.
- Optional providers are not always configured.
- Missing data can reduce usefulness but must not be hidden.

## Related Documents

- [01 Product Vision](01_PRODUCT_VISION.md)
- [02 System Architecture](02_SYSTEM_ARCHITECTURE.md)
- [06 Founder Bible](06_FOUNDER_BIBLE.md)
- [PIA Reasoning Architecture](PIA_REASONING_ARCHITECTURE.md)
- [Portfolio Engine](PORTFOLIO_ENGINE.md)
- [Provider Health and Fallback](PROVIDER_HEALTH_AND_FALLBACK.md)
