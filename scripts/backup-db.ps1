# Sauvegarde PostgreSQL SGEP — Sprint 17
# Usage: .\scripts\backup-db.ps1

param(
    [string]$Host = "localhost",
    [string]$Port = "5432",
    [string]$User = "sgep",
    [string]$Database = "sgep_db",
    [string]$Password = $env:POSTGRES_PASSWORD
)

$ErrorActionPreference = "Stop"
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$backupDir = Join-Path $root "backend\backups"
New-Item -ItemType Directory -Force -Path $backupDir | Out-Null

$outFile = Join-Path $backupDir "sgep_$timestamp.sql"
$gzFile = "$outFile.gz"

if (-not $Password) {
    $Password = "sgep_dev_password"
}

$env:PGPASSWORD = $Password
& pg_dump -h $Host -p $Port -U $User -d $Database -F p -f $outFile

if ($LASTEXITCODE -ne 0) {
    Write-Error "pg_dump a échoué"
}

Compress-Archive -Path $outFile -DestinationPath "$backupDir\sgep_$timestamp.zip" -Force
Remove-Item $outFile

Write-Host "Sauvegarde créée: $backupDir\sgep_$timestamp.zip"
