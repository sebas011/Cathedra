<#
.SYNOPSIS
Safely replaces an installed Cathedra application folder with a new release.

.DESCRIPTION
Office records and backups are intentionally not stored in the application
folder.  This script never touches %LOCALAPPDATA%\Cathedra.  It first keeps a
timestamped copy of the current app folder beside the installation, so the
previous version can be restored if the new release cannot be used.
#>
param(
  [Parameter(Mandatory)]
  [ValidateNotNullOrEmpty()]
  [string]$NewReleaseFolder,

  [Parameter(Mandatory)]
  [ValidateNotNullOrEmpty()]
  [string]$InstalledFolder
)

$ErrorActionPreference = 'Stop'

function Resolve-ExistingDirectory([string]$Path, [string]$Label) {
  $item = Get-Item -LiteralPath $Path -ErrorAction Stop
  if (-not $item.PSIsContainer) {
    throw "$Label must be a folder."
  }
  return $item.FullName
}

$newRelease = Resolve-ExistingDirectory $NewReleaseFolder 'New release folder'
$installed = Resolve-ExistingDirectory $InstalledFolder 'Installed Cathedra folder'

if ($newRelease.TrimEnd('\') -ieq $installed.TrimEnd('\')) {
  throw 'The new release folder and installed folder must be different folders.'
}

if (-not (Test-Path -LiteralPath (Join-Path $newRelease 'Cathedra.exe'))) {
  throw 'The new release folder does not contain Cathedra.exe.'
}

if (Get-Process -Name 'Cathedra' -ErrorAction SilentlyContinue) {
  throw 'Close Cathedra before updating, then run this helper again.'
}

$parent = Split-Path -Parent $installed
$folderName = Split-Path -Leaf $installed
$stamp = Get-Date -Format 'yyyyMMdd-HHmmss'
$previous = Join-Path $parent "$folderName.previous-$stamp"

Write-Host 'Preparing the update. Your office data and backups will remain unchanged.'
Move-Item -LiteralPath $installed -Destination $previous

try {
  Copy-Item -LiteralPath $newRelease -Destination $installed -Recurse -Force
} catch {
  if (Test-Path -LiteralPath $installed) {
    Remove-Item -LiteralPath $installed -Recurse -Force
  }
  Move-Item -LiteralPath $previous -Destination $installed -ErrorAction SilentlyContinue
  throw "The update could not be copied. The prior application folder was restored. $($_.Exception.Message)"
}

Write-Host 'Update complete.'
Write-Host "Previous application version retained at: $previous"
Write-Host 'Launch Cathedra.exe from the installed folder. Your data remains in %LOCALAPPDATA%\Cathedra.'
