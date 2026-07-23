# HANDOVER — For the next AI agent continuing IPOS

You are an AI agent. You have **only this repository** — no prior chat, no hidden context. This file plus `PROJECT_STATE.md` are everything you need to continue. Read both fully before acting.

---

## 0. Your first five minutes

1. Read `PROJECT_STATE.md` (the living index: status, active plan, ordered next steps, file map).
2. Read the active plan `05_blueprint/00_MASTER_PLAN.md` and the meso plans for the current phase (`05_blueprint/meso/`).
3. Run `python scripts/qa_repo.py` — it must exit 0. If not, fix that first.
4. Confirm the branch discipline in §4 below.
5. Start at the first unchecked step in `PROJECT_STATE.md` §3 → today that is **Phase 0 + Phase 1**, spec'd concretely in `05_blueprint/02_PHASE1_WORKPLAN.md`.

## 1. What you are building (and the one sentence that governs every choice)

A local-first, weekly macro **Investment Process OS**: pull ~60 free-source indicators → score each 0–100 → aggregate into **risk budget + stance vector + confidence + contradictions**, governed by a CHOPPY/TRENDY/MOMENTUM regime classifier, exported as `snapshot.json` + a static HTML report, narrated by an LLM only as the last mile.

**The governing principle:** *code computes everything numeric; the LLM only narrates.* Maximize value per token and per euro. Free-only. Automate everything. When two designs tie, choose the simpler and more resilient one.

## 2. What is already done — do NOT redo it

- **Knowledge extraction is complete and QA-verified.** `03_extract/*.jsonl` (34 indicators, 126 rules, 44 process steps) and `04_playbook/modules/*.md` (10 modules) are the frozen knowledge layer. `logs/QA_REPORT.md` shows 204/204 reconciled. Do not re-extract from the PDF. Treat these as read-only inputs; you *seed configs from them* (keeping an `extract_ref` back-pointer), you don't rewrite them.
- **Planning is complete.** The macro plan, 9 meso plans, decision analysis, and 4 research reports exist. Do not re-plan from scratch. If reality contradicts a plan, **amend the plan file and record why** (see §5) — don't silently diverge.

## 3. What is NOT done — your job

**Zero implementation code exists.** No `ipos/` package, no `configs/`, no DuckDB, no ETL, no scoring, no snapshot, no report. Building the walking skeleton is the current frontier. `05_blueprint/02_PHASE1_WORKPLAN.md` tells you exactly which files to create, in what order, with which indicators.

## 4. Rules of engagement (non-negotiable)

- **Constraints (locked):** full macro stack (Equity+Rates+Credit+FX+Commodities); weekly cadence (`as_of_date` = Friday); Windows/local-first; 60 indicators scaling to 120 **without refactor** (registry-driven); outputs are scores + risk budget + stance + confidence + contradictions (**no traffic lights**); never feed the seminar PDF into runs; external composites stored as single series (never rebuilt); **$0** — free data + free/near-free AI only.
- **Branch discipline:** develop on `claude/ipos-blueprint-optimization-xh2med` (create from latest `main` if absent). Commit small with clear messages. Merge to `main` only when a phase's Definition of Done is met and QA is green. Never force-push shared history.
- **Every session ends by updating `PROJECT_STATE.md`** per its §6 checklist. This is what keeps the project chat-independent. If you do nothing else, do this.
- **Free & frugal:** no paid APIs, no always-on servers, no cloud, no RAG/embeddings, no orchestrator. If you think you need one, re-read `05_blueprint/01_DECISION_ANALYSIS.md` — the trade was already made and there is a documented switch-trigger for changing it.

## 5. How to disagree with the plan (the escape hatch)

The plan is a hypothesis, not scripture. Past attempts failed by being *too vague to execute*, so this plan is deliberately concrete — but if a step is wrong or too coarse:
1. **Plan-repair before code:** edit the relevant meso file to fix/refine the step first.
2. Record the change and the reason in `05_blueprint/01_DECISION_ANALYSIS.md` (add a row or a dated note), including the alternative you're now choosing.
3. Then implement. Never let the code and the plan drift apart silently — the next agent must be able to trust the plan.
Each decision in `01_DECISION_ANALYSIS.md` already carries a **switch-trigger + fallback**. If a trigger fires, execute the fallback; don't re-litigate.

## 6. Definition of "done" for the current phase

Phase 1 is done when a single command produces a correct, byte-identical-on-rerun `snapshot.json` for the current week from ~20 real indicators, with a deterministic `report.md`, and `pytest` is green. Full exit criteria: `05_blueprint/02_PHASE1_WORKPLAN.md` §"Definition of Done".

## 7. Map of the thinking (why, not just what)

- **Vision & full requirements** → `Automated Investment Playbook.md` (the original Blueprint: stack, DB DDL, scoring math, prompts, mock MVP) + `05_blueprint/00_MASTER_PLAN.md` §1.
- **Every design choice, its rejected alternatives, and when to switch** → `05_blueprint/01_DECISION_ANALYSIS.md`.
- **The evidence behind the choices (with source URLs, re-checkable)** → `05_blueprint/research/2026-07-19_*.md`.
- **How each subsystem gets built** → `05_blueprint/meso/C1…C9`.
- **Exact next build steps** → `05_blueprint/02_PHASE1_WORKPLAN.md`.
- **What survived / what was lost from the planning session** → `PROJECT_STATE.md` §7.

That is the whole reasoning trail. If you internalize §1's governing principle and follow the phase order, you are aligned with the intent even where the plan is silent.
