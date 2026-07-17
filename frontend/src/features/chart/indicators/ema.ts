export function ema(values: Array<number | null | undefined>, period: number): Array<number | null> {
  const multiplier = 2 / (period + 1);
  let previous: number | null = null;
  return values.map((value, index) => {
    if (typeof value !== 'number') return null;
    if (index < period - 1) return null;
    if (previous == null) {
      const seed = values.slice(index - period + 1, index + 1);
      if (seed.some((item) => typeof item !== 'number')) return null;
      previous = (seed as number[]).reduce((sum, item) => sum + item, 0) / period;
      return previous;
    }
    previous = value * multiplier + previous * (1 - multiplier);
    return previous;
  });
}

