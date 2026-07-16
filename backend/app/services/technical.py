from __future__ import annotations

from typing import Any, Dict, List


INDICATORS = ("EMA20", "EMA50", "EMA200", "SMA20", "SMA50", "SMA200", "RSI14", "MACD", "Volume", "ATR", "VWAP", "Bollinger Bands")


def build_technical_analysis(symbol: str, history: Dict[str, Any]) -> Dict[str, Any]:
    points = history.get("points", [])
    rows = [_clean_point(point) for point in points if _clean_point(point).get("close") is not None]
    if len(rows) < 2:
        return {
            "symbol": symbol,
            "status": "unavailable",
            "indicators": {},
            "series": [],
            "available_indicators": list(INDICATORS),
            "message": "Technical analysis requires provider-returned historical OHLCV data.",
            "message_th": "การวิเคราะห์ทางเทคนิคต้องใช้ข้อมูลราคาและปริมาณย้อนหลังจากผู้ให้บริการ",
            "source": history.get("source", "Unavailable"),
            "disclaimer": "This is not financial advice.",
        }

    closes = [float(row["close"]) for row in rows]
    highs = [float(row["high"] if row["high"] is not None else row["close"]) for row in rows]
    lows = [float(row["low"] if row["low"] is not None else row["close"]) for row in rows]
    volumes = [float(row["volume"] or 0) for row in rows]
    ema20 = _ema(closes, 20)
    ema50 = _ema(closes, 50)
    ema200 = _ema(closes, 200)
    sma20 = _sma(closes, 20)
    sma50 = _sma(closes, 50)
    sma200 = _sma(closes, 200)
    rsi14 = _rsi(closes, 14)
    macd_line, macd_signal, macd_histogram = _macd(closes)
    atr14 = _atr(highs, lows, closes, 14)
    vwap = _vwap(rows)
    upper_band, middle_band, lower_band = _bollinger(closes, 20)
    latest_close = closes[-1]

    indicators = {
        "EMA20": _last(ema20),
        "EMA50": _last(ema50),
        "EMA200": _last(ema200),
        "SMA20": _last(sma20),
        "SMA50": _last(sma50),
        "SMA200": _last(sma200),
        "RSI14": _last(rsi14),
        "MACD": {"line": _last(macd_line), "signal": _last(macd_signal), "histogram": _last(macd_histogram)},
        "Volume": volumes[-1],
        "ATR": _last(atr14),
        "VWAP": _last(vwap),
        "Bollinger Bands": {"upper": _last(upper_band), "middle": _last(middle_band), "lower": _last(lower_band)},
    }
    trend = _trend(latest_close, indicators)
    return {
        "symbol": symbol,
        "status": "ok",
        "available_indicators": list(INDICATORS),
        "indicators": indicators,
        "series": _series(rows, ema20, ema50, ema200, sma20, sma50, sma200, rsi14, macd_line, macd_signal, macd_histogram, atr14, vwap, upper_band, middle_band, lower_band),
        "interpretation": {
            "trend": trend,
            "evidence": _technical_evidence(latest_close, indicators),
            "confidence": "medium" if len(rows) >= 50 else "low",
            "limitations": ["Indicators are calculated from provider-returned historical prices and can lag fast market moves."],
        },
        "source": history.get("source", "Unavailable"),
        "disclaimer": "This is not financial advice.",
    }


def _clean_point(point: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "time": point.get("time"),
        "open": _number(point.get("open")),
        "high": _number(point.get("high")),
        "low": _number(point.get("low")),
        "close": _number(point.get("close")),
        "volume": _number(point.get("volume")),
    }


def _number(value: Any) -> float | None:
    try:
        if value in (None, ""):
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def _sma(values: List[float], period: int) -> List[float | None]:
    output: List[float | None] = []
    for index in range(len(values)):
        if index + 1 < period:
            output.append(None)
            continue
        window = values[index + 1 - period:index + 1]
        output.append(sum(window) / period)
    return output


def _ema(values: List[float], period: int) -> List[float | None]:
    if not values:
        return []
    multiplier = 2 / (period + 1)
    output: List[float | None] = []
    current = values[0]
    for index, value in enumerate(values):
        current = value if index == 0 else (value - current) * multiplier + current
        output.append(current if index + 1 >= min(period, len(values)) else None)
    return output


