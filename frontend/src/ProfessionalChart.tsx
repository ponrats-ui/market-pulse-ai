import React from 'react';
import { api } from './lib/api';
import type { AssetHistory, AssetQuote, TechnicalResponse } from './types/market';

type ChartMode = 'candlestick' | 'ohlc' | 'area' | 'line';
type DrawingTool = 'cursor' | 'trend' | 'horizontal' | 'rectangle' | 'text' | 'arrow';
type Drawing = { id: string; type: DrawingTool; x1: number; y1: number; x2?: number; y2?: number; text?: string };
type ChartRow = Record<string, string | number | null | undefined> & { time: string; open: number | null; high: number | null; low: number | null; close: number | null; volume: number | null; label: string };

type Props = {
  t: Record<string, string>;
  l: Record<string, string>;
  history: AssetHistory | null;
  technical: TechnicalResponse | null;
  activeIndicators: string[];
  toggleIndicator: (indicator: string) => void;
  quote: AssetQuote | null;
  range: string;
  setRange: (range: string) => void;
};

const chartRanges = ['1d', '5d', '1mo', '3mo', '6mo', 'ytd', '1y', '3y', '5y', 'max'];
const chartModes: Array<{ id: ChartMode; label: string }> = [
  { id: 'candlestick', label: 'Candlestick' },
  { id: 'ohlc', label: 'OHLC' },
  { id: 'area', label: 'Area' },
  { id: 'line', label: 'Line' },
];
const indicatorToggles = ['EMA20', 'EMA50', 'EMA200', 'SMA20', 'SMA50', 'SMA200', 'RSI14', 'MACD', 'Bollinger Bands', 'ATR', 'VWAP', 'Volume MA'];
const maFields: Record<string, { key: string; color: string }> = {
  EMA20: { key: 'ema20', color: '#33d17a' },
  EMA50: { key: 'ema50', color: '#f7c948' },
  EMA200: { key: 'ema200', color: '#ff7a7a' },
  SMA20: { key: 'sma20', color: '#35d0ff' },
  SMA50: { key: 'sma50', color: '#a78bfa' },
  SMA200: { key: 'sma200', color: '#94a3b8' },
};
const comparePalettes = ['#f7c948', '#a78bfa', '#fb923c'];

