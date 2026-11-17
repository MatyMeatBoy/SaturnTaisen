# Cargas de fondos de Saturn y su mod HD

Prioridad confirmada por el usuario: terminar Saturn; la ejecución y traducción PC quedan para después. Los recursos PC usados por el mod HD de Saturn sí están dentro de este trabajo.

## Comparación reproducible

Base77b43c6, SDK fijado por config/dependencies.json. Herramienta `tools/benchmark_backgrounds.py`, Clang23.1.3, optimizaciónO3 y SDL software renderer. Se invocan los mismos loaders que utiliza la presentación Saturn. Entradas:19 fondos Saturn únicos y19 alternativas del pack HD. Los originales90/91 son idénticos y no se cuentan dos veces.

Se conservaron binarios baseline/cambio, hashes de entradas y salidas y registros por recurso. Tres repeticiones por condición, alternando el orden. Caché fría significa caché derivada de fondos vacía; no se vació la caché del sistema operativo. Una ejecución concurrente con la suite de pruebas se conservó para correctitud y quedó excluida de las cifras de tiempo.

| Preparación del conjunto de38 fondos | Antes | Cambio |
| --- | ---: | ---: |
| Mediana, caché derivada vacía |5,284s|1,911s|
| Mediana, caché derivada preparada |0,279s|0,280s|

Los38 resultados son idénticos píxel a píxel en todas las comparaciones. Son tiempos del componente, no una medición del arranque completo, los frames del juego ni sus esperas de CD. La caché caliente no muestra una mejora general en esta comparación.

## Cambios verificados

- Caché binaria de superficies preparadas, con dimensiones, orden de bytes definido, versión, tamaño exacto y checksum de datos. Los archivos truncados, alterados o con dimensiones incorrectas se rechazan y regeneran. La escritura temporal se publica por reemplazo, conservando el archivo anterior si falla.
- Migración de las cachés PNG existentes. El contenido original y los masters generados no se modifican.
- Búsqueda acelerada del color más cercano, conservando exactamente la métrica RGB y el primer color en caso de empate. Contrastada con búsqueda exhaustiva para paletas de hasta1693 colores.
- Lectura acotada del master PNG y comprobación de dimensiones antes de decodificar. Hash y decodificación usan los mismos bytes leídos, evitando mezclar revisiones si se cambia el archivo durante la carga.
- Prueba con una escena nocturna real: una caché corrupta se regenera, restaura sus bytes y conserva el fondo mostrado.

La caché directa consume más espacio que PNG. Se está evaluando aparte la representación paletizada/RGB555 y compresión ligera, a petición del usuario; no se presupone que reducir bytes mejore la latencia. Resultados numéricos y límites en `saturn-background-loading.json`; evidencia detallada local bajo local/work/background-bench y local/logs.

La metodología OptiPort se comprobó contra9673006504bf6712b320da70965bc3f65f2dd41a. No se cambiaron los comandos ni los tiempos del CD invitado.
