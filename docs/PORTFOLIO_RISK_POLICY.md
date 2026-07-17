# Portfolio Risk Policy

## Rules

- Never connect to real brokers in this phase.
- Never treat simulated results as real account balances.
- Never fabricate quote prices or portfolio history.
- Reject invalid transactions transparently.
- Show stale or unavailable price states.
- Keep advanced metrics unavailable until sufficient history exists.

## Scenario Policy

Supported scenarios are simple deterministic shocks:

- market falls 10%
- technology falls 15%
- USD strengthens
- interest rates rise
- BTC falls 20%

No Monte Carlo simulation is used in this phase.

## Thai Summary

นโยบายความเสี่ยงของพอร์ตเน้นความโปร่งใส ไม่ใช้ข้อมูลปลอม ไม่เชื่อม broker จริง และไม่ทำ simulation ขั้นสูงถ้าข้อมูลไม่พอ
