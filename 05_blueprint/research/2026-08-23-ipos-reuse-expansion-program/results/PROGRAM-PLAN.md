# Program Plan — IPOS Reuse Expansion

**Effective pinned main:** `6353c1acb768d61a7be83477e1cc4fee55653d97`  
**Status:** RESEARCHING  
**Scope:** Research, evaluation, isolated POCs, independent reviews, consistency audit, and R9 implementation recommendation only. No production IPOS architecture or scoring changes.

## Track inventory

| Track | Objective | Prompt | Dependencies | Required output group |
|---|---|---|---|---|
| R1 | R1 | `ExternalAddonsResearch/prompts/R1_Karakeep_to_IPOS_integration.md` | Preflight | Karakeep gap/capability/POC/integration/MCDA decision |
| R2 | R2 | `ExternalAddonsResearch/prompts/R2_Can_all_required_IPOS_data_be_free.md` | Preflight | coverage report + per-series matrix + free registry candidates |
| R3 | R3 | `ExternalAddonsResearch/prompts/R3_General_Financial_Evidence_Knowledge_Base.md` | Preflight | tools/skills/corpora/options/MCDA recommendation |
| R4 | R4 | `ExternalAddonsResearch/prompts/R4_Karakeep_vs_Zotero.md` | R1 + R3 accepted | head-to-head workload/interop POC and ownership decision |
| R5 | R5 | `ExternalAddonsResearch/prompts/R5_Activepieces_actual_ingestion_POC.md` | Preflight | Activepieces sidecar POC + alternatives/adoption |
| R6 | R6 | `ExternalAddonsResearch/prompts/R6_Ghostfolio_POC_and_alternatives.md` | Preflight | Ghostfolio POC + adapter comparison + architecture decision |
| R7 | R7 | `ExternalAddonsResearch/prompts/R7_Build_the_Trading_Advisor_from_existing_IPOS_knowledge.md` | Preflight | Playbook-to-code mapping + deterministic advisory design |
| R8 | R8 | `ExternalAddonsResearch/prompts/R8_Merge_Karakeep_evidence_with_the_existing_operational_KB.md` | R1 + R3 + R4 accepted | evidence provenance contracts/lifecycle/governance bridge |
| R9 | R9 | `ExternalAddonsResearch/prompts/R9_Final_implementation_plan_for_the_thin_custom_IPOS_layer.md` | R1–R8 + consistency accepted | thin-glue component implementation plan and handover |

## Dependency DAG and waves

- **Wave 0:** completed preflight, repository grounding, prompt inventory, effective re-pin.
- **Wave 1A:** R1, R2, R3 in parallel.
- **Wave 1B:** R5, R6, R7 in parallel after the first batch frees worker slots.
- **Wave 2:** R4 after R1 and R3 are accepted.
- **Wave 3:** R8 after R1, R3, R4 are accepted.
- **Wave 4:** independent cross-track consistency audit.
- **Wave 5:** R9 synthesis and executive summary.

## POC/install operations expected

- **R1:** disposable Karakeep attempt; synthetic web/PDF/transcript/note/RSS/duplicate corpus; blocked installation is acceptable only with evidenced dependency and deterministic next test.
- **R4:** paired Karakeep/Zotero corpus workflow where feasible.
- **R5:** disposable automation sidecar or locally executable fixture harness covering YouTube Atom, email fixture, RSS, dedupe, malformed/unavailable/retry/idempotency cases.
- **R6:** disposable Ghostfolio installation and synthetic multi-asset portfolio; temporary adapter only; current CSV path retained as comparison/fallback.
- No production credentials, private portfolio data, public deployment, paid services, or trade execution.

## Source strategy

`broad landscape → shortlist → official source/repository/license/API verification → implementation details → failure/adversarial search → conclusion`

Consequential tool claims require current official docs/source/release/license evidence. High-risk or contested claims receive corroboration where useful. Repo facts are cited to the effective pin. SEO summaries and GitHub stars are not decision evidence.

## Review rubric

Each R1–R8 output receives an independent 0–2 review on repo grounding, factual grounding, citation accuracy, source quality, coverage, uncertainty, target alignment, reuse-first discipline, POC integrity, and efficiency. Pass requires **≥17/20** with no zero in repo grounding, factual grounding, citation accuracy, or coverage. One narrow correction/re-review is automatic; a second failure is a human gate.

## Human gates

Only launcher §10 gates apply: missing authority, login/credentials, non-disposable installation, real/private financial data, unavoidable paid dependency, second review failure, evidence-balanced material architecture choice, conflict with an explicit current decision, or production-behavior change.

## Expected repository outputs

- `RUN-MANIFEST.json`, this plan, and restartable `PROGRAM-STATE.json`
- One result directory plus `SOURCES.md`, `GAPS_AND_UNCERTAINTIES.md`, `TRACK-MANIFEST.json`, and `REVIEW.md` for R1–R8
- `CROSS-TRACK-CONSISTENCY.md`
- R9's 13 named implementation artifacts plus `implementation_plan.json`
- `FINAL-EXECUTIVE-SUMMARY.md`

## Likely consistency questions

- Karakeep raw evidence/inbox/dashboard ownership versus Zotero bibliographic/PDF ownership.
- Whether Activepieces is only a sidecar and never core weekly orchestration.
- Whether evidence can affect runtime only through explicit versioned promotion and golden tests.
- Whether FTS/metadata is sufficient before semantic retrieval.
- Whether Ghostfolio adds ledger/performance value without displacing the proven CSV path.
- Whether advisory calculations are fully reconstructible without an LLM and remain read-only.
- Whether every proposed custom component is thinner than capability already provided by accepted products or current IPOS.
