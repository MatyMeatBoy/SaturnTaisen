<h1 align="center">🌸 SaturnTaisenFirst</h1>
<p align="center"><strong>Sakura Wars / Sakura Taisen · Sega Saturn</strong><br>Recompilación estática SH-2 · Windows x64</p>
<p align="center">
  <a href="https://github.com/MatyMeatBoy/SaturnTaisenFirst/releases/tag/v0.2.0-test.2"><img alt="v0.2.0-test.2 de prueba" src="https://img.shields.io/badge/release-v0.2.0--test.2-9a4564?style=flat-square"></a>
  <img alt="Windows x64 portátil" src="https://img.shields.io/badge/Windows-x64_portable-77445b?style=flat-square">
  <a href="docs/research/chapter1-battle-progress.md"><img alt="SH-2 AOT estática" src="https://img.shields.io/badge/SH--2-AOT_est%C3%A1tica-bf914d?style=flat-square"></a>
  <a href="docs/releases/v0.2.0-test.2.md"><img alt="Validación local documentada" src="https://img.shields.io/badge/pruebas-informe_local-5d755d?style=flat-square"></a>
  <a href="https://github.com/MatyMeatBoy/OptiPort"><img alt="Método OptiPort" src="https://img.shields.io/badge/m%C3%A9todo-OptiPort-617b91?style=flat-square"></a>
  <a href="LICENSE"><img alt="GPL-3.0-only" src="https://img.shields.io/badge/licencia-GPL--3.0--only-646464?style=flat-square"></a>
</p>

Un regreso al Teatro Imperial con el código SH-2 recompilado, píxeles enteros y mejoras opcionales de presentación. Proyecto público de **MatyMeatBoy**.

**La v0.2.0-test.2 es una prerelease de prueba, no el juego completo certificado.** Incluye nuevas correcciones de transiciones, texto HD de elecciones y el checkpoint de201 retratos preparados, con los límites documentados. No está verificado todavía el capítulo 1 de principio a fin ni la campaña completa. [Alcance de esta entrega](docs/releases/v0.2.0-test.2.md). Los paquetes [v0.1.2](docs/releases/v0.1.2.md) y [v0.1.5](docs/releases/v0.1.5.md) se conservan intactos.

## Jugar

Extrae el release de Windows en una carpeta con permiso de escritura y abre **Jugar.bat**. Las DLL y el importador de partidas van incluidos: para jugar no necesitas instalar Python, MSYS2, compiladores ni SDK. Esta build arranca sin BIOS externa.

El release normal de Git **no incluye discos, BIOS, traducciones binarias, partidas ni recursos PC originales**. Usa tus propios discos traducidos. El paquete personal de traslado del propietario es independiente y no se publica: contiene la build, solo su disco1 inglés y el HD procesado, ya colocado para la detección automática.

El juego final se plantea **unificado y con importación obligatoria de ambos discos**. La prueba personal de un disco no certifica esa transición ni sustituye el trabajo pendiente del importador final.

## Presentación y controles

| Opción | Comportamiento |
|---|---|
| Original | Conserva la composición Saturn y la escala entera del raster original. |
| Mejorado | Recompone escenas reconocidas, con máximo 16:9 y fallback original. |
| Visualización Original | Imagen y diálogo mantienen una escala conjunta. |
| Visualización Zoom | Imagen y diálogo usan escalas enteras independientes según lo que cabe; sombra detrás del diálogo. |
| Texto HD | Fuente opcional con proporciones uniformes y avance nativo, recortada al interior de la caja. |
| Mod HD | Fondos y retratos compatibles; puede usar un pack ya procesado sin instalación PC. |
| Precarga HD | Carga los recursos habilitados antes de jugar; opcional y con mayor uso de memoria. |
| Mandos | SDL3 y reasignación; perfiles M30 Bluetooth/2.4G, con selección manual cuando XInput oculta el modelo. |

Los píxeles se escalan con nearest y multiplicadores enteros. La salida conserva el raster cuadrado; no se aplica una corrección de aspecto fraccional. En superficies más anchas se centra el área16:9, sin modo ultrawide. El marco queda fuera del contenido jugable.

**F11** cambia pantalla completa. **Esc/F1** o **Start+Select/Back** abre ajustes. Launcher y juego comparten la configuración; el launcher se cierra tras confirmar el primer frame listo. **Ver logs.bat** abre los diagnósticos. La importación de partidas trabaja con copias, sin modificar las fuentes.

## Estado verificable

