# Adaptive Quant Engine

## Architecture

Market Pulse AI now has an Adaptive Intelligence Layer:

1. Market Data
2. Feature Engineering
3. Adaptive Weight Engine
4. AI Committee
5. Probability Engine
6. Investment Thesis
7. Risk Engine
8. Recommendation

Thai summary: ระบบนี้ไม่ได้ทำนายราคาแบบตายตัว แต่ประเมินความน่าจะเป็นจากหลักฐานที่อธิบายได้ ตรวจสอบซ้ำได้ และมี version ทุกครั้ง

## Completed Modules

- `analysis_engine/evidence.py`: converts market data into facts, unavailable data, assumptions, and factor inputs.
- `analysis_engine/feature_engineering.py`: creates volatility, liquidity, news-density, size, and pressure features.
- `analysis_engine/asset_class.py`: selects different model assumptions for stocks, ETFs, crypto, commodities, forex, bonds, and indices.
- `analysis_engine/adaptive_weights.py`: adjusts configurable weights by regime, asset class, volatility, liquidity, news density, and confidence.
- `analysis_engine/score_calculator.py`: converts factor inputs to scores and weighted contributions.
- `analysis_engine/probability.py`: estimates bullish, neutral, and bearish probabilities without predicting exact prices.
- `analysis_engine/recommendation.py`: produces independent committee opinions and Chairman AI summary fields.
- `analysis_engine/investment_thesis.py`: creates bull case, bear case, catalysts, risks, valuation note, key metrics, and watchlist items.
- `analysis_engine/risk_engine.py`: produces scenario, stress, sizing, diversification, correlation, liquidity, macro, and tail-risk outputs.
- `analysis_engine/learning.py`: records algorithm version metadata and lifecycle actions.

## Profile Configuration

Weights are loaded from `configs/analysis_profiles.json`; they are not hardcoded in the recommendation path.

Profiles include Balanced, Growth, Value, Momentum, Swing, Defensive, Income, Crypto, Commodity, and ETF. The engine also applies asset-class bias from code-level model descriptors, which are replaceable modules.

## Future Extension Points

Provider-specific adapters can add evidence from Reuters, Finnhub, Polygon, SEC, FRED, TradingEconomics, options APIs, and other sources without rewriting the frontend.

New factors should follow this pattern:

1. Add raw evidence extraction.
2. Add feature engineering.
3. Add factor scoring.
4. Add configurable profile weights.
5. Add test coverage.
6. Update algorithm version metadata.

## Production Rules

- No fabricated values.
- No mock values in production recommendations.
- Missing data is reported as unavailable.
- Probabilities are estimates from evidence, not price targets.
- Every recommendation includes version, confidence, evidence, timestamp, limitations, and conservative action wording.
