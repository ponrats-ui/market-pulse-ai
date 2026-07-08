from __future__ import annotations

from typing import Any, Dict


def sentiment_for_symbol(symbol: str) -> Dict[str, Any]:
    return {
        "symbol": symbol,
        "score": None,
        "label": "Unavailable",
        "source": "Unavailable",
        "provider_configured": False,
        "note": "Sentiment data unavailable.",
        "note_th": "ยังไม่มีข้อมูล sentiment",
    }
