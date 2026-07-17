import { sma } from './sma';

export function bollinger(values: Array<number | null | undefined>, period = 20, deviations = 2) {
  const middle = sma(values, period);
  const upper = values.map((_, index) => {
    const mean = middle[index];
    if (mean == null) return null;
    const window = values.slice(index - period + 1, index + 1) as number[];
    const variance = window.reduce((sum, value) => sum + (value - mean) ** 2, 0) / period;
    return mean + Math.sqrt(variance) * deviations;
  });
  const lower = values.map((_, index) => {
    const mean = middle[index];
    if (mean == null) return null;
    const window = values.slice(index - period + 1, index + 1) as number[];
    const variance = window.reduce((sum, value) => sum + (value - mean) ** 2, 0) / period;
    return mean - Math.sqrt(variance) * deviations;
  });
  return { upper, middle, lower };
}

