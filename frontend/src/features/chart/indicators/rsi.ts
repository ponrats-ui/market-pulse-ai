export function rsi(values: Array<number | null | undefined>, period = 14): Array<number | null> {
  const output = values.map(() => null as number | null);
  for (let index = period; index < values.length; index += 1) {
    let gain = 0;
    let loss = 0;
    for (let offset = index - period + 1; offset <= index; offset += 1) {
      const current = values[offset];
      const previous = values[offset - 1];
      if (typeof current !== 'number' || typeof previous !== 'number') {
        gain = NaN;
        break;
      }
      const change = current - previous;
      if (change >= 0) gain += change;
      else loss += Math.abs(change);
    }
    if (Number.isNaN(gain)) continue;
    output[index] = loss === 0 ? 100 : 100 - 100 / (1 + gain / period / (loss / period));
  }
  return output;
}

