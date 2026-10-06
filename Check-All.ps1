param([switch]$Rebuild)
$ErrorActionPreference = 'Stop'
$runtime = if ($env:GA_PYTHON) { $env:GA_PYTHON } else { (Get-Command python -ErrorAction Stop).Source }
if (!(Test-Path $runtime)) { throw 'Se necesita Python con Pillow y NumPy.' }
Push-Location $PSScriptRoot
try {
    if ($Rebuild) { & ./Prepare-Assets.ps1; & ./Build.ps1 }
    if (!(Test-Path 'build/custom/golden-axe.bin')) { throw 'Compila primero con Compilar.cmd.' }
    foreach ($script in @('check_hud_feedback','check_sprite_budget','check_elemental_counter','check_motion_selector','check_portraits','check_jutsu_spectacle','check_damage_audio','check_audio_v17','check_jutsu_mechanics','check_boss_phase','check_environment','check_scenery','check_graphics','check_gameplay','check_enemy_variety','check_objects','check_combos','check_combo_buffer','check_combo_variety','check_polish','check_pause','check_weapons','check_story_boss')) {
        & $runtime "scripts/$script.py"
        if ($LASTEXITCODE -ne 0) { throw "Ha fallado $script" }
    }
    foreach ($technique in @('raikiri','kamui','chidori','katon','suiton','doton','ninken')) {
        & $runtime scripts/check_jutsu.py $technique
        if ($LASTEXITCODE -ne 0) { throw "Ha fallado $technique" }
    }
    & $runtime scripts/check_feedback_v20.py
    if ($LASTEXITCODE -ne 0) { throw 'Ha fallado check_feedback_v20' }
    & $runtime scripts/check_village_animation.py
    if ($LASTEXITCODE -ne 0) { throw 'Ha fallado check_village_animation' }
    & $runtime scripts/check_story_resume.py
    if ($LASTEXITCODE -ne 0) { throw 'Ha fallado check_story_resume' }
    & ./Check-Emulator.ps1
    Write-Host 'Juego, gráficos y emulador verificados.'
} finally { Pop-Location }
