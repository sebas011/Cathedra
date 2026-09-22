param(
  [switch]$SkipFrontendBuild,
  [switch]$Console
)

$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
$backendPython = Join-Path $projectRoot 'backend\.venv\Scripts\python.exe'
$frontendDirectory = Join-Path $projectRoot 'frontend'
$releaseDirectory = Join-Path $PSScriptRoot 'release'
$buildDirectory = Join-Path $PSScriptRoot 'build'
$applicationName = if ($Console) { 'Cathedra-Diagnostic' } else { 'Cathedra' }
$windowMode = if ($Console) { '--console' } else { '--noconsole' }

if (-not (Test-Path -LiteralPath $backendPython)) {
  throw 'Create the backend virtual environment before building the desktop release.'
}

if (-not $SkipFrontendBuild) {
  Push-Location $frontendDirectory
  try {
    npm run build
  } finally {
    Pop-Location
  }
}

& $backendPython -m pip install -r (Join-Path $PSScriptRoot 'requirements-build.txt')
& $backendPython -m PyInstaller `
  --noconfirm `
  --clean `
  $windowMode `
  --onedir `
  --name $applicationName `
  --distpath $releaseDirectory `
  --workpath $buildDirectory `
  --specpath $PSScriptRoot `
  --paths (Join-Path $projectRoot 'backend') `
  --add-data "$(Join-Path $projectRoot 'frontend\dist');frontend\dist" `
  --add-data "$(Join-Path $projectRoot 'backend\scholardesk_v2_dev.db');backend" `
  (Join-Path $PSScriptRoot 'run_cathedra.py')

Write-Host "Desktop release created at: $(Join-Path $releaseDirectory "$applicationName\$applicationName.exe")"
