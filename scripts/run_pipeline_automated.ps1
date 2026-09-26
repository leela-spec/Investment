# =============================================================================
# IPOS Weekly Pipeline — Automated Headless Execution Script
#
# Robust Windows automation wrapper for the IPOS weekly pipeline.
# Executed by Windows Task Scheduler or run on-demand by the operator.
#
# Responsibilities:
# 1. Resolves repo root and Python virtual environment (.venv).
# 2. Streams and captures execution output to logs\scheduled\run_YYYY-MM-DD.log.
# 3. Executes `python -X utf8 -m ipos.cli weekly`.
# 4. Writes machine-readable health & status to data\exports\automation_status.json.
# 5. Rotates log files, keeping the newest N=8 runs.
# 6. Propagates exit code for Windows Task Scheduler monitoring.
# =============================================================================

[CmdletBinding()]
param(
    [string]$RepoRoot = "",
    [string]$AsOf = "",
    [switch]$SeedOffline,
    [string]$PythonExe = "",
    [int]$KeepLogs = 8
)

$ErrorActionPreference = "Stop"

if (-not $RepoRoot) {
    if ($PSScriptRoot) {
        $RepoRoot = Split-Path -Parent $PSScriptRoot
    } else {
        $RepoRoot = (Get-Location).Path
    }
}

function Log-Message([string]$Msg) {
    $timestamp = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss")
    Write-Host "[$timestamp] [ipos-automation] $Msg"
}

# --- 1. Path Resolution ---
if (-not (Test-Path $RepoRoot)) {
    Write-Error "RepoRoot does not exist: $RepoRoot"
    exit 2
}

$LogsDir = Join-Path $RepoRoot "logs\scheduled"
if (-not (Test-Path $LogsDir)) {
    New-Item -ItemType Directory -Path $LogsDir -Force | Out-Null
}

$ExportsDir = Join-Path $RepoRoot "data\exports"
if (-not (Test-Path $ExportsDir)) {
    New-Item -ItemType Directory -Path $ExportsDir -Force | Out-Null
}

# Locate Python: prefer repo .venv, fallback to PATH
if (-not $PythonExe) {
    $venvPy = Join-Path $RepoRoot ".venv\Scripts\python.exe"
    if (Test-Path $venvPy) {
        $PythonExe = $venvPy
    } else {
        $PythonExe = "python.exe"
    }
}

$TodayStr = (Get-Date).ToString("yyyy-MM-dd")
$LogFile = Join-Path $LogsDir "run_$TodayStr.log"

Log-Message "Starting automated weekly pipeline run"
Log-Message "Repository: $RepoRoot"
Log-Message "Python:     $PythonExe"
Log-Message "Log file:   $LogFile"

# --- 2. Build Invocation Arguments ---
$WeeklyArgs = @("-X", "utf8", "-m", "ipos.cli", "weekly")
if ($AsOf) {
    $WeeklyArgs += @("--as-of", $AsOf)
}
if ($SeedOffline) {
    $WeeklyArgs += "--seed-offline"
}

# --- 3. Execute Pipeline with Timing & Log Capture ---
$StartTime = Get-Date
$ExecutionSuccess = $false
$ExitCode = 1

