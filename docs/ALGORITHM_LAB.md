# Algorithm Lab

Algorithm Lab is the user-facing explanation layer for Market Pulse AI opportunity engines.

## Purpose

Algorithm Lab helps users inspect:

- What the algorithm is designed to find
- Which factors it uses
- Why each factor matters
- How weights contribute to score
- What risks reduce score
- What evidence is missing
- What the algorithm does not claim

## Penny Opportunity Lab

The Penny Opportunity UI exposes score breakdowns from the latest backend snapshot. The panel shows positive weighted score, risk penalty, final score reconciliation, factor contributions, missing evidence, rank reason, and version metadata.

The methodology endpoint is:

`GET /api/opportunities/penny/algorithm`

Candidate explanation endpoint:

`GET /api/opportunities/penny/explain/{symbol}`

Why Not endpoint:

`GET /api/opportunities/penny/why-not/{symbol}`

## Trust Foundation Update

Algorithm Lab panels should show methodology and trust context together. Users should understand that a score is a weighted heuristic based on available evidence, not a probability of profit, personal suitability score, or buy/sell instruction.
