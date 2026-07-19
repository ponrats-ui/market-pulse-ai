export type ChartMode = 'candlestick' | 'ohlc' | 'area' | 'line';
export type DrawingTool = 'cursor' | 'trend' | 'horizontal' | 'rectangle' | 'text' | 'arrow';
export type Drawing = { id: string; type: DrawingTool; x1: number; y1: number; x2?: number; y2?: number; text?: string };
export type ChartRow = Record<string, string | number | null | undefined> & { time: string; open: number | null; high: number | null; low: number | null; close: number | null; volume: number | null; label: string };

export const chartRanges = ['1d', '5d', '1mo', '3mo', '6mo', 'ytd', '1y', '3y', '5y', 'max'];
export const chartModes: Array<{ id: ChartMode; label: string }> = [
  { id: 'line', label: 'Line' },
  { id: 'candlestick', label: 'Candlestick' },
  { id: 'area', label: 'Area' },
  { id: 'ohlc', label: 'OHLC' },
];
export const indicatorToggles = ['EMA20', 'EMA50', 'EMA200', 'SMA20', 'SMA50', 'SMA200', 'RSI14', 'MACD', 'Bollinger Bands', 'ATR', 'VWAP', 'Volume MA'];
export const maFields: Record<string, { key: string; color: string }> = {
  EMA20: { key: 'ema20', color: '#33d17a' },
  EMA50: { key: 'ema50', color: '#f7c948' },
  EMA200: { key: 'ema200', color: '#ff7a7a' },
  SMA20: { key: 'sma20', color: '#35d0ff' },
  SMA50: { key: 'sma50', color: '#a78bfa' },
  SMA200: { key: 'sma200', color: '#94a3b8' },
};
export const comparePalettes = ['#f7c948', '#a78bfa', '#fb923c'];
