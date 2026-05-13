#Requires -Version 5.1
<#
  Full local bootstrap + dev server (Windows, MySQL80 service).
  Example:
    .\run_all.ps1 -RootPassword 'YourMySQLRootPassword'
  Or set MYSQL_ROOT_PASSWORD in .env first, then:
    .\run_all.ps1
  Default dev port is 8001 (override with -Port 8010).
#>
param(
    [string] $RootPassword = "",
    [int] $Port = 8001
)

$ErrorActionPreference = "Stop"
$root = $PSScriptRoot
Set-Location $root

$splat = @{ }
if ($PSBoundParameters.ContainsKey("RootPassword")) {
    $splat.RootPassword = $RootPassword
}
& (Join-Path $root "scripts\setup_local_mysql.ps1") @splat

Write-Host ""
Write-Host "Starting Django at http://127.0.0.1:$Port/ (Ctrl+C to stop)"
& (Join-Path $root ".venv\Scripts\python.exe") (Join-Path $root "manage.py") runserver "127.0.0.1:$Port"
