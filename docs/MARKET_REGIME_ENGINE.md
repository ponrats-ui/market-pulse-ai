# Market Regime Engine

## Purpose

The Market Regime Engine detects market context so the platform can adjust model weighting automatically instead of applying one fixed algorithm to every condition.

Thai summary: Regime Engine ใช้บริบทตลาดเพื่อปรับน้ำหนักของโมเดล ไม่ใช้สูตรเดียวกับทุกตลาด

## Current Implementation

The current detector uses provider-returned price trend and volatility evidence to classify:

- Bull Market
- Bear Market
- Sideways
- Risk-On
- Risk-Off
- High Volatility
- Low Volatility

The architecture reserves extension points for:

- High Inflation
- Low Inflation
- Rate Hike
- Rate Cut
- Liquidity Crisis
- Commodity Super Cycle
- AI Boom
- War
- Election
- Pandemic

## Weight Impact

Regime adjustments are defined in `configs/analysis_profiles.json`.

Examples:

- High Volatility increases risk, volatility, and liquidity emphasis.
- Bear Market increases risk and quality emphasis while reducing momentum.
- Risk-On increases growth, momentum, and sentiment emphasis.
- Risk-Off increases risk, quality, and valuation emphasis.

## Data Integrity

If inflation, central-bank, liquidity, election, war, or pandemic feeds are unavailable, the engine does not guess. Those regimes remain future-ready extension points until real providers are connected.

## Future Providers

Future regime data can come from FRED, TradingEconomics, central-bank calendars, geopolitical feeds, news providers, rates providers, and commodity inventory sources.
