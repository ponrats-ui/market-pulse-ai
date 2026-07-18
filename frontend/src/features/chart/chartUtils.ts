export function rangeToInterval(range: string): string {
  if (range === '1d' || range === '5d') return '1h';
  return '1d';
}

export function normalizeReturnSeries(values: number[]): number[] {
  const base = values.find((value) => Number.isFinite(value) && value !== 0);
  if (!base) return [];
  return values.map((value) => ((value - base) / base) * 100);
}

