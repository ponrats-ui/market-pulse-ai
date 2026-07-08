from __future__ import annotations

from typing import Any, Dict


def economic_calendar() -> Dict[str, Any]:
    return {
        "events": [],
        "source": "Unavailable",
        "provider_configured": False,
        "message": "Economic calendar provider is not configured.",
        "message_th": "ยังไม่ได้ตั้งค่าผู้ให้บริการปฏิทินเศรษฐกิจ",
    }
