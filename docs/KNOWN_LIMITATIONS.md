# Known Limitations

## Data Universe

The exchange master is a curated provider-ready seed, not a complete global exchange database. It includes key US stocks, Thai stocks, ETFs, crypto, commodities, indices, and macro symbols required for V1 testing. Unsupported symbols are intentionally not returned.

## Market Data Providers

Yahoo Finance / yfinance remains the primary market data source. Provider outages, throttling, delistings, or missing fields can cause transparent unavailable states.

## News

News depends on configured providers and public feed availability. The application must not fabricate news when a provider has no live result.

## Economic Calendar

Calendar data is provider-dependent. If a live calendar provider is unavailable, the app should display a transparent unavailable state.

## Portfolio

Portfolio is a local paper/investment assistant foundation. It is not connected to broker accounts, real trading, tax records, or custody systems.

## Recommendation Logic

The production recommendation panel is conservative educational synthesis based on available quote and risk context. It is not a guaranteed forecast, not personalized financial advice, and not an automated trading signal.

## Frontend Cleanup

An older compact control panel implementation remains in frontend/src/main.tsx but is no longer used by the dashboard render path. It can be removed in a later cleanup sprint after Founder approval.

## Thai Summary

ข้อจำกัดหลักคือจักรวาลสินทรัพย์ยังเป็นชุดคัดเลือก, provider บางส่วนอาจไม่มีข้อมูลสด, และคำแนะนำทั้งหมดเป็นข้อมูลเพื่อการศึกษา ไม่ใช่คำสั่งซื้อขายหรือคำทำนายผลตอบแทน
