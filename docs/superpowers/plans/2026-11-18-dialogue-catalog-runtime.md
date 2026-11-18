# Catálogo de diálogo en runtime — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox syntax for tracking.

**Goal:** Preparar el texto del guion una vez y vincularlo al framebuffer nativo antes de sustituir la reconstrucción dinámica de líneas.

**Architecture:** Caché inmutable por contenido exacto y testigo capturado con el framebuffer. La lectura acotada precede al parseo; el render conserva su lógica hasta completar las pruebas del observador.

**Tech Stack:** C++20, lectorDiscFiles, parserTBL existente, SDL y pruebas Clang/fixture privadas.

**Spec:** ../specs/2026-11-18-dialogue-catalog-runtime.md

## Global Constraints

- Solo recursos privados del usuario; ningún guion o dump aGit.
- Windowsx64; C++20; SDK/patches registrados antes de build_runtime.
- Original y Zoom aprobados intactos,16:9 máximo, escala entera.
- No alterar bytes guest, temporizadores, entradas ni reglas de texto.
- Todo cambio SDK se captura en un patch y se valida como árbol compuesto.

## Review Focus

- Tabla parcialmente sobrescrita durante una carga: no producir un testigo válido.
- Puntero fuera del texto o revisión de tabla distinta: no inferir registro por ID.
- Controles no interpretados o geometría fuera de4×31: conservar datos y marcar la preparación visual no admitida.
- Cambio de modo en el selector o pausa: cargar una vez y no introducir trabajo de disco por fotograma.
- Frame mostrado tras run-ahead o carga de estado: usar metadata del framebuffer, nunca RAM restaurada posteriormente.

### Task1: Caché pura y acotada

**Files:** SDKport/dialogue_preload.h; tests/test_dialogue_preload.cpp.

**Interfaces:** namespaceport, DialogueWitness{bool valid;uint32_t table,record,offset;}, PreloadedDialogueLine{uint32_t rawOffset;std::u32string text;}, PreloadedDialogueRecord{id,index,offset,prefix0,prefix1,raw,array4lines,lineCount,simple}, PreloadedDialogueTable{name,fingerprint,bytes,records}. DialoguePreload::Add(string,span<constuint8_t>), Seal(), Sealed(), TableCount(), RecordCount(), ReadyCount(), SourceBytes(), Tables(), Get(witness), Locate(low,high), todos los observadores const. Add devuelvebool; Locate devuelveDialogueWitness; Get devuelveconstPreloadedDialogueRecord*.

- [x] Test RED de tabla válida/CP1252/saltos/prefijos y registro señalado.
- [x] Implementar con parser existente,128tablas,8MiB de bytes fuente,65.535registros globales; impedir Add trasSeal y nombres duplicados. No truncar datos silenciosamente.
- [x] Precompilar hasta4filas/31columnas; conservar raw completo y marcar simple=false ante controles no admitidos. Tabulador permanece sin interpretar.
- [x] Locate exige ambos bancos1MiB, tabla exacta en low+0x24000 y punteroBE32 en high+0x6851C. Validar texto después de4bytes de prefijo y antes/incluyendo NUL; rechazar resultados ambiguos.
- [x] Tests GREEN de límites, revisión alterada, punteros inválidos, tabla truncada, final de cadena y Seal; guardar evidencia.

### Task2: Lectura y captura integradas

**Files:** SDKport/disc_files.h/.cpp, port/port.h, port/main.cpp, port/frontend_sdl.cpp; fixture de lectura.

**Interfaces:** DiscFiles::ReadBounded(name,data,maxBytes), Port::PrepareDialogueCatalog(knownAtlas), shared_ptr<constDialoguePreload> y fbDialogue; copia a shownDialogue bajo fbMutex. Preparación solo con atlas inglés verificado, presentaciónMejorada y textoHD.

- [x] Test RED para ReadBounded: tamaño superior al límite se rechaza antes de leer y deja data vacío; lectura válida y fallo parcial comprobados.
- [x] Leer TBL con presupuesto restante, compilar y sellar antes de publicar el catálogo. Registrar contadores/tiempo bajo SATRECOMP_DIALOGUE_TRACE; sin UI técnica nueva.
- [x] Capturar Locate() en callback de framebuffer propio y copiar testigo junto a softwareShown. No serializarlo con guest.
- [x] Prueba de catálogo real56/29.725,29.723preparables; controles2 conservados. Prueba de muestras conocidas Sumire/María/Iris y elecciones, y rechazo durante carga.
- [x] Comparar hashes/RGB yGUI antes/después, con Original sin precarga nueva. Verificar una sola preparación por sesión/cambio de modo, no una por frame.
- [x] Capturar patch0048, validar árbol compuesto y revisar antes de integrar. No declarar completoT11.

### Task3: Render desde las líneas precargadas

**Files:** frontend/UiTextLine y helper separado de máscara de revelado; coordinar propiedad antes de editar.

- [x] Probar máscara/celda esperada contra atlas y comandos del mismo framebuffer, sin adelantar letras ni borrar glifos desconocidos.
- [x] Usar vistas a líneas inmutables y la fuente ya precocinada; conservar posiciones, placas, color y clip aprobados.
- [x] Repetir revelado, avance,4filas, fundidos y entradas/salidas de retratos; medir cobertura y fallback. Las elecciones requieren identificar su conjunto completo por separado.
- [x] Actualizar pendientes/evidencia y cerrar solo los casos probados, sin modificar test.2.

Evidencia Task3: patch0049, candidato377cb29…;14casos/2.280hashes/104pares RGB iguales. Narrativa con origen64, clip56 intacto y trazas de catálogo efectivas. T11 sigue parcial: elecciones por conjunto y cobertura global pendientes.
