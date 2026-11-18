# Progreso HD

**Objetivo global: 100% verificado. Estado: Verificación pendiente.**

Los porcentajes corresponden al inventario definido para cada fila. Una celda «Sin dato» indica una medición pendiente y un cero indica una ausencia confirmada. Los recuentos de candidatos se detallan por separado.

| Área | Unidad | Inventariado | Emparejado | Preparado | Integrado | Verificado en juego |
| --- | --- | --- | --- | --- | --- | --- |
| Retratos y animación | identidades Saturn | 304/304 (100%) | 302/304 (99,3%) | 302/304 (99,3%) | 302/304 (99,3%) | Sin dato |
| Imágenes de escena | archivos SPR PC candidatos (BG, EVENT, CG, ENDING, TITLE, ICATCH) | 1267/1267 (100%) | 8/1267 (0,6%) | 0/1267 (0%) | 0/1267 (0%) | 0/1267 (0%) |
| Escenas y transiciones | candidatos de escena (112 tablas de diálogo + 54 flujos de vídeo) | 166/166 (100%) | Sin dato | Sin dato | Sin dato | 9/166 (5,4%) |
| Vídeos | clips únicos | 50/50 (100%) | 50/50 (100%) | 0/50 (0%) | 0/50 (0%) | 0/50 (0%) |
| Modo táctico | archivos SPR PC candidatos (UNIT, MAP, ITEM) | 542/542 (100%) | 0/542 (0%) | 0/542 (0%) | 0/542 (0%) | 0/542 (0%) |
| HUD y menús PC/Saturn | imágenes PC candidatas (29 archivos de menú/HUD) | 572/572 (100%) | 0/572 (0%) | 0/572 (0%) | 0/572 (0%) | 0/572 (0%) |
| Fondos decorativos KABE | temas del inventario KABE | 19/19 (100%) | 19/19 (100%) | 19/19 (100%) | 19/19 (100%) | Sin dato |
| Personajes grandes NC | imágenes PC candidatas (147 paquetes) | 3596/3596 (100%) | 0/3596 (0%) | 0/3596 (0%) | 0/3596 (0%) | 0/3596 (0%) |

## Resumen global de integración

| Área | Integrado | Verificado en juego |
| --- | --- | --- |
| Retratos y animación | 302/304 (99,3%) | Sin dato |
| Imágenes de escena | 0/1267 (0%) | 0/1267 (0%) |
| Escenas y transiciones | Sin dato | 9/166 (5,4%) |
| Vídeos | 0/50 (0%) | 0/50 (0%) |
| Modo táctico | 0/542 (0%) | 0/542 (0%) |
| HUD y menús PC/Saturn | 0/572 (0%) | 0/572 (0%) |
| Fondos decorativos KABE | 19/19 (100%) | Sin dato |
| Personajes grandes NC | 0/3596 (0%) | 0/3596 (0%) |

- **Integración global indicativa (media de 7/8 categorías con total): 28,4%.** Cada categoría pesa igual.
- **Integración global ponderada por unidad: 321/6350 (5%).** Mezcla unidades distintas; solo orienta.
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

- 1.267 archivos SPR: 766 BG, 235 EVENT, 222 CG, 13 ENDING, 10 TITLE y 21 ICATCH. Ninguno está emparejado ni integrado todavía; los 19 temas KABE se cuentan aparte.
- 8 pares aprobados por captura (pasada 1 en curso, 537 capturas revisadas): BG1119, BG1209, BG2251, BG1001, BG1002, BG1006, BG1007, BG1021. Registro continuo en docs/research/bg-matching-progress.md.
- **Siguiente paso**. Emparejar cada archivo con su escena Saturn, empaquetarlo e integrarlo; verificar variantes de iluminación y fundidos.

- [pc-asset-census.md](research/pc-asset-census.md).

### Escenas y transiciones

Visitas, elecciones, mapas, combates, menús, películas y transiciones navegadas en ambos discos.

- El índice inicial lista 166 candidatos de recursos y nueve observaciones de ejecución. Una tabla de diálogo o un flujo de vídeo puede aparecer en más de una ruta.
- Pendientes prioritarios: otras rutas de mapa a habitación, continuidad de diálogos y animación en escenas posteriores, combates completos, cambio de disco y clips con subtítulos.
- 166 candidatos del índice privado de recursos; 9 observaciones de ejecución. Emparejado, preparado e integrado siguen sin medir por escena (Sin dato): una tabla o flujo puede aparecer en varias escenas.
- **Siguiente paso**. Vincular cada aparición a una escena o transición estable, registrar el modo nativo y verificar HD, Zoom y fallback cuando corresponda.

- [scene-tagging.md](research/scene-tagging.md).
- [wide-map-crossfades.md](research/wide-map-crossfades.md).
- [chapter-sweep.md](research/chapter-sweep.md).

### Vídeos

Correspondencias completas entre clips Saturn y PC, con sus variantes de montaje, subtítulos, audio y comportamiento de salto.

- 50 clips Saturn únicos (flujos FILM deduplicados entre ambos discos; el cortometraje de 0,15 s del logo queda fuera) frente a 52 MPEG de PC (51 MOVIE + REDLOGO).
- Sin sustitución integrada: falta decodificación MPEG-1/MP2 en el runtime, sincronía de audio, subtítulos y salto.
- 44 pares con duración dentro de 0,5 s y orden consecutivo idéntico (flujo k de /SAKURA4 ↔ MOVIE00k).
- Seis pares con duración distinta (743bce↔009, d33904↔105, b39c1e↔004, ab833c↔011, 7b1472↔102, def7a6↔020 con 3,7 s) se aceptan por contenido: cada clip PC es la mejor coincidencia única en una firma de luminancia de cinco fotogramas frente a los 52 clips PC. Se registran como cortes alternativos.
- **Siguiente paso**. Comprobar audio, subtítulos y saltos de los seis cortes alternativos y diseñar la reproducción PC dentro del runtime.

- [scene-tagging.md](research/scene-tagging.md).
- [intro-petals-transition.md](research/intro-petals-transition.md).

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

Cuerpos y poses fuera del retrato de diálogo. El total de poses y composiciones nativas permanece abierto.

- 147 paquetes PC y 3.596 imágenes decodificadas sin errores de cabecera; 147 pares de nombre candidatos. Faltan las equivalencias por pose y el dibujo en runtime.
- **Siguiente paso**. Vincular índices por pose y validar ancla, proporción y animación en capturas Saturn para cada sustitución.

- [saturn-hd-characters.md](research/saturn-hd-characters.md).
- [pc-character-inventory.json](research/pc-character-inventory.json).

## Actualizar el registro

Añade el resultado revisado a `config/hd-progress.json`. Registra la unidad y el alcance del total, la etapa comprobada y la evidencia pública correspondiente. Usa `null` si falta el inventario o el recuento, y cuenta cada identidad una vez aunque aparezca en varios discos o escenas. Una coincidencia por nombre, la extracción y la decodificación por sí solas cuentan como candidatos. Al aprobar un retrato, actualiza el número de emparejamientos y sus rangos pendientes. Conserva imágenes, vídeos, partidas, guiones y rutas locales de propietario fuera del registro.

```powershell
python tools/build_hd_progress.py
python tools/build_hd_progress.py --check
python -m unittest discover -s tests -p test_hd_progress.py
```
