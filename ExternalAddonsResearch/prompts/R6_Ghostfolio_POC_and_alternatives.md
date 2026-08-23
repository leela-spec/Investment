<system_instruction>
Research portfolio-management sidecars for IPOS and perform a disposable
proof-of-concept implementation of Ghostfolio.

The existing IPOS portfolio-vs-stance module is already operational and must
not be replaced without evidence.

The question is whether a portfolio ledger/performance system adds enough
value to justify running alongside IPOS.
</system_instruction>

<repo_grounding>
Read:
- PROJECT_STATE.md
- 05_blueprint/03_PORTFOLIO_MODULE.md
- ipos/etl/portfolio_csv.py
- ipos/aggregate/portfolio.py
- configs/portfolio_mapping.yaml
- portfolio warehouse migration(s)
- report rendering
- portfolio tests

Understand exactly what IPOS already does before evaluating another system.
</repo_grounding>

<objective>
Answer:

1. What useful portfolio capabilities are missing from IPOS?
2. Does Ghostfolio solve them?
3. Can Ghostfolio feed holdings/transactions into IPOS deterministically?
4. Is another existing product better?
5. Should IPOS retain its current CSV path even if Ghostfolio is added?
</objective>

<alternatives>
Research at least:

- Ghostfolio
- Portfolio Performance
- Wealthfolio if mature enough
- Rotki where relevant
- Maybe Finance if relevant
- other actively maintained open-source portfolio trackers that meet the requirements

Only include alternatives with verifiable active implementations.

Do not include generic budgeting apps unless they genuinely support investment portfolios.
</alternatives>

<requirements>
Evaluate:
- self-host/local
- Windows
- free/open-source licensing
- security
- portfolio holdings
- transactions
- cash
- dividends
- realized/unrealized P&L
- TWR/MWR
- performance history
- allocation
- multi-currency
- instrument metadata
- import
- export
- API
- deterministic machine access
- backup
- current maintenance
- broker compatibility
- finanzen.net Zero
- Smartbroker where feasible
</requirements>

<ghostfolio_poc>
Actually install Ghostfolio in a disposable environment.

Do NOT use the operator's production financial data.

Create a representative synthetic portfolio mirroring the shapes IPOS must handle:
- ETF
- stock
- commodity ETC
- EUR instrument
- USD instrument
- multiple transactions
- dividend/cash event

Test:

1. import path
2. holdings retrieval
3. transactions retrieval
4. API access
5. portfolio valuation
6. export
7. multi-currency behavior
8. restart persistence
9. backup/restore if practical

Then build ONLY A TEMPORARY TEST ADAPTER:

Ghostfolio output/API
→ normalized representation compatible with the existing IPOS portfolio model.

Compare its normalized output against what
ipos/etl/portfolio_csv.py + ipos/aggregate/portfolio.py expect.

Do not merge into production.
</ghostfolio_poc>

<comparison_test>
Run the same synthetic portfolio through:
A. current IPOS CSV path
B. Ghostfolio → test adapter → IPOS-compatible structure

Compare:
- holdings
- currency values
- totals
- weights
- unmapped handling
- missing information
- reproducibility
</comparison_test>

<mcda>
IPOS value added 20
data integrity 15
API/export 15
local/free 10
maturity 10
portfolio analytics 10
operator effort 10
resilience/backup 5
security 5
</mcda>

<deliverables>
1. CURRENT_IPOS_PORTFOLIO_GAPS.md
2. PORTFOLIO_TOOL_LANDSCAPE.md
3. GHOSTFOLIO_POC_RUNBOOK.md
4. GHOSTFOLIO_POC_RESULTS.md
5. TEST_ADAPTER_SPEC.md
6. MCDA.json
7. PORTFOLIO_ARCHITECTURE_DECISION.md

Final choices:
- KEEP_IPOS_ONLY
- IPOS_PLUS_GHOSTFOLIO
- IPOS_PLUS_OTHER
</deliverables>
