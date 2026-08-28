# IPOS Modular Rebuild — 2026-08-28

Status: `ARCHITECTURE_CANDIDATE_V0_1`
Branch: `ipos-modular-rebuild-2026-08-28`
Base commit: `cec42be2aaf922c74ea6b13dc44fe11adfdd618f`

## Purpose

Build a replacement architecture for the current IPOS implementation by combining proven standalone products through supported interfaces. The Investment repository should retain only the user's unique investment methodology and deterministic policy logic.

This project intentionally does **not** modify the current production IPOS implementation on `main`.

## Hard principles

1. Reuse proven software before custom code.
2. Do not invent undocumented integrations.
3. Code computes numeric outputs; AI narrates/orchestrates.
4. Portfolio ingestion remains deterministic and operator-controlled from supplied CSV/PDF inputs.
5. Prefer free/local software. Paid services require explicit value justification and target budget approval.
6. Data egress/privacy is a first-class decision dimension.
7. TradingView Pro is an existing paid asset and should be exploited where its supported features add value.
8. Hermes Agent is the default orchestration candidate; no LangGraph/OpenClaw dependency is assumed.
9. Every integration seam must be proven by a bounded POC before architecture freeze.

## Files

- `01_REVISED_DECISION_MATRIX.md` — current product/function decisions.
- `02_ARCHITECTURE.md` — target system boundaries and data flow.
- `03_COST_PRIVACY_DATA_BOUNDARIES.md` — price, local/cloud, egress, license and role per component.
- `04_TRADINGVIEW_INTEGRATION.md` — supported TradingView use and non-goals.
- `05_HERMES_ORCHESTRATION.md` — why Hermes can replace OpenClaw and its boundaries.
- `06_POC_AND_VALIDATION_PLAN.md` — bounded tests required before freeze.
- `07_OPEN_QUESTIONS.md` — operator questions and unresolved decisions.
- `PROJECT_STATE.json` — machine-readable status.

## Current candidate stack

| Layer | Candidate | Status |
|---|---|---|
| Orchestrator | Hermes Agent | PROVISIONAL_ADOPT |
| Research/evidence | Karakeep self-hosted | PROVISIONAL_ADOPT |
| Market/macro data | OpenBB ODP only, not paid Workspace | TEST_FURTHER |
| Portfolio visualization/analysis | Wealthfolio local app, no Connect | TEST_FURTHER |
| Unique investment policy | Existing IPOS Playbook/rules/governors | KEEP |
| Portfolio optimization | Riskfolio-Lib | PROVISIONAL_ADOPT |
| Technical calculation | TA-Lib where deterministic computation is needed | CONDITIONAL |
| Market technical workbench | Existing TradingView Pro subscription | ADOPT_EXISTING |
| Intake automation | None by default; Activepieces only if a proven gap remains | HOLD |
| Custom dashboard | None by default | DROP_DEFAULT |
| LangGraph | None | DROP |
| OpenClaw | None in this architecture | HOLD/REPLACED_BY_HERMES |

## Research provenance

Primary official sources checked 2026-08-28:

- Hermes Agent MCP/docs: https://hermes-agent.nousresearch.com/docs/user-guide/features/mcp
- Hermes tools: https://hermes-agent.nousresearch.com/docs/user-guide/features/tools/
- OpenBB ODP: https://openbb.co/products/odp/
- OpenBB pricing: https://openbb.co/pricing/
- TradingView chart export: https://www.tradingview.com/support/solutions/43000537255-how-to-export-chart-data/
- TradingView webhooks: https://www.tradingview.com/support/solutions/43000529348-how-to-configure-webhook-alerts/
- Wealthfolio privacy: https://wealthfolio.app/legal/privacy-policy/
- Karakeep docs: https://docs.karakeep.app/
- Riskfolio-Lib: https://github.com/dcajasn/Riskfolio-Lib

## Important non-decision

This project does not yet authorize installation, migration, deletion, or replacement of the existing IPOS runtime. The next phase is evidence-backed POC work only.