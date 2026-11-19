# Progreso HD

**Objetivo global: 100% verificado. Estado: Verificación pendiente.**

Los porcentajes corresponden al inventario definido para cada fila. Una celda «Sin dato» indica una medición pendiente y un cero indica una ausencia confirmada. Los recuentos de candidatos se detallan por separado.

| Área | Unidad | Inventariado | Emparejado | Preparado | Integrado | Verificado en juego |
| --- | --- | --- | --- | --- | --- | --- |
| Retratos y animación | identidades Saturn | 304/304 (100%) | 302/304 (99,3%) | 302/304 (99,3%) | 302/304 (99,3%) | Sin dato |
| Imágenes de escena | archivos SPR PC candidatos (BG, EVENT, CG, ENDING, TITLE, ICATCH) | 1267/1267 (100%) | 712/1267 (56,1%) | Sin dato | 459/1267 (36,2%) | Sin dato |
| Escenas y transiciones | candidatos de escena (112 tablas de diálogo + 54 flujos de vídeo) | 166/166 (100%) | Sin dato | Sin dato | Sin dato | Sin dato |
| Vídeos | clips únicos | 50/50 (100%) | 50/50 (100%) | Sin dato | 44/50 (88%) | Sin dato |
| Modo táctico | archivos SPR PC candidatos (UNIT, MAP, ITEM) | 542/542 (100%) | 0/542 (0%) | 0/542 (0%) | 0/542 (0%) | 0/542 (0%) |
| HUD y menús PC/Saturn | imágenes PC candidatas (29 archivos de menú/HUD) | 572/572 (100%) | 0/572 (0%) | 0/572 (0%) | 0/572 (0%) | 0/572 (0%) |
| Fondos decorativos KABE | temas del inventario KABE | 19/19 (100%) | 19/19 (100%) | 19/19 (100%) | 19/19 (100%) | Sin dato |
| Personajes grandes NC | cuerpos Saturn (archivos NC) | 147/147 (100%) | 129/147 (87,7%) | Sin dato | 6/147 (4%) | Sin dato |

## Resumen global de integración

| Área | Integrado | Verificado en juego |
| --- | --- | --- |
| Retratos y animación | 302/304 (99,3%) | Sin dato |
| Imágenes de escena | 459/1267 (36,2%) | Sin dato |
| Escenas y transiciones | Sin dato | Sin dato |
| Vídeos | 44/50 (88%) | Sin dato |
| Modo táctico | 0/542 (0%) | 0/542 (0%) |
| HUD y menús PC/Saturn | 0/572 (0%) | 0/572 (0%) |
| Fondos decorativos KABE | 19/19 (100%) | Sin dato |
| Personajes grandes NC | 6/147 (4%) | Sin dato |

- **Integración global indicativa (media de 7/8 categorías con total): 46,7%.** Cada categoría pesa igual.
- **Integración global ponderada por unidad: 830/2901 (28,6%).** Mezcla unidades distintas; solo orienta.
- Categorías sin total confirmado: ninguna.

## Qué cuenta en cada etapa

- **Inventariado**. Elementos nativos identificados dentro del alcance declarado.
- **Emparejado**. Correspondencia aprobada del recurso y sus variantes necesarias.
- **Preparado**. Sustitución empacada y validada con el formato del runtime.
- **Integrado**. Sustitución conectada a la ruta de ejecución correspondiente.
- **Verificado en juego**. Elementos distintos validados en capturas o reproducciones trazables.

El objetivo global se alcanza cuando cada categoría tiene un total confirmado y todas sus etapas cubren ese total. Las unidades se evalúan por categoría; el resumen global es solo indicativo.

## Alcance y pendientes

### Retratos y animación

Identidades de los atlas Saturn auditados en ambos discos. Las tiras de ojos y boca se cuentan una vez por identidad.

