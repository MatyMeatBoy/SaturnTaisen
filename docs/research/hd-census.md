# Censo HD por tipo de recurso (THD32)

Una tabla única con denominadores honestos para el «100 %». Se genera **sin discos ni runtime** a partir de `config/hd-chapter-coverage.json`, `config/hd-progress.json`, los inventarios tácticos de `config/` y la tabla de carpetas de [pc-asset-census.md](pc-asset-census.md):

```powershell
python tools/hd_census.py            # imprime la tabla
python tools/hd_census.py --write    # actualiza el bloque de abajo
python tools/hd_census.py --check    # falla si el bloque está desactualizado
python -m unittest tests.test_hd_census
```

## Regla de conteo

- **Candidato**: un archivo PC distinto (o una identidad, cuerpo o clip Saturn en los tipos sin archivo PC por unidad). Cada donante PC cuenta **una vez**, aunque lo usen varias claves Saturn, ambos discos o varios capítulos. Los archivos con los mismos píxeles (`scene_file_duplicate_groups`) cuentan como uno.
- **Escena**: un candidato que el registro ya vincula a una clave Saturn. Los candidatos PC sin ninguna fila del registro (EVENT, casi todo CG) son candidatos, no escenas: caen en «sin pareja / sin conectar».
- **Excluido por diseño** (sale de la meta, con motivo): recortes sobre color clave o imágenes en blanco, rótulo japonés incrustado (TITLE; el jugador ve las capas locales de THD23), KAO (contado en retratos), transiciones FILM nativas cortas. «Composición PC no sigue la cámara» también figura como excluido, pero no es de diseño sino una decisión pendiente de testigo.
- **Estado de un donante**: el mejor de sus filas (`hd` > `wired-unverified` > `paired-not-wired` > `unsupported-size` > `excluded`). Un donante `hd` con otra clave pendiente se cuenta como `hd` y también como **parcial**.
- **Bloqueado**: `paired-not-wired` y `unsupported-size`, con motivo (falta de testigo, tamaño no soportado T105c, falta de conexión en el runtime, composición distinta).
- **Integrado %** = hd / meta. **Verificado %** = donantes con `verified_in_game` en alguna fila `hd` / meta. Es el mismo criterio que `tools/build_hd_progress.py`: escenas 586/1095 y 170/1095 coinciden con [HD_PROGRESS](../HD_PROGRESS.md) (lo comprueba `tests/test_hd_census.py`).
- Las filas «(manual)» no salen del registro: están a mano en `tools/hd_census.py` con su fuente.

<!-- BEGIN HD CENSUS -->

| Tipo | Denominador (candidatos) | Excluidos por diseño | Meta | hd | wired-unverified | Bloqueados | Sin pareja / sin conectar | % integrado | Verificado | % verificado |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Fondos de escena (BG) | 665 | 87 | 578 | 525 | 0 | 0 | 53 | 90,8% | 157 | 27,1% |
| Fondos EVE/BBG (batalla y evento) | 50 | 0 | 50 | 36 | 0 | 8 | 6 | 72,0% | 6 | 12,0% |
| EVENT (SAKURA2/EVENT) | 214 | 0 | 214 | 0 | 0 | 0 | 214 | 0,0% | 0 | 0,0% |
| CG (SAKURA3/CG) | 219 | 0 | 219 | 3 | 0 | 5 | 211 | 1,3% | 3 | 1,3% |
| Finales (SAKURA1/ENDING) | 13 | 0 | 13 | 7 | 0 | 0 | 6 | 53,8% | 2 | 15,3% |
| IC / eyecatch (ICATCH) | 21 | 0 | 21 | 16 | 0 | 0 | 5 | 76,1% | 5 | 23,8% |
| TITLE (tarjetas de episodio PC) | 10 | 10 | 0 | 0 | 0 | 0 | 0 | - | 0 | - |
| Mapas tácticos: suelos | 26 | 0 | 26 | 12 | 0 | 14 | 0 | 46,1% | 12 | 46,1% |
| Unidades tácticas (UNIT) | 291 | 0 | 291 | 0 | 0 | 0 | 291 | 0,0% | 0 | 0,0% |
| HUD y menús (SYSTEM sin KAO) | 572 | 394 | 178 | 18 | 0 | 0 | 160 | 10,1% | 14 | 7,8% |
| ITEM (tarjetas de objeto) | 51 | 0 | 51 | 41 | 0 | 0 | 10 | 80,3% | 1 | 1,9% |
| Cuerpos NC (personajes grandes) | 147 | 0 | 147 | 147 | 0 | 0 | 0 | 100,0% | 48 | 32,6% |
| Retratos (identidades Saturn) | 304 | 0 | 304 | 304 | 0 | 0 | 0 | 100,0% | 10 | 3,2% |
| Vídeos (FILM) | 52 | 2 | 50 | 50 | 0 | 0 | 0 | 100,0% | 2 | 4,0% |
| Fondos decorativos KABE | 19 | 0 | 19 | 19 | 0 | 0 | 0 | 100,0% | 0 | 0,0% |
| Tarjetas de episodio (manual) | 10 | 0 | 10 | 1 | 9 | 0 | 0 | 10,0% | 1 | 10,0% |

