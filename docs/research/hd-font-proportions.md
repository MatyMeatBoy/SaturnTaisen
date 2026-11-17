# Proporciones de la fuente HD

El escalado independiente de cada glifo a su caja de tinta nativa ensanchaba letras estrechas y alteraba sus proporciones. Ahora toda la fuente recibe una transformación uniforme, calculada con el avance y la altura de mayúsculas de referencia. Se conserva el avance del juego de ocho píxeles y una línea base común.

La detección verifica los píxeles de tinta dentro del interior nativo (56,160)–(304,208), permitiendo el último glifo cuando su textura contiene margen transparente. El dibujo HD se recorta al mismo interior proyectado. Texto original y HD siguen siendo opciones independientes.

Verificación: fixture tests/test_text_layout.cpp cubre bordes, tamaños inválidos, letras estrechas, altura y línea base, y viewports enteros a varias resoluciones. Captura real local: local/work/text-layout-qa/natural/scene.png. Compilación nativa correcta; conjunto frontend/matching: 24 pruebas correctas. Esto no constituye una revisión de todos los diálogos.
