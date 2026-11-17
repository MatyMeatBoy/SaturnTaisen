# Herramienta de matching HD y aplicación Saturn

Alcance autorizado: programa para emparejar la mayoría de recursos y calzarlos en el recomp, adaptándose a las resoluciones; revisión del texto dentro de su caja. Se ejecuta en la rama de desarrollo existente, sin agentes y sin alterar v0.1.5.

## Contratos

- Inputs originales de solo lectura. Proyecto de matching, previsualizaciones y derivados bajo local/. Sin subir sprites propietarios.
- Comparación de imágenes normalizadas para análisis; la salida de juego usa rejillas y escalas enteras. Coordenadas/anclajes guardados en unidades nativas.
- Variantes de densidad1 y2: si la escala del viewport es impar se usa la variante1, si es divisible por2 se puede usar la variante2. Se conserva el tamaño máximo del conjunto y no se introduce un factor fraccional de presentación.
- Propuestas por distancia visual y margen frente al segundo candidato. Empates/identidades conflictivas requieren revisión. El parecido no se presenta como probabilidad de acierto.
- GUI local para comparar, elegir candidato, ajustar anclajes y exportar. La exportación produce un proyecto JSON y manifiesto INI con identidades nativas y archivos preparados; publicación atómica.
- Runtime: solo sustituir texturas identificadas y con recursos completos/usables. Validar dimensiones, versiones, rutas, checksums y origen PC conocido. Fallback original en cualquier fallo. Recursos de renderer solo en su hilo.

## Tareas

1. Texto: validar tinta real frente al interior56,160–304,208; evitar sustitución parcial de la última letra y recortar el texto mejorado al interior proyectado. Probar bordes y escalas720p/1080p/4K/ultrawide; probar escena real.
2. Core matching en tools/hd_matching.py: preparar catálogo nativo FCE usando paleta de un estado local validado y catálogo PC de imágenes del decoder existente; ranking, márgenes, hashes y variantes enteras. Tests sintéticos de identidad, ambigüedad, anclajes, alfa y escalas.
3. Interfaz en tools/hd_matcher_ui.py y tools/match_hd_assets.py: revisión por recurso, siguiente pendiente, teclado, persistencia y exportación de resultados aceptados. Servidor solo loopback; imágenes bajo catálogo local. BAT local para abrirlo.
4. Primer consumidor: retratos narrativos40×48 y parches40×16 identificados por bytes nativos, paleta y modo. Aplicación conjunta de piezas conocidas; no reemplazar un retrato a medias. Validación en escena real y opciones del menú.
5. Extender el mismo pipeline a cuerpos NC cuando se verifiquen sus partes/anclajes; no interpretar diferencias de tablas como índices equivalentes.

## Evidencia inicial

El retrato de la escena de Iris coincide por bytes con la identidad FCE0x0015. Su paleta de la captura reproduce los colores originales y su mejor candidato PC es20. En304 retratos, el ranking visual20×40 devuelve la hipótesis ID−1 como primera opción en293 casos y dentro de los primeros5 en304. Con umbral0,06 y margen0,008 se preseleccionan194 casos y todos concuerdan con esa hipótesis. Esto es evidencia para priorizar revisión, no verificación artística de todos los pares.

Ruling: comenzar la aplicación por retratos, cuyo formato nativo y enlace con una textura real ya están demostrados, mientras el matcher admite catálogos PNG de otros recursos. Los cuerpos completos no se declaran integrados por disponer del catálogo.


## Avance verificado

La fuente HD conserva ahora una transformación uniforme para toda la tipografía, referenciada a la altura de mayúsculas del original. Se mantiene el avance nativo de 8 píxeles; las letras estrechas no se ensanchan individualmente. Se recorta al interior del diálogo y se comprueba la tinta real de los glifos. La opción de texto original sigue disponible.

El catálogo contiene 304 identidades nativas y 394 candidatos PC. Tras descartar conflictos entre propuestas, quedan 191 preseleccionadas y 113 pendientes. No equivalen a 191 comparaciones artísticas aprobadas.

Uso local: `python tools/match_hd_assets.py --serve --open`. Permite comparar, ajustar desplazamientos nativos, aceptar/omitir y exportar. El pack solo usa recursos locales del propietario y valida identidad, dimensiones y hashes. Las variantes de densidad 1/2 preservan escalado entero. Los cuerpos NC todavía requieren verificar su formato y anclajes.

Primera escena real: la sustitución del retrato 0x0015 a 1280×720 cambia exclusivamente el rectángulo (202,498)–(322,642) respecto a la captura sin HD. El resto de la escena permanece idéntico. Las expresiones se identifican por bytes, incluyendo parches con transparencia; coincidencias ambiguas conservan el original. Esta evidencia no valida toda la campaña ni todas las expresiones.

Compilación nativa correcta y 24 pruebas de frontend/matching correctas. Quedan la validación completa del conjunto, revisión artística y pruebas adicionales de resoluciones/expresiones.