| Tipo | Motivos de exclusion por diseño | Motivos de bloqueo | Nota |
| --- | --- | --- | --- |
| Fondos de escena (BG) | composición PC no sigue la cámara nativa (3); recorte sobre color clave o imagen en blanco (diseño) (84) | - | 52 claves Saturn distintas `unpaired` (sin donante PC) no entran en el denominador de archivos PC; total escena sin excluidos: 1095. Parcial (hd con otra clave pendiente): 3. |
| Fondos EVE/BBG (batalla y evento) | - | falta de testigo (1); tamaño no soportado (T105c) (7) | - |
| EVENT (SAKURA2/EVENT) | - | - | - |
| CG (SAKURA3/CG) | - | falta de testigo (5) | Parcial (hd con otra clave pendiente): 1. |
| Finales (SAKURA1/ENDING) | - | - | Parcial (hd con otra clave pendiente): 7. |
| IC / eyecatch (ICATCH) | - | - | Parcial (hd con otra clave pendiente): 13. |
| TITLE (tarjetas de episodio PC) | rótulo japonés incrustado (tarjetas: capas locales) (10) | - | - |
| Mapas tácticos: suelos | - | composición PC distinta (conservar nativo salvo testigo) (1); falta conexión en el runtime (12); falta de testigo (1) | 194 SPR de MAP en el volcado PC; 26 son suelos emparejados con las 27 MAP BIN Saturn. Los otros 168 (teselas, objetos, fotogramas) no tienen función asignada: no son denominador hasta emparejarse.  |
| Unidades tácticas (UNIT) | - | - | 27 bancos UNIT Saturn (10 conjuntos distintos): emparejados 0, ambiguos 0. Ningún archivo con estado explicito.  |
| HUD y menús (SYSTEM sin KAO) | KAO: atlas de retratos, contado en retratos (394) | - | 30 claves Saturn de menu sin pareja establecida (`unknown`).  |
| ITEM (tarjetas de objeto) | - | - | 41 archivos ITEM con imagen dibujada; 39 claves Saturn de objeto `unpaired`. Los 57 SPR de ITEM también están en el 542 táctico: aquí se cuentan una vez.  |
| Cuerpos NC (personajes grandes) | - | - | 147 donantes PC SAKURA1/NC y 19 alternos SAKURA3 del mismo conjunto Saturn. Filas del registro por disco/capitulo: 296.  |
| Retratos (identidades Saturn) | - | - | 304 identidades con fila en el registro; el denominador es el de hd-progress.json. 394 caras PC en KAO se cuentan aquí y no en HUD.  |
| Vídeos (FILM) | transición nativa corta sin clip PC (2) | - | 54 apariciones FILM (disco, FAD) -> 50 clips PC (6 por tramos). Verificado solo donde la fila lo declara.  |
| Fondos decorativos KABE | - | - | Sin fila por tema en el registro; el recuento viene de hd-progress.json. 25 WALL PC, 19 temas usados. Verificación: THD25.  |
| Tarjetas de episodio | - | - | Marco y rótulo español de los 10 episodios en el paquete; solo el episodio 1 tiene testigo de dibujo. Los 10 TITLE PC se excluyen (letras japonesas).  |

Escena (7 carpetas SPR): candidatos 1192, excluidos 97, meta 1095, hd 587 (53,6%), verificados 173 (15,7%), bloqueados 13, sin pareja o sin fila 495; de los hd, 24 aún tienen otra clave pendiente (parcial).

Donantes de escena que cuentan en dos estados: 22 hd y excluido a la vez, 24 hd con otra clave pendiente. Rutas físicas extra de familias exactas presentes en el registro: 23. Comparten una identidad de conteo y conservan sus rutas del runtime.

Filas `hd` sin ninguna referencia de evidencia por fila (son `hd` por la tabla del runtime, no por testigo): scene-pictures 935/1197, bodies 207/296, portraits 172/419, film 41/45, menus-hud 0/100, tactical-maps 0/12.

<!-- END HD CENSUS -->

## Discrepancias con HD_PROGRESS y con el registro

