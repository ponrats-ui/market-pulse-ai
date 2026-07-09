# Adaptive Analysis Engine

## Purpose

Market Pulse AI must not depend on one fixed investment algorithm. The adaptive analysis engine separates raw data, evidence, factor scoring, profile weighting, committee opinions, and final recommendation language so the platform can improve over time without frontend rewrites.

Thai summary: ระบบวิเคราะห์ใหม่นี้แยกข้อมูลจริง หลักฐาน คะแนนปัจจัย น้ำหนักตามกลยุทธ์ ความเห็นของคณะกรรมการ AI และข้อเสนอแนะสุดท้าย เพื่อให้ปรับปรุงอัลกอริทึมได้ต่อเนื่องโดยไม่ต้องรื้อ UI

## Architecture

The engine lives in `backend/app/analysis_engine`.

- `profile_loader.py`: loads and validates configurable profiles from `configs/analysis_profiles.json`.
- `evidence.py`: converts provider data into facts, unavailable data, assumptions, and factor inputs.
- `score_calculator.py`: converts evidence into factor scores, applies configurable profile weights, and applies regime adjustments.
- `regime.py`: detects current market regime from returned price and volatility evidence.
- `confidence.py`: calculates confidence from data coverage and score dispersion.
- `recommendation.py`: builds committee opinions and final conservative recommendation text.
- `engine.py`: orchestrates the full reproducible workflow.

## Profiles

Profiles are defined in `configs/analysis_profiles.json`.

Current profiles:

- Balanced
- Growth
- Value
- Momentum
- Swing
- Defensive
- Income
- Crypto
- Commodity
- ETF

Each profile defines weights for factors such as technical, fundamental, macro, news, sentiment, risk, liquidity, valuation, quality, growth, momentum, and volatility. Weights are configuration, not hardcoded business rules.

## Market Regimes

The detector currently supports:

- Bull Market
- Bear Market
- Sideways
- High Volatility
- Low Volatility
- Risk-On
- Risk-Off

Regime adjustments are also configuration-driven. For example, high-volatility regimes increase risk, volatility, and liquidity emphasis.

## Scoring Flow

The engine does not create a recommendation directly from raw indicators.

Flow:

1. Raw provider data
2. Evidence package
3. Factor scores
4. Regime-adjusted profile weights
5. Weighted scores
6. Committee opinions
7. Chairman AI final recommendation

This keeps recommendations explainable and reproducible.

## Transparency

Every adaptive recommendation includes:

- Algorithm version
- Active profile
- Market regime
- Confidence score and label
- Facts used
- Unavailable data
- Assumptions
- Factor scores
- Weighted score contributions
- Committee opinions
- Timestamp

The language remains cautious and never provides direct buy/sell instructions.

## Versioning

The current algorithm version is stored in `configs/analysis_profiles.json`.

Current version: `v1.2`

When scoring logic, factor definitions, or profile weights materially change, update this version and record the change in release notes.

## Extensibility

Future factors can be added by:

1. Adding evidence extraction in `evidence.py`.
2. Adding a factor score in `score_calculator.py`.
3. Adding weights to relevant profiles in `analysis_profiles.json`.
4. Adding tests for the new factor.

Planned future factors may include options flow, insider trading, SEC filings, alternative data, satellite data, ESG, supply chain, shipping, and AI trend data.

## Data Integrity

The engine does not fabricate unavailable fields. Missing provider data is reported in `unavailable_data`, and confidence is reduced when evidence coverage is low.
