# QA Report — Chat Transcript vs Repo

**Transcript source:** `logs/chat_transcript.md` (copied from `Everything from this chat.md`)  
**Goal:** Ensure **all structured artifacts** (JSON objects with `"id"`) in the transcript are present in the repo and match exactly.

## Coverage
- Chat IDs found: **204**
- Repo IDs found: **204**
- Missing: **0**
- Result: ✅ **ALL CHAT IDS FOUND IN REPO**

## Equality
For every transcript JSON object (`indicators`, `process`, `rules`), the repo contains an object with the same `id` and **identical JSON content** (key/value equality).

## Control tests (50)
- 15 indicator object equality checks
- 15 process object equality checks
- 15 rule object equality checks
- 5 module substring checks (repo module file appears verbatim inside transcript)

Result: ✅ **50 / 50 passed**

## How to rerun
```bash
python scripts/qa_repo.py
python scripts/qa_chat_vs_repo.py logs/chat_transcript.md
```
