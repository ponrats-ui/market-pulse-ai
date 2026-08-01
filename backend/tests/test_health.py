import asyncio
import subprocess
import sys

from app import main
from app.providers import yfinance_provider
from app.main import health


def test_health_returns_ok() -> None:
    payload = health()
    assert payload["status"] == "ok"
    assert payload["service"] == "market-pulse-ai"


def test_startup_and_health_do_not_reach_yahoo(monkeypatch) -> None:
    def fail_yahoo(*args, **kwargs):
        raise AssertionError("Yahoo Finance must not be called during startup or health checks.")

    monkeypatch.setattr(yfinance_provider.yf, "Ticker", fail_yahoo)
    monkeypatch.setattr(yfinance_provider.yf, "download", fail_yahoo)

    async def run_lifespan_and_health():
        async with main.lifespan(main.app):
            return main.health()

    payload = asyncio.run(run_lifespan_and_health())

    assert payload["status"] == "ok"


def test_penny_scheduler_is_opt_in_and_uses_bounded_env_config(monkeypatch) -> None:
    captured = {}

    def fake_start_scheduler(*args, **kwargs):
        captured["args"] = args
        captured["kwargs"] = kwargs
        return True

    monkeypatch.setenv("PENNY_OPPORTUNITY_SCHEDULER_ENABLED", "true")
    monkeypatch.setenv("PENNY_OPPORTUNITY_MARKET", "TH")
    monkeypatch.setenv("PENNY_OPPORTUNITY_MAX_PRICE", "10")
    monkeypatch.setenv("PENNY_OPPORTUNITY_LIMIT", "5")
    monkeypatch.setenv("PENNY_OPPORTUNITY_SCHEDULE_MINUTES", "60")
    monkeypatch.setenv("PENNY_OPPORTUNITY_INITIAL_DELAY_SECONDS", "30")
    monkeypatch.setattr(main, "start_penny_opportunity_scheduler", fake_start_scheduler)

    async def run_lifespan():
        async with main.lifespan(main.app):
            return main.health()

    payload = asyncio.run(run_lifespan())

    assert payload["status"] == "ok"
    assert captured["kwargs"] == {
        "market": "TH",
        "limit": 5,
        "frequency_minutes": 60,
        "thai_max_price": 10.0,
        "initial_delay_seconds": 30,
    }


def test_importing_app_main_does_not_eagerly_load_provider_libraries() -> None:
    script = "import sys; import app.main; print('pandas' in sys.modules, 'yfinance' in sys.modules)"
    result = subprocess.run([sys.executable, "-c", script], text=True, capture_output=True, check=True)
    assert result.stdout.strip() == "False False"


def test_local_vite_fallback_port_is_allowed_by_cors(monkeypatch) -> None:
    monkeypatch.delenv("CORS_ALLOWED_ORIGINS", raising=False)
    monkeypatch.setenv("APP_ENV", "development")

    assert main._cors_allowed_origin_regex()
    assert "5174" in main._cors_allowed_origin_regex()


def test_production_cors_does_not_allow_localhost_regex(monkeypatch) -> None:
    monkeypatch.delenv("CORS_ALLOWED_ORIGINS", raising=False)
    monkeypatch.setenv("APP_ENV", "production")

    assert main._cors_allowed_origin_regex() is None
