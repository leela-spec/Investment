"""Tests for IPOS Stop Gate Hook (.agents/hooks/ipos_stop_gate.py)."""

import json
import subprocess
import sys
import tempfile
from pathlib import Path


def run_hook(payload: dict, cwd: Path) -> dict:
    hook_script = Path(__file__).resolve().parent.parent / ".agents" / "hooks" / "ipos_stop_gate.py"
    proc = subprocess.run(
        [sys.executable, str(hook_script)],
        input=json.dumps(payload),
        text=True,
        capture_output=True,
        cwd=str(cwd),
    )
    assert proc.returncode == 0, f"Hook process failed: {proc.stderr}"
    return json.loads(proc.stdout.strip())


def test_stop_gate_inactive_task_allows_stop(tmp_path):
    agents_dir = tmp_path / ".agents"
    agents_dir.mkdir()
    task_file = agents_dir / "current-task.json"
    task_file.write_text(json.dumps({"active": False, "module_id": None, "run_dir": None}), encoding="utf-8")

    payload = {"terminationReason": "model_stop", "workspacePaths": [str(tmp_path)]}
    res = run_hook(payload, agents_dir)
    assert res["decision"] == "allow"


def test_stop_gate_bom_task_file_parsed(tmp_path):
    agents_dir = tmp_path / ".agents"
    agents_dir.mkdir()
    task_file = agents_dir / "current-task.json"
    # Write with UTF-8 BOM
    bom_content = "\ufeff" + json.dumps({"active": False, "module_id": "C11", "run_dir": None})
    task_file.write_text(bom_content, encoding="utf-8")

    payload = {"terminationReason": "model_stop", "workspacePaths": [str(tmp_path)]}
    res = run_hook(payload, agents_dir)
    assert res["decision"] == "allow"


def test_stop_gate_malformed_task_file_fails_closed(tmp_path):
    agents_dir = tmp_path / ".agents"
    agents_dir.mkdir()
    task_file = agents_dir / "current-task.json"
    task_file.write_text("{ unparseable json: true, ", encoding="utf-8")

    payload = {"terminationReason": "model_stop", "workspacePaths": [str(tmp_path)]}
    res = run_hook(payload, agents_dir)
    assert res["decision"] == "continue"
    assert "Malformed or unparseable" in res["reason"]
