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

Launcher HD: tarjeta MOD HD · SATURN implementada. Selección de carpeta o ruta escrita, normalización de carpetas SAKURA1/WALL, verificación/preparación en proceso aparte, selección persistida solo después de completar los 19 fondos y control Activados/Desactivados independiente del texto. El launcher sigue dibujando mientras prepara; el callback de diálogo conserva estado compartido hasta el cierre. Build y prueba de descripción aprobados. Captura real y activación con mando virtual verificadas en perfil aislado: 19/19 preparados con 8 trabajadores, cero fallos. No ejecuta el juego PC ni importa su traducción.

Ampliación explícita del usuario: el HD Saturn incluye sprites de chicas, otros personajes, retratos y expresiones. Inventario reproducible y decodificación del runtime: 147 NC, 3.596 imágenes, 147 nombres con candidatos en Saturn. KAO/KAO_P inventariados aparte. Máscaras y composición aún pendientes; todavía no se dibujan personajes HD. Véase docs/research/saturn-hd-characters.md.

Hallazgo derivado de la investigación solicitada: MAC.L saturado incluía bits inactivos en ambas rutas; reproducción sintética registrada antes del cambio. Ruling: corregir esta semántica antes de seguir con integración visual, porque es un defecto concreto compartido por nativo/referencia. Patch23 registrado; 11.616 casos por ruta y 11 pruebas de máquina aprobados. Regeneración AOT y build del juego aprobados; suite completa en curso. No se atribuye este caso a un bloqueo observado ni se afirma campaña completa.

MAC.L: build completo aprobado (580.328 bloques, 708 archivos regenerados), suite completa 68 pruebas en103,707s, incluidas rutas reales de600 y4.200 frames con cero instrucciones guest interpretadas. Revisión propia de cambios y pruebas: acumulación y saturación sin desbordamiento firmado, S=0 modular sin cambios, orden de lecturas/alias y flags conservados. Sin delegación ni afirmación de campaña completa.

Personajes: además de3.596 NC, el decoder del runtime procesó394 retratos KAO y25 KAO_P:4.015 imágenes verificadas en total. Sigue pendiente la correspondencia y el dibujo HD ingame. Los campos exploratorios solo coinciden en59 de147 pares, de modo que no se usa una correspondencia universal por índice.


Avance posterior: patches24–30 incorporan fuente HD de proporciones uniformes y límites de tinta/clip, herramienta local de matching, primer consumidor de retratos HD validado por bytes/paleta/origen y modo Zoom opcional. El catálogo tiene304 identidades nativas,394 candidatos PC,191 propuestas conservadoras y113 pendientes. La primera escena real cambia únicamente el retrato; no equivale a cuerpos NC completos. Suite de integración de ese bloque:76 pruebas aprobadas. Zoom se probó geométricamente a varias resoluciones y en escena real1440p con igualdad de imagen/tinta; Original continúa como opción por defecto. La composición final añade un ajuste de1px arriba/abajo.

Pendiente próximo: activar y validar el pack de retratos en el perfil de desarrollo, probar densidades/expresiones/fallbacks y avanzar identificación de los cuerpos NC. Después continúan campaña, cambio de disco, mandos y RA; ninguno se declara completo por estas pruebas visuales.
