from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict


class QuoteProvider(ABC):
    name: str

    @abstractmethod
    def get_quote(self, symbol: str) -> Dict[str, Any]:
        raise NotImplementedError


class HistoryProvider(ABC):
    name: str

    @abstractmethod
    def get_history(self, symbol: str, range: str = "1mo", interval: str = "1d") -> Dict[str, Any]:
        raise NotImplementedError


class FundamentalsProvider(ABC):
    name: str

    @abstractmethod
    def get_financials(self, symbol: str) -> Dict[str, Any]:
        raise NotImplementedError


class NewsProvider(ABC):
    name: str

    @abstractmethod
    def fetch(self, symbol: str, limit: int = 10) -> Dict[str, Any]:
        raise NotImplementedError


class CalendarProvider(ABC):
    name: str

    @abstractmethod
    def fetch(self) -> Dict[str, Any]:
        raise NotImplementedError
