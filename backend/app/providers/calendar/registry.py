from __future__ import annotations

from app.providers.calendar.base import unavailable_calendar


class TradingEconomicsCalendarProvider:
    name = "tradingeconomics"

    def fetch_high_impact(self):
        return unavailable_calendar(self.name, "TRADINGECONOMICS_API_KEY is not configured.")


def get_calendar_provider() -> TradingEconomicsCalendarProvider:
    return TradingEconomicsCalendarProvider()