export default function ProfessionalChartPanel({ t, l, history, technical, activeIndicators, toggleIndicator, quote, range, setRange }: Props) {
  const [mode, setMode] = React.useState<ChartMode>('candlestick');
  const [tool, setTool] = React.useState<DrawingTool>('cursor');
  const [drawings, setDrawings] = React.useState<Drawing[]>([]);
  const [redoStack, setRedoStack] = React.useState<Drawing[]>([]);
  const [draft, setDraft] = React.useState<Drawing | null>(null);
  const [hoverIndex, setHoverIndex] = React.useState<number | null>(null);
  const [fullscreen, setFullscreen] = React.useState(false);
  const [compareEnabled, setCompareEnabled] = React.useState(false);
  const [compareHistories, setCompareHistories] = React.useState<Record<string, ChartRow[]>>({});

  const rows = React.useMemo(() => normalizeRows(technical?.series?.length ? technical.series : history?.points ?? []), [technical, history]);
  const compareSymbols = React.useMemo(() => compareSetFor(quote?.symbol ?? ''), [quote?.symbol]);
  React.useEffect(() => {
    if (!compareEnabled || !compareSymbols.length) { setCompareHistories({}); return; }
    let ok = true;
    Promise.all(compareSymbols.map((symbol) => api.history(symbol, range, range === '1d' ? '1h' : '1d').then((payload) => [symbol, normalizeRows(payload.points)] as const).catch(() => [symbol, []] as const)))
      .then((items) => { if (!ok) return; setCompareHistories(Object.fromEntries(items)); })
      .catch((error) => console.error('Failed to load chart comparison histories', error));
    return () => { ok = false; };
  }, [compareEnabled, compareSymbols, range]);

  const domain = React.useMemo(() => priceDomain(rows, activeIndicators), [rows, activeIndicators]);
  const levels = React.useMemo(() => supportResistanceLevels(rows, quote), [rows, quote]);
  const hover = hoverIndex == null ? null : rows[hoverIndex];
  const hasData = rows.length >= 2;
  const show = (name: string) => activeIndicators.includes(name);

  const onPointerMove = (event: React.MouseEvent<SVGSVGElement>) => {
    if (!hasData) return;
    const box = event.currentTarget.getBoundingClientRect();
    const x = ((event.clientX - box.left) / box.width) * 1000;
    setHoverIndex(clamp(Math.round((x - 44) / Math.max(1, 912) * (rows.length - 1)), 0, rows.length - 1));
  };
  const onChartClick = (event: React.MouseEvent<SVGSVGElement>) => {
    if (tool === 'cursor') return;
    const box = event.currentTarget.getBoundingClientRect();
    const x = ((event.clientX - box.left) / box.width) * 1000;
    const y = ((event.clientY - box.top) / box.height) * 620;
    if (tool === 'horizontal') return commitDrawing({ id: cryptoId(), type: tool, x1: 44, y1: y, x2: 956, y2: y });
    if (tool === 'text') return commitDrawing({ id: cryptoId(), type: tool, x1: x, y1: y, text: 'Note' });
    if (!draft) { setDraft({ id: cryptoId(), type: tool, x1: x, y1: y }); return; }
    commitDrawing({ ...draft, x2: x, y2: y });
    setDraft(null);
  };
  const commitDrawing = (item: Drawing) => { setDrawings((value) => [...value, item]); setRedoStack([]); };
  const undo = () => setDrawings((value) => { const next = value.slice(0, -1); const last = value[value.length - 1]; if (last) setRedoStack((redo) => [last, ...redo]); return next; });
  const redo = () => setRedoStack((value) => { const [first, ...rest] = value; if (first) setDrawings((items) => [...items, first]); return rest; });
  const reset = () => { setDrawings([]); setRedoStack([]); setDraft(null); setHoverIndex(null); };
  const download = () => downloadChartPng(quote?.symbol ?? 'chart');

  return <section className={'panel-card professional-panel pro-chart-shell ' + (fullscreen ? 'pro-chart-fullscreen' : '')} aria-label="Professional Chart"><div className="professional-header"><span className="chart-pulse" aria-hidden="true" /><h2>Professional Chart</h2><span className="ml-auto text-xs text-terminal-muted">{history?.points.length ?? 0} {t.points ?? 'points'} | {technical?.source ?? history?.source ?? 'Unavailable'}</span></div><div className="pro-chart-toolbar" role="toolbar" aria-label="Professional chart toolbar"><div className="toolbar-group">{chartRanges.map((item) => <button key={item} className={range === item ? 'toolbar-button active' : 'toolbar-button'} onClick={() => setRange(item)}>{item.toUpperCase()}</button>)}</div><div className="toolbar-group">{chartModes.map((item) => <button key={item.id} className={mode === item.id ? 'toolbar-button active' : 'toolbar-button'} onClick={() => setMode(item.id)}>{item.label}</button>)}</div><div className="toolbar-group"><button className={compareEnabled ? 'toolbar-button active' : 'toolbar-button'} onClick={() => setCompareEnabled((value) => !value)}>Compare</button><button className="toolbar-button" onClick={() => setFullscreen((value) => !value)}>Fullscreen</button><button className="toolbar-button" onClick={reset}>Reset</button><button className="toolbar-button" onClick={download}>Download PNG</button></div></div><details className="pro-chart-indicators"><summary>Indicators and Drawing Tools</summary><div className="indicator-grid">{indicatorToggles.map((item) => <button key={item} className={show(item) ? 'pill watch-button-active' : 'pill'} aria-pressed={show(item)} onClick={() => toggleIndicator(item)}>{item}</button>)}</div><div className="drawing-grid">{(['cursor', 'trend', 'horizontal', 'rectangle', 'text', 'arrow'] as DrawingTool[]).map((item) => <button key={item} className={tool === item ? 'toolbar-button active' : 'toolbar-button'} onClick={() => setTool(item)}>{item}</button>)}<button className="toolbar-button" onClick={undo}>Undo</button><button className="toolbar-button" onClick={redo}>Redo</button><button className="toolbar-button" onClick={reset}>Delete</button></div></details><div className="pro-chart-layout"><div className="pro-chart-canvas">{hasData ? <svg className="pro-chart-svg" viewBox="0 0 1000 620" role="img" aria-label={`${quote?.symbol ?? 'Asset'} professional chart using real provider history`} onMouseMove={onPointerMove} onMouseLeave={() => setHoverIndex(null)} onClick={onChartClick}><defs><linearGradient id="chartAreaFill" x1="0" x2="0" y1="0" y2="1"><stop offset="0%" stopColor="#35d0ff" stopOpacity="0.28" /><stop offset="100%" stopColor="#35d0ff" stopOpacity="0.02" /></linearGradient><marker id="arrowHead" markerWidth="8" markerHeight="8" refX="7" refY="3" orient="auto"><path d="M0,0 L0,6 L7,3 z" fill="#35d0ff" /></marker></defs><rect x="0" y="0" width="1000" height="620" fill="#08111f" rx="8" />{gridLines(domain).map((line) => <g key={line.value}><line x1="44" x2="956" y1={line.y} y2={line.y} stroke="#1e2b3f" strokeDasharray="4 4" /><text x="965" y={line.y + 4} fill="#7e8da8" fontSize="12">{formatNumber(line.value)}</text></g>)}{levels.map((level) => <g key={level.label}><line x1="44" x2="956" y1={yFor(level.value, domain)} y2={yFor(level.value, domain)} stroke={level.color} strokeDasharray="6 4" /><text x="52" y={yFor(level.value, domain) - 5} fill={level.color} fontSize="12">{level.label} {formatNumber(level.value)}</text></g>)}{show('Bollinger Bands') && lineFor(rows, 'bollinger_upper', domain, '#64748b')}{show('Bollinger Bands') && lineFor(rows, 'bollinger_lower', domain, '#64748b')}{mode === 'area' && areaFor(rows, domain)}{mode === 'line' && lineFor(rows, 'close', domain, '#35d0ff', 2.4)}{mode === 'candlestick' && candlesFor(rows, domain)}{mode === 'ohlc' && ohlcFor(rows, domain)}{Object.entries(maFields).map(([name, config]) => show(name) ? lineFor(rows, config.key, domain, config.color, 1.5) : null)}{show('VWAP') && lineFor(rows, 'vwap', domain, '#fb923c', 1.5)}{compareEnabled && Object.entries(compareHistories).map(([symbol, items], index) => compareLine(symbol, items, rows, comparePalettes[index % comparePalettes.length]))}{volumeBars(rows)}{show('Volume MA') && volumeAverage(rows)}{drawings.map(renderDrawing)}{draft && renderDrawing({ ...draft, x2: draft.x1 + 1, y2: draft.y1 + 1 })}{hover && hoverIndex != null && <g><line x1={xForIndex(hoverIndex, rows.length)} x2={xForIndex(hoverIndex, rows.length)} y1="24" y2="548" stroke="#35d0ff" strokeDasharray="3 3" /><circle cx={xForIndex(hoverIndex, rows.length)} cy={yFor(Number(hover.close), domain)} r="4" fill="#35d0ff" /></g>}</svg> : <div className="pro-chart-empty">{technical?.message ?? 'Historical data unavailable from provider.'}</div>}</div><aside className="pro-chart-side"><h3>{quote?.symbol ?? 'Asset'} Crosshair</h3>{hover ? <div className="crosshair-card"><b>{hover.label}</b><span>O {formatNumber(hover.open)}</span><span>H {formatNumber(hover.high)}</span><span>L {formatNumber(hover.low)}</span><span>C {formatNumber(hover.close)}</span><span>V {formatNumber(hover.volume, 0)}</span><span>Daily {formatPercent(dailyChange(rows, hoverIndex ?? 0))}</span></div> : <p className="text-sm text-terminal-muted">Hover the chart for OHLCV and daily percentage.</p>}<h3>PIA Overlay</h3><p>Support, resistance, risk zone and confidence are overlays only. Raw provider prices are never modified.</p><h3>Events</h3><p>Dividend, earnings, split, news and economic event overlays are hidden until a live provider returns event data.</p>{compareEnabled && <p>Compare: {compareSymbols.join(', ')}</p>}<h3>Indicator State</h3><p>RSI {formatNumber(technical?.indicators?.RSI14 as number | null)} | ATR {formatNumber(technical?.indicators?.ATR as number | null)}</p><p>MACD {formatNumber((technical?.indicators?.MACD as Record<string, number | null> | undefined)?.line)}</p></aside></div><div className="pro-chart-footer"><span>{l.realData ?? 'Real provider data only'}</span><span>Support/resistance and zones are educational overlays, not predictions.</span></div></section>;
}

