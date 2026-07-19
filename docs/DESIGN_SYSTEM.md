# Market Pulse AI Design System v1.0

Market Pulse AI uses a professional executive dashboard design system inspired by Bloomberg, TradingView, Morningstar, Apple Human Interface, Linear, and Stripe Dashboard. The system should feel trustworthy, institutional, modern, readable, and calm.

## Design Philosophy

Every screen should help investors understand the answer to "so what?" in less than five seconds.

- Use real data states clearly.
- Lead with executive insight before dense detail.
- Use color only when it communicates meaning.
- Keep motion subtle and purposeful.
- Never make the interface feel like a game, neon terminal, or speculative product.

## Color Tokens

Use semantic tokens instead of raw color values in components.

| Token | Purpose | Value |
| --- | --- | --- |
| `--mp-bg-primary` | App background | `#05070d` |
| `--mp-bg-secondary` | Secondary background | `#08111f` |
| `--mp-bg-card` | Card background | `#0a101c` |
| `--mp-bg-elevated` | Inputs, nested panels | `#101827` |
| `--mp-border` | Card/control border | `#1e2b3f` |
| `--mp-divider` | Internal dividers | `#26364f` |
| `--mp-text-primary` | Primary numbers/headlines | `#f4f8ff` |
| `--mp-text-secondary` | Body text | `#c6d3e6` |
| `--mp-text-muted` | Supporting text | `#8ea0ba` |
| `--mp-text-metadata` | Footnotes/timestamps | `#6f8099` |
| `--mp-positive` | Growth, bullish, healthy | `#39e58d` |
| `--mp-negative` | Loss, bearish, negative | `#ff6678` |
| `--mp-warning` | Caution | `#f5b84b` |
| `--mp-information` | Data/provider info | `#38bdf8` |
| `--mp-ai` | AI/PIA intelligence | `#b78cff` |
| `--mp-health` | Financial health | `#34d399` |
| `--mp-risk` | Risk/reduce/weak | `#fb923c` |
| `--mp-selected` | Selected/focus state | `#35d0ff` |

Tailwind mirrors these as `mp.*` colors in `frontend/tailwind.config.js`.

## Typography

Use the shared typography scale. Avoid arbitrary font sizes.

| Role | Size |
| --- | --- |
| Hero | `1.9rem` |
| Section Title | `0.78rem` |
| Card Title | `0.86rem` |
| Headline | `1.15rem` |
| Body | `0.88rem` |
| Caption | `0.75rem` |
| Metadata | `0.68rem` |
| Button | `0.78rem` |
| Badge | `0.68rem` |

## Spacing

Use the 8px spacing grid:

`4, 8, 12, 16, 20, 24, 32, 40, 48, 64`

Prefer `8`, `12`, and `16` inside dense dashboard surfaces. Use `24+` only for page-level separation.

## Components

Reusable primitives live in:

`frontend/src/components/design-system.tsx`

Available primitives:

- `Card`
- `Badge`
- `Button`
- `IconButton`
- `Tooltip`
- `InfoRow`
- `Metric`
- `ExecutiveSummary`
- `ProgressMeter`
- `RiskMeter`
- `HealthMeter`
- `InsightBox`
- `SectionHeader`

### Card

Cards use:

- 8px radius
- 16px padding
- semantic border
- soft institutional shadow
- optional `SectionHeader`
- optional footer

### Badge

Badges must include icon and text, never color alone.

Supported tones:

- `positive`
- `negative`
- `warning`
- `neutral`
- `info`
- `ai`
- `health`
- `risk`
- `unavailable`

### Button

Button variants:

- `primary`
- `secondary`
- `outline`
- `ghost`
- `danger`
- `icon`

Every button must keep consistent height, radius, focus ring, and typography.

### Executive Insight

Every major card should begin with one executive sentence, maximum 80 characters.

Examples:

- "Ranked assets to review first from real provider data."
- "Current AI stance, confidence, horizon, and risk in one glance."
- "Business quality and balance-sheet strength from available fundamentals."

## Chart Design

Default chart type is Line Chart. Candlestick remains optional.

Charts should use:

- calm grid lines
- readable axes
- consistent tooltip styling
- clear legend chips
- visible selected states
- transparent unavailable states

## Empty States

Empty states must explain why data is unavailable.

Use:

> Unavailable  
> Provider currently unavailable.

Do not show a blank panel, broken-looking card, or fabricated value.

## Loading States

Use skeleton loading for content areas. Avoid spinner-only screens.

Skeletons should use subtle shimmer, low contrast, and stable dimensions.

## Accessibility

- Maintain WCAG AA contrast.
- Provide visible focus rings.
- Use color plus text or icon.
- Keep keyboard navigation intact.
- Use semantic buttons for clickable cards.

## Responsive Rules

Breakpoints:

- Mobile: `< 820px`
- Tablet: `820px-1180px`
- Desktop: `1180px-1535px`
- Large Desktop: `1536px+`

Dense horizontal controls may scroll inside their own container, but the page must not create horizontal overflow.

## Usage Examples

```tsx
<Card title="Chief Investment AI" insight="Current stance and risk in one glance.">
  <Metric label="Recommendation" value="Hold" tone="ai" />
  <Badge tone="warning">Medium Risk</Badge>
  <ProgressMeter value={68} label="Confidence 68%" tone="ai" />
</Card>
```

```tsx
<InsightBox tone="risk">
  Risk is elevated. Review position size before adding exposure.
</InsightBox>
```

## Do

- Use semantic tokens.
- Use one clear executive takeaway per section.
- Format large numbers as K/M/B/T.
- Use badges for important states.
- Use micro visualizations when they clarify signal strength.

## Don't

- Do not hardcode random colors in components.
- Do not use color as the only signal.
- Do not add decorative neon effects.
- Do not increase dashboard height just to add explanations.
- Do not fabricate missing data.
- Do not use arbitrary spacing or font sizes.

## Current Adoption

Design tokens are available through:

- `frontend/src/components/design-system.tsx`
- `frontend/src/styles.css`
- `frontend/tailwind.config.js`

Existing dashboard sections now share the same visual language for executive summaries, badges, meters, cards, focus states, empty states, and responsive containment.
