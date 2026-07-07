from __future__ import annotations

from typing import Any, Dict


def sentiment_for_symbol(symbol: str) -> Dict[str, Any]:
    score = 54 if symbol.endswith("-USD") else 50
    label = "Fear" if score < 40 else "Greed" if score > 60 else "Neutral"
    return {"symbol": symbol, "score": score, "label": label, "source": "mock", "note": "Real provider integration planned."}
