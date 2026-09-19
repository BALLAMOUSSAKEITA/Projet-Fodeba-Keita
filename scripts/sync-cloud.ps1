# Synchronisation cloud (architecture hybride) — sauvegarde vers serveur distant
# Configurez CLOUD_SYNC_* dans .env.production
# Usage: .\scripts\sync-cloud.ps1

param(
    [string]$EnvFile = ".env.production"
)

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $root

if (Test-Path $EnvFile) {
    Get-Content $EnvFile | ForEach-Object {
        if ($_ -match '^\s*([^#][^=]+)=(.*)$') {
            [System.Environment]::SetEnvironmentVariable($matches[1].Trim(), $matches[2].Trim())
        }
    }
}

if ($env:CLOUD_SYNC_ENABLED -ne "true") {
    Write-Host "Sync cloud désactivée (CLOUD_SYNC_ENABLED=false)."
    Write-Host "Activez-la dans .env.production pour synchroniser les sauvegardes."
    exit 0
}

Write-Host "=== Sauvegarde locale ==="
& "$root\scripts\backup-db.ps1"

$backupDir = Join-Path $root "backend\backups"
$latest = Get-ChildItem $backupDir -Filter "sgep_*.zip" | Sort-Object LastWriteTime -Descending | Select-Object -First 1
if (-not $latest) {
    Write-Error "Aucune sauvegarde trouvée."
}

$remote = "$($env:CLOUD_SYNC_USER)@$($env:CLOUD_SYNC_HOST):$($env:CLOUD_SYNC_PATH)/"
Write-Host "=== Envoi vers $remote ==="
scp $latest.FullName "${remote}sgep_latest.zip"
Write-Host "Synchronisation terminée."
