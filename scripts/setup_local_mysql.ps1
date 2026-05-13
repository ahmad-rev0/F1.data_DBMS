#Requires -Version 5.1
<#
.SYNOPSIS
  Local Windows MySQL 8 setup: create database + app user, apply DDL, Django migrate, load CSVs.

.PARAMETER RootPassword
  MySQL root password. If omitted, uses process env MYSQL_ROOT_PASSWORD, then .env MYSQL_ROOT_PASSWORD.

.EXAMPLE
  .\scripts\setup_local_mysql.ps1 -RootPassword 'yourRootPassword'
#>
param(
    [string] $RootPassword = ""
)

$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $ProjectRoot

function Get-DotEnvValue {
    param([string]$Path, [string]$Key)
    if (-not (Test-Path -LiteralPath $Path)) { return "" }
    foreach ($line in Get-Content -LiteralPath $Path) {
        if ($line -match '^\s*#' -or $line -notmatch '\S') { continue }
        if ($line -match "^\s*$Key\s*=\s*(.*)\s*$") {
            return $Matches[1].Trim().Trim('"').Trim("'")
        }
    }
    return ""
}

$envPath = Join-Path $ProjectRoot ".env"
if (-not (Test-Path -LiteralPath $envPath)) {
    Copy-Item (Join-Path $ProjectRoot ".env.example") $envPath -Force
    Write-Host "Created .env from .env.example"
}

$dbName = Get-DotEnvValue $envPath "MYSQL_DATABASE"
if (-not $dbName) { $dbName = "formula1" }
$dbUser = Get-DotEnvValue $envPath "MYSQL_USER"
if (-not $dbUser) { $dbUser = "f1_app" }
$dbPass = Get-DotEnvValue $envPath "MYSQL_PASSWORD"
if (-not $dbPass) { $dbPass = "changeme_app" }

if (-not $RootPassword) {
    $RootPassword = [Environment]::GetEnvironmentVariable("MYSQL_ROOT_PASSWORD", "Process")
}
if (-not $RootPassword) {
    $RootPassword = Get-DotEnvValue $envPath "MYSQL_ROOT_PASSWORD"
}
if (-not $RootPassword) {
    Write-Error "Provide -RootPassword, or set MYSQL_ROOT_PASSWORD in .env, or set env var MYSQL_ROOT_PASSWORD for this session."
}

$mysqlCandidates = @(
    "C:\Program Files\MySQL\MySQL Server 8.4\bin\mysql.exe",
    "C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe"
)
$mysql = $mysqlCandidates | Where-Object { Test-Path $_ } | Select-Object -First 1
if (-not $mysql) {
    Write-Error "mysql.exe not found under Program Files. Install MySQL 8+ or add mysql.exe to PATH."
}

Write-Host "Using: $mysql"

function Invoke-RootSql([string]$Sql) {
    & $mysql -u root --password=$RootPassword -e $Sql
    if ($LASTEXITCODE -ne 0) { throw "mysql failed: $Sql" }
}

Invoke-RootSql "CREATE DATABASE IF NOT EXISTS $dbName CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci;"
Invoke-RootSql "CREATE USER IF NOT EXISTS '$dbUser'@'localhost' IDENTIFIED BY '$dbPass';"
Invoke-RootSql "GRANT ALL PRIVILEGES ON $dbName.* TO '$dbUser'@'localhost'; FLUSH PRIVILEGES;"

Write-Host "Applying database/schema.sql ..."
Get-Content -LiteralPath (Join-Path $ProjectRoot "database\schema.sql") -Raw -Encoding UTF8 |
    & $mysql -u root --password=$RootPassword $dbName
if ($LASTEXITCODE -ne 0) { throw "schema.sql failed" }

Write-Host "Applying database/indexes.sql ..."
Get-Content -LiteralPath (Join-Path $ProjectRoot "database\indexes.sql") -Raw -Encoding UTF8 |
    & $mysql -u root --password=$RootPassword $dbName
if ($LASTEXITCODE -ne 0) { throw "indexes.sql failed" }

if (Test-Path (Join-Path $ProjectRoot "database\procedures.sql")) {
    Write-Host "Applying database/procedures.sql ..."
    Get-Content -LiteralPath (Join-Path $ProjectRoot "database\procedures.sql") -Raw -Encoding UTF8 |
        & $mysql -u root --password=$RootPassword $dbName
    if ($LASTEXITCODE -ne 0) { throw "procedures.sql failed" }
}

if (Test-Path (Join-Path $ProjectRoot "database\triggers.sql")) {
    Write-Host "Applying database/triggers.sql ..."
    Get-Content -LiteralPath (Join-Path $ProjectRoot "database\triggers.sql") -Raw -Encoding UTF8 |
        & $mysql -u root --password=$RootPassword $dbName
    if ($LASTEXITCODE -ne 0) { throw "triggers.sql failed" }
}

$venvPython = Join-Path $ProjectRoot ".venv\Scripts\python.exe"
if (-not (Test-Path $venvPython)) {
    Write-Error "Missing $venvPython - run: python -m venv .venv ; .\.venv\Scripts\pip install -r requirements.txt"
}

Write-Host "Django migrate ..."
& $venvPython (Join-Path $ProjectRoot "manage.py") migrate --noinput

Write-Host "Loading CSVs (this can take 1-2 minutes) ..."
& $venvPython (Join-Path $ProjectRoot "scripts\load_f1_csv.py")

Write-Host ""
Write-Host "Setup complete. Run: .\.venv\Scripts\python manage.py runserver"
Write-Host "Then open http://127.0.0.1:8000/ - create a superuser: .\.venv\Scripts\python manage.py createsuperuser"
