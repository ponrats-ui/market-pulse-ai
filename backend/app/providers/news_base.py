from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict


class NewsProvider(ABC):
    name: str

    @abstractmethod
    def get_news_impact(self, symbol: str) -> Dict[str, Any]:
        raise NotImplementedError
