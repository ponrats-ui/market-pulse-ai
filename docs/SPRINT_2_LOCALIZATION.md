# Sprint 2 Localization

Sprint 2 upgrades Market Pulse AI into a Thai-first bilingual investment dashboard.

## Languages

- Thai is the default language.
- English is available from the top-right language selector.
- The selected language is stored in `localStorage` using `market-pulse-language`.

## Translation Architecture

Frontend translations live in `frontend/src/i18n`:

- `th.ts`
- `en.ts`
- `index.ts`

UI labels, panel titles, status text, disclaimer text, and analysis section headings are pulled from translation objects instead of hardcoded strings.

## Thai Financial Wording

Thai wording is written for investor readability and uses professional terms such as:

- ศูนย์เลือกสินทรัพย์
- รายการติดตาม
- บทวิเคราะห์ AI
- การประเมินความเสี่ยง
- วิเคราะห์งบการเงิน
- แนวรับ / แนวต้าน
- แผนรับมือ

## Notes

Backend analysis remains provider-driven and safe. Frontend wording layers localized professional context on top of the existing Sprint 1 API responses.
