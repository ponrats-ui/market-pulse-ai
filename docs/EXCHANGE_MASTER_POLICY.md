# Exchange Master Policy

## Source Of Truth

`configs/exchange_master.json` is the supported-universe source of truth. The Data Hub normalizes it into records with:

- canonical symbol
- provider symbols
- display symbol
- company name
- Thai name
- aliases
- asset class
- exchange
- country
- currency
- sector
- industry
- index memberships
- enabled flag
- data capabilities

## Coverage Status

Current coverage is partial. The registry preserves the current production subset and does not claim full S&P 500, Nasdaq-100, or SET coverage.

## Required Ingestion Metadata

Future verified ingestion should populate:

- `source`
- `fetched_at`
- `constituent_date`
- `record_count`
- `validation_status`
- `coverage_status`

## Update Process

Use:

```bash
python scripts/update_exchange_master.py --dry-run
python scripts/update_exchange_master.py --validate
python scripts/update_exchange_master.py --apply --input data/exchange_sources/sp500.csv --input data/exchange_sources/nasdaq100.csv --input data/exchange_sources/set.csv
```

The script validates required fields, deduplicates symbols, preserves manual aliases and Thai names, reports added/removed/changed symbols, and refuses to overwrite the production file if validation fails.

## Licensing Boundary

Do not copy or redistribute licensed constituent data without permission. Use official or licensed machine-readable sources and record provenance.

## Thai Summary

Exchange Master ยังเป็นชุดข้อมูลบางส่วน ไม่ใช่รายชื่อครบทุกตลาด การขยาย coverage ต้องใช้ไฟล์ต้นทางที่ตรวจสอบได้ มีสิทธิ์ใช้งานถูกต้อง และบันทึก provenance ทุกครั้ง
