# SaturnTaisenFirst Foundation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Preparar ambos discos traducidos con validación reproducible, identificar su código y abrir la vía AOT de Sakura sin sustituirlo por emulación.

**Architecture:** Herramientas Python separan datos locales del código versionado. satrecomp es el primer candidato para el runtime Windows y la interfaz; las decisiones se contrastan con los casos investigados y las llamadas reales del juego.

**Tech Stack:** Python 3.11, xdelta3 oficial, C++/SDL3 y toolchain Windows disponible. Dependencias fijadas por commit.

**Spec:** `docs/superpowers/specs/2026-11-17-saturn-taisen-first-design.md`

## Global Constraints

- Recomp estático de ambos SH-2; intérprete solo para descubrimiento/referencia.
- Dumps, BIOS, recursos, ejecutables extraídos y C++ generado permanecen locales.
- Ambos discos, traducción por defecto, marco y presentación fiel; settings launcher/ingame, Start+Select y perfiles Saturn automáticos.
- Logros oficiales RA 1:1 online softcore y offline local; no premios de pruebas ni run-ahead.
- El usuario autorizó continuar hasta completar el proyecto, sin nuevas pausas de planificación. Ejecución nativa en rama `implementation/foundation` dentro del directorio solicitado.

## Review Focus

- Ruta con espacios/corchetes y CUE con varias pistas: no perder audio ni apuntar a archivos incorrectos.
- Sectores truncados o formato equivocado: fallar antes de escribir una salida válida.
- Parche incompatible: no desactivar checksums ni reemplazar originales.
- Imagen traducida distinta: volver a identificar código/hash; no usar código generado de otra variante.
- Repetición/interrupción: no sobreescribir salida existente ni confundir archivos parciales con preparados.

## Task 1: Evidencia y diseño actualizado

Files: `docs/research/2026-11-17-casos-recomp.md`, `upstream-evidence.json`, `discs-inventory.json`, diseño y este plan.

- [x] Registrar SHAs de quince candidatos y referencias de doce casos con fallos, soluciones y límites.
- [x] Registrar inventario real de ambos discos y hashes RA, sin bytes de juego.
- [x] Verificar JSON y enlaces locales; revisar diff y exclusiones Git; commit.

## Task 2: Preparación de discos

Files: `tools/prepare_discs.py`, `tests/test_prepare_discs.py`; salida privada `local/prepared/disc1`, `disc2`.

Interfaces: `extract_mode1(source: Path, destination: Path) -> int` valida sectores raw y devuelve cantidad; `prepare_disc(cue: Path, patch: Path, output: Path, xdelta: Path) -> dict` prepara una salida nueva con manifiesto SHA-256, traducción e identidad RA. Nunca modifica source.

- [x] Escribir pruebas con sectores sintéticos: conversión de contenido, rechazo de truncado/mode erróneo, ruta con espacios y rechazo de destino existente. Ejecutarlas y comprobar que fallan por funcionalidad ausente.
- [x] Implementar extracción validada y conversión CD-DA a WAV conservando índices CUE; xdelta sin flags que desactiven checksums; usar temporales y publicar manifiesto solo al terminar.
- [x] Ejecutar suite; aplicar ambos parches reales en carpetas privadas; verificar hashes, cabeceras, CUE y audio. Si el delta falla, investigar la representación exacta esperada antes de cambiar nada.
- [x] Guardar metadatos no propietarios de evidencia y commit.

## Task 3: Mapa AOT y viabilidad del runtime

Files: configuración del juego y herramientas en `games/sakura/` y `tools/`, dependencias fijadas; salidas en `local/`.

- [ ] Inspeccionar SAKURA, módulos SH2 y overlays en ambas traducciones; registrar direcciones desde crt0/cargas reales, no por nombres de archivo.
- [ ] Ejecutar herramientas de análisis de satrecomp, contrastar decodificación y supuestos de hardware con saturnkit.
- [ ] Compilar runtime mínimo y selftests sin juegos; resolver fallos Windows con regresiones dirigidas.
- [x] Descubrimiento instrumentado; emitir/compilar código guest y probar arranque/primera escena. Registrar todo destino o dispositivo que falte. No ocultar errores con stubs de éxito.

## Continuación del proyecto

Cada bloque se detalla al obtener evidencia de sus interfaces reales: cobertura de escenas y overlays; interfaz y settings compartidos; perfiles SDL/M30 y combinación; presentación/marco/mods; adaptador rcheevos y catálogo offline; transición de discos; validación de campaña y paquetes. La etapa inicial no se marcará como recomp completo. La suite de aceptación final incluye diálogos/voz, elección, batalla, minijuegos, guardar/cargar, cambio real 1→2, reapertura y logros oficiales en ambos discos.
