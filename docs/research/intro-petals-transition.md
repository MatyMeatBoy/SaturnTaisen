# Pétalos, destello y primera película de New Game

Auditoría de presentación con `sakura-test1.exe` de 614.024 bloques, SHA-256 `67ef0bdc41321bd19231f637070d6dd39fe6bd17df63527dffde61aa4a79cbb7`. Se usaron el disco 1 inglés y una copia del arte de la versión test.1 en cada perfil aislado. Las capturas y estados permanecen en `local/work/intro-petals-audit`. La ventana de prueba mide 1280 × 720. Los pasos de ventana se numeran desde uno.

## Apertura y título

| Reproducción | Evidencia |
| --- | --- |
| Desde `intro2399.state` sin pulsaciones | El fondo de apertura se funde a negro antes de entrar al título. En `title-petal-fine`, aparecen pétalos pequeños en 3990 y un pétalo gigante en 4026. El marco nativo aparece exactamente en los pasos 4027–4037 y desaparece en 4038. |
| Desde `intro1799.state` con `chapter1-opening-skip.movie` | La apertura se funde a negro tras Start y reaparece el título. `skip-fine` contiene el mismo marco en los pasos muestreados 726, 728, 730, 732 y 734. |

El título mantiene la huella de paleta `91E480C617AD7F6C`. La capa 5 de VDP2 conserva cobertura de 71.680 píxeles en los sondeos. El área visible del título se reduce al quedar tapada por la capa 0 de VDP1. Su máscara cubre 17.928 píxeles en el sondeo 3990, los 71.680 en los de 4026 a 4036 y 19.283 al volver el título en 4037. La selección del fondo exige al menos 1.000 píxeles visibles de su capa. Al desaparecer esa cobertura efectiva, el layout pasa a `native` y dibuja el marco del host.

Los pétalos llegan a VDP1 en una textura dinámica de 320 × 224. El comando normal en VRAM `00100` usa fuente `3A800`, coordenadas (0, 0), modo `00A8` y color `0000`. La textura de la muestra 4032 tiene SHA-256 `0620c6da882b0e2d29a6eb5c1fe88abb94e7d8c4b52179e273b327b9fb0cb`. El módulo `/SAKURA1/LOGO.SH2` coincide completo en Low WRAM en `00204000` durante las muestras 3990, 4026, 4032 y 4038. Tiene 243.200 bytes, LBA 160804 y SHA-256 `0745216059e495e7ba45faf1657bc045317579186bc539802d35b9567cb483ca`. El hash de la textura cambia durante el efecto y sus bytes completos no se encontraron como región estática del módulo.

La imagen nativa 4032 tiene rangos R=229–232, G=212–215 y B=228–230. La imagen 4038 tiene 69.298 píxeles blancos de 71.680 y conserva detalles tenues del título. Un detector de negro o blanco uniforme deja fuera parte del destello. La textura dinámica termina en el borde del cuadro nativo. La auditoría identifica la pérdida de encuadre y la procedencia del efecto. La continuidad de los pétalos en las franjas exteriores queda por implementar.

## New Game y la película narrativa

La ruta continua `new-game-film` usa `title-final.state` y `tests/chapter1-title-new-game.movie`. Registra 6.300 fotogramas en AOT estricto y cero bloques interpretados.

| Fase | Muestra y fuente |
| --- | --- |
| Cierre de Program | Paso 268 con marco nativo. Los pasos muestreados 272–292 son negros a pantalla completa. |
| Carga | Sondeos 400 y 650 con `anchored-menu`. Capa 4 ocupa 71.680 píxeles, paleta `74EA8ADC9B0340CC` de `LOAD.BIN`. |
| Antes de la película | Paso 736 muestra el fondo KABE00 oscurecido, el pie vacío y una sombra rectangular de imagen. El sondeo tiene capa 1 ausente, capa 0 de 1.214 píxeles y capa 3 con contenido desde Y=12. En 840 aparece el distintivo de la esquina, todavía sin capa 1. |
| Película activa | Los sondeos 880, 920, 1200 y 5700 muestran 41.472 píxeles de capa 1 en (16, 8) a (303, 151), región nativa de 288 × 144. El paso 1132 muestra el panorama urbano y conserva el distintivo y el pie vacío. |
| Salida de la película | La imagen blanca de los pasos muestreados 5704–5884 pertenece todavía al recuadro de película. En 5920 se ve el fundido hacia KABE00. Los pasos 5956, 5992 y 6028 muestran flores con el pie vacío. En el sondeo 6000 ya no hay capa 1, la capa 0 vuelve a 1.214 píxeles y la capa 3 queda debajo de Y=160. En 6064 desaparece el pie. A partir de 6100 se ve el rótulo del episodio, una transición aparte. |

El layout anuncia `movie` mientras muestra el panorama con el pie. El bbox que devuelve `AnalyzePresentation` comprende las capas de imagen y pie, y la rama `movieOnly` extrae ese bbox del framebuffer nativo. En las muestras activas el bbox combinado llega de (9, 8) a (314, 219). Es el origen del pie dentro del recorte de película. La capa 1 trazada por separado delimita el recorte de vídeo de 288 × 144.

El pie usa un comando VDP1 modo `00A0`, color `C500`, en (8, 152), de 304 × 64. El distintivo usa modo `00A0`, color `C400`, en (16, 160), de 40 × 48. Los estados muestreados entre 736 y 6000 carecen de los glifos 16 × 16 con colores `C510` o `C570`. La capa 3 aporta el relleno y las sombras y la capa 5 conserva KABE00, paleta `48291F6F1C8A4707`. Los 15.404 bytes de `0100.BIN` y los 54.018 de `0100TBL.BIN` coinciden íntegramente en `00204000` y `00224000` en las muestras de todo el tramo.

La primera película narrativa está dentro de `/SAKURA4` en el desplazamiento 23.695.360, con 21.714.028 bytes, 2.354 muestras STAB e imagen de 288 × 144. SHA-256 `610cb5c5538896968c457937d7101783dfe20d073ae58c0f948ee9ed1eb5dd02`. Sus primeros 128 bytes están presentes en High WRAM `06080000` durante los sondeos activos y también en 6000, donde ya está presente la cabecera del siguiente flujo en `060B0000`. La cabecera residente sirve para identificar el recurso y la capa 1 visible aporta evidencia de la imagen reproducida. El pie vacío en una escena cualquiera requiere conservar su comportamiento nativo. Las muestras pre y pospelícula pertenecen a la transición observada de `0100.BIN`.

Los estados extraídos sirvieron para sondeos puntuales. Intentar reanudar secuencias largas desde las muestras 840 y 5700 produjo hashes distintos de los de la reproducción continua, así que los pasos y la secuencia visual se tomaron de la ruta continua.

## Candidato PC

El ffprobe local inventarió 52 MPEG. `MOVIE000.MPG` es un candidato visual para la apertura, con MPEG-1 de 576 × 288, audio MP2 y duración de 85,942856 s. SHA-256 `8fb04101f255ac257e027d18d5d324d115b47ef1eb14b9bada64ab70aa25dd10`. Las muestras PC de aproximadamente 10,125 y 30,25 s muestran los mismos planos que las capturas Saturn 1200 y 2400. La muestra Saturn 1800 no tuvo una coincidencia cercana en el muestreo. La comparación identifica material compartido y deja por medir el montaje completo, la sincronía y los subtítulos. El vídeo PC sigue fuera del runtime.
