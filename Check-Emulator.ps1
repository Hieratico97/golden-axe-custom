param([switch]$Baseline)
$ErrorActionPreference = 'Stop'
$target = if ($Baseline) { 'baseline' } else { 'custom' }
$rom = Join-Path $PSScriptRoot "build/$target/golden-axe.bin"
if (!(Test-Path $rom)) { throw 'Compile the ROM first with Build.ps1' }
$emulatorDir = Join-Path $PSScriptRoot 'tools/emulator/blastem-win32-0.6.2'
$romArgument = '"' + $rom + '"'
$process = Start-Process -FilePath "$emulatorDir/blastem.exe" -ArgumentList @('-b', '600', $romArgument) -WorkingDirectory $emulatorDir -WindowStyle Hidden -PassThru
if (!$process.WaitForExit(30000)) {
    $process.Kill()
    throw 'Emulator check timed out after 30 seconds'
}
if ($process.ExitCode -ne 0) { throw "Emulator failed: $($process.ExitCode)" }
$report = [ordered]@{ emulator = 'BlastEm 0.6.2'; frames = 600; exitCode = $process.ExitCode; romSHA256 = (Get-FileHash $rom -Algorithm SHA256).Hash.ToLowerInvariant() }
$report | ConvertTo-Json | Set-Content (Join-Path $PSScriptRoot "build/$target/emulator-check.json") -Encoding UTF8
Write-Host '600 frames completed; exit code 0.'