try {
    Push-Location $RepoRoot

    # Execute process and capture standard output + error to log file
    $pinfo = New-Object System.Diagnostics.ProcessStartInfo
    $pinfo.FileName = $PythonExe
    $pinfo.Arguments = ($WeeklyArgs -join " ")
    $pinfo.WorkingDirectory = $RepoRoot
    $pinfo.RedirectStandardOutput = $true
    $pinfo.RedirectStandardError = $true
    $pinfo.UseShellExecute = $false
    $pinfo.CreateNoWindow = $true

    $process = New-Object System.Diagnostics.Process
    $process.StartInfo = $pinfo

    $outBuilder = New-Object System.Text.StringBuilder
    $errBuilder = New-Object System.Text.StringBuilder

    $outEvent = Register-ObjectEvent -InputObject $process -EventName OutputDataReceived -Action {
        if ($EventArgs.Data) { [void]$Event.MessageData.AppendLine($EventArgs.Data) }
    } -MessageData $outBuilder

    $errEvent = Register-ObjectEvent -InputObject $process -EventName ErrorDataReceived -Action {
        if ($EventArgs.Data) { [void]$Event.MessageData.AppendLine($EventArgs.Data) }
    } -MessageData $errBuilder

    [void]$process.Start()
    $process.BeginOutputReadLine()
    $process.BeginErrorReadLine()

    # Wait up to 30 minutes for execution to finish
    $finished = $process.WaitForExit(1800000)

    Unregister-Event -SourceIdentifier $outEvent.Name -ErrorAction SilentlyContinue
    Unregister-Event -SourceIdentifier $errEvent.Name -ErrorAction SilentlyContinue

    if (-not $finished) {
        $process.Kill()
        Log-Message "ERROR: Pipeline timed out after 30 minutes."
        $ExitCode = 124
    } else {
        $ExitCode = $process.ExitCode
    }

    $allOutput = "=== STDOUT ===`n" + $outBuilder.ToString() + "`n=== STDERR ===`n" + $errBuilder.ToString()
    Set-Content -Path $LogFile -Value $allOutput -Encoding utf8

    if ($ExitCode -eq 0) {
        $ExecutionSuccess = $true
        Log-Message "Pipeline execution completed successfully (ExitCode 0)."
    } else {
        Log-Message "Pipeline execution exited with code $ExitCode. Check $LogFile for details."
    }
} catch {
    Log-Message "FATAL: Exception during execution: $_"
    Add-Content -Path $LogFile -Value "`nFATAL EXCEPTION: $_" -Encoding utf8
    $ExitCode = 1
} finally {
    Pop-Location
}

$EndTime = Get-Date
$Duration = [math]::Round(($EndTime - $StartTime).TotalSeconds, 2)

# --- 4. Discover Artifacts & Build Status Record ---
$LatestSnapshotDir = $null
$SnapshotsRoot = Join-Path $RepoRoot "data\exports\snapshots"
if (Test-Path $SnapshotsRoot) {
    $datedDirs = Get-ChildItem -Path $SnapshotsRoot -Directory | Sort-Object Name -Descending
    if ($datedDirs.Count -gt 0) {
        $LatestSnapshotDir = $datedDirs[0].FullName
    }
}

$SnapshotJson = if ($LatestSnapshotDir) { Join-Path $LatestSnapshotDir "snapshot.json" } else { "" }
$ReportHtml = if ($LatestSnapshotDir) { Join-Path $LatestSnapshotDir "report.html" } else { "" }
$ReportMd = if ($LatestSnapshotDir) { Join-Path $LatestSnapshotDir "report.md" } else { "" }

$StatusRecord = [ordered]@{
    "last_run_timestamp" = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
    "execution_status"   = if ($ExecutionSuccess) { "OK" } else { "FAILED" }
    "exit_code"          = $ExitCode
    "duration_seconds"   = $Duration
    "log_file"           = $LogFile
    "snapshot_json"      = if (Test-Path $SnapshotJson) { $SnapshotJson } else { $null }
    "report_html"        = if (Test-Path $ReportHtml) { $ReportHtml } else { $null }
    "report_md"          = if (Test-Path $ReportMd) { $ReportMd } else { $null }
}

$StatusJsonPath = Join-Path $RepoRoot "data\exports\automation_status.json"
$statusJsonText = $StatusRecord | ConvertTo-Json -Depth 4
$utf8NoBom = New-Object System.Text.UTF8Encoding($false)
[System.IO.File]::WriteAllText($StatusJsonPath, $statusJsonText, $utf8NoBom)
Log-Message "Automation status updated -> $StatusJsonPath"

# --- 5. Rotate Old Logs ---
try {
    $existingLogs = Get-ChildItem -Path $LogsDir -Filter "run_*.log" | Sort-Object CreationTime -Descending
    if ($existingLogs.Count -gt $KeepLogs) {
        $logsToDelete = $existingLogs | Select-Object -Skip $KeepLogs
        foreach ($oldLog in $logsToDelete) {
            Remove-Item $oldLog.FullName -Force -ErrorAction SilentlyContinue
        }
    }
} catch {
    # Non-fatal log rotation
}

Log-Message "Run finished in $Duration seconds. Returning exit code $ExitCode."
exit $ExitCode
