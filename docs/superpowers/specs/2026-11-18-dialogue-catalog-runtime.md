# Catálogo de diálogo precargado en runtime

Alcance solicitado por el propietario: usar los guiones del juego como datos internos precargados para el texto HD, conservando fuente/tamaño/espaciado aprobados, revelado, voces, elecciones y Original. Los textos y dumps del propietario permanecen en local/ y no se publican. Esta especificación concreta el trabajo T11 ya solicitado; no cambia el encuadre ni añade una selección nueva al jugador.

## Evidencia

El disco1 inglés contiene56TBL distintos,2.242.176bytes y29.725registros con1.190.080bytes de texto. Hay29.723registros con un máximo de4filas/31columnas y sin controles desconocidos; los dos restantes tienen tabulador. Los mismos56TBL están en disco2. No modificar los tabuladores ni los prefijos sin probar su significado.

En estados v9, la palabra BE32 de HighWRAM0606851C señala el comienzo del texto: Sumire50039 yMaría50064 en0100TBL, Iris10507 en0102TBL. Las tablas completas coinciden en LowWRAM00224000. El cursor del intérprete060685B4 es otro dato y no debe confundirse con el puntero de texto. En elecciones puede quedar el último texto procesado: no atribuir todas las opciones a ese único registro.

## Diseño

Preparar una caché inmutable desde los TBL del disco del usuario. Mantener bytes exactos para identificar la revisión, IDs/prefijos/offsets sin reinterpretar, y líneas UTF32 listas. Acotar lecturas y presupuesto antes de asignar. No generar ni incluir guiones originales en Git.

Capturar un testigo de contenido con cada framebuffer, antes de restaurar RAM de run-ahead. Solo resolver un registro si la tabla completa coincide y el puntero queda en su texto. No buscar por fragmentos ambiguos ni tratar una cabecera FILM residual como fase. La caché y los testigos son datos host, fuera del estado guest.

La primera etapa prepara y verifica el vínculo; todavía no cambia el dibujo. La siguiente etapa usará líneas precargadas y máscaras de revelado nativas, conservando las placas exactas de glifos, colores, clips y posiciones actuales. Los casos no probados conservan el comportamiento existente. No llamar finalizada T11 por tener un observador.

## Invariantes

Windowsx64, C++20 y SDK fijado. Máximo16:9, escala entera, Original y Zoom aprobados intactos. Hashes guest y RGB nativo iguales antes/después; muestras GUI iguales mientras solo se añade el observador. Catálogo ligado a bytes de origen; una tabla de otra traducción no se acepta por compartir IDs. Sin trabajo auxiliar nuevo en headless o en Original antes de activar HD. Sin sincronización RA ni red dentro de este bloque.
