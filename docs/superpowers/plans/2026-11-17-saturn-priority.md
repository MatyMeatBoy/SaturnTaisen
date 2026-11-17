# Prioridad Saturn hasta completar su alcance

El usuario confirmó que Saturn tiene prioridad. La ejecución y traducción de PC quedan aparcadas; se anotan hallazgos útiles, pero no se integra esa plataforma ahora. Sigue autorizado usar recursos PC para el mod HD de Saturn, incluidos sus fondos extendidos.

## Protección y evidencia

- v0.1.5 publicada e inmutable: e6910ec5152e070e10636e606dc219c3af94e62c. BAT principal y paquete estable conservados.
- Desarrollo: implementation/enhanced-v011, base77b43c6;0.2.0-dev. Sin trabajadores delegados.
- Los dumps, partidas del propietario y referencias originales permanecen locales. Pruebas con copias y perfiles separados.
- OptiPort comprobado contra9673006504bf6712b320da70965bc3f65f2dd41a; copia instalada idéntica. Se consultaron protocolo general, profiling, gráficos/memoria y adaptación de runtimes.

## Orden de trabajo

1. Medir y reducir la preparación de fondos de Saturn/HD sin cambiar sus píxeles, su calidad ni los tiempos del CD invitado. Comparar caché de fondos vacía y preparada, declarando que no se vacía la caché del sistema operativo.
2. Completar la integración del mod HD para Saturn y el selector de recursos, conservando texto opcional e identidades verificadas. No presentar una ruta PC jugable.
3. Revisar escenas, subtítulos, sombras, motivos y paletas; composición en enteros y máximo conjunto que cabe a distintas resoluciones. Mantener fallback original cuando falta una sustitución usable.
4. Completar ejemplos locales de presentación en launcher y selector inicial, ajustes y navegación con mandos; el launcher se cierra solo tras confirmar el juego listo.
5. Continuar validación de guardado, importación, progresión/batallas y cambio real de disco. Priorizar cualquier reproducción de bloqueo o pérdida de progreso sobre optimizaciones o decoración.
6. Completar mandos y RetroAchievements dentro del alcance confirmado, con pruebas y limitaciones explícitas.

## Hallazgos para más adelante

Registrar información de PC en la documentación de investigación existente, distinguiendo recursos útiles para Saturn de trabajo necesario para ejecutar/traducir PC. Las 19 identidades de fondos y su importación experimental siguen siendo útiles para el mod HD Saturn; la ruta de juego PC y sus guiones permanecen pendientes.

No usar una suite aprobada ni un checkpoint como prueba de campaña completa. Registrar trabajo implementado, verificado e integrado por separado.

## Bloque de caché compacta verificado

Patch20: caché lossless paleta8/RGB555/RGBA, migración de formato anterior, DEFLATE evaluado y desactivado por latencia. 64 pruebas aprobadas y 38 imágenes idénticas; comparación final 5,128 → 1,960 s de preparación, sin mejora general caliente. No equivale a acelerar toda carga del juego. Diagnóstico optativo del renderer y carga por fondo; búfer de tintado reutilizado.

Pendiente inmediato: separar preparación CPU de subida de texturas, medir trabajadores 1/2/4/8 según memoria y coste, y evitar preparación pesada en primer uso. GPU actual: composición Direct3D11 verificada; rasterizador Saturn GPU todavía no validado. Mantener los dos SH-2 coordinados.

## Ejecución: preparación multinúcleo

Base 7b2b126. Se ejecuta en la rama de desarrollo existente, sin agentes y sin tocar v0.1.5.

1. Separar preparación CPU de subida GPU, conservando los loaders públicos. Prueba: preparar desde trabajador sin renderer y contrastar caché/píxeles con carga existente.
2. Añadir preparación anticipada con trabajadores acotados, tareas que poseen sus entradas, parada y unión antes de cerrar SDL. Solo caché derivada; no se tocan discos ni partidas. Probar límites, cancelación, error y reinicio.
3. Medir 1/2/4/8 trabajadores sobre los mismos 38 fondos, comparando hashes y caché fría/caliente. Elegir configuración por evidencia.
4. Compilar runtime, validar escena real y suite, registrar patch21, revisar y subir bloque.

Ruling: la primera fase precalienta cachés sin retener superficies ni crear texturas desde trabajadores; la subida sigue en el hilo de ventana y el loader síncrono conserva su fallback. Evita cambiar la imagen mostrada mientras llegan resultados y acota memoria a los recursos en curso. No promete eliminar todavía toda pausa de primer uso.

Preparación multinúcleo: tareas 1–4 completadas. Patch21 validado contra árbol compuesto; build nativo aprobado; suite completa 67 pruebas en 122,711s. Escena completa idéntica con 0/4 trabajadores, 19 cachés futuras preparadas. Benchmark final de 38 imágenes: 2,102s (1 trabajador) → 0,478s (8), caché preparada 0,262 → 0,104s. Límites y memoria en docs/research/saturn-background-workers.*.

Revisión propia separada (sin delegación): se revisaron propiedad de entradas/superficies, afinidad SDL, cancelación antes de cierre, límites del pool, fallos de publicación concurrentes y ausencia de cambios en estado invitado. Se reprodujo y corrigió acceso denegado de Windows con ocho productores; aceptación solo tras comparación íntegra del resultado existente. Sin hallazgos críticos adicionales en este bloque. No sustituye revisión independiente ni campaña completa.
