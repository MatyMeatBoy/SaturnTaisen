# Mejora de audio HD

El objetivo es conservar la interpretación, la música y el diseño sonoro de Saturn con la mejor fuente equivalente disponible. El mod incluye voces, música y canciones, efectos y audio de películas. Se mide por identidad de audio reproducida en Saturn. Un WAV de PC puede aparecer muchas veces y un contenedor Saturn puede incluir varias tomas. Las variantes con distinta actuación, letra, mezcla o ritmo quedan para revisión antes de reemplazarlas.

## Inventario y porcentaje

| Familia | Unidad | Primera comprobación |
| --- | --- | --- |
| Voces de historia y combate | Toma identificada por banco, región y evento de reproducción | Extraer del flujo Saturn, localizar la misma toma en PC y cotejar inicio, final y repetición. |
| Música de escena y combate | Tema y variante audible | Determinar si el juego activa una secuencia SCSP o una pista CDDA. Comparar arreglo y región de bucle. |
| Canciones y pistas de galería | Grabación y versión | Comparar voz, letra, duración y edición. Registrar por separado una versión instrumental. |
| Efectos de interfaz, ambiente y combate | Muestra, bucle o composición | Identificar el comando o canal y distinguir efectos independientes de capas simultáneas. |
| Películas | Flujo de audio por montaje compatible | Validar voz, música y sincronía sobre los tramos Saturn y PC del montaje final. |

Registrar candidatos, parejas, preparados, integrados y verificados por separado. Solo un reemplazo que se oiga en juego cuenta como verificado. Las fuentes exclusivas de PC y las mejoras sin ventaja audible quedan como decisiones explícitas. Mantener pendiente el porcentaje de cada familia hasta inventariar el audio Saturn que realmente se usa. El progreso empieza separado del indicador gráfico HD.

## Medición inicial de las fuentes locales

La edición PC contiene 4589 WAV. La lectura de cabeceras dio los siguientes grupos.

| Fuente PC | Archivos | Formato observado |
| --- | ---: | --- |
| Voces de historia | 3343 | Microsoft ADPCM de 4 bits, 22,05 kHz, mono |
| Voces de combate | 498 | Microsoft ADPCM de 4 bits, 22,05 kHz, mono |
| Voces extra | 219 | Microsoft ADPCM de 4 bits, 22,05 kHz, mono |
| Música | 35 | Microsoft ADPCM de 4 bits, 22,05 kHz, estéreo |
| Efectos y sistema | 494 | ADPCM o PCM mono, mayoritariamente 22,05 kHz |
| Vídeos MPG | 52 | MP2 de 192 kb/s, 44,1 kHz, estéreo |

Los dos discos Saturn contienen la misma pista CDDA de 28,373 segundos
en PCM estéreo de 16 bits a 44,1 kHz. Los bancos narrativos VCEADV
ocupan 89.362.432 y 98.607.104 bytes respectivamente. En cada disco se
identificaron 39 archivos tácticos ADP, seis PCM, 14 SE tácticos más
SAKURA.SE y 15 SND de extras. Son conteos de archivos y contenedores,
por lo que el denominador de tomas Saturn sigue pendiente.

El runtime actual ya admite audio PC en los reemplazos completos de
película. Los seis montajes alternativos conservan audio Saturn. Estas
rutas dan un punto de partida para comprobar la sincronía y calidad por
clip. Preparar el resto es trabajo nuevo: el extractor del mod gráfico
no recoge las carpetas VOICE, BGM y SE.

La cabecera de PC tampoco garantiza una mejora. La candidata puede
tener una actuación distinta o un origen comprimido aunque su salida
se reproduzca a 44,1 kHz. La selección se decide comparando audio
decodificado de la misma toma, ancho útil, ruido, distorsión, dinámica
y mezcla. Los conteos de estas tablas aún no representan sustituciones
de calidad aprobadas.

## Ruta de integración

1. El código `port/soundtrack.h` y `runtime/music.h` admite sustitución CDDA y conserva el volumen y fundido del juego. Los CUE preparados tienen una sola pista AUDIO por disco. Antes de usar esa vía, identificar sus reproducciones y comprobar que el tema deseado pasa por ella. La etiqueta de una carpeta BGM de PC no identifica por sí sola un evento Saturn.
2. Las voces narrativas observadas leen sectores de `VCEADV` y los copian a la RAM de sonido. El CD puede quedar pausado mientras la voz sigue audible. La ruta de voz debe mantener la identidad y el estado de reproducción hasta el final, y respetar el avance de texto, la interrupción real de línea y el interruptor Voz. Reutilizar la prueba del parque y añadir combate y cambios de escena. [Evidencia de la voz narrativa](dialogue-voice-advance.md)
3. Para efectos solapados y secuencias SCSP, identificar el sonido antes de mezclar y conservar volumen, panorama, prioridad, envolvente y bucle. Mantener el estado invitado y su tiempo. Evitar comparar la salida estéreo completa para detectar un efecto aislado.
4. Las películas con cortes alternativos ya tienen regiones verificadas. Cualquier mejora de audio sigue el montaje Saturn y su calendario de cortes. Validar el cambio de fuente, la sincronía y los fundidos por clip. [Montaje y cortes existentes](bounded-film-video-spans.md)

## Preparación y launcher

Añadir **Mejora de audio HD** como opción independiente de los gráficos, desactivada inicialmente. El launcher muestra si encuentra la fuente local y permite **Preparar audio HD** usando la edición PC del jugador. Guardar un recibo versionado por identidad, archivo, tamaño y huella. Reutilizar la preparación y recuperación del perfil para actualizar recursos derivados de forma atómica. Los archivos fuente y derivados de audio del jugador quedan locales.

Antes de activar una sustitución, comprobar el recurso y su disponibilidad de reproducción. Hasta que esté listo, la ruta Saturn sigue activa. Preparar conversiones y remuestreo fuera del hilo de emulación. La reproducción consume una cola de memoria acotada y descarta preparaciones atrasadas tras cambios de pista, escena, disco o estado. Evitar operaciones de disco y asignaciones por muestra.

La primera entrega requiere al menos una pareja exacta verificada con la opción activada y los controles de opción desactivada, donante ausente y reapertura de dispositivo. Comparar sincronía y ganancia, memoria máxima, fallos de cola y tiempos p95/p99 de los mismos recorridos con caché fría y templada. Incluir cambios de pista, avance rápido de diálogo y carga de fondo del sistema. Medir antes de fijar un límite de memoria o prometer una mejora de rendimiento.
