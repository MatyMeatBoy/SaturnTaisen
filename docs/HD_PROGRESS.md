# Progreso HD

**Objetivo global: 100% integrado.**

Los porcentajes corresponden al inventario definido para cada fila. Una celda «Sin dato» indica una medición pendiente y un cero indica una ausencia confirmada. Los recuentos de candidatos se detallan por separado.

| Área | Unidad | Inventariado | Emparejado | Preparado | Integrado | Verificado en juego |
| --- | --- | --- | --- | --- | --- | --- |
| Retratos y animación | identidades Saturn | 304/304 (100%) | 304/304 (100%) | 304/304 (100%) | 304/304 (100%) | Sin dato |
| Imágenes de escena | archivos SPR PC candidatos (BG, EVENT, CG, ENDING, TITLE, ICATCH) | 1145/1145 (100%) | 712/1145 (62,1%) | Sin dato | 582/1145 (50,8%) | 57/1145 (4,9%) |
| Escenas y transiciones | candidatos de escena (112 tablas de diálogo + 54 flujos de vídeo) | 166/166 (100%) | Sin dato | Sin dato | Sin dato | Sin dato |
| Vídeos | clips únicos | 50/50 (100%) | 50/50 (100%) | Sin dato | 50/50 (100%) | Sin dato |
| Modo táctico | archivos SPR PC candidatos (UNIT, MAP, ITEM) | 542/542 (100%) | Sin dato | Sin dato | Sin dato | Sin dato |
| HUD y menús PC/Saturn | imágenes PC de menú/HUD (SYSTEM sin KAO + tarjetas de objeto) | 229/229 (100%) | Sin dato | Sin dato | 47/229 (20,5%) | Sin dato |
| Fondos decorativos KABE | temas del inventario KABE | 19/19 (100%) | 19/19 (100%) | 19/19 (100%) | 19/19 (100%) | Sin dato |
| Personajes grandes NC | cuerpos Saturn (archivos NC) | 147/147 (100%) | 147/147 (100%) | Sin dato | 146/147 (99,3%) | 21/147 (14,2%) |

## Resumen global de integración

| Sección | Integrado |
| --- | --- |
| Retratos y animación | 304/304 (100%) |
| Imágenes de escena | 582/1145 (50,8%) |
| Escenas y transiciones | Sin dato |
| Vídeos | 50/50 (100%) |
| Modo táctico | Sin dato |
| HUD y menús PC/Saturn | 47/229 (20,5%) |
| Fondos decorativos KABE | 19/19 (100%) |
| Personajes grandes NC | 146/147 (99,3%) |

**HD total: 1148/1894 (60,6%).** Elementos conectados sobre candidatos de las secciones medidas. La tabla indica por separado la verificación en juego.
- Sin medir todavía (no cuentan): Escenas y transiciones, Modo táctico.

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
- 0152 y 0153 conservan las tres regiones aprobadas. En la sala de mando del capítulo 1 se comprobaron la base y las dos tiras de Iris 00a1 a 1440p, incluido el fundido blanco. El emblema 0169 usa la versión PC aprobada y se comprobó en la carta española a 1440p.
- **Siguiente paso**. Ampliar la verificación natural de parpadeos, boca, efectos y fallback por identidad y escena.

- [portrait-animation-coverage.md](research/portrait-animation-coverage.md). SHA-256 del recibo local `f76f05657f88e9d37af6517e878ccdfd81abc9a8a0db38c899fa1e62bce13aac`.
- [first-sakura-hd-portraits.md](research/first-sakura-hd-portraits.md). SHA-256 del recibo local `8aef026bb744db43f813f3435455fec694a432bc6dbe87ad09a88619c6d9a3b1`.
- [chapter1-sumire-hd-portraits.md](research/chapter1-sumire-hd-portraits.md). SHA-256 del recibo local `3ff2e8dfe039d3c64489ebb784a0c3f7f5b56572148197025ff53840fc857f48`.
- [chapter1-third-hd-portraits.md](research/chapter1-third-hd-portraits.md). SHA-256 del recibo local `182ad5f38ab46b744e8a5ef2682f2e3477792f80c47ef13d7e17b74802ac035e`.
- [v0.1.2.md](releases/v0.1.2.md). SHA-256 del recibo local `e1653a18a41ae3f68acce1fde82c4fba82f6a00228353d160a402d1e5a940b5f`.

### Imágenes de escena

Fondos de escena, eventos, CG, finales, título y eyecatch del dump PC que sustituyen a su equivalente Saturn. Un archivo puede contener varias imágenes.

- El censo incluye 1.267 archivos SPR PC en BG, EVENT, CG, ENDING, TITLE e ICATCH. Los 19 temas KABE se cuentan aparte.
- El cruce TH0 registra 712 archivos PC con correspondencia aceptada. El total integrado de la tabla se calcula desde el registro por capítulo y cuenta una vez los archivos PC compartidos por ambos discos.
- La integración incluye la búsqueda por paleta, la segunda clave de celdas y las sustituciones con reglas específicas como BG2533 e IC01. La columna de verificación en juego cuenta un archivo PC por cada imagen con al menos una aparición HD observada. Es un mínimo documentado. El recuento de recursos preparados y la auditoría de todas las apariciones siguen pendientes.
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

Clips Saturn únicos con sustitución PC completa o con tramos de imagen PC alineados al montaje Saturn.

