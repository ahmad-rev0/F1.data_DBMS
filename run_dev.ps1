#Requires -Version 5.1
<#
  Start Django dev server (default port 8001 so it does not clash with other projects on 8000).
  Examples:
    .\run_dev.ps1
    .\run_dev.ps1 -Port 8010
#>
param(
    [int] $Port = 8001
)

$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

$py = Join-Path $PSScriptRoot ".venv\Scripts\python.exe"
if (-not (Test-Path $py)) {
    Write-Error "Missing $py — create the venv first: python -m venv .venv ; .\.venv\Scripts\pip install -r requirements.txt"
}

Write-Host "F1 platform: http://127.0.0.1:$Port/ (Ctrl+C to stop)"
& $py (Join-Path $PSScriptRoot "manage.py") runserver "127.0.0.1:$Port"
