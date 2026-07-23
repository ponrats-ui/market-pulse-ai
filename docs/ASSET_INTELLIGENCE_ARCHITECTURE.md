# Asset Intelligence Architecture

Market Pulse AI routes each instrument through an explicit Asset Intelligence layer before any opportunity score is interpreted.

## Flow

1. Provider evidence is normalized without fabricating missing fields.
2. Asset classification selects an intelligence profile.
3. The selected profile declares primary evidence, secondary evidence, unsupported domains, and limitations.
4. The relevant intelligence engine builds a reusable report.
5. Opportunity engines consume the report instead of duplicating the same analysis.
6. Explanations expose score, confidence, completeness, missing evidence, versions, and limitations.

## Current RC4 Scope

- Corporate operating companies use Financial Intelligence as their primary evidence layer.
- Financial institutions, insurers, REITs, funds, crypto, macro, and commodity profiles are routed through explicit boundaries.
- Full non-corporate engines are architecture contracts only in this sprint.

## Principle

For company-based assets, financial reality comes before market excitement. Price, news, and technical signals provide context; they do not replace business fundamentals.

