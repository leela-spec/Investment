# POC and Validation Plan

## Goal

Prove the replacement architecture through bounded tests of existing products. Do not build missing platforms during POC work.

## P0 — Privacy/config freeze

Before connecting real portfolio data:
- choose Hermes inference provider policy;
- decide whether raw holdings/transactions may ever enter cloud LLM context;
- keep Wealthfolio Connect off;
- keep Karakeep external AI off or use local Ollama for restricted evidence;
- use OpenBB ODP locally;
- define which TradingView data is safe to store in cloud layouts/alerts.

Pass condition: explicit data-egress policy exists for every component.

## P1 — Deterministic portfolio normalization

Input:
- representative finanzen.net Zero CSV/PDF;
- representative Smartbroker CSV/PDF;
- synthetic edge cases for EUR/USD, fees, dividends, splits and cash.

Test:
- preserve raw files immutably;
- normalize to one canonical local schema;
- validate totals, ISIN/symbol mapping, currency, quantities and transaction signs;
- produce machine-readable validation report.

Pass condition:
- exact reproducible output;
- zero silent drops;
- reconciliation differences explained.

## P2 — Wealthfolio narrow-role POC

Use **only normalized/synthetic portfolio data**, not broker connections.

Evaluate:
- import friction;
- graphics/usability;
- performance reporting;
- allocation breakdown;
- multi-currency presentation;
- export/backup;
- local-only mode;
- read-only MCP usefulness;
- whether target allocations/rebalance plans can be fed through an officially supported interface.

Pass condition:
- clearly improves portfolio understanding/visual planning without becoming another ingestion dependency.

Fail condition:
- meaningful data must be uploaded to vendor cloud;
- import requires fragile custom hacks;
- visualization is not materially better than cheaper alternatives;
- target-weight seam is undocumented and would require custom reverse engineering.

## P3 — OpenBB ODP free/local data POC

Target a small representative set of IPOS data:
- S&P 500 daily/weekly price;
- Fed balance sheet/FRED;
- 10Y-2Y / 10Y-3M curve series;
- high-yield OAS;
- selected global/economic data used by current playbook.

Record for each endpoint:
- exact provider;
- free-key requirement;
- rate limits;
- licensing/redistribution restrictions;
- local caching allowed?;
- data quality/history;
- deterministic reproducibility;
- whether request metadata or credentials leave the host.

Pass condition:
- ODP meaningfully reduces provider-specific glue while preserving free/local operation.

## P4 — Riskfolio-Lib deterministic optimization POC

Input:
- fixed clean return matrix;
- fixed constraints from IPOS;
- fixed solver/settings/seed where relevant.

Run:
- minimum-risk;
- risk-parity/risk-budget candidate;
- CVaR-style constrained candidate;
- optional Black-Litterman test only if views are explicitly defined.

Validate:
- repeatability;
- solver status;
- constraint satisfaction;
- sensitivity to small input changes;
- explainable output schema;
- no network traffic required.

Pass condition:
- reproducible target weights and diagnostics suitable for a deterministic pipeline.

## P5 — TradingView value extraction POC

Test existing subscription capabilities, no new spend:
- export chart data including selected indicators;
- validate one or more local TA-Lib calculations against exported values;
- create 2-3 high-value webhook alerts only;
- test safe JSON payload into a local/Hermes-controlled inbox;
- map TradingView symbols to canonical portfolio identifiers.

Pass condition:
- TradingView meaningfully improves technical monitoring without becoming a private portfolio dependency.

## P6 — Karakeep evidence POC

Test self-hosted/local configuration:
- URL/PDF/RSS capture;
- search and retrieval;
- duplicate handling;
- read-only MCP to Hermes;
- local/no-AI or local-Ollama mode for sensitive content.

Pass condition:
- evidence can be retrieved with source links and bounded context without sending restricted research to external AI by default.

## P7 — Hermes end-to-end orchestration POC

Read-only first.

One complete review should:
1. load canonical portfolio snapshot;
2. call local/open ODP data endpoints;
3. run deterministic IPOS policy evaluation;
4. run Riskfolio candidate optimization;
5. retrieve relevant Karakeep evidence;
6. include TradingView-triggered/CSV technical evidence where relevant;
7. produce an auditable recommendation narrative;
8. stop before any execution/change.

Hard pass gates:
- no invented numbers;
- no silent tool failures;
- data sources traceable;
- all restricted data egress matches policy;
- operator can see what changed and why;
- no additional orchestration framework required.

## P8 — Architecture freeze decision

Only after P0-P7:
- KEEP / REPLACE / DROP each component;
- document total recurring cost;
- document privacy posture;
- document every live interface;
- identify exactly what custom code remains;
- create migration plan from current IPOS implementation.

No production migration before P8.