#!/usr/bin/env bash
# =============================================================================
# IPOS weekly pipeline — Linux cron / systemd automation wrapper
#
# Head-less weekly runner for the full IPOS pipeline. Install as a cron entry:
#
#   # every Saturday 05:00
#   0 5 * * 6  /root/MasterOfArts/IPOS/scripts/run_weekly_cron.sh >> /root/MasterOfArts/IPOS/logs/cron.log 2>&1
#
# Or via a systemd timer (unit snippets at the bottom of this file).
#
# SAFETY CONTRACT (mirrors run.py's fail-safe, C8):
#   * NEVER passes --seed-offline: a missing pull must degrade the run, not
#     fill synthetic rows into live tables.
#   * Uses flock so overlapping invocations (manual + scheduled) cannot
#     interleave DuckDB writes.
#   * Writes an audit log per run; keeps the last N=8 logs.
#   * Exit code propagates the pipeline result for cron/systemd monitoring
#     (FAILED_ATTEMPT => non-zero).
# =============================================================================

set -u

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LOG_DIR="${REPO_ROOT}/logs/cron"
LOCK_FILE="/tmp/ipos-weekly.lock"
KEEP_LOGS=8

# --- locate python -----------------------------------------------------------
if [ -x "${REPO_ROOT}/.venv/bin/python" ]; then
    PYTHON="${REPO_ROOT}/.venv/bin/python"
elif command -v python3 >/dev/null 2>&1; then
    PYTHON="python3"
else
    echo "[ipos-cron] FATAL: no python found" >&2
    exit 2
fi

mkdir -p "${LOG_DIR}"

log() { echo "[ipos-cron $(date '+%Y-%m-%d %H:%M:%S')] $*"; }

# --- single-instance lock ----------------------------------------------------
exec 9>"${LOCK_FILE}"
if ! flock -n 9; then
    log "another IPOS run holds the lock (${LOCK_FILE}); exiting."
    exit 0
fi

# --- environment sanity ------------------------------------------------------
export PYTHONDONTWRITEBYTECODE=1
export PYTHONUNBUFFERED=1
cd "${REPO_ROOT}" || { log "FATAL: cannot cd ${REPO_ROOT}"; exit 2; }

RUN_DATE="$(date +%Y-%m-%d)"
LOG_FILE="${LOG_DIR}/run_${RUN_DATE}.log"

log "starting weekly pipeline: repo=${REPO_ROOT} python=${PYTHON}"

# --- pre-flight ---------------------------------------------------------------
if ! "${PYTHON}" -c "import duckdb, yaml, pydantic" >>"${LOG_FILE}" 2>&1; then
    log "FATAL: python deps missing (duckdb/yaml/pydantic). See ${LOG_FILE}"
    exit 3
fi

# --- run ----------------------------------------------------------------------
# The pipeline stages live in ipos.run (pull -> canonical -> scores ->
# aggregate -> export). Default invocation is LIVE-PULL mode; no synthetic
# seeding is ever passed here by design.
set +e
"${PYTHON}" -X utf8 -m ipos.run "$@" >>"${LOG_FILE}" 2>&1
RC=$?
set -e

# --- post-run bookkeeping ------------------------------------------------------
if [ ${RC} -eq 0 ]; then
    log "pipeline OK -> ${LOG_FILE}"
else
    log "pipeline FAILED rc=${RC} -> ${LOG_FILE}"
fi

# rotate logs, keep newest KEEP_LOGS
ls -1t "${LOG_DIR}"/run_*.log 2>/dev/null | tail -n +"$((KEEP_LOGS + 1))" | xargs -r rm -f

exit ${RC}

# =============================================================================
# systemd alternative — /etc/systemd/system/ipos-weekly.service
# ---------------------------------------------------------------------------
# [Unit]
# Description=IPOS weekly macro pipeline
# After=network-online.target
# Wants=network-online.target
#
# [Service]
# Type=oneshot
# WorkingDirectory=/root/MasterOfArts/IPOS
# ExecStart=/root/MasterOfArts/IPOS/scripts/run_weekly_cron.sh
# TimeoutStartSec=7200
# -----------------------------------------------------------------------------
# /etc/systemd/system/ipos-weekly.timer
# [Unit]
# Description=Run IPOS weekly pipeline Saturday 05:00
#
# [Timer]
# OnCalendar=Sat 05:00
# Persistent=true
#
# [Install]
# WantedBy=timers.target
#
# enable with:  systemctl daemon-reload && systemctl enable --now ipos-weekly.timer
# =============================================================================
