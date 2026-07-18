import { sma } from './sma';

export function volumeMa(values: Array<number | null | undefined>, period = 20): Array<number | null> {
  return sma(values, period);
}

