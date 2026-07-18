# FS-300A Dashboard Density Optimization

## Summary

FS-300A is a dashboard-only information density pass. It does not change backend logic, API contracts, provider integrations, chart data, watchlist logic, or market news behavior.

The dashboard now uses compact summary variants for the largest analysis sections, with detailed reasoning moved behind native expandable disclosure controls.

## Before

The FS-300 dashboard restored a professional three-column terminal layout, but several sections still consumed too much vertical space:

- Chief Investment AI permanently displayed broad factor lists and disclaimer text.
- AI Investment Committee displayed three large analyst cards.
- Risk Analysis displayed all detailed categories, evidence, mitigation, and historical context by default.
- Financial Health used tall metric cards and always-visible risk/action lists.
- Watchlist and news rows had more padding than needed for a terminal workflow.

Baseline measured during FS-300 verification:

| Section | FS-300 Approximate Height |
| --- | ---: |
| Chief Investment AI | Large expanded section; detailed factors always visible. |
| AI Committee | Three-card expanded layout. |
| Risk Analysis | Long category list plus history and action lists. |
| News panel | 248 px at desktop. |
| Mobile asset selector | 520 px after FS-300 cap. |

## After

FS-300A introduces compact dashboard-specific variants:

- `CompactChiefInvestmentCard`
- `CompactAICommittee`
- `CompactRiskPanel`
- `CompactFinancialPanel`

The original full components remain available in the codebase for compatibility, but the dashboard uses the compact versions.

### Chief Investment AI

Default view now shows only:

- Recommendation
- Confidence
- Investment Horizon
- Risk Level
- 2-sentence summary
- Top Positive Factor
- Top Negative Factor
- Top Watch Item
- View Full Analysis disclosure

Detailed positives, negatives, watch plan, and disclaimer are behind `View Full Analysis`.

Measured FS-300A desktop height: about 274 px. This is a major reduction from the always-expanded FS-300 card.

### AI Investment Committee

Default view now shows a compact vote grid:

- Chief AI
- Technical Analyst vote
- Fundamental Analyst vote
- Risk Officer vote
- Overall consensus
- Confidence
- View Details disclosure

Detailed analyst rows are behind `View Details`.

### Risk Analysis

Default view now shows only:

- Overall Risk Score
- Volatility
- Risk Trend
- Top 3 Risks
- Top 3 Mitigation Actions
- View Full Risk Analysis disclosure

Detailed categories, evidence, mitigation, and historical context are collapsed by default.

Measured FS-300A desktop right-rail risk height: about 218 px.

### Financial Health

Financial health now shows:

- Compact summary strip
- Smaller metric grid
- Detail disclosure for risks and action plan

Metric cards have reduced padding and height.

### Chart, News, Watchlist, Spacing

- Professional Chart behavior and data remain unchanged.
- Chart surrounding descriptive text is reduced through CSS.
- Indicator controls remain chip-like.
- News padding is tightened so more items fit in the same rail height.
- Watchlist rows have reduced padding and hide secondary badges in the dense rail view.
- Global dashboard spacing was reduced from FS-300 levels.

## Browser Verification

Local browser verification was run at `http://127.0.0.1:5173`.

| Viewport | Result |
| --- | --- |
| 1920 x 1080 | PASS: no horizontal overflow; first viewport includes opportunities, price strip, chart, news, sentiment, quick assistant, and compact risk. |
| 1536 x 864 | PASS: no horizontal overflow; chart and right-rail summary panels visible in first viewport. |
| 1366 x 768 | PASS: no horizontal overflow; chart begins in first viewport and dense right rail remains visible. |
| 390 x 844 | PASS: no page-level horizontal overflow; asset selector remains capped and opportunities begin in the first viewport. |

Browser console errors from the application: none observed.

Desktop and mobile viewport screenshots were captured in the browser verification output. The automation environment did not persist image files into the repository, so this document records the measured layout results instead of linking saved screenshot artifacts.

## Validation

- Frontend build: PASS.
- Backend tests: PASS, 113 tests passed.
- Browser verification: PASS.
- No backend files changed.
- No API contracts changed.
- No mock data introduced.

## Known Limitations

- On very small mobile screens, the chart body still appears below the opportunities block because asset search remains first in the flow.
- The existing dashboard file contains legacy text from previous phases; FS-300A did not expand scope into copy restoration beyond the compact dashboard additions.
- Exact before/after screenshot files are not committed because the browser runtime captured images in-session but did not persist them to the project filesystem.

## Acceptance Decision

PASS for FS-300A density optimization.

The dashboard is materially denser, the largest analysis sections are collapsed by default, and validation passed without backend or API changes.
