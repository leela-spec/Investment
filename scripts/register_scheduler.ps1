# =============================================================================
# IPOS weekly pipeline — Windows Task Scheduler registration
#
# Registers a scheduled task that runs the full IPOS weekly pipeline every
# SATURDAY at 06:00 local time, headless (no window flash), logging output to
# logs\scheduled\ and recording status to data\exports\automation_status.json.
#
# USAGE (from PowerShell in the repo root):
#   .\scripts\register_scheduler.ps1                 # register/update task
#   .\scripts\register_scheduler.ps1 -Status         # check task registration & last run
#   .\scripts\register_scheduler.ps1 -Unregister     # remove the task
#   .\scripts\register_scheduler.ps1 -RunNow         # trigger one run immediately
#
# PARAMETERS (all overridable):
#   -TaskName    : Scheduled task name (default: "IPOS Weekly Pipeline")
#   -RunTime     : Time of day to run on Saturday (default: "06:00")
#   -RepoRoot    : Root directory of repository (default: auto-detected)
# =============================================================================

[CmdletBinding()]
param(
    [switch]$Unregister,
    [switch]$RunNow,
    [switch]$Status,
    [string]$TaskName = "IPOS Weekly Pipeline",
    [string]$RepoRoot = "",
    [string]$RunTime = "06:00"
)

$ErrorActionPreference = "Stop"

if (-not $RepoRoot) {
    if ($PSScriptRoot) {
        $RepoRoot = Split-Path -Parent $PSScriptRoot
    } else {
        $RepoRoot = (Get-Location).Path
    }
}

function Info($msg)  { Write-Host "[ipos-scheduler] $msg" }
function Fail($msg)  { Write-Error "[ipos-scheduler] $msg"; exit 1 }

# --- 1. Query Status Mode ---
if ($Status) {
    $existing = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
    if (-not $existing) {
        Info "Task '$TaskName' is NOT registered."
        exit 0
    }
    $info = Get-ScheduledTaskInfo -TaskName $TaskName -ErrorAction SilentlyContinue
    Info "Task Name       : $TaskName"
    Info "State           : $($existing.State)"
    Info "Last Run Time   : $($info.LastRunTime)"
    Info "Last Task Result: $($info.LastTaskResult)"
    Info "Next Run Time   : $($info.NextRunTime)"
    
    $statusJson = Join-Path $RepoRoot "data\exports\automation_status.json"
    if (Test-Path $statusJson) {
        Info "--- Latest Automation Status Record ---"
        Get-Content $statusJson | Write-Host
    }
    exit 0
}

# --- 2. Unregister Mode ---
if ($Unregister) {
    if (Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue) {
        Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
        Info "Task '$TaskName' removed successfully."
    } else {
        Info "Task '$TaskName' not present; nothing to remove."
    }
    exit 0
}

# --- 3. Resolve Runner Script ---
$AutomatedRunner = Join-Path $RepoRoot "scripts\run_pipeline_automated.ps1"
if (-not (Test-Path $AutomatedRunner)) {
    Fail "Automated runner script not found at: $AutomatedRunner"
}

$PowershellExe = "$env:SystemRoot\System32\WindowsPowerShell\v1.0\powershell.exe"
$ActionArgs = "-NoProfile -ExecutionPolicy Bypass -File `"$AutomatedRunner`""

Info "Repo Root : $RepoRoot"
Info "Runner    : $AutomatedRunner"
Info "Schedule  : Every Saturday at $RunTime"

# --- 4. Build Trigger / Settings / Action ---
$Trigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Saturday -At $RunTime

$Settings = New-ScheduledTaskSettingsSet `
    -StartWhenAvailable `
    -DontStopIfGoingOnBatteries `
    -AllowStartIfOnBatteries `
    -ExecutionTimeLimit (New-TimeSpan -Hours 2) `
    -MultipleInstances IgnoreNew

$Action = New-ScheduledTaskAction `
    -Execute $PowershellExe `
    -Argument $ActionArgs `
    -WorkingDirectory $RepoRoot

$Principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType Interactive -RunLevel Limited

# --- 5. Register Task ---
$existing = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
if ($existing) {
    Set-ScheduledTask -TaskName $TaskName -Trigger $Trigger -Settings $Settings -Action $Action | Out-Null
    Info "Task '$TaskName' successfully UPDATED."
} else {
    Register-ScheduledTask -TaskName $TaskName `
        -Action $Action -Trigger $Trigger -Settings $Settings `
        -Principal $Principal -Description `
        "IPOS weekly investment pipeline: pull -> score -> aggregate -> riskfolio -> action matrix -> export." | Out-Null
    Info "Task '$TaskName' successfully REGISTERED."
}

# --- 6. Immediate Run ---
if ($RunNow) {
    Info "Triggering task '$TaskName' now..."
    Start-ScheduledTask -TaskName $TaskName
    Start-Sleep -Seconds 3
    $state = (Get-ScheduledTask -TaskName $TaskName).State
    Info "Task current state: $state"
}

Info "Done."
