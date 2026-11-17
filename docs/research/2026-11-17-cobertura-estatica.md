# Ampliación de cobertura estática

`tools/static_program.py` utiliza las definiciones SH-2 de la dependencia fijada. Extrae el primer archivo regular de la raíz ISO9660 y su dirección de carga de la cabecera Saturn, sin extraer recursos a rutas elegidas por la imagen. Comprueba los límites de cada extensión y las copias little/big endian de los campos de directorio. También admite imágenes binarias con una base explícita.

El análisis sigue llamadas y ramas directas, retornos de llamadas y punteros alineados que apuntan dentro del programa. Reconoce el patrón de switch `MOVA / MOV.W / ADD / JMP`, con límite obtenido de una comparación unsigned `CMP/HI` y su rama de exclusión. Incluye la variante que coloca la copia del índice en el delay slot. No adivina el final de una tabla recorriendo datos vecinos.

La primera ampliación por punteros añadió 4.209 candidatos al conjunto que se había obtenido jugando. La continuación encontró una entrada ausente en `0x0601AB1A`; el análisis del código identificó una tabla de offsets relativos. El reconocedor se probó primero con un programa sintético que fallaba, después con el caso real. Otros patrones y destinos observados se incorporaron mediante descubrimiento instrumentado, sin introducir un intérprete SH-2 de respaldo en producción.

El informe `static-program-analysis.json` registra hashes y conteos de los cuatro programas iniciales: dos discos, traducción inglesa y japonés original. La ampliación inicial reunió 16.767 variantes. El análisis exhaustivo posterior conserva todos los prefijos decodificables desde direcciones alineadas: el conjunto combinado actual tiene 253.159 variantes, sin funciones agrupadas. Esto incluye entradas alternativas y candidatos sin ejecutar: el número no equivale a porcentaje del juego completado.

## Evidencia de ejecución

- La continuación de 18.001 fotogramas desde el estado del teatro coincide, fotograma a fotograma, entre intérprete y AOT con 12.943 variantes. Informe local `post-theater-parity.json`.
- Tras ampliar a los cuatro programas, los 4.200 fotogramas del arranque conservan los hashes del intérprete de referencia anterior. El runtime acepta las reglas de los 16.767 bloques, sin avisos de incompatibilidad.
- La inspección de María permite mover el cursor, observar zonas distintas y seleccionar la boca para continuar la conversación. La ruta de 4.201 fotogramas llega después al diálogo con Yoneda bajo AOT estricto.
- 22 pruebas Python pasan, incluidas extracción ISO truncada, llamadas/punteros, ramas, tablas relativas acotadas y delay slots inválidos. Se conserva una advertencia ResourceWarning del lector de definiciones del generador upstream; no es un fallo de las pruebas.

Los estados son únicamente instrumentos locales de investigación con el mismo runtime y la misma imagen. No sustituyen validar el guardado del juego ni su identidad entre perfiles. Siguen pendientes otras rutas, combate, minijuegos, sonido contrastado con referencia y cambio real de disco.

El conjunto exhaustivo conserva también el prefijo de 47 instrucciones cuando el siguiente salto necesita su delay slot. Con 253.159 variantes, el arranque de 4.200 fotogramas conserva los hashes anteriores y una continuación de 12.001 fotogramas desde el puesto de venta se ejecuta en AOT estricto hasta el menú de opciones original. Los 12.001 hashes de esa continuación coinciden con el intérprete; la referencia se repitió tras aplicar el parche de caché CD. La navegación con pulsaciones de 30 fotogramas permite seleccionar Exit y salir al menú de objetos.

El parche 0007 invalida la caché de sectores al reinstalar el lector de disco. Una prueba sintética reproduce primero el sector obsoleto y verifica después el contenido del nuevo medio en el mismo FAD. No equivale a una transición de campaña validada.
