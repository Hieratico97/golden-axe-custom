$ErrorActionPreference = 'Stop'
if (!(Test-Path (Join-Path $PSScriptRoot 'scripts/prepare_custom.py'))) {
    throw 'El integrador y los generadores de arte están excluidos de la copia pública. Consulta README.md y docs/LOCAL_SETUP.md.'
}
$runtime = if ($env:GA_PYTHON) { $env:GA_PYTHON } else { (Get-Command python -ErrorAction Stop).Source }
if (!(Test-Path $runtime)) { throw 'Se necesita Python con Pillow y NumPy para preparar los recursos.' }
Push-Location $PSScriptRoot
try {
    & $runtime scripts/prepare_custom.py
    if ($LASTEXITCODE -ne 0) { throw 'No se pudieron convertir los recursos.' }
} finally { Pop-Location }
