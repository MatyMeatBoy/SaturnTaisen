# Retratos HD durante mezclas blancas

Patch 0037. La guarda anterior compara el retrato nativo sin efectos con el framebuffer ya mezclado por VDP2. Una diferencia válida causada por la mezcla blanca provoca fallback. Permitir simplemente un color aproximado sería incorrecto: dibujaría el HD sin el fundido y podría aceptar un sprite tapado.

El compositor conserva por píxel si el sprite participa realmente en una mezcla blanca y con qué peso. Sombras, offsets no nulos, mezclas aditivas o efectos no probados invalidan ese dato. La sustitución exige el mismo peso aceptado y la coincidencia RGB exacta de **todos** los píxeles opacos del retrato presentado. Se aceptan los pesos observados 5, 15 y 25 sobre 32, además del caso sin efecto. La textura HD recibe la transformación entera correspondiente, conserva su alfa y su clave de caché incluye el peso. Ninguna inferencia de blanco se realiza solo por el parecido de los colores.

## Validación

- `test_portrait_match.cpp`: mezcla exacta, pesos admitidos, alfa, metadatos incompletos, píxeles ocluidos/diferentes y caso sin efecto.
- `test_vdp2_color.cpp`: el compositor real mezcla un sprite sintético sobre blanco con pesos 5/15/25, emite el peso correcto y produce exactamente el RGB de la transformación HD; la mezcla aditiva se rechaza. No se duplica la fórmula como oráculo independiente.
- Build aislada del renderer/frontend aprobada; no se sustituyó el ejecutable compartido.
- Dos puntos de Yoneda (`office-return-3000` y `6000`) ejecutaron 132 fotogramas cada uno con cero bloques interpretados y mantuvieron la sustitución sin efecto. El replay adicional de 1.800 fotogramas no observó mezcla blanca; no se usa como prueba positiva del fundido.
- `morning-9000.state`, SHA-256 `81de5f7ba12e092b174ee98a64e386c979460cc17d8c0b13b9407850668ca2b8`, sí confirmó el retrato `0009` con mezcla **25/32** y densidad HD2 a 2560×1440. Los 132 hashes por fotograma coinciden con test.1. En esta muestra concreta el RGB presentado coincide exactamente con el nativo, por lo que no se atribuye una diferencia visual inexistente. El registro demuestra que se acepta y transforma el HD durante la mezcla.
- `test_portrait_white_runtime.py` compara HD activado/desactivado en ese testigo, exige el trace `density=2 white_mix=25`, cero bloques interpretados y paridad guest/RGB. Los pesos 5/15 quedan cubiertos por el compositor sintético, no por una ruta real anunciada como probada.

Los estados, packs, imágenes y logs quedan privados bajo `local/work/portrait-white-*`. La mejora está preparada para futuras builds; los ZIP publicados no se reemplazan. Quedan pendientes otras animaciones, identidades sin match, efectos distintos y pruebas físicas de interacción.
