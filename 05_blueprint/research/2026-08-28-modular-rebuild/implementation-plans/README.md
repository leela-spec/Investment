# IPOS Modular Rebuild — Implementation Plans

This directory is the execution authority for the modular infrastructure build on branch `ipos-modular-rebuild-2026-08-28`.

## Start here

1. `00_PROGRAM.yaml` — dependency graph, waves, global stop conditions.
2. `01_EXECUTOR_CONTRACT.yaml` — mandatory CLI-AI execution/verification discipline.
3. `02_CLI_LAUNCHER.yaml` — minimal instruction for starting or resuming one module.
4. `03_REPORT_SCHEMAS.yaml` — required implementation and independent verification artifacts.
5. `04_RESEARCH_PROVENANCE.yaml` — external official-source research behind the plans.
6. Execute exactly one `M*.yaml` module at a time.

## Module map

| ID | Purpose |
|---|---|
| M01 | Existing Hermes baseline / Investment profile |
| M02 | Hermes Telegram group + authenticated webhooks |
| M03 | Minimal HTTPS public ingress |
| M04 | Activepieces self-hosted event platform |
| M05 | WEB.DE + Gmail event flows |
| M06 | Action/Watch register via Activepieces Tables |
| M07 | Karakeep evidence custody |
| M08 | Video/audio/transcription/chart-frame pipeline |
| M09 | Reuse validated Transcript-to-Knowledge skill |
| M10 | OpenBB ODP free/local market-macro data POC |
| M11 | Deterministic broker CSV/PDF normalization |
| M12 | Wealthfolio local portfolio UX POC |
| M12P | Preserve/expose deterministic IPOS policy layer |
| M13 | Riskfolio-Lib deterministic optimization |
| M14 | TA-Lib technical engine |
| M15 | TradingView event bridge |
| M16 | Scalable zero-token local technical watchdog |
| M17 | Manual support/resistance/Fib/trendline registry |
| M18 | Weekly Hermes investment review |
| M19 | Independent end-to-end acceptance/failure injection |
| M90 | Future research: automated TradingView drawing extraction |

## Operator launch phrase

Use a new CLI-AI session for the chosen module:

> Execute module M01 using `05_blueprint/research/2026-08-28-modular-rebuild/implementation-plans/02_CLI_LAUNCHER.yaml`. Follow its dependency, context-management, testing, stop, and independent-verification contracts exactly. Do not execute the next module automatically.

Replace `M01` only after the previous module has a passing verification receipt or explicit operator waiver.
