import { sma } from './sma';

export function atr(rows: Array<{ high: number | null; low: number | null; close: number | null }>, period = 14): Array<number | null> {
  const trueRanges = rows.map((row, index) => {
    if (row.high == null || row.low == null) return null;
    const previousClose = rows[index - 1]?.close;
    if (previousClose == null) return row.high - row.low;
    return Math.max(row.high - row.low, Math.abs(row.high - previousClose), Math.abs(row.low - previousClose));
  });
  return sma(trueRanges, period);
}

