# IPOS Runbooks & Operational Procedures

This directory contains executable runbooks and operational workflow procedures for IPOS.

## Runbooks & Procedures

| File | Title | Description | Domain |
|---|---|---|---|
| [`extraction_process.md`](extraction_process.md) | Playbook Extraction Runbook | Process for extracting knowledge from seminar source materials into structured modules and JSONL. | Knowledge Base |
| [`WF05_IPOS_WEEKLY_MACRO_REGIME.md`](WF05_IPOS_WEEKLY_MACRO_REGIME.md) | IPOS Weekly Macro Regime Pipeline | Saturday 05:00 scheduled pipeline evaluating 22 indicators, calculating macro regime scores, and updating registers. | Automated Pipeline |
| [`WF06_IPOS_EVIDENCE_CUSTODY_WATCHDOG.md`](WF06_IPOS_EVIDENCE_CUSTODY_WATCHDOG.md) | IPOS Research Evidence Watchdog | Karakeep custody watchdog archiving macroeconomic research, SingleFile captures, and cryptographic SHA-256 receipts. | Research Custody |
| [`WF07_RESEARCH_TO_PORTFOLIO_DECISION_FLOW.md`](WF07_RESEARCH_TO_PORTFOLIO_DECISION_FLOW.md) | Research-to-Portfolio Decision Flow | End-to-end logical progression from transcribed Karakeep research to Buy/Hold/Sell/Trim portfolio rebalancing. | Portfolio Governance |
