from __future__ import annotations

from datetime import date, timedelta
from typing import Any, Dict


def economic_calendar() -> Dict[str, Any]:
    today = date.today()
    events = [
        ("Fed meeting", "US", "high", ["^GSPC", "^IXIC", "BTC-USD"], "ติดตามท่าทีดอกเบี้ยและสภาพคล่องโลก", "Watch rate guidance and global liquidity."),
        ("CPI", "US", "high", ["DXY", "^TNX", "GC=F"], "เงินเฟ้ออาจกระทบค่าเงินและพันธบัตร", "Inflation can affect FX and bonds."),
        ("Nonfarm Payrolls", "US", "medium", ["DXY", "^GSPC"], "ตลาดแรงงานมีผลต่อคาดการณ์ดอกเบี้ย", "Labor data can shift rate expectations."),
        ("Oil inventory", "US", "medium", ["CL=F", "BZ=F"], "สต็อกน้ำมันมีผลต่อพลังงานระยะสั้น", "Inventory can affect near-term energy prices."),
        ("Earnings season", "Global", "medium", ["AAPL", "MSFT", "NVDA"], "ผลประกอบการอาจเพิ่มความผันผวนรายตัว", "Earnings can increase single-name volatility."),
        ("Bank of Thailand meeting", "TH", "medium", ["THB=X", "PTT.BK", "KBANK.BK"], "ติดตามดอกเบี้ยและค่าเงินบาท", "Watch rates and Thai baht implications."),
    ]
    return {"events": [{"date": (today + timedelta(days=i * 7)).isoformat(), "name": name, "region": region, "impact_level": impact, "related_assets": assets, "note_th": th, "note_en": en} for i, (name, region, impact, assets, th, en) in enumerate(events)], "source": "curated-placeholder"}
