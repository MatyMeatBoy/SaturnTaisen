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

Cada disco Saturn contiene una pista CDDA distinta de 28,373 segundos
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

### Primeras coincidencias y formato de música

MOVIE000 ya usa la pista PC en el reemplazo completo. La comparación
de la misma película conserva su envolvente en tres ventanas y el
retorno al audio Saturn funciona al saltarla. El flujo Saturn es mono
PCM de 16 bits a 32 kHz. El PC contiene estéreo real en MP2 a 44,1 kHz,
con correlación izquierda/derecha 0,651 y una señal lateral a −6,71 dB
respecto al centro. La ventaja observada es la separación estéreo.
Este caso permite fijar el primer control independiente de audio del
launcher.

En 34 de 35 WAV BGM de PC, un prefijo de ocho bytes con la marca
`loop` precede al primer bloque ADPCM dentro de la región de datos.
El largo declarado excluye ese prefijo. Los 35 temas decodifican
cuando se normaliza el archivo y se conserva el valor de bucle aparte.
OTOME usa la forma estándar. Falta determinar la unidad del bucle
antes de usar el valor en reproducción. Desde la galería Saturn,
ADVBGM02 y ADVBGM03 son candidatos para comparar con SM02 y SM03.
Todavía requieren comprobar melodía, arreglo y bucle. Esas pistas
salen del SCSP y necesitan un punto de sustitución propio.

## Ruta de integración

1. El código `port/soundtrack.h` y `runtime/music.h` admite sustitución CDDA y conserva el volumen y fundido del juego. Los CUE preparados tienen una sola pista AUDIO por disco. Antes de usar esa vía, identificar sus reproducciones y comprobar que el tema deseado pasa por ella. La etiqueta de una carpeta BGM de PC no identifica por sí sola un evento Saturn.
2. Las voces narrativas observadas leen sectores de `VCEADV` y los copian a la RAM de sonido. El CD puede quedar pausado mientras la voz sigue audible. La ruta de voz debe mantener la identidad y el estado de reproducción hasta el final, y respetar el avance de texto, la interrupción real de línea y el interruptor Voz. Reutilizar la prueba del parque y añadir combate y cambios de escena. [Evidencia de la voz narrativa](dialogue-voice-advance.md)
3. Para efectos solapados y secuencias SCSP, identificar el sonido antes de mezclar y conservar volumen, panorama, prioridad, envolvente y bucle. Mantener el estado invitado y su tiempo. Evitar comparar la salida estéreo completa para detectar un efecto aislado.
4. Las películas con cortes alternativos ya tienen regiones verificadas. Cualquier mejora de audio sigue el montaje Saturn y su calendario de cortes. Validar el cambio de fuente, la sincronía y los fundidos por clip. [Montaje y cortes existentes](bounded-film-video-spans.md)

## Preparación y launcher

Añadir **Mejora de audio HD** como opción independiente de los gráficos, desactivada inicialmente. El launcher muestra si encuentra la fuente local y permite **Preparar audio HD** usando la edición PC del jugador. Guardar un recibo versionado por identidad, archivo, tamaño y huella. Reutilizar la preparación y recuperación del perfil para actualizar recursos derivados de forma atómica. Los archivos fuente y derivados de audio del jugador quedan locales.

Antes de activar una sustitución, comprobar el recurso y su disponibilidad de reproducción. Hasta que esté listo, la ruta Saturn sigue activa. Preparar conversiones y remuestreo fuera del hilo de emulación. La reproducción consume una cola de memoria acotada y descarta preparaciones atrasadas tras cambios de pista, escena, disco o estado. Evitar operaciones de disco y asignaciones por muestra.

La primera entrega requiere al menos una pareja exacta verificada con la opción activada y los controles de opción desactivada, donante ausente y reapertura de dispositivo. Comparar sincronía y ganancia, memoria máxima, fallos de cola y tiempos p95/p99 de los mismos recorridos con caché fría y templada. Incluir cambios de pista, avance rápido de diálogo y carga de fondo del sistema. Medir antes de fijar un límite de memoria o prometer una mejora de rendimiento.

La utilidad `tools/normalize_pc_bgm.py` separa el prefijo y valida
la extensión RIFF antes de entregar WAV estándar. Se verificaron las
35 pistas de la edición local con FFmpeg sin errores de decodificación.
OTOME pasó sin cambios. Las pruebas sintéticas cubren archivos normales,
el prefijo conocido y extensiones truncadas o inválidas. El valor de
bucle se conserva como metadato sin aplicarlo a la reproducción.

### Efectos de combate PCMSE

`tools/audit_pcmse_pairs.py` coteja los dos bancos PCMSE.BIN
del Saturn y la tabla SE.TAB de PC. Los bancos son idénticos.
Su directorio contiene 12 entradas con datos y dos vacías.
El despachador Saturn de 0x0601983C asigna los IDs 41–51 y
54, que coinciden con las entradas STATIC de PC. El informe
registra tamaños, huellas y formato WAV, sin copiar muestras.

El primer ataque normal de Sakura activa el ID 42 de forma
natural. Después del campo 378, el despachador recibe 0x2A y
copia la fila 1 desde 0x060E97CC. En los campos 381 y 386 se
observa el canal SCSP 6 con PCM8 a aproximadamente 15,99 kHz,
centrado, sin envío DSP y con los primeros 4096 y 8192 bytes
exactos de la fila en la RAM de sonido. Su pareja por ID es
0042.WAV. El efecto 51 queda identificado en ambos formatos,
con un disparo natural todavía pendiente. El informe de IDs
no mide la mejora audible ni suma integraciones al mod.
