# C6 — Snapshot & AI Layer (Meso Plan)

**Owns:** `snapshot.json` schema + exporter, token design, prompt contracts, LLM invocation (optional at runtime), `report.md` generation.
**Depends on:** C3, C4, C5. **Feeds:** C7, the human.
**Prime directive:** *code computes, LLM narrates.* The system is fully functional with the LLM switched off.

## Token design (the "value per token" core)

Weekly budget, enforced in code (exporter counts tokens ≈ chars/4 and trims by priority):

| Block | Cap | Content & trimming rule |
|-------|-----|------------------------|
| System+role prompt (frozen) | 600 | Contract, schema, style; **never** interpolate dates/values into it (cache-correct hygiene, diffable runs) |
| Playbook excerpt | 3,000 | From C5, priority-ordered, whole-module granularity |
| snapshot.json (minified) | 4,000 | Overall block + modules + regime + contradictions + movers/drivers **+ only surfaced indicators** (movers ∪ extremes ∪ contradiction-members — not all 60; full table stays in DB/report) |
| Output (structured) | 1,800 | Fixed sections, bullet caps per section |
| **Total** | **≤ ~9.4k/week** | ≈ 40k tokens/month |

## Decisions

1. **`snapshot.json` v1 schema** = Blueprint sample, plus: `schema_version`, `scoring_version`, `prompt_version`, `regime` block (label/confidence/risk_scaler/policy_selectors), `playbook_selection`, `data_quality` (stale series, failed sources), `flags` (per `snapshot_flags.md`). Two renditions: `snapshot.json` (pretty, archived) and `snapshot.min.json` (minified, AI-facing). Exported to `data/exports/snapshots/YYYY-MM-DD/`.
2. **Provider ladder ($0-first, all pluggable behind one interface):**
   1. **Gemini free tier** (default automated path; one call/week is trivially within limits; be aware free-tier data may train Google models — snapshot contains no personal/portfolio data in MVP),
   2. **manual paste** into a Claude Project / ChatGPT (0 € marginal, frontier quality — the exporter writes `prompt_bundle.md` = system+playbook+snapshot concatenated for one-click copy),
   3. **cheap API + Batch (−50%)** (Haiku/GPT-mini/Flash class ≈ 2–8 ¢/month — quality upgrade for cents),
   4. **local Ollama** (Qwen-class 8–14B; fine for narration since all numbers are pre-computed; offline resilience).
   Provider set in `configs/ai.yaml`; `none` is a valid value.
3. **Structured output everywhere:** report generated as JSON per schema (sections as fields with word caps) → rendered to `report.md` by code. Eliminates parse failures/retries (the hidden token cost). Temperature 0 where supported; pinned model versions; `prompt_version` + model id recorded in report metadata.
4. **Prompt contracts** (versioned files in `prompts/`, seeded from the Blueprint's three templates): `weekly_checkup.md` (facts/movers/contradictions/drivers), `suitability.md` (stance + invalidation triggers), `contradiction_deepdive.md` (hypotheses + resolving data + monitoring plan — run only when severity=high, so most weeks cost one call, not three).
5. **Deterministic fallback `report.md`:** template-rendered (jinja2) from snapshot alone — risk budget, regime, movers, contradictions as tables/bullets. Always generated; LLM narration, when enabled, is *appended* as an "Interpretation" section. Resilience rank-4 property: no provider, no problem.
6. **No caching dependency:** weekly cadence never hits provider prompt caches (TTL minutes–24h) — decided to *not* engineer for caching; Batch API + structured outputs are the levers that matter here.

## Implementation steps

1. `ipos/export/snapshot.py` — builder + budget trimmer + both renditions + archive write.
2. `ipos/export/report.py` — jinja2 deterministic report; `prompts/` seeded from Blueprint templates (edited to structured-output JSON schemas).
3. `ipos/ai/provider.py` — interface + `gemini.py`, `anthropic_.py`, `openai_.py`, `ollama_.py`, `none.py` (~30 lines each); `prompt_bundle.md` writer.
4. pytest: budget enforcement (oversized fixture → correct trim order), schema validity (jsonschema), determinism (same DB ⇒ identical snapshot bytes), report renders with `provider: none`.

## Definition of done
- Weekly run yields `snapshot.json`, `snapshot.min.json`, `prompt_bundle.md`, `report.md` under budget; with `provider: none` everything still works; with Gemini free key the interpretation section appears; all metadata (versions) stamped.

**Effort:** M. **Recurring tokens:** ≤ ~40k/month ≈ **$0.00–0.08/month** (the only recurring token cost in the whole system).