- Checkpoint reproducible. 201 identidades con base, ojos y boca disponibles. Se comprobaron 402 PNG a dos densidades. El paquete v0.1.2 entregado conserva 191 retratos.
- Capítulo 1. 91/123 identidades con las tres regiones preparadas y 32 pendientes. Los seis FCE de alcance figuran en la auditoría.
- Se verificaron en juego las bases de Sakura 0013 y 0014, Sumire 0045 y María 0064. En Sumire 0040 y 0041 se observó la primera tira a Y=16. En el tercer lote quedan pendientes las tiras en juego y la verificación de las otras cuatro bases.
- 394 candidatos PC. La disponibilidad de las tiras en el paquete deja pendiente la cobertura acumulada por identidad durante gameplay.
- Lote 7: 0152 (buzo) y 0153 (monstruo) aceptados con ajuste nulo; identidad inequívoca, candidato ID-1 y puntaje de bordes independiente de paleta dentro del ruido. Incluyen base, ojos y boca. Quedan 00a1 (tiras de ojos intercambiadas) y 0169 (carta con otro diseño en PC).
- **Siguiente paso**. Revisar las identidades pendientes y validar parpadeo, boca, ambas tiras simultáneas, efectos y fallback en juego.

Rangos de ID Saturn pendientes en hexadecimal

`00a1` `0169`

- [portrait-animation-coverage.md](research/portrait-animation-coverage.md). SHA-256 del recibo local `f76f05657f88e9d37af6517e878ccdfd81abc9a8a0db38c899fa1e62bce13aac`.
- [first-sakura-hd-portraits.md](research/first-sakura-hd-portraits.md). SHA-256 del recibo local `8aef026bb744db43f813f3435455fec694a432bc6dbe87ad09a88619c6d9a3b1`.
- [chapter1-sumire-hd-portraits.md](research/chapter1-sumire-hd-portraits.md). SHA-256 del recibo local `3ff2e8dfe039d3c64489ebb784a0c3f7f5b56572148197025ff53840fc857f48`.
- [chapter1-third-hd-portraits.md](research/chapter1-third-hd-portraits.md). SHA-256 del recibo local `182ad5f38ab46b744e8a5ef2682f2e3477792f80c47ef13d7e17b74802ac035e`.
- [v0.1.2.md](releases/v0.1.2.md). SHA-256 del recibo local `e1653a18a41ae3f68acce1fde82c4fba82f6a00228353d160a402d1e5a940b5f`.

### Imágenes de escena

Fondos de escena, eventos, CG, finales, título y eyecatch del dump PC que sustituyen a su equivalente Saturn. Un archivo puede contener varias imágenes.

- El censo incluye 1.267 archivos SPR PC en BG, EVENT, CG, ENDING, TITLE e ICATCH. Los 19 temas KABE se cuentan aparte.
- El cruce TH0 registra 712 archivos PC con una correspondencia aceptada en los catálogos de BG, EVE y pantallas IC. La tabla de huellas de paleta contiene 459 entradas y 459 archivos SPR distintos con integración en el código fuente.
- El preparador copia el material HD desde la edición PC del propietario. Falta un recuento de archivos preparados y verificados individualmente. Las imágenes de variante ancha, escenas EVE y eyecatches mantienen su ruta nativa.
- **Siguiente paso**. Confirmar los pares restantes y validar variantes de iluminación, desplazamiento y fundidos en juego.

- [pc-asset-census.md](research/pc-asset-census.md).
- [hd-chapter-coverage.md](research/hd-chapter-coverage.md).
- [saturn-bg-format.md](research/saturn-bg-format.md).

### Escenas y transiciones

Visitas, elecciones, mapas, combates, menús, películas y transiciones navegadas en ambos discos.

- El índice enriquecido lista 166 candidatos de recursos y 26 observaciones de ejecución, incluidas 17 del barrido de episodios.
- Una tabla de diálogo o un flujo de vídeo puede aparecer en varias rutas. Las observaciones de estados y capturas carecen de un denominador común con las 166 entradas de recursos.
- **Siguiente paso**. Vincular cada aparición a una escena o transición y verificar HD, Zoom y fallback cuando corresponda.

