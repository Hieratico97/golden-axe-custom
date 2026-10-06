param([ValidateSet('kakashi','naruto','sasuke','sakura','ninja','anbu','renegado')][string]$Personaje='kakashi')
$ErrorActionPreference='Stop'
$editable=Join-Path $PSScriptRoot 'assets/editable'
New-Item -ItemType Directory -Path $editable -Force | Out-Null
$document=Join-Path $editable "$Personaje.ase"
if (!(Test-Path $document)) { Copy-Item (Join-Path $PSScriptRoot "assets/custom/$Personaje.ase") $document }
Start-Process -FilePath (Join-Path $PSScriptRoot 'tools/libresprite/libresprite.exe') -ArgumentList ('"'+$document+'"')
