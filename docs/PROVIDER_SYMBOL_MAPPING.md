# Provider Symbol Mapping

## Purpose

Provider symbol mapping keeps internal asset identity separate from vendor-specific request symbols.

Market Pulse AI may store and display canonical asset symbols differently from the symbol format expected by a market data provider. The mapper is responsible for converting supported internal symbols into provider-safe symbols and rejecting unsupported variants before any provider request is made.

## Thai Equity Mapping

For Thai equities, Market Pulse AI treats the common share as the default research universe.

| User or Registry Input | Internal Common Share | Yahoo Finance Symbol | Status |
| --- | --- | --- | --- |
| `AOT` | `AOT` | `AOT.BK` | Supported |
| `AOT.BK` | `AOT` | `AOT.BK` | Supported |
| `PTT` | `PTT` | `PTT.BK` | Supported |
| `PTT.BK` | `PTT` | `PTT.BK` | Supported |
| `AOT-F` | `AOT` | None | Excluded |
| `AOT-F.BK` | `AOT` | None | Excluded |

The mapper never appends `.BK` twice. It trims whitespace, uppercases ASCII ticker symbols, removes a single `.BK` exchange suffix for normalization, and then rebuilds the provider symbol only for supported common shares.

## Foreign Board and Special Symbols

The default Thai Emerging Opportunities universe excludes foreign-board and special-board variants before any provider call.

Examples:

- `ACAP-F.BK` is classified as `foreign_board_excluded`.
- `AOT-F.BK` is classified as `foreign_board_excluded`.
- `AOT-P.BK` is classified as `special_board_excluded`.
- `AOT.BK.BK` is classified as `duplicate_exchange_suffix`.

These exclusions are diagnostics, not provider failures. They should not produce noisy delisted-symbol logs.

## Production Rule

Do not embed provider-specific symbol string manipulation inside opportunity engines. Engines should ask the Data Hub mapper for a provider-safe symbol and use mapper diagnostics to explain unsupported variants.

## Thai Summary

ระบบแยกสัญลักษณ์ภายในออกจากสัญลักษณ์ที่ผู้ให้บริการข้อมูลต้องการใช้ หุ้นไทยทั่วไปจะถูกส่งไป Yahoo Finance ในรูปแบบ `.BK` เช่น `AOT.BK` ส่วนสัญลักษณ์กระดานต่างประเทศ เช่น `AOT-F.BK` จะถูกตัดออกก่อนเรียก provider และแสดงเป็น diagnostic แทนการมองว่าเป็นข้อมูลผิดพลาดจากตลาด
