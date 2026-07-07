from abc import ABC, abstractmethod
from typing import Any, Dict, List


class MarketDataProvider(ABC):
    """Provider contract for market data integrations."""

    @abstractmethod
    def get_asset_snapshot(self, symbol: str) -> Dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    def get_history(self, symbol: str, period: str = "1mo") -> List[Dict[str, Any]]:
        raise NotImplementedError

    @abstractmethod
    def get_financials(self, symbol: str) -> Dict[str, Any]:
        raise NotImplementedError
