# Progreso HD

**Objetivo global: 100% verificado. Estado: Indeterminado.**

Los porcentajes corresponden al inventario definido para cada fila. Una celda «Sin dato» indica una medición pendiente y un cero indica una ausencia confirmada. Los recuentos de candidatos se detallan por separado.

| Área | Unidad | Inventariado | Emparejado | Preparado | Integrado | Verificado en juego |
| --- | --- | --- | --- | --- | --- | --- |
| Retratos y animación | identidades Saturn | 304/304 (100%) | 300/304 (98,6%) | 300/304 (98,6%) | 300/304 (98,6%) | Sin dato |
| Vídeos | clips únicos | 50/50 (100%) | 44/50 (88%) | 0/50 (0%) | 0/50 (0%) | 0/50 (0%) |
| HUD y menús PC/Saturn | pantallas y piezas compartidas | Sin dato | Sin dato | Sin dato | Sin dato | Sin dato |
| Fondos decorativos KABE | temas del inventario KABE | 19/19 (100%) | 19/19 (100%) | 19/19 (100%) | 19/19 (100%) | Sin dato |
| Personajes grandes NC | poses y composiciones nativas | Sin dato | Sin dato | Sin dato | Sin dato | Sin dato |
| Escenas y transiciones | escenas distintas en ejecución | Sin dato | Sin dato | Sin dato | Sin dato | Sin dato |

## Qué cuenta en cada etapa

- **Inventariado**. Elementos nativos identificados dentro del alcance declarado.
- **Emparejado**. Correspondencia aprobada del recurso y sus variantes necesarias.
- **Preparado**. Sustitución empacada y validada con el formato del runtime.
- **Integrado**. Sustitución conectada a la ruta de ejecución correspondiente.
- **Verificado en juego**. Elementos distintos validados en capturas o reproducciones trazables.

El objetivo global se alcanza cuando cada categoría tiene un total confirmado y todas sus etapas cubren ese total. Las unidades se evalúan por categoría, sin promediarlas.

## Alcance y pendientes

### Retratos y animación

Identidades de los atlas Saturn auditados en ambos discos. Las tiras de ojos y boca se cuentan una vez por identidad.

- Checkpoint reproducible. 201 identidades con base, ojos y boca disponibles. Se comprobaron 402 PNG a dos densidades. El paquete v0.1.2 entregado conserva 191 retratos.
- Capítulo 1. 91/123 identidades con las tres regiones preparadas y 32 pendientes. Los seis FCE de alcance figuran en la auditoría.
- Se verificaron en juego las bases de Sakura 0013 y 0014, Sumire 0045 y María 0064. En Sumire 0040 y 0041 se observó la primera tira a Y=16. En el tercer lote quedan pendientes las tiras en juego y la verificación de las otras cuatro bases.
- 394 candidatos PC. La disponibilidad de las tiras en el paquete deja pendiente la cobertura acumulada por identidad durante gameplay.
- **Siguiente paso**. Revisar las identidades pendientes y validar parpadeo, boca, ambas tiras simultáneas, efectos y fallback en juego.

Rangos de ID Saturn pendientes en hexadecimal

`00a1` `0152-0153` `0169`

- [portrait-animation-coverage.md](research/portrait-animation-coverage.md). SHA-256 del recibo local `f76f05657f88e9d37af6517e878ccdfd81abc9a8a0db38c899fa1e62bce13aac`.
- [first-sakura-hd-portraits.md](research/first-sakura-hd-portraits.md). SHA-256 del recibo local `8aef026bb744db43f813f3435455fec694a432bc6dbe87ad09a88619c6d9a3b1`.
- [chapter1-sumire-hd-portraits.md](research/chapter1-sumire-hd-portraits.md). SHA-256 del recibo local `3ff2e8dfe039d3c64489ebb784a0c3f7f5b56572148197025ff53840fc857f48`.
- [chapter1-third-hd-portraits.md](research/chapter1-third-hd-portraits.md). SHA-256 del recibo local `182ad5f38ab46b744e8a5ef2682f2e3477792f80c47ef13d7e17b74802ac035e`.
- [v0.1.2.md](releases/v0.1.2.md). SHA-256 del recibo local `e1653a18a41ae3f68acce1fde82c4fba82f6a00228353d160a402d1e5a940b5f`.

### Vídeos

Correspondencias completas entre clips Saturn y PC, con sus variantes de montaje, subtítulos, audio y comportamiento de salto.

