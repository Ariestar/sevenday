#requires -version 5.1
<#
Purpose: Package the project into a clean zip for transfer on Windows (PowerShell).
- Excludes: .git, .venv, __pycache__, *.pyc, real secrets (.env, config/production.env, *.key, *.pem)
- Output: zq_match_backend_transfer.zip at repo root
Run:
  powershell -ExecutionPolicy Bypass -File .\scripts\package_transfer.ps1
#>

$ErrorActionPreference = 'Stop'

# Resolve repository root based on this script location
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RepoRoot = Resolve-Path (Join-Path $ScriptDir '..')
Set-Location $RepoRoot

$Stage = Join-Path $RepoRoot 'transfer_stage'
$ZipPath = Join-Path $RepoRoot 'zq_match_backend_transfer.zip'

# Clean previous
if (Test-Path $Stage) { Remove-Item -Recurse -Force $Stage }
if (Test-Path $ZipPath) { Remove-Item -Force $ZipPath }

New-Item -ItemType Directory -Force -Path $Stage | Out-Null

# Copy everything first (exclude the staging directory itself)
Write-Host 'Copying project files to staging...'
Get-ChildItem -Path $RepoRoot -Force | Where-Object { $_.Name -ne 'transfer_stage' } | ForEach-Object {
  $src = $_.FullName
  Write-Host "  -> $src"
  Copy-Item -Path $src -Destination $Stage -Recurse -Force
}

# Remove unwanted directories
$dirsToRemove = @('.git', '.venv', '__pycache__')
foreach ($name in $dirsToRemove) {
  Get-ChildItem -Path $Stage -Recurse -Directory -Filter $name -ErrorAction SilentlyContinue | ForEach-Object {
    Write-Host "Removing directory: $($_.FullName)"
    Remove-Item -Recurse -Force $_.FullName
  }
}

# Remove unwanted files (pyc)
Get-ChildItem -Path $Stage -Recurse -Include *.pyc -File -ErrorAction SilentlyContinue | Remove-Item -Force

# Remove sensitive files
$filesToRemove = @(
  '.env',
  'config/production.env'
)
foreach ($rel in $filesToRemove) {
  $full = Join-Path $Stage $rel
  if (Test-Path $full) {
    Write-Host "Removing sensitive file: $full"
    Remove-Item -Force $full
  }
}

# Remove key/cert files if any
Get-ChildItem -Path $Stage -Recurse -Include *.key,*.pem -File -ErrorAction SilentlyContinue | ForEach-Object {
  Write-Host "Removing key/cert file: $($_.FullName)"
  Remove-Item -Force $_.FullName
}

# Create zip
Write-Host "Creating ZIP: $ZipPath"
Compress-Archive -Path (Join-Path $Stage '*') -DestinationPath $ZipPath -Force

Write-Host 'Done.' -ForegroundColor Green
Write-Host "ZIP created at: $ZipPath" -ForegroundColor Green
