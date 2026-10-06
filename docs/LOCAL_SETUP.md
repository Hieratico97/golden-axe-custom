# Requisitos locales y componentes omitidos

La publicación no permite construir el juego completo. Instalar Python y un emulador no recupera los archivos excluidos.

## Herramientas propias que funcionan sin el juego

- `scripts/audit_public_tree.py`: comprueba los archivos destinados a publicación.
- `scripts/check_local_requirements.py`: informa de dependencias locales ausentes.
- `scripts/rom.py`: opera sobre imágenes que el usuario proporciona localmente. Su comando `patch` crea un archivo privado; no implica permiso para publicarlo.
- `scripts/audio_score.py`: construye tablas de composiciones y efectos sintetizados propios; no contiene muestras grabadas de la serie.

## Pruebas y ejecución del proyecto local

| Requisito | Ruta esperada por las herramientas |
| --- | --- |
| ROM propia de prueba compatible con los módulos | `build/custom/golden-axe.bin` |
| Desensamblado e integrador omitidos | `source/ga.asm`, `source/ga.macrosetup.asm`, `scripts/prepare_custom.py` y generadores enumerados en `omitted-scripts.json` |
| Gráficos y recursos locales completos | `assets/generated/`, `assets/custom/`, `assets/reference/` |
| Núcleo libretro de Windows | `tools/libretro/genesis_plus_gx_libretro.dll` |
| BlastEm portátil compatible con el wrapper | `tools/emulator/blastem-win32-0.6.2/blastem.exe` |
| Ensamblador y conversor compatibles con las fuentes locales | `source/AS/win32/asw.exe`, `source/AS/win32/gap2bin.exe` y sus archivos de soporte |

Los programas de terceros se instalan por separado y mantienen sus propias licencias. No se incluyen ejecutables. El código del frontend espera una DLL compatible con la arquitectura de Python.

```powershell
$env:GA_PYTHON = (Get-Command python).Source
python scripts/check_local_requirements.py --runtime
```

Después de completar una copia local autorizada, las pruebas se ejecutan con `Check-All.ps1`. No hay una ruta pública de descarga de ROMs, del integrador o del arte excluido.

## Montaje de vídeo

`make_development_video.py`, `make_development_video_60s.py` y `make_development_video_editorial.py` son fuentes del montaje, no vídeos publicados. Necesitan una grabación, audio y un informe de referencia locales. Se deben adaptar sus rutas de entrada a un material cuyo uso esté autorizado. Las variantes documentan la evolución de la composición hasta una pantalla dividida editorial de un minuto.

La tipografía de los montajes utiliza fuentes instaladas en Windows; esas fuentes no se redistribuyen.
