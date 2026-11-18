# Transiciones panorámicas del capítulo 1

Se usó el ejecutable nativo de Windows, el disco 1 traducido y estados locales del propietario. Las capturas corresponden a una ventana SDL oculta de 1280×720 con vista Zoom. Cada ejecución usó una copia independiente de la memoria de respaldo. Los fotogramas son relativos a la carga del estado indicado.

| Inicio | Reproducción | Resultado observado |
| --- | --- | --- |
| `intro1799.state` | `tests/chapter1-opening-skip.movie` | `opening → row-gradient → title → native → title`. Las capturas 91 y 181 son negras. El título aparece a más tardar en la captura 271. |
| `title-final.state` | `tests/chapter1-title-new-game.movie` | `title → native → row-gradient → native → row-gradient → backdrop → movie`. Menú de título en 200, pantalla LOADING con marco 4:3 en 400 y 650, película narrativa panorámica en 1000 y 1450. |
| `map-room.state` | `tests/chapter1-map-dining-hall.movie` | `row-gradient → native → backdrop → narrative`. Mapa en 250 y 330, fundido hacia el comedor en 500, diálogo en 750. |
| `theater.state` | `tests/theater-dialogues.movie` | La misma secuencia de layouts del mapa al diálogo. Escena con Sumire en 250 y conversación en 1000–2700. |
| `resume-chapter-6000.state` | `tests/chapter1-lips-confirm.movie` | El menú LIPS nocturno se ve en 8 y 32, desaparece a más tardar en 59 y la respuesta está completa en 230. Los 450 fotogramas mantienen `narrative`. Otro LIPS, desde `prebattle-3000.state`, conservó el mismo layout. |

Ejecutar las pruebas con `python -m unittest discover -s tests -p test_widescreen_transitions.py -v`. Verifican las transiciones de apertura, New Game, comedor y LIPS y comparan los hashes de todos los fotogramas entre las presentaciones Original y Mejorada. Omiten cada ruta cuando faltan sus estados privados. Los videos de entrada contienen únicamente pulsaciones del mando.

## Hallazgos en la compilación examinada

- **Pantalla de carga.** Un estado guardado antes del fotograma 400 de la ruta New Game contiene toda la pantalla LOADING en la capa 4. La huella FNV-1a de 512 bytes de la paleta es `74EA8ADC9B0340CC`, correspondiente al inicio de `SAKURA1/LOAD.BIN` (76.672 bytes). Coinciden 93 bloques no triviales de 256 bytes con la VRAM del estado.
- **Intermedio.** `intermission-down.state`, `intermission-up.state` y `night-patrol-12000.state` mostraron el menú Save/Status/Resume con marco 4:3. La capa 4 contiene el fondo completo, Sakura y el logotipo. La capa 0 contiene el recuadro de selección. La paleta de capa 4 `E9107F892185CCC8` coincide con `ICLOGO.BIN` y `LOAD01.BIN`, así que la huella por sí sola es ambigua. Los tres estados comparten la firma de página `79F284B5622630A4`. En `intermission-down.state` se recuperaron 86 bloques de `IC01.BIN` en VRAM, principalmente con desplazamiento de archivo `+0x48C80`, y 41 de `ICLOGO.BIN` en `+0x34280`. `exit-battle-save.state` ya usa `anchored-menu`, con la paleta `530FF280499422C3` de `IC01.BIN`. La capa 4 está desactivada en `intermission-save.state`, que muestra la pantalla de estado.
- **Texto HD en LIPS.** Dos ejecuciones de la misma ruta nocturna con Estilo de texto HD y Original producen capturas idénticas mientras se ven las opciones en los fotogramas 8 y 32. En 230, tras la selección, cambian 8.008 píxeles de la línea de respuesta dentro del rectángulo `(346,510)–(946,542)` de la captura. El filtro actual admite filas de diálogo desde la coordenada de origen Y=160. Las opciones del cuadro superior quedan fuera de ese filtro. Estas ejecuciones no registraron sustituciones verificadas de retratos.
- **Fundidos.** La traza emite cambios de layout sin número de fotograma. Las capturas muestreadas sustentan los fotogramas indicados y dejan sin medir los límites exactos del fallback `native` durante los fundidos. La auditoría de estados locales tampoco establece cobertura continua del capítulo.

