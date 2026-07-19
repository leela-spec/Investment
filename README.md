# ipos_playbook_repo

> **New session? Start with [`PROJECT_STATE.md`](PROJECT_STATE.md)** — the index: status, active plan, next steps, decision log, file map.

Local-first, token-efficient artifacts extracted from a seminar PDF into:
- Playbook modules (`04_playbook/modules/*.md`)
- Structured JSONL extracts (`03_extract/*.jsonl`)

## How to use later
1) Build weekly data pipeline → produce `snapshot.json`
2) For weekly AI reports, include:
   - snapshot
   - only the relevant Playbook modules (retrieval by tags/module_id)

## Contents
- `00_runbook/extraction_process.md` — the extraction runbook
- `03_extract/` — indicators/rules/process JSONL
- `04_playbook/modules/` — compact rules modules (Markdown)
- `05_blueprint/00_MASTER_PLAN.md` — macro implementation plan (vision, validated stack, feature ranking, phases)
- `05_blueprint/meso/C1…C9` — meso plans per cluster (decisions, steps, definition of done)
