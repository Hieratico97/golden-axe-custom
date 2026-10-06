$ErrorActionPreference = 'Stop'
& "$PSScriptRoot/Build.ps1" -Baseline
& "$PSScriptRoot/Build.ps1"
& python "$PSScriptRoot/scripts/rom.py" patch "$PSScriptRoot/build/baseline/golden-axe.bin" "$PSScriptRoot/build/custom/golden-axe.bin" "$PSScriptRoot/build/golden-axe-custom.ips"
if ($LASTEXITCODE -ne 0) { throw 'Patch export failed' }