- [scene-tagging.md](research/scene-tagging.md).
- [wide-map-crossfades.md](research/wide-map-crossfades.md).
- [chapter-sweep.md](research/chapter-sweep.md).
- [hd-chapter-coverage.md](research/hd-chapter-coverage.md).

### Vídeos

Correspondencias completas entre clips Saturn y PC, con sus variantes de montaje, subtítulos, audio y comportamiento de salto.

- 50 clips Saturn únicos y emparejados. La tabla del runtime conecta el vídeo PC para 44 clips y conserva el vídeo y el audio Saturn en los seis cortes alternativos.
- El preparador copia películas si la edición PC las incluye. MOVIE000 y MOVIE001 tienen observaciones de vídeo en juego. La validación completa de subtítulos, audio, sincronización, salto y cambio de disco sigue abierta.
- **Siguiente paso**. Verificar audio y vídeo a velocidad normal, saltos y reanudaciones, subtítulos y ambos discos.

- [scene-tagging.md](research/scene-tagging.md).
- [intro-petals-transition.md](research/intro-petals-transition.md).
- [video-equivalence.md](research/video-equivalence.md).

### Modo táctico

Unidades, mapas y objetos del modo táctico PC que sustituyen piezas del mapa y combate Saturn, pegados al mundo y al scroll.

- 542 archivos SPR: 291 UNIT, 194 MAP y 57 ITEM, más 141 MAP DAT y datos de mapa. Ninguno emparejado ni integrado todavía.
- **Siguiente paso**. Emparejar unidades, mapas y objetos con sus piezas Saturn y validar anclaje y scroll en capturas.

- [pc-asset-census.md](research/pc-asset-census.md).

### HUD y menús PC/Saturn

Inventario conjunto por pantalla o pieza equivalente, incluidos elementos de mapa, batalla, estados y guardado.

- Se observaron menús tácticos en Saturn y se ajustó su presentación. Falta vincular las piezas HD compartidas y contar las pantallas cubiertas.
- Inventario de cabeceras PC: 29 archivos y 572 entradas de imagen sin errores de cabecera (pc-menu-hud-inventory.json). Ninguna está emparejada todavía con una pieza Saturn.
- **Siguiente paso**. Emparejar cada entrada con su pantalla o pieza Saturn, empaquetarla y conectarla al renderizador; separar sustitución HD y ajuste del layout Saturn.

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

Cuerpos Saturn fuera del retrato de diálogo. La cara y sus cuadros se auditan aparte.

- Se auditaron 147 paquetes de cuerpos Saturn frente a 147 paquetes PC que contienen 3.596 imágenes. Hay 129 pares de cuerpo utilizables según el mapa y la revisión. Los recuentos usan cuerpos, una unidad por archivo Saturn.
- Se observaron seis cuerpos dibujados en HD en estados de juego. Según el cuadro, los ojos o la boca pueden seguir nativos. Sigue pendiente el recuento de poses, expresiones, fundidos y apariciones verificadas.
- **Siguiente paso**. Comprobar los cuerpos restantes y las expresiones con fallback nativo.

- [saturn-hd-characters.md](research/saturn-hd-characters.md).
- [pc-character-inventory.json](research/pc-character-inventory.json).
- [saturn-bg-format.md](research/saturn-bg-format.md).

## Actualizar el registro

Añade el resultado revisado a `config/hd-progress.json`. Registra la unidad y el alcance del total, la etapa comprobada y la evidencia pública correspondiente. Usa `null` si falta el inventario o el recuento, y cuenta cada identidad una vez aunque aparezca en varios discos o escenas. Una coincidencia por nombre, la extracción y la decodificación por sí solas cuentan como candidatos. Al aprobar un retrato, actualiza el número de emparejamientos y sus rangos pendientes. Conserva imágenes, vídeos, partidas, guiones y rutas locales de propietario fuera del registro.

```powershell
python tools/build_hd_progress.py
python tools/build_hd_progress.py --check
python -m unittest discover -s tests -p test_hd_progress.py
```
