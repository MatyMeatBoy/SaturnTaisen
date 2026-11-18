# Composición de la caja de diálogo en Zoom

La caja nativa mezcla su relleno y sus sombras con el fondo floral nativo. En la presentación Mejorada, el compositor guarda el color ya mezclado como píxel opaco de `foreground`. Zoom desplaza esa imagen y el fondo floral ampliado se pinta con su propia transformación. Por eso el patrón de flores queda fijado a la posición antigua dentro de la caja mientras el patrón exterior sigue el fondo del host.

La toma del usuario muestra el vestíbulo del teatro. El registro de diálogo que aparece en la captura está en `0100TBL.BIN`, ID 50035, índice 469. El ensayo del vestíbulo usa otro instante del mismo fondo. No se reutilizó una captura como fuente de píxeles para la prueba.

## Mezcla medida en Saturn

Se restauraron estados locales en el test.1 aislado y se capturaron, en un solo fotograma, la salida nativa de 320 × 224 y las máscaras y colores de las capas individuales. Se midieron los píxeles entre Y=153 y 219 donde solo tienen cobertura las capas 3 y 5 de la composición. La capa 3 es NBG1 y gana la prioridad. La capa 5 es NBG3 y aporta el fondo floral.

Los estados ordinarios tienen `CCCTL=0002`, que habilita el cálculo de color de NBG1, y `CCRNA=0A1F`, con razón 10 para NBG1. `SFCCMD`, `LNCLEN` y la ventana de cálculo están a cero en la muestra. El peso de NBG1 es 21/32 y el de NBG3 es 11/32. El resultado exacto por canal es `(21 * panel + 11 * fondo) >> 5`.

| Estado de origen | Igualdad RGB en la zona aislada | Glifos nativos visibles |
| --- | ---: | ---: |
| `after-options-3000.state`, vestíbulo | 14.043 de 14.043 | 111 de 111 píxeles iguales al color VDP1 |
| `office-return-3000.state` | 11.191 de 11.191 | 2.966 de 2.966 |
| `iris-correct-room-3000.state` | 12.599 de 12.599 | 1.492 de 1.492 |
| `office-return-6000.state`, mezcla de retrato aparte | 14.154 de 14.154 | Sin glifos del pie en la muestra |
| `resume-chapter-6000.state`, pie durante LIPS | 14.154 de 14.154 después de aplicar el desplazamiento de color | Sin glifos del pie en la muestra |

La capa 3 aporta colores RGB (248, 248, 248), (80, 80, 80) y (120, 120, 120) en las regiones medidas, incluidos el relleno claro y las sombras. Por ejemplo, en (56, 160) del vestíbulo, el fondo (232, 232, 184) y el relleno (248, 248, 248) dan (242, 242, 226). En (29, 153), el gris de sombra (80, 80, 80) se mezcla con (224, 240, 192) y da (129, 135, 118). Reducir toda la caja a blanco con una sola transparencia perdería esas sombras.

En el estado LIPS, `COAR/G/B=01F0` aplica −16 a los tres canales. Los 14.154 píxeles coinciden si se resta después del desplazamiento de bits y se limita a [0,255]. Restar primero solo al color superior dio cero coincidencias. En el estado de fundido de retrato, `CCCTL=0042` habilita también cálculo de color de sprites. La tabla mide exclusivamente los píxeles del panel fuera de la cobertura de sprites. Los glifos C510 de los tres estados ordinarios se cotejaron por nibbles de tinta no cero con la capa 0. En esos estados conservan los colores opacos de VDP1.

## Metadatos mínimos para recomponer

En el punto de composición nativa que ya conoce las capas ganadoras, capturar una receta de panel únicamente cuando la fórmula que se va a reproducir se aplique a ese píxel.

