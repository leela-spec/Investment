# Target-First Execution Reporting Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the active target-product handover enforce concise, decision-oriented reporting and point E02 only at the bounded CAD custom-asset probe.

**Architecture:** Modify the active handover contract in place. Add one reporting discipline section, replace the stale E02 frontier/matrix with the native-backup verdict, and reduce the next action to the disposable probe. Evidence details remain linked in `implementation-runs/E02/20260923-225605/` rather than duplicated.

**Tech Stack:** Markdown, Git, existing E02 evidence artifacts.

## Global Constraints

- Apply the rule only to `HANDOVER_TARGET_PRODUCT_EXECUTION_2026-09-24.md`.
- Preserve `AGENTS.md` unchanged.
- Keep E02 fail-closed and do not start E03.
- Keep private broker and Wealthfolio files outside Git.
- Preserve `Portfolio Status Quo/SomeRandomLastAnswersTOCOntinue.md`.

---

### Task 1: Update the active execution handover

**Files:**
- Modify: `HANDOVER_TARGET_PRODUCT_EXECUTION_2026-09-24.md`

**Interfaces:**
- Consumes: `docs/superpowers/specs/2026-09-24-target-first-execution-reporting-design.md`, `implementation-runs/E02/20260923-225605/RECONCILIATION_REPORT.md`, and `implementation-runs/E02/20260923-225605/CAD_CUSTOM_ASSET_PROBE.md`.
- Produces: the authoritative execution and reporting contract for subsequent target-product work.

- [ ] **Step 1: Add the target-first communication discipline**

Insert after “Mission and execution discipline” a section requiring routine reports to contain only target, intended value, verdict, material gap, and one next action. State that hashes, schemas, row calculations, and command output belong in evidence files unless requested or essential to explain a material failure.

- [ ] **Step 2: Add the investigation stop rule**

State: before continuing an investigation, ask whether its result can change the product decision or next action; stop if it cannot.

- [ ] **Step 3: Refresh the E02 frontier**

Replace the stale “reconciliation pending” text with the proven verdict: native import and backup pass, but computed holdings omit NDA 1,000 and PSYC 10,000 and cash is overstated by EUR 41,037.75. Keep `INTEGRATION_STATUS = "NOT_CONNECTED"`.

- [ ] **Step 4: Replace the stale acceptance matrix and next action**

Point detailed evidence to `RECONCILIATION_REPORT.md`. Make the only next action the 28-row disposable EUR custom-asset probe documented in `CAD_CUSTOM_ASSET_PROBE.md`. State the binary decision: if it reconciles, repair through supported product workflows; if it fails, classify Wealthfolio as unsuitable for this ledger and stop investing in E02 integration.

- [ ] **Step 5: Verify the handover**

Run:

```powershell
rg -n "Target-first communication|investigation|41,037.75|CAD_CUSTOM_ASSET_PROBE|Do not start E03" HANDOVER_TARGET_PRODUCT_EXECUTION_2026-09-24.md
git diff --check -- HANDOVER_TARGET_PRODUCT_EXECUTION_2026-09-24.md
```

Expected: every required rule and current E02 decision appears; `git diff --check` exits 0.

- [ ] **Step 6: Commit**

```powershell
git add -- HANDOVER_TARGET_PRODUCT_EXECUTION_2026-09-24.md
git commit -m "Refocus target-product execution handover"
```

