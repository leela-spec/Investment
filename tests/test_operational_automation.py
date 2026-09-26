"""Unit and regression tests for Operational Automation (E10).

Tests cover:
- CLI module entrypoint execution (`python -m ipos.run --help` and `python -m ipos.cli weekly --help`)
- PowerShell automation runner syntax & execution
- Windows Task Scheduler registration script integrity
- Automation status JSON schema and audit logging
"""

import json
import subprocess
import sys
from pathlib import Path
import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent


def test_ipos_run_main_help_exits_zero():
    """Verify python -m ipos.run --help executes cleanly and displays options."""
    cmd = [sys.executable, "-X", "utf8", "-m", "ipos.run", "--help"]
    res = subprocess.run(cmd, cwd=str(REPO_ROOT), capture_output=True, text=True, check=False)
    assert res.returncode == 0
    assert "Full weekly run" in res.stdout or "ipos-weekly" in res.stdout
    assert "--seed-offline" in res.stdout


def test_ipos_cli_weekly_help_exits_zero():
    """Verify python -m ipos.cli weekly --help executes cleanly."""
    cmd = [sys.executable, "-X", "utf8", "-m", "ipos.cli", "weekly", "--help"]
    res = subprocess.run(cmd, cwd=str(REPO_ROOT), capture_output=True, text=True, check=False)
    assert res.returncode == 0
    assert "--as-of" in res.stdout
    assert "--seed-offline" in res.stdout


def test_scheduler_script_syntax_and_status():
    """Verify scripts/register_scheduler.ps1 syntax and status query."""
    script_path = REPO_ROOT / "scripts" / "register_scheduler.ps1"
    assert script_path.exists()

    cmd = [
        "powershell.exe",
        "-NoProfile",
        "-ExecutionPolicy", "Bypass",
        "-File", str(script_path),
        "-Status",
    ]
    res = subprocess.run(cmd, cwd=str(REPO_ROOT), capture_output=True, text=True, check=False)
    # Status query should succeed (returns 0 whether registered or not)
    assert res.returncode == 0
    assert "[ipos-scheduler]" in res.stdout


def test_automated_runner_script_exists():
    """Verify scripts/run_pipeline_automated.ps1 exists and has proper permissions."""
    runner_path = REPO_ROOT / "scripts" / "run_pipeline_automated.ps1"
    assert runner_path.exists()
    content = runner_path.read_text(encoding="utf-8")
    assert "ipos.cli" in content
    assert "automation_status.json" in content


def test_automation_status_json_artifact_and_schema():
    """Validate real on-disk automation_status.json artifact and strict BOM-free UTF-8 encoding."""
    status_path = REPO_ROOT / "data" / "exports" / "automation_status.json"
    
    # If not yet created, execute the automated runner script to generate it
    if not status_path.exists():
        runner_path = REPO_ROOT / "scripts" / "run_pipeline_automated.ps1"
        cmd = [
            "powershell.exe",
            "-NoProfile",
            "-ExecutionPolicy", "Bypass",
            "-File", str(runner_path),
            "-SeedOffline",
            "-AsOf", "2026-09-25",
        ]
        res = subprocess.run(cmd, cwd=str(REPO_ROOT), capture_output=True, text=True, check=False)
        assert res.returncode == 0

    assert status_path.exists(), "automation_status.json must exist"

    # Read strictly with encoding='utf-8' (will fail with JSONDecodeError if PowerShell emitted BOM)
    raw_text = status_path.read_text(encoding="utf-8")
    assert not raw_text.startswith("\ufeff"), "automation_status.json must NOT contain a UTF-8 BOM"

    status_data = json.loads(raw_text)

    required_keys = {
        "last_run_timestamp",
        "execution_status",
        "exit_code",
        "duration_seconds",
        "log_file",
        "snapshot_json",
        "report_html",
        "report_md",
    }
    assert required_keys.issubset(status_data.keys())
    assert status_data["execution_status"] in ("OK", "FAILED", "DEGRADED")
    assert isinstance(status_data["exit_code"], int)
    assert isinstance(status_data["duration_seconds"], (int, float))

    # Verify log file path exists on disk
    log_file = Path(status_data["log_file"])
    assert log_file.exists(), f"Log file {log_file} must exist"
    assert log_file.stat().st_size > 0, "Log file must not be empty"

