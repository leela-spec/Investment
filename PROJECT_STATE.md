# PROJECT_STATE — IPOS (Investment Process OS)

> **READ THIS FIRST.** This file is the single entry point for any new session (human or AI).
> It answers: What is this? Where are we? Which plan is active? What happens next? Where is everything?
> **Hard rule:** update this file at the end of every working session (checklist at the bottom). It supersedes `For next chat.md` (old handover, kept for history).

**Last updated:** 2026-07-19 · **Updated by:** planning session (blueprint optimization) · **Branch of record:** `main`

---

## 1. What is IPOS? (30 seconds)

A **local-first, weekly Investment Process OS** on Windows: ~60 free-source indicators (→120 later) across Equity/Rates/Credit/FX/Commodities are pulled, scored 0–100, and aggregated into **risk budget (0–100) + stance vector + confidence + contradictions**, governed by a regime classifier (CHOPPY/TRENDY/MOMENTUM). Output: a compact `snapshot.json` + static HTML report; an LLM only *narrates* the pre-computed numbers (≤ ~9.4k tokens/week, ≈ $0). Knowledge base: rules extracted from a 231-page seminar PDF into modular Playbook files (never re-fed into runs).

## 2. Where are we? (status)

| Workstream | Status |
|---|---|
| **B — Knowledge extraction** (PDF → modules + JSONL) | ✅ **DONE & QA-verified** (204/204 IDs reconciled; 10 modules; 34 indicators, 126 rules, 44 process steps; `scripts/qa_repo.py` green) |
| **A — Implementation planning** | ✅ **DONE** (this session): macro master plan + 9 meso plans + decision analysis + research archive |
| **A — Implementation code** | ❌ **NOT STARTED** — zero code exists. This is the current frontier. |

**Active plan:** `05_blueprint/00_MASTER_PLAN.md` (v1.0, 2026-07-19) — 5 phases, ranked by impact per token/effort.
**Current phase:** ready to start **Phase 0 (scaffold) + Phase 1 (walking skeleton, ~20 golden indicators)**.

## 3. What happens next? (in order — do not reorder without recording why)

1. **Phase 0:** `ipos/` package scaffold, uv toolchain, pydantic config loading, pytest wiring → meso plan `C1`, steps 1–2.
2. **URGENT within Phase 1:** seed the raw archive (`scripts/backfill_seed.py`) — FRED truncated ICE BofA OAS history to a rolling 3-year window in Apr 2026; every week of delay loses a week of history permanently → `C2`, step 3.
3. **Phase 1 (walking skeleton):** registry (~20 FRED/Stooq indicators) → DuckDB init → pull → weekly canonical → percentile/band scores → module aggregation → `snapshot.json` → deterministic `report.md`. Exit test: one command, idempotent, green → `C1`–`C3`, `C6` (partial), `C8` (CLI only).
4. **Phase 2 (core value):** z-score+confidence, contradictions engine, regime classifier, static HTML report, playbook retrieval + LLM narration, Task Scheduler → `C3`–`C8`.
5. **Phase 3:** expand to 60 indicators, scrapes, golden-snapshot tests, hardening → `C2`, `C9`.
6. **Phase 4 (optional):** Streamlit explorer, COT/ISM subindices, 120 indicators.

Details, file-by-file steps and **Definition of Done per cluster**: `05_blueprint/meso/C1…C9`.

## 4. Key decisions & why (1-line each; full analysis with alternatives + switch triggers → `05_blueprint/01_DECISION_ANALYSIS.md`)

- **Depth-first walking skeleton** before indicator breadth (extraction is done; code is the constraint).
- **DuckDB** single-file warehouse; weekly job = sole writer, readers read-only (D2).
- **Static self-contained HTML report** is the primary UI; Streamlit demoted to optional explorer — *the one deliberate change vs. the original Blueprint* (D3).
- **Plain CLI + Windows Task Scheduler**, no orchestrator (D4).
- **$0 data**: FRED backbone + Stooq/yfinance dual-source + free-key fallbacks + isolated scrapes; **archive-everything from day 1** (D5).
- **LLM = last-mile narrator**, snapshot-first, no RAG; provider ladder Gemini-free → manual paste → cheap API batched → Ollama; system fully functional with AI off (D6).
- **uv + pandas-at-edges + pandera + pytest/golden snapshots** (D7).
- **Every threshold/config row keeps `extract_ref` provenance** back to `03_extract/*.jsonl` (auditability to PDF page level).

## 5. File map (where everything lives)

| Path | What it is |
|---|---|
| `PROJECT_STATE.md` | **This file — the index. Start here.** |
| `05_blueprint/00_MASTER_PLAN.md` | Macro plan: vision, constraints, principles, validated architecture, feature ranking, 5 phases, risks |
| `05_blueprint/01_DECISION_ANALYSIS.md` | Risk/benefit/cost/performance per decision, **alternatives + switch triggers**, risk register |
| `05_blueprint/meso/C1…C9_*.md` | Per-cluster implementation plans (options → decision → steps → Definition of Done) |
| `05_blueprint/research/2026-07-19_*.md` | Archived evidence: transcript digest, free data sources, stack validation, LLM token patterns |
| `Automated Investment Playbook.md` | The original full Blueprint (deliverables 1–9: stack, schema DDL, scoring math, prompts, mock MVP) |
| `04_playbook/modules/*.md` (10 files) | Playbook knowledge modules (regime, stops, sentiment, technicals, governors) — runtime retrieval targets |
| `03_extract/*.jsonl` | Structured extraction (34 indicators / 126 rules / 44 process) — **upstream knowledge, runtime never reads it directly; configs are seeded from it with provenance** |
| `00_runbook/extraction_process.md` | Extraction runbook (workstream B — done; reuse only if new source PDFs arrive) |
| `scripts/qa_*.py` | Repo QA (all green as of 2026-07-19); extend per meso plan C9 |
| `logs/` | Extraction QA report + transcript copy |
| `For next chat.md` | **Superseded** old handover (2026-02-14) — historical context only |
| `Everything from this chat.md` | Extraction transcript (source of truth for extraction; not the blueprint chat) |
| *(future)* `ipos/`, `configs/`, `data/`, `tests/` | Implementation — will be created in Phase 0/1 per meso plans |

## 6. Session protocol (how any future chat resumes work)

**Kickoff (2 minutes):** read this file → read the meso plan(s) for the current phase → run `python scripts/qa_repo.py` → start at the first unchecked step in §3.
**Working rules:** follow meso steps; if a step is too coarse, refine it *in the meso file first*, then code (plan-repair before code). Free-only, token-frugal, everything scripted/testable. Commit small, push to a feature branch, merge to `main` when the phase's Definition of Done is demonstrably met.
**Before ending every session (checklist):**
- [ ] `PROJECT_STATE.md`: update "Last updated", §2 status, §3 next steps (check off / reorder with reason)
- [ ] New decisions? → add to `01_DECISION_ANALYSIS.md` (incl. alternatives + switch trigger)
- [ ] New evidence/research? → archive under `05_blueprint/research/YYYY-MM-DD_*.md`
- [ ] QA scripts green, work committed & pushed

## 7. Honesty note on continuity (2026-07-19)

This plan generation ran in an ephemeral cloud container. Everything load-bearing was written to the repo: plans, decision analysis with alternatives, and the four research reports (archived verbatim from the analysis agents). What is *not* preserved: the agents' raw intermediate browsing transcripts — only their final findings (with source URLs) survive, which is sufficient to re-verify any claim. If a future session doubts a finding, re-run the research; the questions asked are documented at the top of each research file.
