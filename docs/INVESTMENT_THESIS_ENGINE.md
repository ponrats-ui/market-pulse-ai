# Investment Thesis Engine

## Purpose

The Investment Thesis Engine converts explainable evidence into a structured thesis for each asset. It does not produce generic summaries and does not provide guaranteed investment outcomes.

Thai summary: Thesis Engine สร้างมุมมองการลงทุนจากหลักฐานจริง แยก bull case, bear case, catalysts, risks และสิ่งที่ต้องติดตามต่อไป

## Output Structure

Each thesis includes:

- Investment Thesis
- Bull Case
- Bear Case
- Catalysts
- Risks
- Valuation
- Key Metrics
- What to Monitor Next

## Evidence Rules

The thesis can only use evidence returned by providers or explicitly marked as unavailable. If valuation, financial statements, macro feeds, news feeds, or correlation data are missing, the thesis must say unavailable.

## Probability Integration

The thesis references the Probability Engine:

- Bullish Probability
- Neutral Probability
- Bearish Probability

These are confidence-adjusted estimates, not price predictions.

## Risk Integration

The thesis is paired with the Risk Engine, which adds scenario analysis, stress test language, position-size caution, diversification impact, correlation status, liquidity risk, macro risk, tail risk, and recommended action.

## Future Extension Points

Future provider modules can enrich thesis quality with:

- SEC filings
- Earnings transcripts
- Analyst estimates
- Options flow
- Insider transactions
- ESG data
- Supply chain data
- Shipping data
- AI trend data
