export function vwap(rows: Array<{ high: number | null; low: number | null; close: number | null; volume: number | null }>): Array<number | null> {
  let cumulativePriceVolume = 0;
  let cumulativeVolume = 0;
  return rows.map((row) => {
    if (row.high == null || row.low == null || row.close == null || row.volume == null || row.volume <= 0) return null;
    const typicalPrice = (row.high + row.low + row.close) / 3;
    cumulativePriceVolume += typicalPrice * row.volume;
    cumulativeVolume += row.volume;
    return cumulativeVolume ? cumulativePriceVolume / cumulativeVolume : null;
  });
}

