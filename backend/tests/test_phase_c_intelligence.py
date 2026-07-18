from app.analysis_engine.engine import build_adaptive_recommendation
from app.analysis_engine.probability import estimate_probabilities
from app.services.qa_assistant import answer_question


def _quote(change: float = 1.4):
    return {
        "symbol": "NVDA",
        "price": 200,
        "change_percent": change,
        "market_cap": 3_000_000_000_000,
        "trailing_pe": 30,
        "volume": 50_000_000,
        "asset_type": "global_stock",
        "source": "test",
        "timestamp": "2026-01-01T00:00:00Z",
    }


def _history(direction: str = "up"):
    closes = [130 - index for index in range(30)] if direction == "down" else [100 + index for index in range(30)]
    return {"points": [{"time": f"t{index}", "close": close} for index, close in enumerate(closes)]}


def test_committee_members_have_distinct_responsibilities() -> None:
    payload = build_adaptive_recommendation("NVDA", _quote(), _history(), "Balanced")
    members = {item["member"]: item for item in payload["committee_opinions"]}
    assert set(members) == {"Technical Analyst", "Fundamental Analyst", "Macro Economist", "News Analyst", "Risk Manager"}
    assert "trend" in members["Technical Analyst"]["responsibilities"]
    assert "valuation" in members["Fundamental Analyst"]["responsibilities"]
    assert "interest rates" in members["Macro Economist"]["responsibilities"]
    assert "news impact" in members["News Analyst"]["responsibilities"]
    assert "downside" in members["Risk Manager"]["responsibilities"]
    assert len({members[name]["interpretation"] for name in members}) == 5


def test_probability_totals_and_conflict_explanation() -> None:
    probabilities = estimate_probabilities(51, {"score": 0.25, "label": "low"})
    total = probabilities["bullish_probability"] + probabilities["neutral_probability"] + probabilities["bearish_probability"]
    assert total == 100
    assert probabilities["signal_conflicts"]
    assert "not exact price predictions" in probabilities["explanation"]


def test_low_data_response_is_cautious_and_reproducible() -> None:
    first = build_adaptive_recommendation("BTC-USD", {"symbol": "BTC-USD", "asset_type": "crypto"}, {"points": []}, "Balanced")
    second = build_adaptive_recommendation("BTC-USD", {"symbol": "BTC-USD", "asset_type": "crypto"}, {"points": []}, "Balanced")
    assert first["final_recommendation"]["recommendation"] == "Wait"
    assert first["confidence"]["label"] == "low"
    assert first["probability"] == second["probability"]
    assert first["algorithm_version"] == "v1.2"


def test_conflicting_signals_are_explained() -> None:
    payload = build_adaptive_recommendation("AAPL", _quote(change=2), _history("down"), "Balanced")
    assert payload["probability"]["signal_conflicts"]
    assert payload["final_recommendation"]["conflict"]


def test_recommendation_language_policy() -> None:
    payload = build_adaptive_recommendation("GLD", _quote(), _history(), "Balanced")
    text = str(payload).lower()
    for restricted in ("guaranteed", "certain", "must buy", "sure profit"):
        assert restricted not in text
    assert payload["final_recommendation"]["recommendation"] in {"Accumulate", "Buy", "Hold", "Wait", "Reduce", "Avoid", "Sell"}
    assert "This is not financial advice" in payload["final_recommendation"]["disclaimer"]


def test_assistant_response_contains_phase_c_sections() -> None:
    analysis = {
        "bullish_factors": ["Momentum improved"],
        "bearish_factors": ["Valuation risk"],
        "trend": "constructive",
        "final_recommendation": {"recommendation": "Hold"},
        "confidence": {"label": "medium"},
        "evidence": {"unavailable_data": ["macro provider unavailable"]},
    }
    response = answer_question(
        "Should I buy?",
        "NVDA",
        "en",
        {"price": 200, "change_percent": 1.2, "source": "test"},
        {"risk_score": 6, "volatility_level": "medium"},
        analysis,
    )
    assert response["concise_overview"]
    assert response["positive_factors"] == ["Momentum improved"]
    assert response["negative_factors"] == ["Valuation risk"]
    assert response["pia_view"] == "Hold"
    assert response["confidence"] == "medium"
    assert "macro provider unavailable" in response["unavailable_data"]
