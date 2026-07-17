export function sma(values: Array<number | null | undefined>, period: number): Array<number | null> {
  return values.map((_, index) => {
    if (index < period - 1) return null;
    const window = values.slice(index - period + 1, index + 1);
    if (window.some((value) => typeof value !== 'number')) return null;
    return (window as number[]).reduce((sum, value) => sum + value, 0) / period;
  });
}