| Área | Estado y evidencia |
|---|---|
| Arranque y AOT | Arranque desde cero y rutas probadas sin intérprete SH-2 guest. |
| Exploración | 119.781 frames continuos de una ruta de exploración; no equivale a capítulo completo. |
| Guardado/carga | Puntos concretos del episodio 1 y partidas de investigación; campaña y cambio real de disco pendientes. |
| Combate | Tutorial, movimiento, defensa y ataques Sakura/Sumire probados. Submenús separados en Mejorado; las pruebas AOT/intérprete del SDK no certifican victoria ni campaña. |
| HD | Fondos y retratos integrados con validación y fallback. Cuerpos/poses/expresiones completos pendientes. |
| PixelGen v1 | Franja derecha Stage01 integrada y anclada al scroll del mundo; cámara y sprites comprobados en rutas concretas. |
| Táctico16:9/HUD | Stage01 habilitado en Mejorado y menús corregidos. Otros escenarios, HUD completo y batalla entera siguen pendientes. |
| RetroAchievements | Pendiente: no se anuncian logros online/offline como disponibles. |
| PC | Se usan recursos para el mod Saturn; ejecución y traducción de la versión PC aparcadas. |

Las fuentes PC de cuerpos conservarán una sola escala basada en altura, con el eje de cabeza/torso alineado al original; no se deformarán para llenar una caja. La compatibilidad física de todos los firmwares M30 y la RX 6900 XT del equipo de destino requieren comprobación allí.

[Progresión y combate](docs/research/chapter1-battle-progress.md) · [Mandos M30](docs/research/m30-controller-profiles.md) · [PixelGen v1](docs/research/pixelgen-v1.md) · [Guardados](docs/research/save-import.md)

<!-- BEGIN HD PROGRESS -->

## Progreso HD

[![Retratos HD preparados](https://img.shields.io/badge/Retratos_HD_preparados-201%2F304%20%2866.1%25%29-9a4564?style=flat-square)](docs/HD_PROGRESS.md) [![Fondos KABE preparados](https://img.shields.io/badge/Fondos_KABE_preparados-19%2F19%20%28100%25%29-5d755d?style=flat-square)](docs/HD_PROGRESS.md) [![HD global verificado](https://img.shields.io/badge/HD_global-Indeterminado-646464?style=flat-square)](docs/HD_PROGRESS.md)

**Objetivo global: 100% verificado. Estado: Indeterminado.**

| Área | Preparado | Verificado en juego |
| --- | --- | --- |
| Retratos y animación | 201/304 (66,1%) | Sin dato |
| Vídeos | 0 | 0 |
| HUD y menús PC/Saturn | Sin dato | Sin dato |
| Fondos decorativos KABE | 19/19 (100%) | Sin dato |
| Personajes grandes NC | Sin dato | Sin dato |
| Escenas y transiciones | Sin dato | Sin dato |

[Inventario, alcance de los porcentajes y pendientes](docs/HD_PROGRESS.md).

<!-- END HD PROGRESS -->

## OptiPort y rendimiento

Aplicamos [OptiPort](https://github.com/MatyMeatBoy/OptiPort): reproducciones, comparaciones, cambios acotados y evidencia ligada al artefacto. Las badges describen tecnología, entrega y documentación; no son porcentajes de juego completado ni garantías de estabilidad universal.

La preparación CPU de 38 fondos pasó de2,102s con un trabajador a0,478s con ocho en la medición registrada; es preparación de recursos, **no una mejora demostrada del FPS ni de toda carga del juego**. Las texturas SDL se crean en el hilo del renderer. [Condiciones y límites](docs/research/saturn-background-workers.md).

## Desarrollo

Entrada para colaboradores: [pendientes actuales](docs/PENDIENTES.md) y [handoff técnico/artístico](docs/HANDOFF.md). Distinguen el trabajo local de las versiones entregadas y explican el método PixelGen v1, las pruebas y la coordinación entre bots.

Python 3.11+, Git, CMake/Ninja/Clang y SDL3. La dependencia satrecomp está fijada por commit y los cambios se distribuyen como patches reproducibles. Los dumps, estados, código generado y recursos propios permanecen en `local/`, fuera de Git.

```powershell
python -m unittest discover -s tests -v
python tools/build_runtime.py build
python tools/build_runtime.py recompile
python tools/build_launcher.py
```

El descubrimiento con intérprete se usa exclusivamente para investigar cobertura; la producción rechaza fallback SH-2. Los servicios BIOS/hardware reimplementados y el 68000 de audio son componentes separados del runtime. El conjunto de bloques candidatos no representa porcentaje de decompilación ni cobertura de campaña.

[Diseño](docs/superpowers/specs/2026-11-17-saturn-taisen-first-design.md) · [Board Saturn](docs/superpowers/plans/2026-11-17-saturn-priority.md) · [Referencias](docs/research/2026-11-17-investigacion.md) · [Licencias](THIRD_PARTY_NOTICES.md)
