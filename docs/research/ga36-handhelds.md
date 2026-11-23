# SaturnTaisen en GA36-MB v1.2 y R36S

## Ruta elegida

La primera plataforma es GA36-MB v1.2 con GoodLuckOS A33, ARMv7 con EABI hard-float, cuatro Cortex-A7, 512 MiB de RAM nominal y panel 640 × 480. La segunda es R36S con RK3326 y Linux AArch64. Cada una necesita su propio binario. La configuración de referencia de GA36 está en `docs/ports.md` y `docs/firmware.md` del repositorio ClonDiClon-GA36-MB1.2-20260416. Las experiencias de DynaBrothers y ReKHCoM allí documentan el arranque desde un archivo `.puppy`, la carga del perfil de mandos y las diferencias entre SDL2 y SDL3 en KMSDRM.

El candidato usa Saturn AOT y conserva la composición y controles de Saturn en ambos idiomas. La salida normal de 320 × 224 ocupa 640 × 448 a escala 2×, centrada en el panel de 640 × 480. No expone Zoom ni el conjunto completo de mejoras de escritorio. El launcher lee los discos preparados del idioma seleccionado y conserva guardados y ajustes en perfiles independientes. GoodLuckOS proporciona ALSA, el perfil de mando y el framebuffer del panel.

El piloto de arte PC reutiliza únicamente las capas que ya reconoce el compositor de la pantalla de título. Se habilita con `SATRECOMP_GA36_PC_ASSETS` y mantiene las máscaras, paleta y coordenadas del compositor de Saturn. Los recursos de PC de otras escenas tienen que mantener ese mismo registro. Por ejemplo, una imagen de PC de 576 × 320 y un cuadro de Saturn de 288 × 144 requieren comprobar origen y recorte antes de sustituir el cuadro de 576 × 288 a 2×. Un escalado directo en los dos ejes deformaría el original. Los discos y donantes proceden de la instalación local del jugador.

## Cambios del port

