# Market-Adjusted Asset Score

## Purpose

The Market-Adjusted Asset Score explains the currently selected asset within its relevant market environment.

It does not replace the existing Opportunity Score. The original Opportunity Score remains the asset-specific score used for opportunity ranking and screening.

## Formula

Market-Adjusted Asset Score =

`(Asset Opportunity Score * 0.70) + (Relevant Market Condition Score * 0.30)`

Example:

`(68 * 0.70) + (59 * 0.30) = 65.3`

Displayed score: `65 / 100`

The calculation is deterministic and uses provider-returned inputs only.

## Market Context Mapping

The selected asset remains the primary subject. Market context is supporting evidence.

| Asset type | Market context |
| --- | --- |
| Thai equities ending in `.BK` | SET market proxy |
| US equities | S&P 500 market proxy |
| US technology equities and technology ETFs | NASDAQ100 market proxy |
| Crypto assets | Bitcoin market proxy |
| Gold and precious metals | Gold market proxy |
| Oil and energy assets | Oil market proxy |
| FX pairs | Currency and macro proxy |
| Bond yields | US 10Y yield proxy |

Mapping uses symbol, asset type, exchange, country, sector, and industry metadata when available.

## Interpretation Ranges

| Score | English label | Thai label |
| --- | --- | --- |
| 80-100 | Strong | แข็งแกร่ง |
| 65-79 | Cautiously Positive | ระมัดระวังเชิงบวก |
| 50-64 | Neutral / Await Confirmation | เป็นกลาง / รอการยืนยัน |
| 35-49 | Cautious | ระมัดระวัง |
| 0-34 | High Risk | ความเสี่ยงสูง |

## Missing Data Behavior

Market Pulse AI follows the Zero Mock Policy.

If the asset score or relevant market score is unavailable, the system does not calculate a combined score and does not substitute a neutral value.

The UI displays a transparent unavailable state and explains which input is incomplete.

## Distinction From Opportunity Score

Opportunity Score:

- Asset-specific
- Used for opportunity ranking
- Built from available quote and fundamental signals

Market-Adjusted Asset Score:

- Selected-asset specific
- Adds relevant market context
- Used for explainability and research support

## Disclaimer

This score is educational research support only. It is not financial advice, a prediction, or a buy/sell recommendation. Users remain responsible for their own investment decisions and risk management.
