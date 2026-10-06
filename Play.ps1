param([switch]$Baseline)
$ErrorActionPreference = 'Stop'
$target = if ($Baseline) { 'baseline' } else { 'custom' }
$rom = Join-Path $PSScriptRoot "build/$target/golden-axe.bin"
if (!(Test-Path $rom)) {
    if ($Baseline) { & "$PSScriptRoot/Build.ps1" -Baseline } else { & "$PSScriptRoot/Build.ps1" }
}
$emulatorDir = Join-Path $PSScriptRoot 'tools/emulator/blastem-win32-0.6.2'
# Interactive emulator requested for playing and testing the project.
Start-Process -FilePath "$emulatorDir/blastem.exe" -ArgumentList @('"' + $rom + '"') -WorkingDirectory $emulatorDir -WindowStyle Normal