function normalizeRows(points: Array<Record<string, unknown> | { time: string; open: number | null; high: number | null; low: number | null; close: number | null; volume: number | null }>): ChartRow[] {
  return points.map((point) => ({ ...point, time: String(point.time ?? ''), open: num(point.open), high: num(point.high), low: num(point.low), close: num(point.close), volume: num(point.volume), label: point.time ? new Date(String(point.time)).toLocaleDateString(undefined, { month: 'short', day: 'numeric' }) : 'N/A' })).filter((row) => row.close != null);
}
function num(value: unknown): number | null { return typeof value === 'number' && Number.isFinite(value) ? value : value == null ? null : Number.isFinite(Number(value)) ? Number(value) : null; }
function priceDomain(rows: ChartRow[], active: string[]) { const values = rows.flatMap((row) => [row.high, row.low, row.close, ...Object.values(maFields).map((config) => active.includes(fieldName(config.key)) ? num(row[config.key]) : null), active.includes('Bollinger Bands') ? num(row.bollinger_upper) : null, active.includes('Bollinger Bands') ? num(row.bollinger_lower) : null]).filter((value): value is number => typeof value === 'number'); const min = Math.min(...values); const max = Math.max(...values); const pad = (max - min || Math.abs(max) || 1) * 0.08; return { min: min - pad, max: max + pad }; }
function fieldName(key: string) { return key.toUpperCase().replace('EMA', 'EMA').replace('SMA', 'SMA'); }
function xForIndex(index: number, length: number) { return 44 + (index / Math.max(1, length - 1)) * 912; }
function yFor(value: number, domain: { min: number; max: number }) { return 404 - ((value - domain.min) / Math.max(1e-9, domain.max - domain.min)) * 380; }
function pathFor(rows: ChartRow[], key: string, domain: { min: number; max: number }) { return rows.map((row, index) => ({ x: xForIndex(index, rows.length), y: row[key] == null ? null : yFor(Number(row[key]), domain) })).filter((point) => point.y != null).map((point, index) => `${index ? 'L' : 'M'}${point.x.toFixed(2)},${Number(point.y).toFixed(2)}`).join(' '); }
function lineFor(rows: ChartRow[], key: string, domain: { min: number; max: number }, color: string, width = 1.2) { const d = pathFor(rows, key, domain); return d ? <path key={`${key}-${color}`} d={d} fill="none" stroke={color} strokeWidth={width} strokeLinecap="round" strokeLinejoin="round" /> : null; }
function areaFor(rows: ChartRow[], domain: { min: number; max: number }) { const d = pathFor(rows, 'close', domain); return d ? <><path d={`${d} L956,404 L44,404 Z`} fill="url(#chartAreaFill)" /><path d={d} fill="none" stroke="#35d0ff" strokeWidth="2.4" /></> : null; }
function candlesFor(rows: ChartRow[], domain: { min: number; max: number }) { const w = Math.max(2, Math.min(10, 760 / Math.max(1, rows.length))); return <g>{rows.map((row, index) => { const x = xForIndex(index, rows.length); const open = yFor(row.open ?? row.close ?? 0, domain); const close = yFor(row.close ?? row.open ?? 0, domain); const high = yFor(row.high ?? row.close ?? 0, domain); const low = yFor(row.low ?? row.close ?? 0, domain); const up = (row.close ?? 0) >= (row.open ?? row.close ?? 0); return <g key={row.time}><line x1={x} x2={x} y1={high} y2={low} stroke={up ? '#33d17a' : '#ff7a7a'} /><rect x={x - w / 2} y={Math.min(open, close)} width={w} height={Math.max(2, Math.abs(close - open))} fill={up ? '#33d17a' : '#ff7a7a'} rx="1" /></g>; })}</g>; }
function ohlcFor(rows: ChartRow[], domain: { min: number; max: number }) { return <g>{rows.map((row, index) => { const x = xForIndex(index, rows.length); const open = yFor(row.open ?? row.close ?? 0, domain); const close = yFor(row.close ?? row.open ?? 0, domain); const high = yFor(row.high ?? row.close ?? 0, domain); const low = yFor(row.low ?? row.close ?? 0, domain); const up = (row.close ?? 0) >= (row.open ?? row.close ?? 0); return <g key={row.time} stroke={up ? '#33d17a' : '#ff7a7a'}><line x1={x} x2={x} y1={high} y2={low} /><line x1={x - 5} x2={x} y1={open} y2={open} /><line x1={x} x2={x + 5} y1={close} y2={close} /></g>; })}</g>; }
function volumeBars(rows: ChartRow[]) { const max = Math.max(...rows.map((row) => row.volume ?? 0), 1); return <g>{rows.map((row, index) => { const x = xForIndex(index, rows.length); const h = ((row.volume ?? 0) / max) * 94; const up = (row.close ?? 0) >= (row.open ?? row.close ?? 0); return <rect key={`${row.time}-v`} x={x - 2} y={532 - h} width="4" height={h} fill={up ? '#33d17a88' : '#ff7a7a88'} />; })}<text x="52" y="548" fill="#7e8da8" fontSize="12">Volume</text></g>; }
function volumeAverage(rows: ChartRow[]) { const values = rows.map((row) => row.volume ?? 0); const ma = values.map((_, index) => index < 19 ? null : values.slice(index - 19, index + 1).reduce((a, b) => a + b, 0) / 20); const max = Math.max(...values, 1); const d = ma.map((value, index) => value == null ? null : `${index ? 'L' : 'M'}${xForIndex(index, rows.length).toFixed(2)},${(532 - (value / max) * 94).toFixed(2)}`).filter(Boolean).join(' '); return d ? <path d={d} fill="none" stroke="#f7c948" strokeWidth="1.4" /> : null; }
function gridLines(domain: { min: number; max: number }) { return Array.from({ length: 5 }, (_, index) => { const value = domain.min + ((domain.max - domain.min) / 4) * index; return { value, y: yFor(value, domain) }; }); }
function supportResistanceLevels(rows: ChartRow[], quote: AssetQuote | null) { const recent = rows.slice(-40); const lows = recent.map((row) => row.low ?? row.close).filter((value): value is number => typeof value === 'number'); const highs = recent.map((row) => row.high ?? row.close).filter((value): value is number => typeof value === 'number'); const allHighs = rows.map((row) => row.high ?? row.close).filter((value): value is number => typeof value === 'number'); const allLows = rows.map((row) => row.low ?? row.close).filter((value): value is number => typeof value === 'number'); const levels = [{ label: 'Support', value: Math.min(...lows), color: '#33d17a' }, { label: 'Resistance', value: Math.max(...highs), color: '#ff7a7a' }, { label: '52W High', value: Math.max(...allHighs), color: '#f7c948' }, { label: '52W Low', value: Math.min(...allLows), color: '#35d0ff' }]; if (quote?.previous_close) levels.push({ label: 'Prev Close', value: quote.previous_close, color: '#a78bfa' }); return levels.filter((level) => Number.isFinite(level.value)); }
function compareSetFor(symbol: string) { if (symbol.endsWith('.BK')) return ['PTT.BK', 'AOT.BK', 'KBANK.BK'].filter((item) => item !== symbol).slice(0, 3); return ['AAPL', 'MSFT', 'NVDA'].filter((item) => item !== symbol).slice(0, 3); }
function compareLine(symbol: string, items: ChartRow[], baseRows: ChartRow[], color: string) { if (items.length < 2 || baseRows.length < 2) return null; const values = items.map((row) => row.close).filter((value): value is number => typeof value === 'number'); const start = values[0]; if (!start) return null; const returns = values.map((value) => ((value - start) / start) * 100); const min = Math.min(...returns, -10); const max = Math.max(...returns, 10); const domain = { min, max }; const rows = returns.map((value, index) => ({ time: String(index), label: symbol, open: value, high: value, low: value, close: value, volume: null })); return <g key={symbol}>{lineFor(rows, 'close', domain, color, 1.8)}<text x="820" y={40 + comparePalettes.indexOf(color) * 16} fill={color} fontSize="12">{symbol} normalized %</text></g>; }
function renderDrawing(item: Drawing) { if (item.type === 'text') return <text key={item.id} x={item.x1} y={item.y1} fill="#d9e7ff" fontSize="16">{item.text}</text>; if (item.type === 'rectangle') return <rect key={item.id} x={Math.min(item.x1, item.x2 ?? item.x1)} y={Math.min(item.y1, item.y2 ?? item.y1)} width={Math.abs((item.x2 ?? item.x1) - item.x1)} height={Math.abs((item.y2 ?? item.y1) - item.y1)} fill="#35d0ff18" stroke="#35d0ff" />; return <line key={item.id} x1={item.x1} y1={item.y1} x2={item.x2 ?? item.x1} y2={item.y2 ?? item.y1} stroke="#35d0ff" strokeWidth="2" markerEnd={item.type === 'arrow' ? 'url(#arrowHead)' : undefined} />; }
function dailyChange(rows: ChartRow[], index: number) { if (index <= 0) return null; const current = rows[index]?.close; const previous = rows[index - 1]?.close; return current != null && previous ? ((current - previous) / previous) * 100 : null; }
function formatNumber(value: number | null | undefined, digits = 2) { return value == null || !Number.isFinite(Number(value)) ? 'N/A' : new Intl.NumberFormat('en-US', { maximumFractionDigits: digits }).format(Number(value)); }
function formatPercent(value: number | null | undefined) { return value == null || !Number.isFinite(Number(value)) ? 'N/A' : `${value >= 0 ? '+' : ''}${Number(value).toFixed(2)}%`; }
function clamp(value: number, min: number, max: number) { return Math.max(min, Math.min(max, value)); }
function cryptoId() { return Math.random().toString(36).slice(2); }
function downloadChartPng(symbol: string) { const svg = document.querySelector('.pro-chart-svg'); if (!(svg instanceof SVGSVGElement)) return; const serializer = new XMLSerializer(); const source = serializer.serializeToString(svg); const image = new Image(); const blob = new Blob([source], { type: 'image/svg+xml;charset=utf-8' }); const url = URL.createObjectURL(blob); image.onload = () => { const canvas = document.createElement('canvas'); canvas.width = 1400; canvas.height = 868; const context = canvas.getContext('2d'); if (!context) return; context.fillStyle = '#08111f'; context.fillRect(0, 0, canvas.width, canvas.height); context.drawImage(image, 0, 0, canvas.width, canvas.height); URL.revokeObjectURL(url); const link = document.createElement('a'); link.href = canvas.toDataURL('image/png'); link.download = `${symbol}-professional-chart.png`; link.click(); }; image.src = url; }
