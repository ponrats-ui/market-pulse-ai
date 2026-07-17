import type { AssetQuote } from '../../types/market';
import { maFields, type ChartRow } from './chartTypes';

export function ChartLegend({ quote, activeIndicators, rows, formatNumber }: { quote: AssetQuote | null; activeIndicators: string[]; rows: ChartRow[]; formatNumber: (value: number | null | undefined, digits?: number) => string }) {
  const latest = rows[rows.length - 1] ?? {};
  const visibleAverages = Object.entries(maFields).filter(([name]) => activeIndicators.includes(name));
  return <div className="pro-chart-legend" aria-label="Visible chart layers"><span>{quote?.symbol ?? 'Asset'} | {quote?.currency ?? 'Currency unavailable'}</span>{visibleAverages.map(([name, config]) => <span key={name} style={{ color: config.color }}>{name}: {formatNumber(latest[config.key] as number | null)}</span>)}{activeIndicators.includes('Bollinger Bands') && <span>Bollinger Bands: visible</span>}{activeIndicators.includes('Volume MA') && <span>Volume MA: visible when volume exists</span>}</div>;
}
