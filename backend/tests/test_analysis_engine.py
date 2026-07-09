import json

from app.analysis_engine.confidence import calculate_confidence
from app.analysis_engine.engine import build_adaptive_recommendation
from app.analysis_engine.asset_class import get_asset_class_model
from app.analysis_engine.adaptive_weights import adapt_weights
from app.analysis_engine.profile_loader import get_profile, load_profiles
from app.analysis_engine.probability import estimate_probabilities
from app.analysis_engine.score_calculator import apply_profile_weights, calculate_factor_scores


def sample_evidence():
    return {
        "raw_data": {"quote": {"symbol": "AAPL"}, "history": {"points": [{"close": 100}] * 25}},
        "factor_inputs": {
            "daily_change_percent": 1.5,
            "history_performance_percent": 8.0,
            "average_absolute_move_percent": 0.8,
            "market_cap": 1_000_000_000,
            "trailing_pe": 24.0,
            "volume": 12_000_000,
            "asset_type": "global_stock",
        },
        "unavailable_data": [],
    }


def test_profile_loading_from_config() -> None:
    profiles = load_profiles()
    assert profiles["algorithm_version"] == "v1.2"
    assert "Balanced" in profiles["profiles"]
    assert "Momentum" in profiles["profiles"]


def test_profile_loader_validates_custom_profile(tmp_path) -> None:
    profile_path = tmp_path / "analysis_profiles.json"
    profile_path.write_text(
        json.dumps({
            "algorithm_version": "test-version",
            "default_profile": "Balanced",
            "profiles": {"Balanced": {"weights": {"technical": 1, "risk": 1}}},
        }),
        encoding="utf-8",
    )
    profile = get_profile("Balanced", profile_path)
    assert profile["algorithm_version"] == "test-version"
    assert profile["weights"]["technical"] == 1


def test_score_calculation_and_weighting() -> None:
    scores = calculate_factor_scores(sample_evidence())
    weighted = apply_profile_weights(scores, {"technical": 1, "risk": 1, "liquidity": 1})
    assert 0 <= scores["technical"] <= 100
    assert 0 <= weighted["weighted_score"] <= 100
    assert set(weighted["normalized_weights"]) == {"technical", "risk", "liquidity"}


def test_confidence_calculation_reports_label() -> None:
    scores = calculate_factor_scores(sample_evidence())
    weighted = apply_profile_weights(scores, {"technical": 1, "risk": 1, "liquidity": 1})
    confidence = calculate_confidence(sample_evidence(), weighted)
    assert confidence["label"] in {"low", "medium", "high"}
    assert 0 <= confidence["score"] <= 1


def test_engine_reports_version_profile_regime_and_evidence() -> None:
    quote = {
        "symbol": "AAPL",
        "price": 200,
        "change_percent": 1.4,
        "market_cap": 3_000_000_000_000,
        "trailing_pe": 30,
        "volume": 50_000_000,
        "asset_type": "global_stock",
        "source": "test",
    }
    history = {"points": [{"time": f"t{index}", "close": 100 + index} for index in range(30)]}
    payload = build_adaptive_recommendation("AAPL", quote, history, "Balanced")
    assert payload["algorithm_version"] == "v1.2"
    assert payload["profile"] == "Balanced"
    assert payload["market_regime"] in {"Bull Market", "Bear Market", "Sideways", "High Volatility", "Low Volatility", "Risk-On", "Risk-Off"}
    assert payload["evidence"]["facts"]
    assert payload["probability_engine"]["bullish_probability"] >= 0
    assert payload["investment_thesis"]["bull_case"]
    assert payload["risk_engine"]["scenario_analysis"]
    assert payload["learning"]["lifecycle"] == ["experiment", "promote", "rollback"]
    assert payload["final_recommendation"]["disclaimer"] == "This is not financial advice. No assured outcome or direct buy/sell instruction is provided."


def test_asset_class_models_apply_different_biases() -> None:
    crypto = get_asset_class_model("crypto")
    etf = get_asset_class_model("etf")
    assert crypto["asset_class"] == "Crypto"
    assert etf["asset_class"] == "ETF"
    assert crypto["factor_bias"] != etf["factor_bias"]


def test_adaptive_weights_change_for_high_volatility_and_low_confidence() -> None:
    weights = {"risk": 10, "volatility": 10, "momentum": 10, "liquidity": 10}
    adjusted = adapt_weights(
        weights,
        {"risk": 1.1},
        {"factor_bias": {"volatility": 1.2}},
        {"market_volatility": "high", "liquidity": "available", "news_density": "unavailable"},
        {"label": "low"},
    )
    assert adjusted["risk"] > weights["risk"]
    assert adjusted["momentum"] < weights["momentum"]


def test_probability_engine_is_not_price_prediction() -> None:
    probabilities = estimate_probabilities(62, {"score": 0.6})
    assert round(probabilities["bullish_probability"] + probabilities["neutral_probability"] + probabilities["bearish_probability"], 1) == 100.0
    assert "not exact price predictions" in probabilities["explanation"]
