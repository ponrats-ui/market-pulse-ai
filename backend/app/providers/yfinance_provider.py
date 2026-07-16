from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List

import pandas as pd
import yfinance as yf

from app.providers.base import MarketDataProvider

VALID_RANGES = {"1d", "5d", "1mo", "3mo", "6mo", "ytd", "1y", "3y", "5y", "max"}
VALID_INTERVALS = {"1h", "1d", "1wk"}
THAI_STOCKS = {"SET.BK", "^SET.BK", "^SET50.BK", "PTT.BK", "AOT.BK", "CPALL.BK", "DELTA.BK", "KBANK.BK", "SCB.BK", "TTB.BK", "ADVANC.BK"}
GLOBAL_STOCKS = {"AAPL", "MSFT", "NVDA", "TSLA", "AMZN", "GOOG", "GOOGL", "META", "AMD", "TSM"}
ETFS = {"SPY", "VOO", "QQQ", "VTI", "GLD", "SLV", "SOXX"}
BOND_ETFS = {"TLT"}
REITS = {"VNQ"}
GLOBAL_INDICES = {"^GSPC", "^IXIC", "^DJI", "^N225", "^HSI", "^GDAXI"}
COMMODITIES = {"CL=F", "BZ=F", "NG=F", "GC=F", "SI=F", "PL=F", "HG=F"}
MACRO = {"DX-Y.NYB", "^TNX"}


