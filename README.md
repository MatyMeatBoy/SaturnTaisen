# SaturnTaisenFirst

Proyecto de recompilación estática de **Sakura Taisen / Sakura Wars 1 para Sega Saturn**, con la traducción inglesa suministrada por el propietario del proyecto.

**Estado:** implementación inicial. Ambos discos ingleses están preparados localmente y sus hashes coinciden con RetroAchievements. Hay un ejecutable Windows de investigación: 119.781 fotogramas continuos de exploración en AOT estricto, y guardado del episodio 1 con carga desde un arranque nuevo verificada. Todavía no es un recomp completo ni se ha validado la campaña.

## Objetivos confirmados

- Recompilar el código SH-2 a código nativo; mantener las funciones necesarias del hardware en un runtime.
- Incorporar localmente los dos discos y la traducción inglesa.
- Integrar la transición entre discos y conservar las partidas.
- Conservar la proporción original, maximizar una presentación nítida y rellenar el espacio restante con un marco.
- Repositorio privado bajo MatyMeatBoy.
- Ajustes compartidos entre launcher y menú ingame (Start + Select).
- Mandos generales y perfiles automáticos Saturn para modelos reconocidos, incluidos M30.
- Logros oficiales RetroAchievements 1:1, online softcore y offline local, con pestaña y avisos con badge.
- Traducción y mods compatibles instalados activados por defecto, con interruptores individuales.

Los dumps, BIOS, parches binarios, recursos extraídos, código generado del juego y partidas se mantienen locales y fuera del repositorio.

## Documentación

- [Investigación y referencias](docs/research/2026-11-17-investigacion.md)
- [Catálogo verificable de proyectos](docs/research/projects.json)
- [Diseño propuesto](docs/superpowers/specs/2026-11-17-saturn-taisen-first-design.md)
- [Problemas resueltos en doce recompilaciones y su aplicación](docs/research/2026-11-17-casos-recomp.md)
- [Plan y alcance de la primera etapa](docs/superpowers/plans/2026-11-17-foundation.md)

## Desarrollo local

Python 3.11+, Git, CMake/Ninja/Clang y SDL3. En esta máquina se usa MSYS2 CLANG64 en `C:/msys64/clang64`; puede indicarse otro prefijo mediante `--toolchain`. La dependencia satrecomp se fija por commit y se le aplican parches revisables; sigue su licencia GPL-3.0-only.

```powershell
python -m unittest discover -s tests -v
python tools/build_runtime.py check-disc
python tools/build_runtime.py check-video
python tools/build_runtime.py check-machine
python tools/build_runtime.py build
python tools/build_runtime.py discover --frames 30000 --movie tests/theater.movie
python tools/build_runtime.py recompile
python tools/build_runtime.py run
```

`discover` utiliza interpretación exclusivamente para obtener cobertura. El ejecutable y `run` usan AOT estricto por defecto: se detienen si necesitan interpretar una instrucción SH-2 guest. Las funciones agrupadas y el enlace de llamadas host requieren habilitación experimental explícita; la ruta validada usa el despachador de bloques. Los servicios de hardware/BIOS reimplementados y el 68000 de audio son partes separadas del runtime.

La base de bloques y los C++ generados no se incluyen en Git; cada desarrollador debe generarlos desde sus imágenes. Los comandos actuales son herramientas de desarrollo, no el launcher final ni la transición de discos. `tests/theater.movie` recorre la narración inicial con pulsaciones de A hasta el mapa del teatro; no cubre las ramas, las batallas ni la campaña completa. La preparación japonesa está disponible con `prepare_discs.py --original --cue ... --output ...`; su cobertura AOT y el selector de idioma aún se están integrando. Los avisos del runtime sobre hardware o composición no se consideran resueltos por el simple hecho de que arranque.

Las comprobaciones sintéticas de vídeo y máquina no necesitan dumps. Comprueban la composición de capas y sprites, búsquedas CD por pista/FAD, invalidación de sectores al cambiar de lector y rechazo de servicios BIOS desconocidos en modo estricto. La comparación larga entre intérprete y AOT se ejecuta así:

```powershell
python tools/verify_runtime.py --frames 30000 --movie tests/theater.movie --timeout 600
```

El analizador complementario puede leer directamente el programa inicial de una ISO preparada:

```powershell
python tools/static_program.py --disc-iso "local/prepared/disc1/Track 01.iso" --output local/work/sakura/static-disc1.txt
```

`--all-entries` conserva además los prefijos válidos de todas las direcciones alineadas; produce muchos más candidatos y aumenta el tiempo y tamaño de compilación. Sigue punteros, llamadas y ramas, y reconoce tablas de salto relativas con una comprobación de rango. Su salida contiene código derivado del juego y debe permanecer local. Son candidatos adicionales: todavía hacen falta descubrimiento de otros saltos indirectos y overlays, comprobación de bytes en el runtime y pruebas de las rutas reales.

Las pruebas con estos discos corresponden al runtime adaptado de satrecomp y están detalladas en `docs/research/runtime-validation.json`. Los demás proyectos se consultan como referencias de código; su existencia o las afirmaciones de sus autores no prueban que Sakura Taisen completo funcione.

El generador conserva las posiciones de los bloques en `local/work/sakura/block-order.json` para añadir cobertura sin reescribir archivos C++ anteriores. El manifiesto rechaza variantes retiradas o cambios de partición; otra base requiere un directorio y manifiesto nuevos. Sigue siendo necesario comprobar los bytes guest durante la ejecución.

Para contrastar la carga de una partida propia del episodio 1 (archivo 1 en la pausa), el verificador puede iniciar cada modo con una copia independiente de la misma memoria nativa de 32 KiB:

```powershell
python tools/verify_runtime.py --frames 9098 --movie tests/cold-load.movie --backup-seed "ruta/al/backup.bin" --timeout 240
```

La imagen de origen se lee y se registra mediante SHA-256; cada ejecución modifica su propia copia privada. Los estados de investigación también necesitan conservar la memoria de guardado de su sesión.
