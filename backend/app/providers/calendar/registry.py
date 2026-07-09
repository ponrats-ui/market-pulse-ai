from __future__ import annotations

import os

from app.providers.calendar.base import unavailable_calendar


class TradingEconomicsCalendarProvider:
    name = "tradingeconomics"

    def fetch_high_impact(self):
        if os.getenv("TRADING_ECONOMICS_KEY") or os.getenv("TRADINGECONOMICS_API_KEY"):
            return unavailable_calendar(self.name, "TradingEconomics transport is not enabled in this build.")
        return unavailable_calendar(self.name, "TRADING_ECONOMICS_KEY is not configured.")


def get_calendar_provider() -> TradingEconomicsCalendarProvider:
    return TradingEconomicsCalendarProvider()
