from __future__ import annotations

from typing import Any, Dict, Iterable, List


def rank_candidates(
    candidates: Iterable[Dict[str, Any]],
    *,
    score_field: str,
    confidence_field: str = "data_confidence",
    completeness_field: str = "data_completeness",
    liquidity_path: tuple[str, str] = ("scores", "liquidity"),
    risk_field: str = "risk_penalty",
    symbol_field: str = "symbol",
    limit: int = 5,
) -> List[Dict[str, Any]]:
    ranked = sorted(
        candidates,
        key=lambda item: (
            -_number(item.get(score_field)),
            -_number(item.get(confidence_field)),
            -_number(item.get(completeness_field)),
            -_number((item.get(liquidity_path[0]) or {}).get(liquidity_path[1])),
            _number(item.get(risk_field)),
            str(item.get(symbol_field) or ""),
        ),
    )
    return [{**item, "rank": index + 1} for index, item in enumerate(ranked[: max(1, limit)])]


def _number(value: Any) -> float:
    try:
        if value is None:
            return 0.0
        return float(value)
    except (TypeError, ValueError):
        return 0.0
