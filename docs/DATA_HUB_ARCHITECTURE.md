# Market Pulse Data Hub Architecture

## Purpose

The Data Hub creates one provider-independent foundation for symbols, capabilities, provider routing, and normalized data contracts. It is not a TradingView-scale exchange database; it is the canonical data layer for the current Market Pulse AI product scope.

## Flow

Exchange Master -> Symbol Resolver -> Provider Router -> Normalized Contracts -> Cache -> Backend Services -> Frontend / PIA

## Components

- `backend/app/data_hub/exchange_master.py`: loads `configs/exchange_master.json`, normalizes asset records, applies clean Thai aliases, validates duplicates and malformed records.
- `backend/app/data_hub/symbol_resolver.py`: resolves user input and aliases such as `TTB` to canonical symbols such as `TTB.BK`.
- `backend/app/data_hub/provider_router.py`: selects providers by data type, routes through current yfinance/Yahoo Finance adapters, and returns transparent unavailable states.
- `backend/app/data_hub/capabilities.py`: reports quote/history/fundamentals/news/calendar/risk/comparison/portfolio capability status per canonical asset.
- `backend/app/data_hub/contracts/`: provider-independent dataclasses for assets, quote, history, fundamentals, news, calendar, and provider status.

## Current Migration

Search, Compare, Portfolio, Financials, quote/history route helpers, and Data Hub diagnostic APIs now consume canonical resolution. Existing public API response contracts remain backward-compatible.

## Thai Summary

Data Hub ทำหน้าที่เป็นชั้นกลางให้ทุกโมดูลใช้สัญลักษณ์สินทรัพย์ชุดเดียวกัน ลดปัญหา alias เช่น `TTB` และ `TTB.BK` ถูกมองเป็นคนละสินทรัพย์ และยังคงแสดงข้อจำกัดของข้อมูลอย่างโปร่งใส
