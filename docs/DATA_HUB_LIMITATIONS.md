# Data Hub Limitations

## Partial Universe

The current exchange master is a curated supported subset. Full S&P 500, Nasdaq-100, and SET coverage requires verified constituent files or licensed provider ingestion.

## Provider Coverage

yfinance and public Yahoo Finance RSS can return missing, delayed, throttled, or inconsistent fields. The Data Hub records partial and unavailable states rather than inventing values.

## Fundamentals

Equity fundamentals are partial where yfinance exposes equivalent fields. Crypto, commodities, indices, FX, and macro instruments are marked not applicable for corporate financial statements.

## News

News is provider-dependent. Related-symbol and impact metadata is conservative classifier output from returned headlines, not a guarantee of market impact.

## Calendar

Economic calendar remains provider-not-configured until a live provider key/source is configured.

## Thai Summary

ข้อจำกัดหลักคือจักรวาลสินทรัพย์ยังไม่ครบทุกตลาด และข้อมูลจริงขึ้นกับ provider จึงต้องแสดงสถานะ partial หรือ unavailable อย่างตรงไปตรงมา