- 50 clips Saturn únicos (flujos FILM deduplicados entre ambos discos; el cortometraje de 0,15 s del logo queda fuera) frente a 52 MPEG de PC (51 MOVIE + REDLOGO).
- 44 pares con duración dentro de 0,5 s y orden consecutivo idéntico (flujo k de /SAKURA4 ↔ MOVIE00k). Seis pares requieren revisión de montaje por diferencia de duración: 743bce↔009, d33904↔105, b39c1e↔004, ab833c↔011, 7b1472↔102 y def7a6↔020 (3,7 s).
- Sin sustitución integrada: falta decodificación MPEG-1/MP2 en el runtime, sincronía de audio, subtítulos y salto.
- **Siguiente paso**. Revisar el montaje de los seis pares con diferencia de duración, comprobar audio/subtítulos/saltos y diseñar la reproducción PC dentro del runtime.

- [scene-tagging.md](research/scene-tagging.md).
- [intro-petals-transition.md](research/intro-petals-transition.md).

### HUD y menús PC/Saturn

Inventario conjunto por pantalla o pieza equivalente, incluidos elementos de mapa, batalla, estados y guardado.

- Se observaron menús tácticos en Saturn y se ajustó su presentación. Falta vincular las piezas HD compartidas y contar las pantallas cubiertas.
- **Siguiente paso**. Inventariar las pantallas y piezas compartidas por edición. Separar sustitución HD y ajustes del layout Saturn.

- [tactical-menu-independent-reference.md](research/tactical-menu-independent-reference.md).
- [v0.2.0-test.1.md](releases/v0.2.0-test.1.md).

### Fondos decorativos KABE

Los 19 temas decorativos únicos del catálogo KABE con alternativas HD, incluidos los pares día/noche catalogados.

- 19 variantes de fondo listas para el runtime. La precarga y la paridad del loader miden los recursos preparados. La cobertura de escenas se registra aparte.
- **Siguiente paso**. Reunir validaciones por tema y escena, incluidas variantes de iluminación, fundidos, diálogos y transiciones.

- [provenance.json](../assets/generated/pc-backgrounds/provenance.json).
- [saturn-background-workers.md](research/saturn-background-workers.md).
- [v0.1.2.md](releases/v0.1.2.md). SHA-256 del recibo local `e1653a18a41ae3f68acce1fde82c4fba82f6a00228353d160a402d1e5a940b5f`.

### Personajes grandes NC

Cuerpos y poses fuera del retrato de diálogo. El total de poses y composiciones nativas permanece abierto.

- 147 paquetes PC y 3.596 imágenes decodificadas. Hay 147 pares de nombre candidatos. Faltan las equivalencias por pose.
- **Siguiente paso**. Vincular índices por pose y validar ancla, proporción y animación en capturas Saturn para cada sustitución.

- [saturn-hd-characters.md](research/saturn-hd-characters.md).
- [pc-character-inventory.json](research/pc-character-inventory.json).

### Escenas y transiciones

Visitas, elecciones, mapas, combates, menús, películas y transiciones navegadas en ambos discos.

- El índice inicial lista 166 candidatos de recursos y nueve observaciones de ejecución. Una tabla de diálogo o un flujo de vídeo puede aparecer en más de una ruta.
- Pendientes prioritarios: otras rutas de mapa a habitación, continuidad de diálogos y animación en escenas posteriores, combates completos, cambio de disco y clips con subtítulos.
- **Siguiente paso**. Vincular cada aparición a una escena o transición estable, registrar el modo nativo y verificar HD, Zoom y fallback cuando corresponda.

- [scene-tagging.md](research/scene-tagging.md).
- [wide-map-crossfades.md](research/wide-map-crossfades.md).
- [chapter-sweep.md](research/chapter-sweep.md).

## Actualizar el registro

Añade el resultado revisado a `config/hd-progress.json`. Registra la unidad y el alcance del total, la etapa comprobada y la evidencia pública correspondiente. Usa `null` si falta el inventario o el recuento, y cuenta cada identidad una vez aunque aparezca en varios discos o escenas. Una coincidencia por nombre, la extracción y la decodificación por sí solas cuentan como candidatos. Al aprobar un retrato, actualiza el número de emparejamientos y sus rangos pendientes. Conserva imágenes, vídeos, partidas, guiones y rutas locales de propietario fuera del registro.

```powershell
python tools/build_hd_progress.py
python tools/build_hd_progress.py --check
python -m unittest discover -s tests -p test_hd_progress.py
```
