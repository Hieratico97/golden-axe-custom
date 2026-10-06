$ErrorActionPreference = 'Stop'
$rom = Join-Path $PSScriptRoot 'build/baseline/golden-axe.bin'
if (!(Test-Path $rom)) { & "$PSScriptRoot/Build.ps1" -Baseline }
& java -jar "$PSScriptRoot/reference-32x/tools/DataVis/target/DataVis.jar" -c "$PSScriptRoot/reference-32x/config/datavis.yaml" -o "$PSScriptRoot/assets/reference" $rom
if ($LASTEXITCODE -ne 0) { throw 'Graphics export failed' }