def _rsi(values: List[float], period: int) -> List[float | None]:
    output: List[float | None] = [None]
    gains: List[float] = []
    losses: List[float] = []
    for previous, current in zip(values, values[1:]):
        change = current - previous
        gains.append(max(change, 0))
        losses.append(abs(min(change, 0)))
        if len(gains) < period:
            output.append(None)
            continue
        recent_gains = gains[-period:]
        recent_losses = losses[-period:]
        avg_gain = sum(recent_gains) / period
        avg_loss = sum(recent_losses) / period
        if avg_loss == 0:
            output.append(100.0)
        else:
            rs = avg_gain / avg_loss
            output.append(100 - (100 / (1 + rs)))
    return output


def _macd(values: List[float]) -> tuple[List[float | None], List[float | None], List[float | None]]:
    ema12 = _ema(values, 12)
    ema26 = _ema(values, 26)
    line = [(fast - slow) if fast is not None and slow is not None else None for fast, slow in zip(ema12, ema26)]
    compact = [value for value in line if value is not None]
    signal_compact = _ema(compact, 9)
    signal: List[float | None] = [None] * (len(line) - len(signal_compact)) + signal_compact
    histogram = [(value - sig) if value is not None and sig is not None else None for value, sig in zip(line, signal)]
    return line, signal, histogram


def _atr(highs: List[float], lows: List[float], closes: List[float], period: int) -> List[float | None]:
    true_ranges: List[float] = []
    for index, high in enumerate(highs):
        previous_close = closes[index - 1] if index > 0 else closes[index]
        true_ranges.append(max(high - lows[index], abs(high - previous_close), abs(lows[index] - previous_close)))
    return _sma(true_ranges, period)


def _vwap(rows: List[Dict[str, Any]]) -> List[float | None]:
    output: List[float | None] = []
    cumulative_price_volume = 0.0
    cumulative_volume = 0.0
    for row in rows:
        high = row["high"] if row["high"] is not None else row["close"]
        low = row["low"] if row["low"] is not None else row["close"]
        close = row["close"]
        volume = row["volume"] or 0
        typical = (high + low + close) / 3
        cumulative_price_volume += typical * volume
        cumulative_volume += volume
        output.append(cumulative_price_volume / cumulative_volume if cumulative_volume else None)
    return output


def _bollinger(values: List[float], period: int) -> tuple[List[float | None], List[float | None], List[float | None]]:
    middle = _sma(values, period)
    upper: List[float | None] = []
    lower: List[float | None] = []
    for index, mid in enumerate(middle):
        if mid is None:
            upper.append(None)
            lower.append(None)
            continue
        window = values[index + 1 - period:index + 1]
        variance = sum((value - mid) ** 2 for value in window) / period
        deviation = variance ** 0.5
        upper.append(mid + 2 * deviation)
        lower.append(mid - 2 * deviation)
    return upper, middle, lower


def _series(rows: List[Dict[str, Any]], *columns: List[float | None]) -> List[Dict[str, Any]]:
    names = ("ema20", "ema50", "ema200", "sma20", "sma50", "sma200", "rsi14", "macd", "macd_signal", "macd_histogram", "atr", "vwap", "bollinger_upper", "bollinger_middle", "bollinger_lower")
    result: List[Dict[str, Any]] = []
    for index, row in enumerate(rows):
        item = {**row}
        for name, column in zip(names, columns):
            item[name] = column[index] if index < len(column) else None
        result.append(item)
    return result


def _last(values: List[Any]) -> Any:
    for value in reversed(values):
        if value is not None:
            return value
    return None


def _trend(latest_close: float, indicators: Dict[str, Any]) -> str:
    ema20 = indicators.get("EMA20")
    ema50 = indicators.get("EMA50")
    if isinstance(ema20, (int, float)) and isinstance(ema50, (int, float)):
        if latest_close > ema20 > ema50:
            return "constructive"
        if latest_close < ema20 < ema50:
            return "under pressure"
    return "mixed"


def _technical_evidence(latest_close: float, indicators: Dict[str, Any]) -> List[str]:
    evidence = [f"Latest close used for indicators: {round(latest_close, 4)}."]
    rsi = indicators.get("RSI14")
    if isinstance(rsi, (int, float)):
        evidence.append(f"RSI14 is {round(rsi, 2)}, interpreted as overbought above 70 and oversold below 30.")
    atr = indicators.get("ATR")
    if isinstance(atr, (int, float)):
        evidence.append(f"ATR is {round(atr, 4)}, used as a volatility and position-sizing reference.")
    return evidence
