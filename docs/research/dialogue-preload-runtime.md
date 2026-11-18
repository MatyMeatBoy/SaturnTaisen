# Precarga y testigo del diálogo nativo

Patch0048 prepara un catálogo inmutable del disco antes de dibujar el texto HD. Conserva ID, índice, offset, prefijos y bytes originales; precompila las líneas CP1252 sin corregir la prosa ni las traducciones. El contenido extraído permanece en `local/`. Este bloque añade la precarga y el observador; el render todavía usa su reconocimiento de glifos existente.

## Identificación

En cinco estados privados, el BE32 de High WRAM `0x0606851C` señala el texto del registro actual. La tabla completa está en Low WRAM `0x00224000`. El testigo exige ambos bancos de 1 MiB y coincidencia byte a byte de toda la tabla, no solo del registro o de su ID. Rechaza tablas alteradas, coincidencias ambiguas y punteros fuera del texto. La posición del terminador NUL es válida. No atribuir semántica a los prefijos sin evidencia adicional.

| Muestra | Tabla | ID | Índice | Offset del prefijo |
| --- | --- | --- | --- | --- |
| Sumire | 0100TBL.BIN | 50039 | 473 | 32930 |
| María | 0100TBL.BIN | 50064 | 498 | 34408 |
| Iris | 0102TBL.BIN | 10507 | 546 | 34608 |
| LIPS de dos opciones | 0102TBL.BIN | 10250 | 284 | 21420 |
| LIPS de tres opciones | 0102TBL.BIN | 10035 | 63 | 11110 |

En LIPS, un puntero identifica un registro procesado, no el conjunto completo de opciones. El puntero también puede persistir al desaparecer el diálogo: no basta para decidir que debe mostrarse una página. La integración visual posterior debe verificar los glifos y su máscara de revelado del mismo framebuffer.

## Límites y ciclo de vida

El lector rechaza el tamaño declarado antes de reservar o leer; una lectura incompleta deja la salida vacía. El catálogo admite como máximo 128 tablas, 8 MiB de fuente y 65.535 registros; cada parser TBL admite hasta 4 MiB. Se sella antes de publicarlo mediante `shared_ptr<const DialoguePreload>`. Los nombres repetidos y las adiciones después del sellado se rechazan.

Los 56 TBL ingleses contienen 29.725 registros y 2.242.176 bytes fuente. Hay 29.723 registros preparables como hasta cuatro líneas de 31 columnas. Los otros dos conservan sus tabuladores y quedan marcados como no preparables; no se truncan ni se sustituyen por espacios. Las tablas son idénticas entre los dos discos ingleses comprobados.

La preparación se activa una vez, con atlas inglés verificado, Mejorado y texto HD. También se consulta al cambiar de modo en el menú. Original, headless y el backend GPU activo no preparan el catálogo; al volver a Original o texto nativo no se busca un registro por fotograma. La ruta observada es la de software predeterminada del proyecto.

El callback de la máquina captura el testigo junto a los píxeles bajo `fbMutex`; SDL copia ambos juntos. Esto evita consultar la RAM ya restaurada después de run-ahead. No se serializa con el huésped. `SATRECOMP_DIALOGUE_TRACE` informa una preparación por sesión y cambios del registro mostrado, identificados por el serial del framebuffer.

## Evidencia y límites

La prueba sintética de lectura falló por ausencia de la API y luego pasó con archivo válido, tamaño excesivo, archivo ausente y lectura parcial. El fixture del catálogo pasó con Clang y cubre límites, sellado, CP1252, controles, geometría y punteros. Un programa privado leyó el corpus completo y las cinco muestras; alterar el último byte de cada tabla invalidó el testigo.

Build de desarrollo de 674.023 bloques: SHA256 `191e2e0a701bc0624727ea09fd06ba4caf836ecf4f824cca451bd09172907bf2`. La comparación integrada usa como referencia el candidato patch0047, sin modificar los paquetes entregados. Resultados privados en `local/work/dialogue-preload-runtime/result.json`, con logs, hashes y capturas por perfil. Catorce ejecuciones cubrieron Sumire, María, Iris, LIPS de dos/tres opciones, Original e Iris con run-ahead2. En cada par coincidieron los60hashes, tres capturas RGB nativas y una captura GUI a1440p:420hashes comparados,21pares nativos y siete pares GUI. Todos terminaron con cero interpretados. Cada ejecución Mejorada registró una sola precarga y el registro esperado; Original no precargó. Los tiempos de preparación de esas ejecuciones no acreditan una mejora del rendimiento de carga del juego.

Pendiente: dibujar desde las líneas precargadas con máscara de revelado nativa, mantener placas/clip/fundidos, identificar todos los registros de elecciones y verificar la cobertura por ruta. Ni el catálogo completo ni cinco testigos prueban que todo el texto HD esté resuelto. No incluido en v0.2.0-test.2.
