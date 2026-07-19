# C9 — QA, Testing & Governance (Meso Plan)

**Owns:** test suites, golden snapshots, version governance, the 60→120 expansion protocol, and continuity of the existing QA culture (`scripts/qa_*.py`).
**Depends on:** all. **Protects:** comparability over years — the system's long-term value.

## Decisions

1. **Three-layer test pyramid (Blueprint's strategy, made concrete):**
   - **Data tests** (run *inside* every weekly run, not only CI): PK/dupe integrity, freshness-vs-allowed-lag per critical series, sanity ranges, archive-write verification. Failures feed confidence/fail-safe, not just CI red.
   - **Logic tests** (pytest, fixture-driven, no network): scoring monotonicity/inversion/damping (C3), regime classification on synthetic paths + hysteresis (C4), retrieval budget (C5), snapshot budget/schema/determinism (C6), fail-safe paths (C8).
   - **Regression tests — golden snapshots:** fixture DB for a frozen historical week ⇒ committed `snapshot.golden.json`; any diff fails until intentionally regenerated (`--update-golden`) with a version bump. This is the guard against silent drift when tuning weights/bands.
2. **Version governance (freeze-and-bump, Blueprint rule operationalized):** three independent version stamps recorded in every snapshot/report:
   - `scoring_version` — bump on any change to methods/lookbacks/bands/weights; policy: **recompute full history** under the new version (DuckDB makes this seconds at 60–120 indicators), keep old `fact_score` rows tagged via `params_json`;
   - `playbook_version` — bump on module content changes (front-matter `version` aggregated by index build);
   - `prompt_version` — bump on prompt-contract edits.
   A `CHANGELOG.md` in `05_blueprint/` records every bump + rationale (one line each).
3. **Existing QA scripts stay authoritative for the knowledge layer** and get extended, not replaced: `qa_repo.py` additionally validates registry↔extract provenance (`extract_ref` resolves), playbook index freshness, `snapshot_flags.md` ↔ code flag parity (flags emitted by code must be documented, and vice versa).
4. **Expansion protocol 34→60→120 (the ROI gate, operationalized):** an indicator flips `deferred → active` only when a checklist passes (source chain probed by `ipos-doctor`, scoring params set, playbook_ref present, one backfill pull archived, appears correctly in a dry-run snapshot). Checklist automated as `ipos-doctor --check-series <id>`. `needs_verification: true` extract items require a source/threshold verification note before seeding.
5. **CI-lite:** no cloud CI required (local-first); `uv run pytest -q` wired as pre-commit habit + a monthly scheduled "doctor + tests" task. If the repo lives on GitHub anyway (it does), a minimal Actions workflow running pytest on push is free and harmless — optional, not load-bearing.
6. **Docs-as-contract:** `blueprint_map.md` (C5) reviewed at each phase end; a phase is "done" only when its map rows say so and its meso-plan Definition-of-Done is demonstrably met.

## Implementation steps

1. `tests/` layout: `test_config.py`, `test_etl.py`, `test_scoring.py`, `test_regime.py`, `test_retrieval.py`, `test_snapshot.py`, `test_failsafe.py`, `test_golden.py` + `tests/fixtures/` (recorded pulls, synthetic paths, frozen-week DB builder).
2. Golden harness: `tests/golden/build_fixture_db.py` + committed golden JSON + `--update-golden` flow.
3. Extend `scripts/qa_repo.py` (provenance, index, flag parity).
4. `CHANGELOG.md` seed; version stamps threaded through C3/C5/C6 code.
5. Optional `.github/workflows/pytest.yml` (10 lines).

## Definition of done
- `uv run pytest` green and < 30 s; golden diff demonstrably catches a 1-point weight change; doctor checklist blocks an unverified series activation; version stamps visible in a produced snapshot.

**Effort:** M (spread across phases; golden harness lands with Phase 2). **Recurring tokens:** 0.
