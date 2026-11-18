# Sombra de la viñeta narrativa en el primer combate

La viñeta con los tres antagonistas aparece en la referencia inglesa `local/work/sakura/battle-entry-ref-002500.png`. La misma imagen sigue activa en el estado `battle-entry-ref-3000.state`, que muestra una línea posterior. Se comprobó la segunda muestra mediante una captura nativa de 320×224 y un sondeo de capas del mismo fotograma. **La viñeta de combate no proyecta una sombra rectangular.**

## Composición nativa

- La viñeta ocupa exactamente el rectángulo `x=16, y=8, ancho=288, alto=144` en VDP2 NBG3, capa 5 del sondeo. Su máscara contiene 41.472 píxeles válidos, todos dentro del rectángulo. El terreno queda visible a los lados y entre la imagen y el diálogo.
- Los sprites de las unidades y el cuadro de diálogo con su remate oscuro aparecen en VDP1, capa 0. La viñeta y el cuadro son piezas distintas.
- Los registros VDP2 del estado tienen `CLOFEN=007F`, `CLOFSL=0000` y `COAR=COAG=COAB=01FC`. Esto resta 4 a cada canal de la composición con saturación en 0. El ajuste afecta también a terreno lejos de la viñeta. `CCCTL=0001` habilita el cálculo de color de NBG0.

Se compararon las franjas donde caería una sombra desplazada hacia abajo y a la derecha, en coordenadas nativas y con límites finales exclusivos.

| Región | Comparación RGB |
| --- | --- |
| Derecha, X=304–308 e Y=8–152 | Los 576 píxeles coinciden con un plano visible tras el ajuste global de −4. |
| Debajo, X=20–308 e Y=152–156 | 972 píxeles coinciden con el plano visible tras el ajuste global. Otros 97 coinciden con la mezcla de color NBG0 con razón 0. Los 83 restantes coinciden con el oscurecimiento VDP1 a la mitad después del ajuste global, en la huella localizada de un sprite de unidad entre X=235 y X=268. |

La huella VDP1 debajo de la imagen ocupa 17, 20, 22 y 24 píxeles en esas cuatro filas. Está localizada en la unidad que cruza la franja y no forma una banda rectangular bajo el cuadro.

## Presentación Mejorada

Con el binario aislado de 643.320 bloques, los dos perfiles de prueba registraron `native` para este estado. El área central completa de 320×224 coincide píxel a píxel entre Original y Mejorada, y coinciden los 12 hashes del juego. Una captura previa del mismo estado con la traza `tactical` y la extensión lateral activa también coincide en cada píxel del centro. La ruta táctica amplía terreno a los lados. La escena observada no usa el pase de sombra del Zoom narrativo.

Si se recompone esa viñeta en una presentación futura, corresponde conservar el borde sin sombra de la imagen, el remate del cuadro de diálogo y las sombras locales de las unidades. La prueba se limita a esta viñeta táctica del capítulo 1.

Los artefactos están en `local/work/battle-story-inset-shadow`. `frame1/frame-000001.png` y `frame1/layer-layer{0..5}*.png` contienen la captura y los planos sincronizados. `check-frame1.py` repite el recuento. La captura panorámica anterior está en `local/work/chapter1-wide-state-coverage-v2/battle-entry-ref-3000/shot.png`.
