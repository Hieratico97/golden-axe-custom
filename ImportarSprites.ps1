param([ValidateSet('kakashi','naruto','sasuke','sakura','ninja','anbu','renegado')][string]$Personaje='kakashi')
$ErrorActionPreference='Stop'
$document=Join-Path $PSScriptRoot "assets/editable/$Personaje.ase"
if (!(Test-Path $document)) { throw 'Primero abre y guarda el personaje con EditarSprites.ps1.' }
$overrides=Join-Path $PSScriptRoot 'assets/overrides'
New-Item -ItemType Directory -Path $overrides -Force | Out-Null
& (Join-Path $PSScriptRoot 'tools/libresprite/libresprite.exe') --batch $document --sheet (Join-Path $overrides "$Personaje-sheet.png") --sheet-type horizontal
if ($LASTEXITCODE -ne 0) { throw 'LibreSprite no pudo exportar las poses.' }
& (Join-Path $PSScriptRoot 'Prepare-Assets.ps1')
& (Join-Path $PSScriptRoot 'Build.ps1')
