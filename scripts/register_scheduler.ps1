# =============================================================================
# IPOS weekly pipeline — Windows Task Scheduler registration
#
# Registers a scheduled task that runs the full IPOS weekly pipeline every
# SATURDAY at 05:00 local time, headless (no window flash), logging output to
# logs\scheduled\.
#
# USAGE (from an elevated PowerShell in the repo root):
#   .\scripts\register_scheduler.ps1                 # register/update task
#   .\scripts\register_scheduler.ps1 -Unregister     # remove the task
#   .\scripts\register_scheduler.ps1 -RunNow         # trigger one run immediately
#
# PARAMETERS (all overridable):
#   -PythonExe   : python.exe to use (defaults to repo .venv, else PATH python)
#   -RepoRoot    : defaults to the parent of this script's directory
#
# SAFETY:
#   * Never passes --seed-offline. A failed pull must NOT fill synthetic rows
#     into live tables (see purge_synthetic.py incident 2026-07-27).
#   * The task runs whether or not the user is logged on (-LogonType S4U is
#     avoided deliberately; we use the current user interactive token so the
#     venv and any mounted drives resolve normally).
# =============================================================================

[CmdletBinding()]
param(
    [switch]$Unregister,
    [switch]$RunNow,
    [string]$TaskName = "IPOS Weekly Pipeline",
    [string]$RepoRoot = (Split-Path -Parent $PSScriptRoot),
    [string]$PythonExe = "",
    [string]$RunTime = "05:00"
)

$ErrorActionPreference = "Stop"

function Info($msg)  { Write-Host "[ipos-scheduler] $msg" }
function Fail($msg)  { Write-Error "[ipos-scheduler] $msg"; exit 1 }

# --- resolve paths -----------------------------------------------------------
$LogsDir = Join-Path $RepoRoot "logs\scheduled"
if (-not (Test-Path $LogsDir)) { New-Item -ItemType Directory -Path $LogsDir | Out-Null }

# Prefer the project venv's python; fall back to whatever is on PATH.
if (-not $PythonExe) {
    $venvPy = Join-Path $RepoRoot ".venv\Scripts\python.exe"
    if (Test-Path $venvPy) { $PythonExe = $venvPy } else { $PythonExe = "python.exe" }
}
if (-not (Get-Command $PythonExe -ErrorAction SilentlyContinue) -and -not (Test-Path $PythonExe)) {
    Fail "python executable not found: $PythonExe"
}

# The weekly entrypoint. run.py exposes the full staged pipeline;
# `python -m ipos.run` executes it with default (live-pull) settings.
$Runner = Join-Path $RepoRoot "ipos\run.py"
if (-not (Test-Path $Runner)) { Fail "runner not found: $Runner" }

$ActionArgs = @("-X", "utf8", "-m", "ipos.run")
Info "repo      : $RepoRoot"
Info "python    : $PythonExe"
Info "action    : $PythonExe $($ActionArgs -join ' ')"
Info "schedule  : every Saturday at $RunTime"

# --- unregister mode ---------------------------------------------------------
if ($Unregister) {
    if (Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue) {
        Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
        Info "task '$TaskName' removed."
    } else {
        Info "task '$TaskName' not present; nothing to remove."
    }
    exit 0
}

# --- build trigger / settings / action ---------------------------------------
$Trigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Saturday -At $RunTime

$Settings = New-ScheduledTaskSettingsSet `
    -StartWhenAvailable `
    -DontStopIfGoingOnBatteries `
    -AllowStartIfOnBatteries `
    -ExecutionTimeLimit (New-TimeSpan -Hours 2) `
    -MultipleInstances IgnoreNew
# StartWhenAvailable: run missed schedules after wake/sleep.
# MultipleInstances IgnoreNew: never overlap two weekly runs.

$Action = New-ScheduledTaskAction `
    -Execute $PythonExe `
    -Argument ($ActionArgs -join " ") `
    -WorkingDirectory $RepoRoot

$Principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType Interactive -RunLevel Limited

# --- register ----------------------------------------------------------------
$existing = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
if ($existing) {
    Set-ScheduledTask -TaskName $TaskName -Trigger $Trigger -Settings $Settings -Action $Action | Out-Null
    Info "task '$TaskName' UPDATED."
} else {
    Register-ScheduledTask -TaskName $TaskName `
        -Action $Action -Trigger $Trigger -Settings $Settings `
        -Principal $Principal -Description `
        "IPOS weekly macro pipeline: data pull -> DuckDB -> scoring -> regime -> snapshot export." | Out-Null
    Info "task '$TaskName' REGISTERED."
}

# Wrap the action with log capture by registering a cmd wrapper instead, so
# stdout/stderr land in logs\scheduled\<date>.log for auditability.
$WrapCmd = "/c cd /d `"$RepoRoot`" && `"$PythonExe`" -X utf8 -m ipos.run >> `"$LogsDir\run_%DATE:/=-%.log`" 2>&1"
$WrapAction = New-ScheduledTaskAction -Execute "$env:ComSpec" -Argument $WrapCmd -WorkingDirectory $RepoRoot
Set-ScheduledTask -TaskName $TaskName -Action $WrapAction | Out-Null
Info "log capture wired -> $LogsDir"

# --- optional immediate run ---------------------------------------------------
if ($RunNow) {
    Info "triggering one run now..."
    Start-ScheduledTask -TaskName $TaskName
    Start-Sleep -Seconds 5
    $state = (Get-ScheduledTask -TaskName $TaskName).State
    Info "task state: $state"
}

Info "done."
