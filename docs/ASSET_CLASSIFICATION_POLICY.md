# Asset Classification Policy

Asset classification is explicit and visible. The system must not infer every ticker as a normal operating company.

## Classification Output

Every classification exposes:

- symbol, exchange, and market
- asset class and subtype
- sector and industry when available
- selected intelligence profile
- primary evidence domain
- classification source and confidence
- limitations and fallback status

## Supported Classes

Corporate equities, preferred equities, REITs, business trusts, ETFs, funds, crypto, precious metals, commodities, currencies, indices, and unknown instruments are handled separately.

## Boundaries

ETFs are not treated as operating companies. Crypto, metals, commodities, FX, and broad indices do not receive corporate Financial Intelligence. When classification is uncertain, the system shows uncertainty instead of applying an unsafe model.