- Usar el `top` y el `second` reales, antes de la reasignación de `presentationSource`. En la primera implementación, admitir NBG1 arriba y NBG3 abajo con mezcla normal de dos pantallas. El ID de `source` por sí solo puede apuntar a la capa inferior. Por ejemplo, durante la entrada de la primera película, `CCCTL=000A` permite mezclar NBG3 y `PRINB=0500` le asigna prioridad 5, por encima de NBG1.
- Guardar el RGB superior de 24 bits antes de mezclar y el peso inferior (w = razón + 1). El valor 0 del peso puede indicar que se conserva el píxel opaco actual. El desplazamiento RGB firmado debe corresponder a la capa superior y aplicarse después de `>> 5`. Si se agrupa por línea o receta, conservar los cambios de registro del fotograma. Para un primer alcance limitado, usar solo desplazamiento cero y conservar los demás píxeles nativos.
- Preservar el camino actual para modos no reproducidos, píxeles con sombra de sprite adicional, retratos y ornamentos visibles. El RGB superior conserva las sombras que sí pertenecen a NBG1. Las operaciones sin receta válida siguen por el camino nativo.
- Cuando se borre tinta nativa para dibujar un glifo HD ya validado, capturar también la misma receta para el par de capas que usa `underSprites`. Consumirla únicamente en las posiciones donde se retire esa tinta. De lo contrario, las posiciones borradas volverían a mostrar el patrón floral fijado al origen. Los glifos nativos y los retratos visibles conservan su tratamiento y su orden.

Para cada píxel de destino, usar las transformaciones enteras vigentes para buscar el color superior en la caja y el color floral inferior en la posición de fondo que corresponde a ese mismo destino. Empezar con el fondo host sin desplazamiento de color para la mezcla y aplicar el desplazamiento de la capa superior una vez al final. Mantener el orden de dibujo de la imagen, su sombra y la caja. El denominador nativo es 32 y el truncado es entero. El alfa convencional de 8 bits tiene otro denominador.

## Validación propuesta

Verificar primero que la receta reconstruya todos los píxeles medidos cuando se alimenta con el fondo nativo. En vista Zoom comparar el límite superior e inferior de la caja con el fondo host en las mismas coordenadas y comprobar las sombras, el retrato y la posición del texto. Repetir con texto original y HD, y con un estado que tenga desplazamiento de color. Mantener paridad de hashes de fotograma del huésped y comprobar el fallback para mezclas fuera de alcance.

Las evidencias locales están en `local/work/dialogue-panel-audit`, con los hashes de estado, registros, capas de una sola captura y los recuentos de `exact-mix.json` y `offset-exact.json`. La auditoría valida el modelo de mezcla en las muestras indicadas. La recomposición en el host sigue siendo una propuesta.

`port/panel_compositing.h` implementa el cálculo por píxel en `CompositePanelPixel`. La receta expresa el peso inferior y el desplazamiento firmado posterior. Si la receta está vacía o excede los rangos admitidos, se devuelve el píxel nativo. `tests/test_panel_compositing.cpp` comprueba las muestras del vestíbulo, Iris y LIPS, más las saturaciones y el fallback. El renderer aún no captura ni consume estas recetas.

## Integración en desarrollo

Patch40 captura las recetas en el compositor y recompone el panel sobre el fondo host en coordenadas de pantalla. El encuadre y la región superior se conservan: en el testigo office-return-3000 a1440p, los12 hashes guest coinciden y todos los píxeles por encima deY1048 son idénticos a test.1. La diferencia RGB queda en(386,1048)–(2198,1440), dentro del grupo de diálogo y sus sombras. Revisión visual local aprobó la continuidad del patrón; esto no acredita aún todos los fundidos ni paneles del juego. Los glifosHD borrados usan receta underPanelMix; mezclas no soportadas conservan RGB nativo.

El mismo bloque conserva el fondo de mapa cuando el cursor oculta el borde: underSource prueba que el fondo inferior esNBG0 antes de usar underSprites. Desde map-room.state, tests/map-left-edge.movie reproduce200 fotogramas: test.1 cambia row-gradient→native, candidato permanece row-gradient, hashes guest idénticos y cero bloques interpretados. Evidencia privada local/work/map-left-edge-probe.
