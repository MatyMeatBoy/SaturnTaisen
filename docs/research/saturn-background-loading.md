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

La representación final usa paleta de 8 bits o RGB555 cuando reproduce exactamente todos los colores, con RGBA como alternativa. El conjunto ocupa 16.145.238 bytes frente a 39.312.064 de RGBA directo. DEFLATE reduce a 5.368.794 bytes, pero eleva la mediana caliente de 0,251 a 0,290 segundos y la preparación de 1,920 a 2,059 segundos: queda desactivado por defecto. La lectura admite la versión anterior de caché y rechaza datos sobrantes o truncados. Resultados numéricos y límites en `saturn-background-loading.json`; evidencia detallada local bajo local/work/background-bench y local/logs.

La metodología OptiPort se comprobó contra9673006504bf6712b320da70965bc3f65f2dd41a. No se cambiaron los comandos ni los tiempos del CD invitado.

## Comparación final y límites de la siguiente etapa

La comparación final independiente, tres repeticiones alternadas con 38 imágenes idénticas, registra 5,128 → 1,960 segundos con caché derivada vacía, y 0,268 → 0,274 segundos preparada. No hay mejora general demostrada en caliente. Las 64 pruebas pasan; incluyen round-trip de formatos, compatibilidad anterior, corrupción y regeneración en escena real. Resultados en `saturn-background-compression.json`.

Una observación de la escena nocturna a 1280×720 con Direct3D 11 registra 55,374/5,277 ms de CPU para cargar el fondo Saturn en frío/caliente, y 61,309/12,559 ms para HD. Incluye llamadas de subida, pero no espera de GPU ni demuestra frame pacing. Queda trabajo para evitar el coste de primer uso.

El equipo observado tiene Ryzen 7 7435HS (8 núcleos, 16 hilos) y RTX 4060 Laptop. La composición SDL ya usa Direct3D 11; la rasterización Saturn sigue en CPU. Preparar recursos independientes es candidato a paralelismo acotado. Las texturas del renderer de ventana deben crearse/usarse en su hilo; la preparación CPU debe separarse antes de introducir trabajadores. No se paralelizan los SH-2 sin preservar su memoria y temporización compartidas.