class YFinanceProvider(MarketDataProvider):
    name = "yfinance"

    def get_quote(self, symbol: str) -> Dict[str, Any]:
        try:
            ticker = yf.Ticker(symbol)
            info = self._safe_info(ticker)
            fast_info = self._safe_fast_info(ticker)
            history = ticker.history(period="5d", interval="1d", auto_adjust=False)
            latest = self._latest_row(history)

            price = self._first_float(
                self._fast_value(fast_info, "last_price"),
                self._fast_value(fast_info, "lastPrice"),
                info.get("regularMarketPrice"),
                latest.get("Close"),
            )
            previous_close = self._first_float(
                self._fast_value(fast_info, "previous_close"),
                self._fast_value(fast_info, "previousClose"),
                info.get("regularMarketPreviousClose"),
                self._previous_close(history),
            )
            change = self._safe_float(price - previous_close) if price is not None and previous_close not in (None, 0) else None
            change_percent = self._safe_float((change / previous_close) * 100) if change is not None and previous_close else None

            quote = {
                "symbol": symbol,
                "name": self._safe_string(info.get("shortName") or info.get("longName") or symbol),
                "asset_type": infer_asset_type(symbol),
                "currency": self._safe_string(self._fast_value(fast_info, "currency") or info.get("currency") or infer_currency(symbol)),
                "price": price,
                "previous_close": previous_close,
                "change": change,
                "change_percent": change_percent,
                "open": self._first_float(info.get("regularMarketOpen"), latest.get("Open")),
                "high": self._first_float(info.get("regularMarketDayHigh"), latest.get("High")),
                "low": self._first_float(info.get("regularMarketDayLow"), latest.get("Low")),
                "volume": self._first_float(info.get("regularMarketVolume"), latest.get("Volume")),
                "market_cap": self._first_float(info.get("marketCap"), self._fast_value(fast_info, "market_cap")),
                "trailing_pe": self._safe_float(info.get("trailingPE")),
                "price_to_book": self._safe_float(info.get("priceToBook")),
                "price_to_sales": self._safe_float(info.get("priceToSalesTrailing12Months")),
                "trailing_eps": self._safe_float(info.get("trailingEps")),
                "earnings_growth": self._safe_float(info.get("earningsGrowth")),
                "revenue_growth": self._safe_float(info.get("revenueGrowth")),
                "debt_to_equity": self._safe_float(info.get("debtToEquity")),
                "return_on_equity": self._safe_float(info.get("returnOnEquity")),
                "return_on_assets": self._safe_float(info.get("returnOnAssets")),
                "return_on_invested_capital": self._safe_float(info.get("returnOnCapital")),
                "beta": self._safe_float(info.get("beta")),
                "dividend_yield": self._safe_float(info.get("dividendYield")),
                "sector": self._safe_string(info.get("sector")) if info.get("sector") else None,
                "industry": self._safe_string(info.get("industry")) if info.get("industry") else None,
                "exchange": self._safe_string(info.get("exchange") or info.get("fullExchangeName")) if info.get("exchange") or info.get("fullExchangeName") else None,
                "country": self._safe_string(info.get("country")) if info.get("country") else None,
                "logo_url": self._safe_string(info.get("logo_url") or info.get("logoUrl")) if info.get("logo_url") or info.get("logoUrl") else None,
                "icon_url": self._safe_string(info.get("logo_url") or info.get("logoUrl")) if info.get("logo_url") or info.get("logoUrl") else None,
                "provider_logo_url": self._safe_string(info.get("logo_url") or info.get("logoUrl")) if info.get("logo_url") or info.get("logoUrl") else None,
                "logo_provider": self.name if info.get("logo_url") or info.get("logoUrl") else None,
                "logo_available": bool(info.get("logo_url") or info.get("logoUrl")),
                "source": self.name,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
            if price is None:
                quote["error"] = "No latest price was returned by yfinance for this symbol."
            return quote
        except Exception as exc:
            return self._quote_error(symbol, exc)

    def get_history(self, symbol: str, range: str = "1mo", interval: str = "1d") -> Dict[str, Any]:
        selected_range = range if range in VALID_RANGES else "1mo"
        selected_interval = interval if interval in VALID_INTERVALS else "1d"
        try:
            ticker = yf.Ticker(symbol)
            if selected_range == "3y":
                end = datetime.now(timezone.utc)
                start = end - timedelta(days=365 * 3 + 7)
                history = ticker.history(start=start.date().isoformat(), end=end.date().isoformat(), interval=selected_interval, auto_adjust=False)
            else:
                history = ticker.history(period=selected_range, interval=selected_interval, auto_adjust=False)
            points = self._history_frame_to_points(history)
            response: Dict[str, Any] = {
                "symbol": symbol,
                "range": selected_range,
                "interval": selected_interval,
                "points": points,
                "source": self.name,
            }
            if not points:
                response["error"] = "No historical prices were returned by yfinance for this symbol."
            return response
        except Exception as exc:
            return {
                "symbol": symbol,
                "range": selected_range,
                "interval": selected_interval,
                "points": [],
                "source": self.name,
                "error": str(exc),
            }

    def get_financials(self, symbol: str) -> Dict[str, Any]:
        try:
            ticker = yf.Ticker(symbol)
            info = self._safe_info(ticker)
            income = self._safe_statement(getattr(ticker, "financials", None))
            balance = self._safe_statement(getattr(ticker, "balance_sheet", None))
            cashflow = self._safe_statement(getattr(ticker, "cashflow", None))
            revenue = self._statement_value(income, "Total Revenue")
            gross_profit = self._statement_value(income, "Gross Profit")
            operating_income = self._statement_value(income, "Operating Income")
            net_income = self._statement_value(income, "Net Income")
            operating_cash_flow = self._statement_value(cashflow, "Operating Cash Flow", "Total Cash From Operating Activities")
            free_cash_flow = self._first_float(info.get("freeCashflow"), self._statement_value(cashflow, "Free Cash Flow"))
            assets = self._statement_value(balance, "Total Assets")
            liabilities = self._statement_value(balance, "Total Liabilities Net Minority Interest", "Total Liab")
            equity = self._statement_value(balance, "Stockholders Equity", "Total Stockholder Equity")
            cash = self._first_float(info.get("totalCash"), self._statement_value(balance, "Cash And Cash Equivalents", "Cash"))
            debt = self._first_float(info.get("totalDebt"), self._statement_value(balance, "Total Debt"))
            fields = {
                "symbol": symbol,
                "revenue": revenue,
                "grossProfit": gross_profit,
                "operatingIncome": operating_income,
                "netIncome": net_income,
                "ebitda": self._first_float(info.get("ebitda"), self._statement_value(income, "EBITDA")),
                "operatingCashFlow": operating_cash_flow,
                "totalAssets": assets,
                "totalLiabilities": liabilities,
                "totalEquity": equity,
                "totalDebt": debt,
                "revenueTrend": self._safe_float(info.get("revenueGrowth")),
                "netProfitTrend": self._safe_float(info.get("earningsGrowth")),
                "grossMargin": self._safe_float(info.get("grossMargins")),
                "operatingMargin": self._safe_float(info.get("operatingMargins")),
                "netMargin": self._safe_float(info.get("profitMargins")),
                "debtToEquity": self._safe_float(info.get("debtToEquity")),
                "cashFlowQuality": self._cash_flow_quality(operating_cash_flow, net_income),
                "roe": self._safe_float(info.get("returnOnEquity")),
                "roa": self._safe_float(info.get("returnOnAssets")),
                "eps": self._safe_float(info.get("trailingEps")),
                "pe": self._safe_float(info.get("trailingPE")),
                "pbv": self._safe_float(info.get("priceToBook")),
                "ps": self._safe_float(info.get("priceToSalesTrailing12Months")),
                "peg": self._safe_float(info.get("pegRatio")),
                "intrinsicValue": None,
                "totalCash": cash,
                "freeCashFlow": free_cash_flow,
                "revenueGrowth": self._safe_float(info.get("revenueGrowth")),
                "earningsGrowth": self._safe_float(info.get("earningsGrowth")),
                "dividendYield": self._safe_float(info.get("dividendYield")),
                "threeToFiveYearTrend": None,
                "balanceSheetStrength": None,
                "earningsQuality": None,
                "valuationRisk": None,
                "source": self.name,
            }
            fields["field_provenance"] = {
                key: {
                    "provider": self.name,
                    "source": "yfinance.info" if key in {"roe", "roa", "eps", "pe", "pbv", "ps", "peg", "dividendYield", "revenueGrowth", "earningsGrowth"} else "yfinance.statements",
                    "available": value is not None,
                }
                for key, value in fields.items()
                if key not in {"symbol", "source", "field_provenance"}
            }
            return fields
        except Exception as exc:
            return {"symbol": symbol, "source": self.name, "error": str(exc)}

    def _history_frame_to_points(self, history: Any) -> List[Dict[str, Any]]:
        if history is None or history.empty:
            return []
        points: List[Dict[str, Any]] = []
        for index, row in history.iterrows():
            points.append({
                "time": self._to_iso(index),
                "open": self._safe_float(row.get("Open")),
                "high": self._safe_float(row.get("High")),
                "low": self._safe_float(row.get("Low")),
                "close": self._safe_float(row.get("Close")),
                "volume": self._safe_float(row.get("Volume")),
            })
        return points

    def _quote_error(self, symbol: str, exc: Exception) -> Dict[str, Any]:
        return {
            "symbol": symbol,
            "name": symbol,
            "asset_type": infer_asset_type(symbol),
            "currency": infer_currency(symbol),
            "price": None,
            "previous_close": None,
            "change": None,
            "change_percent": None,
            "open": None,
            "high": None,
            "low": None,
            "volume": None,
            "market_cap": None,
            "trailing_pe": None,
            "price_to_book": None,
            "price_to_sales": None,
            "trailing_eps": None,
            "earnings_growth": None,
            "revenue_growth": None,
            "debt_to_equity": None,
            "return_on_equity": None,
            "return_on_assets": None,
            "return_on_invested_capital": None,
            "beta": None,
            "dividend_yield": None,
            "sector": None,
            "industry": None,
            "exchange": None,
            "country": None,
            "logo_url": None,
            "icon_url": None,
            "provider_logo_url": None,
            "logo_provider": None,
            "logo_available": False,
            "source": self.name,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "error": str(exc),
        }

    def _safe_info(self, ticker: yf.Ticker) -> Dict[str, Any]:
        try:
            return ticker.info or {}
        except Exception:
            return {}

    def _safe_fast_info(self, ticker: yf.Ticker) -> Any:
        try:
            return ticker.fast_info
        except Exception:
            return {}

    def _safe_statement(self, statement: Any) -> Any:
        try:
            if statement is None or statement.empty:
                return None
            return statement
        except Exception:
            return None

    def _statement_value(self, statement: Any, *labels: str) -> float | None:
        if statement is None:
            return None
        for label in labels:
            try:
                if label in statement.index and len(statement.columns):
                    return self._safe_float(statement.loc[label].iloc[0])
            except Exception:
                continue
        return None

    def _cash_flow_quality(self, operating_cash_flow: float | None, net_income: float | None) -> str | None:
        if operating_cash_flow is None or net_income in (None, 0):
            return None
        ratio = operating_cash_flow / net_income
        if ratio >= 1:
            return "operating cash flow covers reported net income"
        if ratio >= 0:
            return "operating cash flow is positive but below reported net income"
        return "operating cash flow is negative"

    def _fast_value(self, fast_info: Any, key: str) -> Any:
        try:
            if isinstance(fast_info, dict):
                return fast_info.get(key)
            return getattr(fast_info, key, None)
        except Exception:
            return None

    def _latest_row(self, history: Any) -> Dict[str, Any]:
        if history is None or history.empty:
            return {}
        row = history.iloc[-1]
        return row.to_dict() if hasattr(row, "to_dict") else {}

    def _previous_close(self, history: Any) -> float | None:
        if history is None or history.empty:
            return None
        if len(history.index) > 1:
            return self._safe_float(history["Close"].iloc[-2])
        return self._safe_float(history["Close"].iloc[-1])

    def _first_float(self, *values: Any) -> float | None:
        for value in values:
            safe = self._safe_float(value)
            if safe is not None:
                return safe
        return None

    def _safe_float(self, value: Any) -> float | None:
        try:
            if value is None or pd.isna(value):
                return None
            return float(value)
        except (TypeError, ValueError):
            return None

    def _safe_string(self, value: Any) -> str:
        return str(value) if value not in (None, "") else "N/A"

    def _to_iso(self, value: Any) -> str:
        try:
            return value.to_pydatetime().astimezone(timezone.utc).isoformat()
        except Exception:
            return datetime.now(timezone.utc).isoformat()


def infer_asset_type(symbol: str) -> str:
    if symbol.endswith("-USD"):
        return "crypto"
    if symbol in THAI_STOCKS:
        return "thai_stock" if not symbol.startswith("^") else "index"
    if symbol in GLOBAL_STOCKS:
        return "global_stock"
    if symbol in ETFS:
        return "etf"
    if symbol in BOND_ETFS:
        return "bond_etf"
    if symbol in REITS:
        return "reit"
    if symbol in GLOBAL_INDICES or symbol.startswith("^"):
        return "index"
    if symbol in COMMODITIES or symbol.endswith("=F"):
        return "commodity"
    if symbol.endswith("=X"):
        return "fx"
    if symbol in MACRO:
        return "macro"
    return "global_stock"


def infer_currency(symbol: str) -> str:
    if symbol.endswith(".BK") or symbol in {"SET.BK", "^SET.BK", "^SET50.BK"}:
        return "THB"
    if symbol.endswith("=X"):
        return "FX"
    if symbol == "^TNX":
        return "%"
    return "USD"
