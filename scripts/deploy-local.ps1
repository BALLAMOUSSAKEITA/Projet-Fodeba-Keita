# Déploiement production — serveur local école Fodeba Keita
# Usage: .\scripts\deploy-local.ps1

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $root

if (-not (Test-Path ".env.production")) {
    Copy-Item ".env.production.example" ".env.production"
    Write-Host "Fichier .env.production créé — MODIFIEZ les mots de passe avant la mise en production."
}

Write-Host "=== Déploiement SGEP (production) ==="
docker compose -f docker-compose.prod.yml --env-file .env.production up -d --build

Write-Host ""
Write-Host "Services démarrés. Accès :"
$publicUrl = (Get-Content .env.production | Where-Object { $_ -match "^PUBLIC_URL=" }) -replace "PUBLIC_URL=", ""
if (-not $publicUrl) { $publicUrl = "http://localhost" }
Write-Host "  Application : $publicUrl"
Write-Host "  API docs    : $publicUrl/docs"
Write-Host ""
Write-Host "Monitoring (optionnel) :"
Write-Host "  docker compose -f docker-compose.prod.yml -f monitoring/docker-compose.monitoring.yml up -d"
