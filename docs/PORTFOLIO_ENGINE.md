# Portfolio Engine

## Scope

The portfolio engine is a simulated paper-trading engine. It does not connect to real brokers and does not place orders.

## Core Accounting

The engine preserves and validates:

- initial cash
- buy and sell transactions
- partial sells and sell-all workflows
- repeated buys and average cost
- cash balance
- realized and unrealized P/L
- market value and total portfolio value
- transaction history
- reset transactions
- canonical symbols from the Data Hub

## Analytics

The engine calculates allocation, cash ratio, daily P/L, daily return, realized/unrealized P/L, risk score, diversification score, and simple scenario shocks. History-dependent analytics such as Sharpe ratio, max drawdown, volatility, and correlation remain transparent unavailable until persisted portfolio value history exists.

## Thai Summary

Portfolio Engine เป็นระบบจำลองเท่านั้น ไม่เชื่อมต่อ broker จริง และต้องบอกตรงๆ เมื่อข้อมูลไม่พอสำหรับ analytics บางส่วน
