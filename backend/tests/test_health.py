import asyncio

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
