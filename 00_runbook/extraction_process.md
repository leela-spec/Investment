# IPOS Playbook Extraction Runbook (Local-First, Token-Efficient)

This repo contains **extracted artifacts** from the seminar PDF, captured as:
- **Playbook modules** (Markdown)
- **Structured extracts** (`*.jsonl`) for indicators, rules, and process steps

The goal is to avoid re-feeding the full PDF into future runs. Instead, future prompts consume:
- `snapshot.json` (weekly)
- a *small* subset of relevant Playbook modules

---

## Extraction Loop (repeat per chunk)

1) **DOC_MAP**
- Identify topics/subtopics + likely modules
- Mark pages as: rules / indicators / process / chart-only / low-value

2) **ROI_GATE**
- Classify items as:
  - `active_now` (MVP-impact + implementable)
  - `defer` (valuable later, not MVP)
  - `drop` (not operationalizable)
- Avoid “nice-to-have” extraction unless it moves weekly decisions.

3) **INDICATOR_EXTRACT** (active only)
- Append to `03_extract/indicators.jsonl`

4) **RULE_EXTRACT** (active only)
- Append to `03_extract/rules.jsonl`

5) **PROCESS_EXTRACT** (active only)
- Append to `03_extract/process.jsonl`

6) **PLAYBOOK_WRITE**
- Write **one compact module** at a time into `04_playbook/modules/`

7) Periodically: **QA_COVERAGE**
- Check coverage vs A2 macro stack + weekly cadence + scoring 0–100 + contradictions

---

## Hard Policies

### Composite Indicator Policy (do not rebuild)
If an indicator is a published or proprietary composite (e.g., Fear & Greed, proprietary vendor signals):
- Store **only the composite value** as a single series (external input).
- Do **not** attempt to reconstruct components unless explicitly requested.
- Prefer “extremes-only” rules.

### MVP ROI Filter
Extract an item as `active_now` only if it:
- improves weekly decisions (risk budget / stance / contradictions), **and**
- can be sourced or computed robustly.

Everything else is `defer` (kept as reference for later phases).

---

## Output Contract (resumable)
Every extraction run must:
- produce at least one concrete artifact (even if a stub),
- end with a clear **CHECKPOINT** (what was written / where we are),
- end with **NEXT ACTION** (the next stage and page range).

---

## Where things live
- `03_extract/indicators.jsonl` — indicator registry candidates (time-series + transforms + defaults)
- `03_extract/rules.jsonl` — scoring/gating/contradictions rules (machine-friendly)
- `03_extract/process.jsonl` — workflow/governance steps (machine-friendly)
- `04_playbook/modules/*.md` — human-readable Playbook modules for retrieval
