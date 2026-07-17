from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict


@dataclass(frozen=True)
class DeliveryResult:
    channel: str
    generated: bool
    sent: bool
    status: str
    failure_reason: str | None
    timestamp: str


class NotificationChannel:
    name = "base"

    def generate(self, payload: Dict[str, Any]) -> DeliveryResult:
        return DeliveryResult(
            channel=self.name,
            generated=True,
            sent=False,
            status="provider_unavailable",
            failure_reason="Outbound delivery is disabled in Phase E.",
            timestamp=datetime.now(timezone.utc).isoformat(),
        )


class EmailChannel(NotificationChannel):
    name = "email"


class LineChannel(NotificationChannel):
    name = "line"


class TelegramChannel(NotificationChannel):
    name = "telegram"


class WebPushChannel(NotificationChannel):
    name = "web_push"


CHANNELS = {
    "email": EmailChannel(),
    "line": LineChannel(),
    "telegram": TelegramChannel(),
    "web_push": WebPushChannel(),
}


def generate_notification(channel: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    provider = CHANNELS.get(channel) or NotificationChannel()
    return provider.generate(payload).__dict__
