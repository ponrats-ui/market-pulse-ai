import type { AssetQuote } from '../../types/market';
import type { ChartRow } from './chartTypes';

export function ChartTooltip({ quote, hover, hoverIndex, rows, formatNumber, formatPercent, dailyChange }: { quote: AssetQuote | null; hover: ChartRow | null; hoverIndex: number | null; rows: ChartRow[]; formatNumber: (value: number | null | undefined, digits?: number) => string; formatPercent: (value: number | null | undefined) => string; dailyChange: (rows: ChartRow[], index: number) => number | null }) {
  return <><h3>{quote?.symbol ?? 'Asset'} Crosshair</h3>{hover ? <div className="crosshair-card" aria-live="polite"><b>{hover.label}</b><span>O {formatNumber(hover.open)}</span><span>H {formatNumber(hover.high)}</span><span>L {formatNumber(hover.low)}</span><span>C {formatNumber(hover.close)}</span><span>V {formatNumber(hover.volume, 0)}</span><span>Daily {formatPercent(dailyChange(rows, hoverIndex ?? 0))}</span></div> : <p className="text-sm text-terminal-muted">Hover the chart for OHLCV and daily percentage.</p>}</>;
}
