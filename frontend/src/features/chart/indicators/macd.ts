import { ema } from './ema';

export function macd(values: Array<number | null | undefined>, fast = 12, slow = 26, signalPeriod = 9) {
  const fastLine = ema(values, fast);
  const slowLine = ema(values, slow);
  const line = values.map((_, index) => fastLine[index] == null || slowLine[index] == null ? null : Number(fastLine[index]) - Number(slowLine[index]));
  const signal = ema(line, signalPeriod);
  const histogram = line.map((value, index) => value == null || signal[index] == null ? null : value - Number(signal[index]));
  return { line, signal, histogram };
}

