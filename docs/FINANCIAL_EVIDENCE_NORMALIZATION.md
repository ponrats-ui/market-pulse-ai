# Financial Evidence Normalization

The normalizer maps provider fields into stable internal facts.

## Examples

- `totalRevenue` -> revenue
- `netIncome` -> net income
- `operatingCashFlow` -> operating cash flow
- `freeCashFlow` -> free cash flow
- `returnOnEquity` or `roe` -> ROE
- `debtToEquity` or derived debt/equity -> debt to equity

## Rule

Provider fields may be camelCase or snake_case. Missing fields remain `null` and are reported as missing evidence.

