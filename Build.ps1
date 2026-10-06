param([switch]$Baseline)
$ErrorActionPreference = 'Stop'
$root = $PSScriptRoot
$target = if ($Baseline) { 'baseline' } else { 'custom' }
$inputDir = if ($Baseline) { Join-Path $root 'source' } else { Join-Path $root 'game' }
if (!(Test-Path (Join-Path $inputDir 'ga.asm'))) {
    throw 'Esta copia pública omite el motor y los recursos del juego. Consulta el principio de README.md y docs/LOCAL_SETUP.md.'
}
$outputDir = Join-Path $root "build/$target"
New-Item -ItemType Directory -Path $outputDir -Force | Out-Null
# Build in a temporary staging directory so stale assembler files cannot mask failures.
$stage = Join-Path $outputDir ([guid]::NewGuid().ToString())
New-Item -ItemType Directory -Path $stage | Out-Null
Copy-Item (Join-Path $inputDir '*.asm') -Destination $stage
if (!$Baseline -and (Test-Path (Join-Path $root 'assets/custom'))) {
    Copy-Item (Join-Path $root 'assets/custom') -Destination (Join-Path $stage 'custom') -Recurse
}
$oldMessages = $env:AS_MSGPATH
$oldAnsi = $env:USEANSI
Push-Location $stage
try {
    $env:AS_MSGPATH = Join-Path $root 'source/AS/win32'
    $env:USEANSI = 'n'
    & "$root/source/AS/win32/asw.exe" -xx -c -E -A ga.asm
    if ($LASTEXITCODE -ne 0 -or (Test-Path ga.log)) { throw "Assembly failed: $stage" }
    & "$root/source/AS/win32/gap2bin.exe" ga.p rom.bin ga.h
    if ($LASTEXITCODE -ne 0 -or !(Test-Path rom.bin)) { throw 'ROM conversion failed' }
    & python "$root/scripts/rom.py" finalize rom.bin
    if ($LASTEXITCODE -ne 0) { throw 'Invalid ROM' }
    if ($Baseline) {
        $hash = (Get-FileHash rom.bin -Algorithm SHA256).Hash.ToLowerInvariant()
        if ($hash -ne 'e9f5340ecf8151253eb6fcda136c4d4d8940e373340ce2eeb2bf24f9f6c1004d') {
            throw "Baseline does not match the expected original: $hash"
        }
    }
    Copy-Item rom.bin (Join-Path $outputDir 'golden-axe.bin') -Force
    Write-Host "ROM ready: $outputDir/golden-axe.bin"
} finally {
    Pop-Location
    $env:AS_MSGPATH = $oldMessages
    $env:USEANSI = $oldAnsi
}
