<h1 align="center">🌸 SaturnTaisenFirst</h1>
<p align="center"><strong>Sakura Wars / Sakura Taisen · Sega Saturn</strong><br>Recompilación estática para Windows x64</p>
<p align="center">
  <a href="https://github.com/MatyMeatBoy/SaturnTaisenFirst/releases"><img alt="Versión 0.1.5 checkpoint" src="https://img.shields.io/badge/versi%C3%B3n-0.1.5_checkpoint-9a4564?style=flat-square"></a>
  <img alt="Plataforma Windows x64" src="https://img.shields.io/badge/plataforma-Windows_x64-77445b?style=flat-square">
  <a href="docs/research/runtime-validation.json"><img alt="SH-2: AOT estática" src="https://img.shields.io/badge/SH--2-AOT_est%C3%A1tica-bf914d?style=flat-square"></a>
  <a href="LICENSE"><img alt="Licencia GPL-3.0-only" src="https://img.shields.io/badge/licencia-GPL--3.0--only-5d755d?style=flat-square"></a>
  <img alt="Estado: desarrollo" src="https://img.shields.io/badge/estado-en_desarrollo-d1a0ad?style=flat-square">
</p>

Un regreso al Teatro Imperial con los píxeles de Saturn, una presentación cuidada y la traducción inglesa suministrada por el propietario. Repositorio privado de **MatyMeatBoy**.

**v0.1.5 es un checkpoint de desarrollo hacia v0.2.** Añade selección Original/Mejorado, composición panorámica por capas, menú Sakura a resolución de ventana y fuente nítida opcional. Se han generado extensiones decorativas preliminares para las 20 variantes Saturn y las 19 de PC. Las de PC no se activan en el paquete v0.1.5; su integración continúa en la rama de desarrollo. Su presencia no implica que la versión PC, su traducción o el pack HD completo sean jugables. Consulta las [notas del checkpoint](docs/releases/v0.1.5.md).

La rama continúa en **0.2.0-dev** después del checkpoint. La carga experimental de fondos PC compatibles está disponible por CLI; la importación de medios PC desde la interfaz y el resto del pack HD siguen pendientes.

**v0.1 es una versión de desarrollo.** Están verificados el arranque, 119.781 fotogramas continuos de exploración AOT, guardado/carga del episodio 1 y cargas de partidas públicas del episodio 8 y Finale en el disco 2. La entrada al primer combate coincide con la referencia durante 3.001 frames repetidos, y 9.001 más llegan a su primer campo jugable en AOT. La campaña completa, todas las batallas y la transición automática real de discos todavía no están validadas.

El launcher usa una temática de cerezos inspirada en NewSnapRecomp, solo la captura local de la pantalla de título e importación de partidas en copias separadas. El juego se centra con **escala entera y nearest**, con un marco adaptable. [Notas de la v0.1](docs/releases/0.1.md) · [Diseño](docs/superpowers/specs/2026-11-17-v01-launcher.md) · [Validación](docs/research/runtime-validation.json) · [Formatos de partidas](docs/research/save-import.md).

## Objetivos confirmados

- Recompilar el código SH-2 a código nativo; mantener las funciones necesarias del hardware en un runtime.
- Incorporar localmente los dos discos y la traducción inglesa.
- Integrar la transición entre discos y conservar las partidas.
- Escalar únicamente en enteros, conservar los píxeles originales y rellenar el espacio restante con un marco adaptable.
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

La base de bloques y los C++ generados no se incluyen en Git; cada desarrollador debe generarlos desde sus imágenes. El launcher nativo se construye con `python tools/build_launcher.py`; la transición automática de discos sigue pendiente. `tests/theater.movie` recorre la narración inicial con pulsaciones de A hasta el mapa del teatro; no cubre las ramas, las batallas ni la campaña completa. La preparación japonesa está disponible con `prepare_discs.py --original --cue ... --output ...`; su cobertura AOT y el selector de idioma aún se están integrando. Los avisos del runtime sobre hardware o composición no se consideran resueltos por el simple hecho de que arranque.

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
