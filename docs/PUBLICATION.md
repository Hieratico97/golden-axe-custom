# Política de publicación

La copia pública se exportó desde la última versión local estable, v0.29, utilizando una lista permitida. El directorio de trabajo completo, sus respaldos y el historial de otros proyectos no se publican.

## Material excluido

ROMs, IPS con recursos omitidos, desensamblado original, fuentes regeneradas que lo incorporan, arte y generadores de la adaptación, guion, vídeos, audio capturado, capturas, referencias descargadas, ejecutables y dependencias de terceros. También se excluyen credenciales, contactos, rutas personales y enlaces privados de Drive.

La atribución a una obra o a un autor no sustituye a una autorización para redistribuir sus materiales. Por ello la copia publica herramientas y extensiones propias, y describe expresamente las dependencias ausentes.

## Añadir cambios

1. Mantener los recursos de prueba locales en las carpetas ignoradas.
2. Añadir solo archivos cuyo contenido completo se haya revisado.
3. Actualizar conscientemente la lista permitida de `.gitignore` si hace falta un archivo nuevo.
4. Ejecutar `python scripts/audit_public_tree.py` antes de crear un commit.
5. Revisar también el diff de Git. La detección por patrones complementa esa revisión.

Las pruebas que dependen de la ROM no se ejecutan durante la auditoría de publicación. Un fallo por falta de recursos no debe resolverse añadiendo el juego original, secretos o arte de terceros al repositorio.

## Historial

La primera publicación utiliza un historial nuevo con archivos ya seleccionados. Los materiales excluidos no se añaden primero para borrarlos después. Tampoco se incluyen en releases, Git LFS, adjuntos o enlaces privados en la documentación.

## Licencia y procedencia

MIT se aplica al código y a la documentación propios incluidos en esta publicación. El desensamblado utilizado localmente se atribuye a Lorenzo / lory1990; no se incluye. La distribución de referencia Golden Axe 32X Edition y sus materiales tampoco se incluyen. Los emuladores, ensambladores y editores conservan las licencias de sus proyectos.
