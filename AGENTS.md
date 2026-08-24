# Investment (IPOS) Project Context & Authority Routing

## Current Truth and Entrypoints
- Project Overview: `README.md`
- Handover Contract: `HANDOVER.md`
- Living Index & State: `PROJECT_STATE.md`
- Master Plan: `05_blueprint/00_MASTER_PLAN.md`
- Cluster Plans: `05_blueprint/meso/`
- Playbook Rules: `04_playbook/modules/`
- Extraction Runbook: `00_runbook/extraction_process.md`

## Codebase Modules
- Pipeline & Core Engine: `ipos/`
- Macro Rule Advisor Engine: `ipos/advisor/rule_engine.py` (evaluates 126 seminar rules & 44 process steps)
- Backtest & Simulation Engine: `ipos/backtest/engine.py` (regime accuracy & drawdown suppression)
- Active 22-Indicator Registry: `configs/registry.yaml`
- Expanded 120-Indicator Registry Candidate: `configs/registry_120.yaml`
- Automation Scripts: `scripts/register_scheduler.ps1` (Windows), `scripts/run_weekly_cron.sh` (Linux)
- Research Archive: `docs/architecture/openclaw_research/` (April 2026 multi-analyst reference)

## Invariants & Exclusions
- Raw Sources: `Sources/` is read-only input material; do not mutate directly.
- Canonical Branch: `main` (commit directly; no feature branches).
- Governing Axiom: *Code computes everything numeric; the LLM only narrates.*
