# C8 — Automation & Operations (Meso Plan)

**Owns:** the run contract, Windows Task Scheduler integration, logging, fail-safe behavior, health checks. Goal: **zero-touch weeks** — the human's only weekly job is reading the report.
**Depends on:** all runtime clusters.

## Options considered (2026 web-validated)

| Option | Verdict |
|--------|---------|
| One idempotent CLI + **Task Scheduler** (Blueprint) | ✅ **Chosen.** Consensus best practice for single-machine weekly jobs. |
| Prefect / Dagster local | ❌ Confirmed overkill (services, UI, deps) for one linear weekly DAG. Revisit only if the DAG ever branches heavily. |
| NSSM background service | ❌ Weekly cadence needs no resident process. |

## Decisions

1. **One entry point, staged:** `uv run ipos-weekly [--as-of YYYY-MM-DD]` = pull → validate → canonicalize → features → scores → aggregate → snapshot → report → (optional) narrate. Stages are functions with explicit inputs; `--from-stage`/`--only-stage` for reruns. **Idempotent:** same `as_of` re-run ⇒ identical outputs (PK upserts + deterministic transforms).
2. **Scheduling (scripted, never clicked):** `scripts/register_task.ps1` uses the `ScheduledTasks` PowerShell module to register "IPOS Weekly", Saturday 08:00, action `uv run ipos-weekly` in repo dir, with **StartWhenAvailable = true** (missed-start catch-up — laptop-off case) and "run whether user is logged on or not". Unregister/`--dry-run` flags included. `schtasks.exe` one-liner documented as fallback.
3. **Run contract & fail-safe (Blueprint policy, hardened):**
   - Run header logged: `run_id`, `as_of`, git hash, config hash, registry hash.
   - Non-critical series failure ⇒ stale flag, confidence hit, run continues.
   - **Critical** series failure ⇒ no snapshot overwrite; write `FAILED_ATTEMPT` row in `run_log` + `reports/latest.html` banner from last good snapshot ("stale as of …").
   - Any unhandled exception ⇒ exit code ≠ 0 (Task Scheduler records it), full traceback in log, DB untouched beyond completed stage (stage-level transactionality).
4. **Logging:** std `logging` → rotating `logs/etl.log` (keep 12) **+** structured `run_log` table (per-stage rows: duration, rows in/out, failures, retries) — the DB is the observability backend; the report's data-quality banner reads it.
5. **Notification (free, local):** Windows toast (PowerShell `BurntToast` optional) + the report file itself; no cloud/webhook dependency. Optional later: e-mail via user SMTP.
6. **`ipos-doctor` (health check, on demand + monthly task):** verifies API keys present, one probe call per source type, DB integrity (PK dupes, orphan series), staleness table (each critical series' last obs age vs allowed lag), scheduled-task existence + last result, archive growth. Output: console table + exit code.
7. **Backups:** DuckDB file + configs zipped weekly post-run into `data/backups/` (keep 8); archive/ is append-only anyway. Restore = unzip. One function, cheap insurance.

## Implementation steps

1. `ipos/cli.py` (argparse or typer) — `ipos-weekly`, `ipos-init`, `ipos-pull`, `ipos-score`, `ipos-doctor`, `ipos-backfill`.
2. `ipos/run.py` — stage runner + run_log writes + fail-safe logic.
3. `scripts/register_task.ps1` (+ `unregister`), `scripts/README.md` snippet.
4. Backup step + rotation.
5. pytest: fail-safe paths (critical-missing fixture ⇒ snapshot preserved, FAILED_ATTEMPT row), exit codes, idempotent re-run.

## Definition of done
- Fresh Windows machine: `uv sync` → `ipos-init` → `ipos-backfill` → `register_task.ps1` = fully automated weekly operation; unplugging the network for a week produces a degraded-but-honest report, not a crash; `ipos-doctor` green.

**Effort:** S–M. **Recurring tokens:** 0. **Recurring human time:** ~0 min/week (read the report).