Los registros, capturas y sondeos de capas están en `local/work/worker-wide-transitions`. Las subcarpetas `opening-skip`, `title-start`, `map-room`, `theater-dialogues`, `lips-patrol` y `lips-original-text` corresponden a las rutas de la tabla y a la comparación de texto.

## Captura de glifos LIPS

El listado VDP1 de `resume-chapter-6000.state` contiene sprites normales de glifo con modo `0080` y tamaño `0210` (16×16). Los glifos coinciden byte a byte con el atlas inglés que usa el diálogo. Las opciones inactivas usan color `C510`. La opción seleccionada usa `C570` y también conserva el resaltado en la capa VDP2. Las tres filas empiezan en Y=54, 78 y 102. El LIPS de `prebattle-3000.state` usa Y=62 y 94. Estos dos cuadros requieren reconocer ambos colores y distintas alturas.

`frontend_sdl.cpp` admite `C510` y Y=160–196. `NarrativeInkFits` restringe la tinta al recuadro inferior y `SakuraUi::GameText` aplica `NarrativeClip`. En vista Zoom, el cuadro de opciones pertenece a la transformación de la imagen. El diálogo inferior usa otra transformación. Se necesita asignar una transformación y un recorte a cada grupo de líneas.

El sondeo de capas muestra el marco, el temporizador, la figura de Sakura y la tinta de las opciones en VDP1. La capa 3 de VDP2 contiene el relleno y resaltado del recuadro. `underSprites` vuelve a componer el píxel sin toda la capa VDP1. Restaurar así los píxeles de tinta de una opción puede retirar también los píxeles de Sakura que deben verse bajo el cuadro translúcido. Una sustitución fiel requiere componer cada píxel sin el glifo y conservar el valor VDP1 anterior a ese comando. Los datos auxiliares pueden mantenerse fuera de la serialización del estado.

Para verificar una futura sustitución, repetir la ruta nocturna en HD y Original. El cambio debe ceñirse al texto del recuadro mientras se ven las opciones, preservar marco, temporizador, resaltado y retrato, y conservar la igualdad de los hashes del juego. Repetir en vista Zoom y en la vista que conserva el encuadre original.

### Casos para validar una placa de glifos

| Caso | Evidencia esperada |
| --- | --- |
| Tres opciones nocturnas desde `resume-chapter-6000.state` | HD modifica únicamente la zona de los glifos respecto de Original, incluidos los de la fila seleccionada. El resaltado VDP2, el temporizador y el marco coinciden para el mismo fotograma. |
| Dos opciones desde `prebattle-3000.state` | Se reconocen las filas a Y=62 y Y=94. La fila seleccionada mantiene su color. |
| Tinta por encima de la figura VDP1 | Al ocultar una fila, la placa conserva la figura bajo el panel con su mezcla de color. Un caso sintético con el mismo valor VDP1 escrito por un glifo y por un sprite posterior comprueba que la visibilidad se siga por orden de dibujo. |
| Glifo no reconocido, fila ocluida o placa sin datos del framebuffer mostrado | Los píxeles nativos de esa fila permanecen intactos. Tras restaurar un estado, se espera una placa válida antes de retirar tinta. |
| Vista Zoom y encuadre original | El texto HD sigue la transformación del panel y queda dentro de sus bordes. El diálogo inferior conserva su propia posición. |
| Confirmación y vencimiento del temporizador | El texto de opciones desaparece con el cuadro. La respuesta, la selección y los hashes de todos los fotogramas coinciden entre Original y Mejorada. |

Estado de la auditoría inicial: la placa aún no estaba implementada. La implementación posterior y sus pruebas reales están en [texto HD de elecciones](chapter1-choice-hd.md). El replay automatizado actual comprueba layout y paridad del estado. La comparación HD/Original de las capturas 8, 32 y 230 documenta el punto de partida para probar la sustitución.

## Correcciones posteriores a la auditoría

El intermedio acepta la paleta secundaria del logotipo únicamente si la imagen nativa IC01 coincide con el framebuffer presentado: al menos 80 % de muestras, al menos 60 % por cuadrante y diversidad visible suficiente. Un fundido uniforme no satisface esta comprobación. Se verificaron los tres estados afectados y el menú de salida del combate con el layout `anchored-menu`. La pantalla LOAD.BIN dispone ahora de un fondo generativo provisional y conserva su columna animada original. El ajuste de fase entre sus mosaicos y el centro protegido aún requiere pulido visual; disponer de layout panorámico no acredita una transición visual terminada.