- 50 clips Saturn únicos con imagen PC integrada: 44 sustituciones completas y 6 sustituciones por tramos. Para estos últimos se conservan el audio Saturn y los tramos nativos que respetan el montaje original.
- MOVIE004 y MOVIE011 tienen testigos en la historia. Los otros cuatro cortes alternativos se verificaron con reproducciones controladas. El preparador usa los archivos de la edición PC del jugador.
- **Siguiente paso**. Verificar los cortes alternativos en las rutas de historia pendientes y comprobar subtítulos, saltos y reanudaciones en el paquete.

- [scene-tagging.md](research/scene-tagging.md).
- [intro-petals-transition.md](research/intro-petals-transition.md).
- [video-equivalence.md](research/video-equivalence.md).
- [bounded-film-video-spans.md](research/bounded-film-video-spans.md).

### Modo táctico

Unidades, mapas y objetos del modo táctico PC que sustituyen piezas del mapa y combate Saturn, pegados al mundo y al scroll.

- El censo contiene 542 archivos SPR, repartidos en 291 UNIT, 194 MAP y 57 ITEM. Registra también 141 MAP DAT y los datos de mapa.
- Se verificó el suelo de MAP01, MAP02, MAP04, MAP05, MAP06 y MAP21. MAP05 se verificó con la cámara fija. La verificación cubre la capa de suelo. El inventario completo de sustituciones por archivo para mapas, unidades y objetos sigue pendiente.
- **Siguiente paso**. Emparejar unidades, mapas y objetos con sus piezas Saturn y validar anclaje y scroll en capturas.

- [pc-asset-census.md](research/pc-asset-census.md).
- [stage01-pc-ground.md](research/stage01-pc-ground.md).
- [map02-pc-ground.md](research/map02-pc-ground.md).
- [map04-pc-ground.md](research/map04-pc-ground.md).
- [map06-pc-ground.md](research/map06-pc-ground.md).
- [stage21-pc-ground.md](research/stage21-pc-ground.md).

### HUD y menús PC/Saturn

Inventario conjunto por pantalla o pieza equivalente, incluidos elementos de mapa, batalla, estados y guardado.

- Las pruebas de presentación de Saturn cubrieron menús tácticos. Las sustituciones de recursos se verifican por pieza y por pantalla.
- El censo PC reúne 29 archivos y 572 entradas de imagen con cabeceras validadas.
- El censo PC reúne 572 imágenes SYSTEM; las 394 de KAO cuentan como retratos y se suman las 50 imágenes de objeto candidatas: 228. La tabla calcula las integraciones desde el registro. Incluye tarjetas de objeto, los dos marcos FONT_CSL y los emblemas CD-1 y CD-2.
- **Siguiente paso**. Completar el cruce por imagen del censo, registrar las sustituciones HD y verificar cada menú en juego.

- [tactical-menu-independent-reference.md](research/tactical-menu-independent-reference.md).
- [v0.2.0-test.1.md](releases/v0.2.0-test.1.md).
- [PENDIENTES.md](PENDIENTES.md).

### Fondos decorativos KABE

Los 19 temas decorativos únicos del catálogo KABE con alternativas HD, incluidos los pares día/noche catalogados.

- 19 variantes de fondo listas para el runtime. La precarga y la paridad del loader miden los recursos preparados. La cobertura de escenas se registra aparte.
- **Siguiente paso**. Reunir validaciones por tema y escena, incluidas variantes de iluminación, fundidos, diálogos y transiciones.

- [provenance.json](../assets/generated/pc-backgrounds/provenance.json).
- [saturn-background-workers.md](research/saturn-background-workers.md).
- [v0.1.2.md](releases/v0.1.2.md). SHA-256 del recibo local `e1653a18a41ae3f68acce1fde82c4fba82f6a00228353d160a402d1e5a940b5f`.

### Personajes grandes NC

Cuerpos Saturn fuera del retrato de diálogo. La cara y sus cuadros se auditan aparte.

- Se auditaron 147 paquetes de cuerpos Saturn frente a 147 paquetes PC que contienen 3.596 imágenes. El registro cuenta los cuerpos emparejados e integrados por archivo Saturn, una vez aunque lo compartan ambos discos.
- La verificación cuenta cada cuerpo una vez a partir del registro de capítulos. Quedan por comprobar otras poses, expresiones y fundidos.
- **Siguiente paso**. Comprobar los cuerpos restantes y las expresiones con fallback nativo.

- [saturn-hd-characters.md](research/saturn-hd-characters.md).
- [pc-character-inventory.json](research/pc-character-inventory.json).
- [saturn-bg-format.md](research/saturn-bg-format.md).
- [coverage-campaign-v026.md](research/coverage-campaign-v026.md).

## Actualizar el registro

Añade el resultado revisado a `config/hd-progress.json`. Registra la unidad y el alcance del total, la etapa comprobada y la evidencia pública correspondiente. Usa `null` si falta el inventario o el recuento, y cuenta cada identidad una vez aunque aparezca en varios discos o escenas. Una coincidencia por nombre, la extracción y la decodificación por sí solas cuentan como candidatos. Al aprobar un retrato, actualiza el número de emparejamientos y sus rangos pendientes. Conserva imágenes, vídeos, partidas, guiones y rutas locales de propietario fuera del registro.

```powershell
python tools/build_hd_progress.py
python tools/build_hd_progress.py --check
python -m unittest discover -s tests -p test_hd_progress.py
```
