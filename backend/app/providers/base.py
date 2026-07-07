from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict


class MarketDataProvider(ABC):
    """Provider contract for normalized market data integrations."""

    name: str

    @abstractmethod
    def get_quote(self, symbol: str) -> Dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    def get_history(self, symbol: str, range: str = "1mo", interval: str = "1d") -> Dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    def get_financials(self, symbol: str) -> Dict[str, Any]:
        raise NotImplementedError
