# Contributing to Market Pulse AI

Thank you for your interest in contributing to Market Pulse AI. This project aims to be a cautious, educational, open-source financial intelligence platform.

## Ways to Contribute

- Improve frontend usability, accessibility, and localization.
- Improve backend data reliability, caching, and provider abstraction.
- Add tests, documentation, and deployment guidance.
- Report bugs with clear reproduction steps.
- Suggest features that preserve the project's risk-aware investment research tone.

## Development Setup

Backend:

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python -m pytest
```

Frontend:

```bash
cd frontend
npm install
npm run build
```

## Contribution Guidelines

- Keep changes focused and easy to review.
- Do not commit secrets, private API keys, paid API credentials, or personal data.
- Do not add investment wording that implies guaranteed outcomes.
- Preserve the financial advice disclaimer.
- Use English for documentation, with a short Thai summary where useful.
- Run relevant tests and builds before opening a pull request.

## Pull Request Checklist

- The change is scoped to Market Pulse AI.
- Tests or build validation pass.
- Documentation is updated when behavior or architecture changes.
- No secrets or generated dependency folders are committed.

## Thai Summary

ยินดีรับ contribution ที่ช่วยให้ระบบปลอดภัยขึ้น ใช้งานง่ายขึ้น และยังคงน้ำเสียงการวิเคราะห์แบบระมัดระวัง ห้ามใส่ API key หรือคำแนะนำลงทุนแบบรับประกันผลลัพธ์
