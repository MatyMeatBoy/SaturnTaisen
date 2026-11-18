# Precarga y testigo del diálogo nativo

Patch0048 prepara un catálogo inmutable del disco antes de dibujar el texto HD. Conserva ID, índice, offset, prefijos y bytes originales; precompila las líneas CP1252 sin corregir la prosa ni las traducciones. Patch0049 usa vistas de esas líneas para la narrativa verificada. El contenido extraído permanece en `local/`; las elecciones LIPS conservan su reconocimiento por glifos.

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

## Consumo visual de las líneas precargadas

Patch0049 compara cada mosaico observado con el byte esperado del registro del mismo framebuffer. Una fila solo toma la vista del catálogo si sus celdas coinciden y no faltan letras antes de la última celda visible; los huecos de espacios son válidos. La vista termina en esa última celda, por lo que no adelanta letras. El catálogo sellado pertenece a Port durante toda la sesión; mover la lista de dibujo no deja referencias a cadenas temporales.

La rejilla medida de los comandos empieza en x=64, con avance8 y filas160/172/184/196. El recorte de tinta conserva x=56: son límites distintos. Una prueba real detectó que el prototipo con origen56 permanecía en fallback; además de comparar imágenes, las pruebas exigen trazas `catalog=1`. La inspección de las263filas de31caracteres del corpus encontró un espacio al final de todas ellas. La guarda de tinta sigue rechazando contenido que salga del interior probado.

Se conservan la fuente precocinada, avance, línea base, clip, color y comprobación de placas/propietarios. Cuando no hay una fila probada se conserva la ruta de reconocimiento anterior. Los tres alias de bitmap detectados en el atlas inglés (bytes0x82/0xA0/0xAD) no aparecen en ninguno de los29.725registros; otras localizaciones deberán revisar su desambiguación antes de habilitar el mismo mapeo. Los dos registros con tabulador no se convierten por esta vía.

El candidato674.182/patch0049 tiene SHA256 `377cb29b9e05d2f70d8a97c838e0cd9ccc511046ff690da54953b60dac5a0ba7`. Se comparó contra el host0048 del candidato postcombatee7dd1c0…, conservando el código guest. Los siete casos iniciales comprobaron420hashes,21pares RGB nativos y siete GUI a1440p. Incluyen Original, run-ahead2 y las dos elecciones existentes; estas últimas no acreditan texto LIPS desde el catálogo.

Otros seis casos comprobaron960hashes y50pares RGB nativos/GUI: revelado parcial de cuatro filas, página completa, continuación de segunda fila, biblioteca de cuatro filas, muestra de oficina y avance conB durante una voz. Las trazas verificaron el uso efectivo del catálogo, también en y=196 y desde una sola letra visible. Los1.380hashes y78pares RGB de ambas suites coincidieron, con cero interpretados. Evidencia privada: `local/work/dialogue-render-runtime-v2/result.json` y `local/work/dialogue-render-dynamic/result.json`.

La transición mapa→floral/novela añadió900hashes y26pares RGB iguales (17GUI y nueve nativos), con muestreo de la entrada/fundido entre400y550 y del diálogo posterior. La traza también confirmó consumo del catálogo. Evidencia: `local/work/dialogue-render-map-fade/result.json`. Total de las tres suites:14casos,2.280hashes y104pares RGB, todos iguales a la referencia y con cero interpretados.

Pendientes: identificar los conjuntos completos de elecciones, probar vencimiento de LIPS y ampliar cobertura por ruta/capítulo, transiciones y fuentes de otras traducciones. Ni el catálogo completo ni estas muestras prueban que todo el texto HD esté resuelto. No incluido en v0.2.0-test.2.
