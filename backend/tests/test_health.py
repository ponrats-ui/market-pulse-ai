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


def test_importing_app_main_does_not_eagerly_load_provider_libraries() -> None:
    script = "import sys; import app.main; print('pandas' in sys.modules, 'yfinance' in sys.modules)"
    result = subprocess.run([sys.executable, "-c", script], text=True, capture_output=True, check=True)
    assert result.stdout.strip() == "False False"
