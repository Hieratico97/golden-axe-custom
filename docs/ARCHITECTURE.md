# Arquitectura y alcance de los módulos

Las extensiones de `scripts/*-engine.asm` se escribieron para integrarse en un motor existente. Referencian símbolos y estados nativos que no se publican. No se ensamblan por separado y no sustituyen al desensamblado omitido.

| Archivo | Responsabilidad |
| --- | --- |
| `custom-engine.asm` | Arranque, despacho de entidades, flujo de fase, pausa y victoria. |
| `arcade-engine.asm` | Técnicas, costes, objetos, poses y rutinas de presentación del combate. |
| `combos-engine.asm`, `damage-engine.asm`, `motion-engine.asm` | Variantes de combo, reacciones y selección de movimiento. |
| `jutsu-impact-engine.asm`, `boss-phase-engine.asm` | Respuesta al contacto, interacciones de técnicas y otra fase del jefe. |
| `scene-engine.asm`, `scenery-engine.asm`, `village-animation-engine.asm` | Streaming de escenario y animación de detalles. |
| `sprite-trim-engine.asm` | Control conservador del presupuesto de sprites por línea. |
| `ui-engine.asm` | Presentación y feedback de interfaz. |
| `audio-engine.asm`, `audio_score.py` | Secuenciador 68000, timbres, notas y efectos FM/PSG propios. |
| `emulate.py` | Callbacks libretro, mando, captura, audio y lectura de memoria. |
| `playtest.py`, `check_*.py` | Navegación mediante controles y aserciones sobre estados observados. |
| `record_gameplay.py`, `review_*.py`, `diagnose_*.py` | Grabación, revisión de imágenes y diagnóstico. |
| `scene_stream.py` | Asignación offline de tiles y eventos reversibles de scroll. |
| `rom.py` | Cabecera, checksum y exportación de un IPS con comprobación byte a byte. |

## Restricciones de la consola

Los recursos locales se convierten a tiles de 8 × 8 y a las paletas del VDP. Los sprites grandes se dividen en piezas de hardware. Los efectos y actores comparten límites de transferencia y de dibujo por línea, por lo que una mejora visual puede introducir pausas, pérdidas de piezas o tapar al personaje.

El diagnóstico observa VRAM, tablas de sprites, estados de animación y muestras de audio. El frontend de pruebas usa entradas de mando; leer RAM para verificar no equivale a modificarla para forzar un resultado.

## Integración que falta

El integrador privado generaba tablas, empaquetaba recursos y aplicaba cambios al desensamblado. Se ha omitido porque mezcla arte de la adaptación y fragmentos del motor original. `story-engine.asm` y los generadores de personajes y escenarios también se han omitido. Sus nombres están enumerados en `omitted-scripts.json`.

En una adaptación nueva, los módulos deben integrarse con un motor y unos recursos cuya utilización y publicación estén autorizadas. Se deben recalcular símbolos, VRAM y layout; los offsets observados en el proyecto local no son una interfaz universal.
