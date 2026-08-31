#!/usr/bin/env python3
"""Antigravity Stop hook: resist premature module completion.

This hook is intentionally conservative and bounded. It only activates when
.agents/current-task.json has active=true. It never blocks errors/max-step exits,
and after three model-stop attempts it allows termination to avoid infinite loops.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path


def emit(decision: str, reason: str = "") -> None:
    out = {"decision": decision}
    if reason:
        out["reason"] = reason
    print(json.dumps(out))


def main() -> None:
    try:
        payload = json.load(sys.stdin)
    except Exception:
        emit("allow")
        return

    # Do not interfere with genuine errors, max-step termination, or repeated loops.
    if payload.get("terminationReason") != "model_stop":
        emit("allow")
        return
    if int(payload.get("executionNum", 1)) > 3:
        emit("allow", "IPOS stop gate released after bounded retries; record BLOCKED if work is incomplete.")
        return

    workspaces = payload.get("workspacePaths") or []
    if not workspaces:
        emit("allow")
        return
    root = Path(workspaces[0])
    task_file = root / ".agents" / "current-task.json"
    if not task_file.exists():
        emit("allow")
        return

    try:
        task = json.loads(task_file.read_text(encoding="utf-8"))
    except Exception:
        emit("allow")
        return

    if not task.get("active", False):
        emit("allow")
        return

    module_id = str(task.get("module_id", "UNKNOWN"))
    run_dir_value = task.get("run_dir")
    if not run_dir_value:
        emit("continue", f"{module_id} is active but current-task.json has no run_dir. Create the run directory and execution evidence before stopping.")
        return

    run_dir = root / str(run_dir_value)
    required = [
        "TARGET_PROOF.md",
        "preflight.json",
        "test-results.json",
        "IMPLEMENTATION_REPORT.md",
        "VERIFICATION_REPORT.md",
    ]
    missing = [name for name in required if not (run_dir / name).exists()]
    if missing:
        emit(
            "continue",
            f"{module_id} is not complete. Missing required proof artifacts: {', '.join(missing)}. Continue execution or record a genuine BLOCKED_HUMAN_GATE state.",
        )
        return

    report = (run_dir / "VERIFICATION_REPORT.md").read_text(encoding="utf-8", errors="replace").upper()
    accepted = any(token in report for token in ["VERDICT: PASS", "VERDICT**: `PASS`", "VERDICT: `PASS`"]) or "PASS_WITH_LIMITATIONS" in report
    blocked = "BLOCKED_HUMAN_GATE" in report
    failed = "VERDICT: FAIL" in report or "VERDICT**: `FAIL`" in report

    if failed:
        emit("allow", f"{module_id} verifier returned FAIL. Stop is allowed; do not advance to another module. Repair in a new bounded run.")
        return
    if blocked:
        emit("allow", f"{module_id} reached a human gate. Stop is allowed and user input is required.")
        return
    if not accepted:
        emit(
            "continue",
            f"{module_id} has a verification report but no accepted verifier verdict. Invoke ipos-proof-verifier and resolve the verdict before claiming completion.",
        )
        return

    emit("allow")


if __name__ == "__main__":
    main()
