from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List

import yfinance as yf

from app.providers.base import MarketDataProvider


class YFinanceProvider(MarketDataProvider):
    def get_asset_snapshot(self, symbol: str) -> Dict[str, Any]:
        ticker = yf.Ticker(symbol)
        info = ticker.fast_info
        history = ticker.history(period="1mo", interval="1d")

        last_price = self._safe_float(getattr(info, "last_price", None))
        previous_close = self._safe_float(getattr(info, "previous_close", None))
        if last_price is None and not history.empty:
            last_price = self._safe_float(history["Close"].iloc[-1])
        if previous_close is None and len(history.index) > 1:
            previous_close = self._safe_float(history["Close"].iloc[-2])

        change = None
        change_percent = None
        if last_price is not None and previous_close not in (None, 0):
            change = last_price - previous_close
            change_percent = (change / previous_close) * 100

        return {
            "symbol": symbol,
            "price": last_price,
            "previousClose": previous_close,
            "change": change,
            "changePercent": change_percent,
            "currency": getattr(info, "currency", None) or "USD",
            "asOf": datetime.now(timezone.utc).isoformat(),
            "source": "yfinance",
            "history": self._history_frame_to_points(history),
        }

    def get_history(self, symbol: str, period: str = "1mo") -> List[Dict[str, Any]]:
        history = yf.Ticker(symbol).history(period=period, interval="1d")
        return self._history_frame_to_points(history)

    def get_financials(self, symbol: str) -> Dict[str, Any]:
        ticker = yf.Ticker(symbol)
        info = ticker.info or {}
        return {
            "symbol": symbol,
            "revenueTrend": "Placeholder until normalized statement history is enabled.",
            "netProfitTrend": "Placeholder until normalized statement history is enabled.",
            "grossMargin": self._safe_float(info.get("grossMargins")),
            "netMargin": self._safe_float(info.get("profitMargins")),
            "debtToEquity": self._safe_float(info.get("debtToEquity")),
            "cashFlowQuality": "Needs operating cash flow and earnings consistency review.",
            "roe": self._safe_float(info.get("returnOnEquity")),
            "roa": self._safe_float(info.get("returnOnAssets")),
            "eps": self._safe_float(info.get("trailingEps")),
            "pe": self._safe_float(info.get("trailingPE")),
            "pbv": self._safe_float(info.get("priceToBook")),
            "dividendYield": self._safe_float(info.get("dividendYield")),
            "threeToFiveYearTrend": "Placeholder for 3-5 year revenue, margin, and earnings trend.",
            "balanceSheetStrength": "Review leverage, liquidity, and refinancing risk before relying on valuation.",
            "earningsQuality": "Review recurring earnings versus one-time items.",
            "valuationRisk": "Valuation may be sensitive to rates, growth assumptions, and market sentiment.",
            "source": "yfinance",
        }

    def _history_frame_to_points(self, history: Any) -> List[Dict[str, Any]]:
        if history is None or history.empty:
            return []
        points: List[Dict[str, Any]] = []
        for index, row in history.tail(45).iterrows():
            points.append({
                "date": index.strftime("%Y-%m-%d"),
                "close": self._safe_float(row.get("Close")),
                "volume": self._safe_float(row.get("Volume")),
            })
        return points

    def _safe_float(self, value: Any) -> float | None:
        try:
            if value is None:
                return None
            return float(value)
        except (TypeError, ValueError):
            return None
