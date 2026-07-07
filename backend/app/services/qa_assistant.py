from __future__ import annotations

from typing import Any, Dict


def answer_question(question: str, selected_symbol: str, language: str, quote: Dict[str, Any], risk: Dict[str, Any], analysis: Dict[str, Any]) -> Dict[str, Any]:
    lang = "th" if language == "th" else "en"
    price = quote.get("price")
    change = quote.get("change_percent")
    score = risk.get("risk_score")
    vol = risk.get("volatility_level", "unknown")
    facts = [
        f"symbol={selected_symbol}",
        f"price={price}",
        f"change_percent={change}",
        f"risk_score={score}",
        f"volatility={vol}",
    ]
    if lang == "th":
        answer = (
            f"ข้อเท็จจริง: {selected_symbol} มีราคาล่าสุด {price if price is not None else 'ไม่พร้อมใช้งาน'} "
            f"และเปลี่ยนแปลงรายวัน {round(change, 2) if isinstance(change, (int, float)) else 'ไม่พร้อมใช้งาน'}%. "
            f"การตีความ: ความเสี่ยงอยู่ระดับ {score if score is not None else 'ประเมินไม่ได้'}/10 และความผันผวนอยู่ในโซน {vol}. "
            "มุมมองนี้ยังมีความไม่แน่นอนจากสภาพคล่อง ข่าว และข้อมูลผู้ให้บริการ จึงควรใช้เพื่อการศึกษาและวางแผนรับมือเท่านั้น"
        )
        follow = ["ต้องการเปรียบเทียบกับสินทรัพย์ตัวใด", "ต้องการดูความเสี่ยงพอร์ตหรือไม่"]
        risks = ["ความผันผวนระยะสั้น", "ข้อมูลตลาดอาจล่าช้าหรือไม่ครบ", "ข่าวสามารถเปลี่ยนมุมมองได้เร็ว"]
    else:
        answer = (
            f"Facts: {selected_symbol} last price is {price if price is not None else 'unavailable'} and daily change is "
            f"{round(change, 2) if isinstance(change, (int, float)) else 'unavailable'}%. Interpretation: risk is "
            f"{score if score is not None else 'unknown'}/10 with {vol} volatility. This view remains uncertain because liquidity, headlines, and provider data can change. Use it for research and risk planning only."
        )
        follow = ["Which asset should we compare it against?", "Do you want to review portfolio concentration?"]
        risks = ["Short-term volatility", "Market data may be delayed or incomplete", "Headlines can change the setup quickly"]
    return {
        "answer": answer,
        "facts_used": facts,
        "risks": risks,
        "follow_up_questions": follow,
        "disclaimer": "This is not financial advice.",
        "analysis_context": analysis.get("trend"),
    }
