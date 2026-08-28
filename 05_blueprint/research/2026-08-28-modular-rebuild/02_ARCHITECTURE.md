# Candidate Architecture v0.1

## Macro view

```text
                    EXTERNAL RESEARCH / NEWS / DOCUMENTS
                                  |
                                  v
                       +---------------------+
                       | KARAKEEP SELF-HOST  |
                       | evidence / archive  |
                       +----------+----------+
                                  | MCP / REST (read-first)
                                  |
                                  v
+----------------+       +--------+---------+       +----------------------+
| TRADINGVIEW    |------>|      HERMES      |<------| OPENBB ODP (LOCAL)   |
| Pro, cloud UI  |alert  | orchestrator     | MCP   | macro/market data    |
| charts/screens |hooks  | narrator/operator|       | provider adapters    |
+--------+-------+       +----+---------+----+       +----------+-----------+
         |                    |         |                       |
         | CSV export         |         |                       | normalized data
         v                    |         |                       v
+----------------------+      |         |             +----------------------+
| LOCAL DATA STAGING   |<-----+         +------------>| IPOS POLICY LAYER    |
| immutable raw inputs |                              | unique rules/governors|
+----------+-----------+                              +----------+-----------+
           ^                                                         |
           |                                                         | constraints/views
           |                                                         v
+----------+-----------+                                  +--------------------+
| CSV/PDF NORMALIZER   |                                  | RISKFOLIO-LIB      |
| deterministic local  |                                  | local optimization |
+----------+-----------+                                  +---------+----------+
           ^                                                        |
           | operator CSV/PDF                                      | target weights
           |                                                        v
   BROKER EXPORTS                                          +--------------------+
                                                          | WEALTHFOLIO LOCAL  |
                                                          | visual/performance |
                                                          | allocation/planning|
                                                          +--------------------+
```

## Ownership boundaries

### Hermes owns
- orchestration and sequencing;
- invoking approved deterministic tools;
- querying read-only MCPs;
- assembling evidence;
- narration and explanation;
- asking operator approval at decision gates;
- scheduled review workflows.

Hermes does **not** own:
- portfolio math;
- indicator computation;
- optimization;
- broker/PDF normalization;
- canonical source-of-truth data;
- automatic order execution.

### TradingView owns
- interactive charting;
- technical exploration;
- screeners;
- alerts and event triggers;
- visual validation of market structure;
- optional CSV extraction of chart series/indicators.

TradingView does **not** own:
- canonical portfolio ledger;
- private local source data;
- unrestricted automated historical data extraction;
- IPOS policy decisions.

### OpenBB ODP owns
- normalization/access to supported public and third-party financial/economic data providers;
- local Python/REST/MCP exposure of those data;
- provider abstraction.

OpenBB ODP does **not** own:
- the portfolio;
- IPOS scoring/governance;
- research evidence archive;
- a paid graphical workspace by default.

### Wealthfolio owns, if POC passes
- clean visual portfolio presentation;
- performance and allocation analysis;
- local portfolio exploration;
- human review of target allocation/rebalancing.

It does **not** own ingestion from brokers in this architecture. Connect stays disabled unless explicitly approved.

### IPOS owns
- unique investment knowledge;
- extracted seminar rules;
- regime logic;
- drawdown/risk-budget governors;
- CRV gates;
- contradictions;
- decision policy and explanation schema.

### Riskfolio-Lib owns
- deterministic optimization from clean inputs and explicit constraints.

## Data flow

1. Broker/export inputs arrive as operator-provided files.
2. Files are preserved unchanged in a raw input area.
3. Deterministic normalization converts them to a canonical portfolio schema.
4. Canonical portfolio data feeds Wealthfolio for visual analysis and feeds Riskfolio/IPOS for computation.
5. OpenBB ODP retrieves needed market/macro/fundamental series from selected providers.
6. TradingView supplies operator chart analysis, alerts, and selectively exported chart/indicator CSV data where legally/supported.
7. Karakeep stores research/news/evidence separately from numerical state.
8. IPOS policy consumes deterministic snapshots, not free-form web text.
9. Riskfolio computes candidate allocations under IPOS constraints.
10. Hermes narrates the state, contrasts evidence, presents alternatives, and stops at human approval gates.

## Safety defaults

- All MCP connections start **read-only** where possible.
- No broker execution integration in v0.1.
- No cloud portfolio sync.
- No OpenBB paid Workspace.
- No custom UI work.
- No custom workflow platform unless a concrete missing capability is proven.
- No AI-generated numeric facts are accepted without deterministic source output.