1. **ITEM contado dos veces.** Los 542 SPR del modo táctico incluyen los 57 ITEM, y HUD suma 51 imágenes de objeto. El censo los cuenta solo en ITEM. Hay además tres cifras (57 archivos, 51 imágenes, 41 archivos dibujados).
2. **Tácticos sin estado.** De los 542, solo 26 suelos tienen fila (11 `hd`). Las 291 UNIT quedan sin pareja (0 emparejadas). Los 168 SPR de MAP restantes (teselas, objetos, fotogramas) no tienen función asignada; el 542 los trata como candidatos y no lo son todavía. Por eso HD_PROGRESS marca «Sin dato» en la fila táctica y no entra en el total.
3. **EVENT y CG casi sin filas.** 214 EVENT y 211 CG distintos no tienen ninguna fila: son el 85 % de lo que falta en «escena» (425 de 495 sin pareja). Los 1.095 de HD_PROGRESS ya los incluyen en el denominador, así que el 53,5 % integrado es correcto, pero el 100 % depende de THD09.
4. **Donantes `hd` parciales y mixtos.** 23 donantes `hd` aún tienen otra clave pendiente (filas IC `paired-not-wired`, fotos de finales, etc.) y 22 son `hd` en una clave y `excluded` en otra (recortes BG3xxx reutilizados). El 586 los cuenta enteros.
5. **Duplicados exactos.** El inventario agrupa 134 nombres en 59 familias. Se reprodujeron 36 familias byte a byte y otras 23 por secuencia de subimágenes RGBA, con las mismas dimensiones e índices. En el registro hay 23 familias con dos rutas físicas cada una. Las filas conservan pc para el archivo real del runtime y comparten pc_identity para el inventario.
6. **`hd` por tabla, no por testigo.** Filas `hd` sin ninguna referencia de evidencia propia: escenas 935/1196, cuerpos 207/296, retratos 172/419, vídeo 41/45. Es lo que define `hd` (entrada en la tabla del runtime), pero no es observación: el verificado en juego es el piso documentado.
7. **NC.** Los 19 NC de SAKURA3 tienen el mismo nombre y número de imágenes que su donante SAKURA1, y el mismo recurso Saturn ya registrado en ambos discos. Ningún disco incluye una ruta nativa /SAKURA3/NC*.BIN. Los 19 contenedores PC tienen SHA-256 distinto y una primera imagen de 480 píxeles de alto, salvo NC27 de 477, frente a 320 de SAKURA1. Los alternos son candidatos para los mismos 147 cuerpos. El [inventario](../../config/hd-body-alternates.json) conserva rutas, tamaños, colores de esquina y hashes. Un alterno necesita sus propias pruebas de silueta, posicionamiento y caras antes de sustituir un donante.
8. **Retratos.** 304 identidades Saturn frente a 394 caras PC (KAO). HD_PROGRESS marca el verificado como «Sin dato»; el registro lleva 10 identidades con `verified_in_game`.
9. **Filas pendientes de conectar.** El registro conserva los siete finales del disco 1, trece intermedios del disco 2, doce minijuegos y un par BBG. Las condiciones de cierre están en [SHARDS.md](../SHARDS.md).
10. **Vídeos.** 54 apariciones (disco, FAD) = 50 clips PC distintos + 2 transiciones nativas excluidas (MOVIE015 aparece en ambos discos).

## Qué falta para el 100 % por tipo

| Tipo | Falta | Quién |
| --- | --- | --- |
| Fondos BG | 53 sin pareja (52 claves Saturn `unpaired`); verificar 423 de 578 | Agente (revisión de pares, THD02/03/05); ruta/propietario para testigos naturales |
| EVE/BBG | 7 de tamaño no soportado (T105c) y 1 sin testigo; 6 sin pareja | Agente (soporte de tamaño); ruta (THD06) |
| EVENT | 214 sin ninguna fila: pareo por subimagen | Agente + propietario (necesita decodificar el lado Saturn de los discos), THD09 |
| CG | 6 sin testigo (fotos del disco 2) y 211 sin fila | Agente (THD09), ruta de finales (THD08) |
| Finales | 6 sin pareja; fotos y disco 1 sin testigo | THD08; propietario para el testigo del disco 1 |
| IC | 5 sin pareja y 13 filas intermedias sin ruta ni estado guardado | Ruta/mesa de integración (THD07) |
| Suelos tácticos | 13 sin ensamblador de suelo, 1 sin testigo, 1 composición distinta; verificar 15 | Agente + mesa de integración (parche del runtime) |
| Unidades | 291 sin pareja | Agente (`tactical-pairing.md`); propietario para piezas Saturn |
| HUD/SYSTEM | 160 imágenes sin pareja o sin conectar | Agente + mesa de integración (T109/THD20-21) |
| ITEM | 10 imágenes abiertas; verificar 50 | Agente/mesa de integración |
| Cuerpos NC | verificar 99 de 147 | Ruta (THD10-12) |
| Retratos | verificar 294 de 304 | Ruta/mesa de integración |
| Vídeos | verificar 48 de 50 | Ruta/propietario (THD26-27) |
| KABE | verificación por tema | Ruta (THD25) |
| Tarjetas de episodio | testigos de los episodios 2-10 | Ruta (THD23) |

## Límites

- Offline: no se decodifica ningún disco. El denominador PC viene de la tabla de carpetas de pc-asset-census.md (volcado de la edición del propietario).
- El censo no cambia estados ni toca el registro; los fallos se abren como filas en [PENDIENTES](../PENDIENTES.md) (THD42-THD45).
