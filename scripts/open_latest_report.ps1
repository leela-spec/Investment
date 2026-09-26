# =============================================================================
# Open Latest IPOS Report in Default Web Browser
#
# Quick operator launcher to locate and view the newest interactive report.
# =============================================================================

[CmdletBinding()]
param(
    [string]$RepoRoot = ""
)

if (-not $RepoRoot) {
    if ($PSScriptRoot) {
        $RepoRoot = Split-Path -Parent $PSScriptRoot
    } else {
        $RepoRoot = (Get-Location).Path
    }
}

$SnapshotsRoot = Join-Path $RepoRoot "data\exports\snapshots"
if (-not (Test-Path $SnapshotsRoot)) {
    Write-Error "No snapshots found in $SnapshotsRoot. Run the pipeline first."
    exit 1
}

$datedDirs = Get-ChildItem -Path $SnapshotsRoot -Directory | Sort-Object Name -Descending
if ($datedDirs.Count -eq 0) {
    Write-Error "No snapshot directories found in $SnapshotsRoot."
    exit 1
}

$LatestDir = $datedDirs[0].FullName
$ReportHtml = Join-Path $LatestDir "report.html"

if (-not (Test-Path $ReportHtml)) {
    Write-Error "report.html not found in $LatestDir."
    exit 1
}

Write-Host "[ipos-launcher] Opening latest report: $ReportHtml"
Start-Process $ReportHtml