- El lanzador de GA36 usa el framebuffer si `/dev/fb0` está disponible para lectura y escritura. La copia sale del renderer software de SDL3 hacia la región visible validada de 640 × 480 XRGB8888. SDL3 también se construye con KMSDRM y ALSA de carga dinámica. El conector DSI está en `card1` para la configuración documentada. [API del framebuffer](https://docs.kernel.org/fb/api.html) · [Selección DRM de SDL3](https://wiki.libsdl.org/SDL3/SDL_HINT_KMSDRM_DEVICE_INDEX)
- La ventana simulada tenía el mínimo de escritorio de 704 × 512, que impedía usar el framebuffer del panel. El build de GA36 fija su superficie lógica a 640 × 480 y la escala a 2×.
- Los estados v9 de desarrollo fallaban en ARMv7 porque el bloque de estado del DSP incluía un puntero de tamaño nativo. En ARMv7 se conservan los campos del DSP y el espacio de disco de 64 bits, sin interpretar los bytes de la dirección. El estado de título de 64 bits cargó y avanzó 150 cuadros en ARMv7 después del ajuste. Esto cubre ese formato de diagnóstico. La suspensión del juego requiere pruebas aparte.
- El registro AOT por páginas evita materializar de golpe cada dirección reanudable del juego. El compositor de 2× también puede omitir la captura auxiliar de planos y objetos cuando el piloto de arte PC está apagado.

## Comparación con la edición PC

El `ADVcore.exe` extraído de la edición de PC es Win32 x86. Tiene señales de empaquetado y utiliza interfaces históricas de DirectDraw, DirectInput y DirectSound. La investigación no encontró código fuente compilable del motor ni un proyecto público de decompilación con cobertura y licencia verificables. Los SPR, WAV y MPG y las tablas de guion sirven de entrada para reutilizar recursos. Un motor nativo de PC necesita validar ejecución de guiones, LIPS, reglas tácticas, temporización, control y guardados antes de equipararlo a Saturn. Su coste y rendimiento todavía no se pueden medir contra el port actual.

## Protocolo de verificación

- QEMU ejecuta código ARMv7 con `-cpu cortex-a7` y el cargador y bibliotecas de una imagen GoodLuckOS A33 montada en solo lectura. Permite comprobar ABI y comparar variantes del mismo ejecutable con las mismas entradas. La tasa del simulador incluye traducción dinámica de QEMU y no equivale a la del dispositivo. [QEMU en modo usuario](https://www.qemu.org/docs/master/user/main.html)
- Separar arranque en ambos idiomas, prueba de mapa, primer ataque, ventana simulada y piloto de capas PC. Verificar paridad de estados cuando las pruebas usen las mismas entradas y guardar la captura de la configuración efectivamente usada.
- Para aprobar una versión de dispositivo, medir audio, mandos, KMSDRM y estabilidad con partidas y ventanas de carga reales. El objetivo es 59,94 campos/s, con 16,68 ms por campo. Medir memoria y percentiles de tiempos por tramo.

## Evidencia disponible

El intérprete ARMv7 abrió el disco preparado en español y completó 120 cuadros en QEMU con el cargador de GoodLuckOS A33. La medida de control fue 24,01 FPS y 195,50 ms p99. El estado de desempeño en hardware todavía no está medido.

La biblioteca SDL3 compilada para ARM hard-float requiere como máximo `GLIBC_2.29`. Una prueba del backend `fbdev` sobre memoria mapeada reprodujo todos los píxeles de dos colores y conservó intactos el padding, el desplazamiento y las filas externas del framebuffer. La comprobación simuló las consultas de geometría que configuraría el kernel y usó la biblioteca del candidato.

El título inglés también se reprodujo con la ventana real de SDL sobre el framebuffer simulado de 640 × 480. La instantánea de control coincide píxel a píxel con y sin captura auxiliar. En la comparación con el donante de PC cambiaron 9.112 píxeles dentro de la caja `(144, 96)–(380, 350)`. Se usaron el disco preparado y el `TITLE.SPR` locales. No se midió la cadencia del panel ni se probaron los mandos en hardware.

### AOT ARMv7

Base `34dced635775c29fc5dbc38e8a6f8c1da1235a38`, SDK compuesto `5b81aa5d06fb43ed015be3dd92d1789aa7706813` y los parches portátiles de `patches/platform/`. Se compiló para `arm-linux-gnueabihf` con Clang, sysroot Focal y `-mcpu=cortex-a7 -mfpu=neon-vfpv4 -mfloat-abi=hard`. El ELF pide `/lib/ld-linux-armhf.so.3` y hasta `GLIBC_2.29`. Los objetos generados se compilaron con `-Os`.

El texto AOT supera el alcance de `R_ARM_PREL31` con la tabla de excepciones al comienzo. `tools/ga36_arm_aot_layout.py` coloca `.ARM.exidx` entre las dos partes del texto. El ELF de referencia enlazó y conservó la tabla de excepciones completa. La tabla AOT contiene 674.182 bloques en el registro inmediato y corresponde a la base de cobertura usada para R36S. El ELF de Windows se construyó con registros adicionales.

La comparación de 120 cuadros por prueba en AOT estricto produjo hashes idénticos al cambiar del registro inmediato a 65 páginas precargadas. El RSS es el máximo muestreado del proceso `qemu-arm`, incluida su traducción y por separado de la memoria del sistema de la consola.

| Recorrido | p99 inmediato | p99 paginado | RSS inmediato | RSS paginado |
| --- | ---: | ---: | ---: | ---: |
| Arranque inglés | 76,84 ms | 62,11 ms | 528 MiB | 324 MiB |
| Arranque español | 40,16 ms | 41,10 ms | 528 MiB | 320 MiB |
| Primer ataque | 249,39 ms | 203,47 ms | 543 MiB | 343 MiB |
| Mapa de Ogami | 110,46 ms | 78,10 ms | 507 MiB | 305 MiB |

Los promedios paginados de combate y mapa fueron 13,13 y 14,29 cuadros/s en QEMU. Los registros de serie y mediciones están en `local/build/ga36-a33/proof-native-warm-suite*`.

En una prueba A/B/B/A de 180 cuadros del primer ataque, el build elegido usó `-O3` en 10 unidades de CPU, vídeo y audio y conservó `-Os` en las tablas generadas. Con las mismas 65 páginas precargadas, la mediana de p95 pasó de 96,46 a 85,26 ms y la de p99 de 300,33 a 286,52 ms. El RSS permaneció en torno a 350 MiB y los cuatro hashes de estado coincidieron. Las cifras de las dos pasadas de cada variante variaron con la carga del banco.

Una segunda comparación A/B/B/A del mapa de Ogami, también de 180 cuadros por pasada, conservó los cuatro hashes. La mediana de p95 pasó de 98,48 a 87,62 ms y la de p99 de 130,61 a 107,55 ms. El RSS se mantuvo alrededor de 304 MiB. El binario del paquete también reprodujo los 120 cuadros del control AArch64 de mapa con el mismo hash.

El perfil del primer ataque sin ventana separó el costo por subsistema. Después del primer cuadro, las medianas fueron 29,36 ms en CPU SH-2, 22,97 ms en VDP y 18,57 ms en sonido emulado. La mediana total fue 72,35 ms. El primer cuadro, que carga el estado de prueba, midió 813,17 ms y dedicó 424,05 ms a CPU SH-2. Esto permite priorizar la ejecución y la inicialización del estado antes de sacar conclusiones a partir de la presentación del panel.

El mismo binario AOT reprodujo el título sobre framebuffer simulado con las mismas dos capturas de 640 × 480 obtenidas con el intérprete. La entrada a Nueva partida desde el título completó 880 cuadros y llegó al primer cuadro de diálogo. El RSS muestreado de ese tramo fue 418 MiB en el proceso QEMU. Los hashes de mapa y primer ataque también coincidieron con los de la referencia AArch64 de R36S.

El disco preparado en español llegó al título en un arranque de 1.300 cuadros, con vídeo SDL simulado. Este recorrido y la transición de Nueva partida en inglés se verificaron con el binario elegido para el ZIP de laboratorio. Desde el estado de título en español se repitió la captura con y sin donante de PC en el framebuffer simulado. Los píxeles coincidieron en ese cuadro, por lo que la sustitución localizada queda por comprobar en esa secuencia. La sustitución sí quedó demostrada en el título inglés.

## Entrega

`local/entregas/SaturnTaisen-v0.3.8-ga36-mb12-rc1-lab.zip`, 280.699.505 bytes comprimidos y 24 entradas. Se verificaron CRC, SHA-256 del ZIP, hashes del manifiesto y permisos de ejecución del binario y del script. Incluye los dos accesos de GoodLuckOS, SDL3, la precarga probada y los parches de plataforma. Los discos, BIOS, donantes PC, partidas y estados quedan en el entorno local del jugador.

La aprobación para uso estable requiere medir velocidad sostenida y estabilidad de cuadros en la GA36 y comprobar el panel, audio, mandos, salida al frontend y suspensión. La revisión de R36S queda separada.

Se retiraron las imágenes de disco y de arranque regenerables de los ensayos cerrados. La referencia AOT se comprimió y se verificó su SHA-256 al leer el ejecutable restaurado. Quedaron el ejecutable vigente, la receta, las herramientas de compilación reutilizadas y la evidencia de pruebas. El laboratorio mide alrededor de 3,15 GB y el árbol completo 63,45 GB lógicos, excluyendo puntos de reanálisis. El árbol ya excedía el límite de 20 GB antes de este bloque.
