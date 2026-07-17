from __future__ import annotations

from typing import Any, Dict, List


def answer_question(question: str, selected_symbol: str, language: str, quote: Dict[str, Any], risk: Dict[str, Any], analysis: Dict[str, Any]) -> Dict[str, Any]:
    lang = "th" if language == "th" else "en"
    price = quote.get("price")
    change = quote.get("change_percent")
    score = risk.get("risk_score")
    vol = risk.get("volatility_level", "unknown")
    recommendation = _recommendation(analysis, change, score)
    confidence = _confidence(analysis, price, score)
    facts = [
        f"symbol={selected_symbol}",
        f"price={price}",
        f"change_percent={change}",
        f"risk_score={score}",
        f"volatility={vol}",
        f"source={quote.get('source', 'Unavailable')}",
    ]
    missing = _missing_data(price, change, score, analysis)
    if lang == "th":
        answer = _thai_answer(selected_symbol, price, change, score, vol, recommendation, confidence, facts, missing, analysis, risk)
        follow = ["ต้องการเปรียบเทียบกับสินทรัพย์ตัวใด", "ต้องการดูผลต่อพอร์ตหรือความกระจุกตัวหรือไม่"]
        risks = ["ความผันผวนระยะสั้น", "ข้อมูลตลาดอาจล่าช้าหรือไม่ครบ", "ข่าวและ macro สามารถเปลี่ยนมุมมองได้เร็ว"]
    else:
        answer = _english_answer(selected_symbol, price, change, score, vol, recommendation, confidence, facts, missing, analysis, risk)
        follow = ["Which asset should we compare it against?", "Do you want to review portfolio concentration?"]
        risks = ["Short-term volatility", "Market data may be delayed or incomplete", "Headlines and macro conditions can change the setup quickly"]
    return {
        "answer": answer,
        "concise_overview": _overview(selected_symbol, price, change),
        "positive_factors": analysis.get("bullish_factors") or [],
        "negative_factors": analysis.get("bearish_factors") or [],
        "current_risks": risks,
        "pia_view": recommendation,
        "confidence": confidence,
        "evidence_used": facts,
        "unavailable_data": missing,
        "follow_up_questions": follow,
        "facts_used": facts,
        "risks": risks,
        "disclaimer": "This is not financial advice.",
        "analysis_context": analysis.get("trend"),
        "recommendation": recommendation,
        "missing_data": missing,
    }


def _thai_answer(symbol: str, price: Any, change: Any, score: Any, vol: Any, recommendation: str, confidence: str, facts: List[str], missing: List[str], analysis: Dict[str, Any], risk: Dict[str, Any]) -> str:
    return "\n".join([
        f"Concise overview / ข้อเท็จจริง: {symbol} ราคาล่าสุด {price if price is not None else 'ยังไม่มีข้อมูล'} และเปลี่ยนแปลงรายวัน {_display_percent(change)}",
        f"Positive factors: {_join_or_none(analysis.get('bullish_factors'))}",
        f"Negative factors: {_join_or_none(analysis.get('bearish_factors') or risk.get('main_risks'))}",
        f"Current risks: คะแนนความเสี่ยง {score if score is not None else 'ประเมินไม่ได้'}/10 และความผันผวน {vol}",
        f"PIA view: {recommendation}. ใช้เป็นกรอบวิเคราะห์เชิงการศึกษา ไม่ใช่คำสั่งซื้อขาย",
        f"Confidence: {confidence}",
        f"Evidence used: {', '.join(facts)}",
        f"Unavailable data: {', '.join(missing) if missing else 'ไม่พบช่องว่างข้อมูลสำคัญจาก payload ปัจจุบัน'}",
        "Follow-up questions: ต้องการเปรียบเทียบกับสินทรัพย์ตัวใด? | ต้องการดูผลต่อพอร์ตหรือไม่?",
        "Disclaimer: This is not financial advice.",
    ])


def _english_answer(symbol: str, price: Any, change: Any, score: Any, vol: Any, recommendation: str, confidence: str, facts: List[str], missing: List[str], analysis: Dict[str, Any], risk: Dict[str, Any]) -> str:
    return "\n".join([
        f"Concise overview: {symbol} last price is {price if price is not None else 'unavailable'} and daily change is {_display_percent(change)}.",
        f"Positive factors: {_join_or_none(analysis.get('bullish_factors'))}",
        f"Negative factors: {_join_or_none(analysis.get('bearish_factors') or risk.get('main_risks'))}",
        f"Current risks: risk score is {score if score is not None else 'unknown'}/10 with {vol} volatility.",
        f"PIA view: {recommendation}. Treat this as educational research, not an order to trade.",
        f"Confidence: {confidence}",
        f"Evidence used: {', '.join(facts)}",
        f"Unavailable data: {', '.join(missing) if missing else 'No major missing field in the current payload.'}",
        "Follow-up questions: Which asset should we compare it against? | Do you want to review portfolio impact?",
        "Disclaimer: This is not financial advice.",
    ])


def _recommendation(analysis: Dict[str, Any], change: Any, risk_score: Any) -> str:
    final = analysis.get("final_recommendation") or analysis.get("adaptive_engine", {}).get("final_recommendation") or {}
    action = final.get("recommendation")
    if action:
        return str(action)
    if not isinstance(change, (int, float)) or not isinstance(risk_score, (int, float)):
        return "Wait"
    if risk_score >= 8:
        return "Avoid"
    if risk_score >= 7:
        return "Reduce" if change < 0 else "Wait"
    if change <= -5:
        return "Wait"
    if change >= 4 and risk_score <= 4:
        return "Accumulate"
    if change >= 1 and risk_score <= 5:
        return "Hold"
    return "Hold"


def _confidence(analysis: Dict[str, Any], price: Any, score: Any) -> str:
    adaptive_confidence = analysis.get("confidence")
    if isinstance(adaptive_confidence, dict) and adaptive_confidence.get("label"):
        return str(adaptive_confidence["label"])
    return "medium" if price is not None and score is not None else "low"


def _overview(symbol: str, price: Any, change: Any) -> str:
    return f"{symbol}: price={price if price is not None else 'unavailable'}, daily_change={_display_percent(change)}"


def _display_percent(value: Any) -> str:
    return f"{round(value, 2)}%" if isinstance(value, (int, float)) else "unavailable"


def _join_or_none(items: Any) -> str:
    if isinstance(items, list) and items:
        return "; ".join(str(item) for item in items[:4])
    return "Unavailable"


def _missing_data(price: Any, change: Any, score: Any, analysis: Dict[str, Any]) -> List[str]:
    missing: List[str] = []
    if price is None:
        missing.append("price")
    if change is None:
        missing.append("daily_change")
    if score is None:
        missing.append("risk_score")
    if not analysis.get("bullish_factors"):
        missing.append("bullish_factors")
    if not analysis.get("bearish_factors"):
        missing.append("bearish_factors")
    adaptive_missing = analysis.get("evidence", {}).get("unavailable_data") if isinstance(analysis.get("evidence"), dict) else None
    if isinstance(adaptive_missing, list):
        missing.extend(str(item) for item in adaptive_missing)
    return list(dict.fromkeys(missing))
