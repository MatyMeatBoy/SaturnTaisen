# Handoff de SaturnTaisen para GA36-MB v1.2

## Traspaso rápido a otro PC

1. Usa esta rama para consultar los parches. La RC1 de laboratorio parte de `34dced635775c29fc5dbc38e8a6f8c1da1235a38` (0.3.8). Mantén un solo checkout.
2. Copia por privado únicamente `local/entregas/SaturnTaisen-v0.3.8-ga36-mb12-rc1-lab.zip` y su `.sha256` si sólo vas a probar. El ZIP se instala conservando `.local/` y `ports/` en la carpeta personal de GoodLuckOS. Coloca el CUE y sus pistas en `ports/saturntaisen/game/es/disc1/` o `game/en/disc1/`. El segundo disco es opcional para el arranque. El paquete pesa 280.699.505 bytes y su SHA‑256 es `0b060875bddd1a8746666c072ba57b021d2cc61c6047ded3de9fc6b894d3f63d`.
3. Si vas a compilar, conserva por privado la base de descubrimiento `local/work/sakura/blocks.txt`, `block-order.json` y los insumos de ese mismo árbol. Usa `gen/` existente o vuelve a generar las unidades con la acción `recompile` de `tools/build_runtime.py` sobre el SDK validado. El árbol ARM usado tenía 674.182 bloques. Guarda tus CUE, BIOS, estados y donantes PC fuera de Git. Los objetos, cachés, máquinas virtuales y capturas masivas se regeneran en el PC nuevo. Evita copiar `local/` entero.

## Reconstruir el ARMv7

1. Recupera el commit del SDK y el orden de los 325 parches leyendo `git show 34dced635:config/dependencies.json`. Aplica esa lista en una copia aislada del SDK. El árbol compuesto antes de los parches portátiles fue `5b81aa5d06fb43ed015be3dd92d1789aa7706813`. Evita usar el SDK activo de otro colaborador.
2. Aplica en orden `r36s-original-only.patch`, `r36s-aot-pages.patch`, `ga36-armhf-state.patch` y `ga36-hd-2x-pilot.patch` desde `patches/platform/`. Define `SATRECOMP_R36S` y `SATRECOMP_GA36_HD_PILOT`. En el árbol de SDL3 3.4.18 aplica `ga36-sdl3-fbdev.patch`. SDL3 se construyó en Focal armhf con dummy/software, KMSDRM/GLES2 y ALSA dinámico. Reutiliza el sysroot Focal y el toolchain `platform/goodluckos/armv7-focal.cmake` de DynaBrothers si están disponibles. Se usaron Clang, CMake/Ninja, zlib armhf, libstdc++ de GCC 10, y las fuentes de ImGui e Inter que fija el proyecto.
3. Configura CMake para `-DGAME=sakura` con `GAME_DIR` apuntando a `games/sakura`, `WORK_DIR` a `local/work/sakura` y `SDL3_DIR` al árbol armhf compilado. El objetivo es `arm-linux-gnueabihf`, con `-mcpu=cortex-a7 -mfpu=neon-vfpv4 -mfloat-abi=hard`. Compila las unidades AOT con `-Os -DNDEBUG`. La RC1 usó `-O3` para `machine/{sh2,machine,vdp,cd}.cpp`, `video/{renderer,layers,vdp1,raster}.cpp` y `sound/{chip,m68k}.cpp`, además de `port/{main,frontend_sdl}.cpp` y el registro paginado en `runtime/recomp.cpp`.
4. Conserva el archivo de respuesta del enlace que enumera los objetos. Ejecuta `python tools/ga36_arm_aot_layout.py ruta/link.rsp ruta/arm-aot-exidx.ld`. Pasa `-Wl,-T,ruta/arm-aot-exidx.ld` a Clang/LLD junto con libstdc++ estática, `-rtlib=libgcc -unwindlib=libgcc -pthread -ldl` y el RUNPATH literal `$ORIGIN/lib`. El script coloca `.ARM.exidx` entre las mitades del `.text`, necesario por el alcance de `R_ARM_PREL31`. La RC pide `/lib/ld-linux-armhf.so.3` y símbolos hasta `GLIBC_2.29`. Usa el `warm-pages.txt` del ZIP para repetir las mediciones con las mismas 65 páginas.

## Siguiente prueba

La RC1 entregada sigue en Original a 2× sobre 640×480. El cambio de diagnóstico quedó preparado para construir. Tras aplicar los parches anteriores, añade `ga36-diagnostic-wide.patch` y `SATRECOMP_GA36_WIDE_DIAGNOSTIC`. Instala el nuevo binario como `ports/saturntaisen/diag/sakura` y copia `ga36-launch.sh` al mismo directorio que el launcher existente con el nombre `diagnostico.sh`. Por ejemplo, desde el directorio del port ejecuta `/bin/sh diagnostico.sh es wide`. Usa `original` para la referencia. El launcher aísla el perfil y recoge `frames.csv`, `run.log` y `system.log` en `user/diagnostico.*`. `SATURNTAISEN_DIAG_FRAMES` permite ajustar el límite de la sesión.

En esta propuesta, wide usa el compositor del port en la salida física de 640×480 y conserva el fallback nativo. En el panel 4:3 se debe validar cómo llena el fondo y cómo conserva las capas jugables con escala entera. El parche de diagnóstico quedó sin compilar ni probar. La RC1 sí tiene verificación funcional en QEMU, alrededor de 13–14 cuadros/s en mapa y combate. El objetivo físico sigue en 59,94 Hz. Prioriza medir el primer ataque, mapa de Ogami, transición de Nueva partida y audio con el mismo medio y la misma entrada en ambas variantes. [Resultados y límites de la RC1](ga36-handhelds.md)

## RC2 de laboratorio: despacho y comparación en placa

La RC2 es un **overlay privado que requiere la RC1** instalada. Conserva el ejecutable RC1, su SDL, sus discos y sus guardados; añade `ports/saturntaisen/rc2/sakura`, un acceso de juego con perfil separado y una batería automática RC1/RC2/RC2/RC1. La batería inicia el disco español cuatro veces durante 750 cuadros sin entrada y guarda los resultados aislados en `user/rc2-bateria.*`. Recoge tiempos, memoria, temperatura, frecuencias y muestras de CPU por núcleo/hilo cuando el firmware las expone. La copia de partida en cada caso permanece dentro de la carpeta privada; no publicar ese contenido.

Para reconstruir: usa exactamente la base y las opciones anteriores. Sobre el SDK aislado aplica primero `r36s-aot-pages.patch` y luego `ga36-aot-fast-dispatch.patch`; compila `runtime/recomp.cpp` con `-O3`, sin regenerar las unidades AOT si son las mismas. El objeto paginado original recompilado en esta investigación coincidió byte a byte con el de RC1. Sustituye únicamente ese objeto en el enlace ARMv7 y conserva el script de layout de RC1. El ejecutable candidato ensayado tiene SHA-256 `5cce1a6fcd0a695488de5e39e628516a91b442b8c718bf9872d64564e5a214a1`; la referencia RC1 tiene `985689164b37813098a2b03240c092e515c98a9688a4ef6446d9f327228c6886`. Usa `tools/package_ga36_rc2.py` para crear un overlay nuevo; nunca reemplaces los ZIP entregados.

El cambio evita llamar al cargador cuando la cola de la página ya está vacía y omite una comprobación redundante en la tabla rápida. En QEMU, AOT estricto con las mismas entradas dio hashes idénticos de estado y audio en 600 cuadros del arranque español y 120 del primer ataque; no certifica un capítulo completo. La prueba de cuatro pasadas mostró variación fuerte, sin una ganancia concluyente. La RC2 **no está probada en la GA36 física**, no garantiza una mejora ni 80 FPS y debe compararse antes de promoverla. El contador 0/0 de bloques en estos logs no prueba ausencia de interpretación: el conteo por entrada está desactivado salvo grabación; la comprobación de AOT estricto es la protección usada en QEMU.

La batería anterior `SATRECOMP_VIDEO_THREADS=0/1` no comparó configuraciones: ese ajuste pertenece al backend Ymir y no se usa en la RC1 de máquina propia. El primer diagnóstico físico registró 8,51 FPS en el arranque y vídeo con perfil de tiempos activo; otro control sin ese perfil registró 9,06 FPS en los primeros 1.140 cuadros. El usuario observó lentitud hasta cerca del final del vídeo. No extrapolar al combate.

## Rebased onto 0.3.9/main (2026-11-25)

- The GA36 branches (`codex/ga36-handoff`, `codex/ga36-rc2-diagnostico`) are merged into this branch from `origin/main` (`c06a9d6`). The `.gitignore` exception now covers every `*.patch`, `*.sh` and `*.puppy` under `patches/platform/`.
- Composite SDK of main (pinned `67a5fd4` + the 325 listed patches, 0001..0339) has tree `5b81aa5d06fb43ed015be3dd92d1789aa7706813`, identical to the RC1 base. All six SDK-side platform patches apply unchanged in the documented order: `r36s-original-only`, `r36s-aot-pages`, `ga36-armhf-state`, `ga36-hd-2x-pilot`, `ga36-aot-fast-dispatch`, `ga36-diagnostic-wide`. No refresh was needed. They also apply on top of the pending `0340-sakura-power-memory.patch` (checked against the unmerged file, read only).
- Compiled (objects only, no link): the five touched units (`port/frontend_sdl.cpp`, `port/main.cpp`, `runtime/game.cpp`, `runtime/recomp.cpp`, `sound/state.cpp`) with `SATRECOMP_OWN_MACHINE SATRECOMP_R36S SATRECOMP_GA36_HD_PILOT SATRECOMP_GA36_WIDE_DIAGNOSTIC` for the host (msys2 clang 23, x86_64 mingw), for the host without the platform defines, and for `arm-linux-gnueabihf` (`-mcpu=cortex-a7 -mfpu=neon-vfpv4 -mfloat-abi=hard`, Focal sysroot of DynaBrothers, `-stdlib=libstdc++`, SDL3 3.4.18 headers). `ga36-diagnostic-wide.patch` compiles for the first time.
- Check: `python tools/check_patch_stack.py --platform` applies the platform patches on top of the current stack (`SATRECOMP_DEP_DIR` selects an isolated SDK checkout).
- Not done: full ARMv7 link of the current stack (AOT units, layout script, SDL3 armhf), the SDL3 `ga36-sdl3-fbdev.patch` check, and every physical board test. FPS target 59.94 Hz is still open: RC1 measured about 9 FPS on the GA36 and 13-14 FPS in QEMU; RC2 has no board measurement.

## Parches de rendimiento preparados (sin medir)

Tres parches nuevos en `patches/platform/` se aplican sobre el árbol del laboratorio después de los anteriores. Compilan para `arm-linux-gnueabihf` con las opciones de `build-fast-core.py`, pero ninguno se ha enlazado, medido en QEMU ni comparado por hash de estado.

- `ga36-perf-sound.patch`: `Chip::Envelope` sale antes en voces aparcadas (Release, nivel 0x3FF, sin bypass) y conserva todos los almacenamientos del camino general. Revisado por lectura: el camino general deja exactamente el mismo estado. Ganancia esperada pequeña.
- `ga36-perf-sh2.patch`: `SameCode` compara en palabras de 32 bits en ARMv7. Resultado idéntico; sólo afecta a reverificaciones de código, no al despacho normal.
- `ga36-perf-vdp.patch`: añade `port/ga36_blit2x.h`, conversión ABGR→XRGB y duplicado 2× con NEON en una sola pasada al fbdev. La variante C++ coincide con la referencia en el host; la NEON no se ha ejecutado y el helper aún no está conectado al frontend.

Siguientes candidatos de mayor impacto, anotados en `local/build/ga36-a33/perf-*/NOTES.md`: colapsar las 128 llamadas por muestra al DSP del SCSP cuando el programa es corto, cachear la última página en `LoadPendingPage`, época de código de 32 bits en `Matches`, A/B de `-marm` frente a Thumb‑2 y presentar el cuadro en otro núcleo con doble búfer.

### RC2 de laboratorio (acumulativa, sin medir)

`local/build/ga36-a33/rc2/sakura` enlaza el mismo `link.rsp` de la RC1 sustituyendo dos objetos: `recomp.cpp` con `r36s-aot-pages.patch` + `ga36-perf-sh2.patch`, y `sound/chip.cpp` con `ga36-perf-sound.patch`, ambos a `-O3`. `rc2/build.py` lo reproduce. El enlace terminó correctamente (1.106.532.456 bytes; SHA‑256 en `rc2/sakura.sha256`). `ga36-perf-vdp.patch` todavía no entra porque el helper no está conectado. Falta el A/B/B/A en QEMU contra `aot-fast-ga36/sakura` (primer ataque y mapa) con comparación de hashes antes de empaquetarla.

### Handoff del bloque de rendimiento (2026-11-25 00:57)

Estado: implementado y compilado; no probado; no incluido en ningún paquete. No hay commit de estos archivos.

Archivos nuevos del bloque:
- `patches/platform/ga36-perf-sh2.patch`, `ga36-perf-sound.patch` y `ga36-perf-vdp.patch`.
- `local/build/ga36-a33/rc2/` contiene `src/` (copias parcheadas), `obj/`, `build.py`, `link.rsp`, `sakura` y `sakura.sha256`.
- `local/build/ga36-a33/perf-{sh2,sound,vdp}/` contiene las notas, las copias de trabajo y los objetos de prueba.

Pasos siguientes, en orden:
1. Medición A/B/B/A desde `local/build/ga36-a33`. El script de benchmark recibe la etiqueta, el escenario (`attack` o `map`), el número de cuadros y los binarios. Las pasadas A/B/B/A se lanzan con los binarios en ese orden:
   `python benchmark-armhf-cputime-private.py rc2-ab-attack attack 180 aot-fast-ga36/sakura rc2/sakura rc2/sakura aot-fast-ga36/sakura`
   Repetir con `map`. Los hashes `OPTI36S_HASH_*` de RC1 y RC2 deben coincidir. Si difieren, quitar primero `ga36-perf-sound.patch`.
2. Con hashes iguales y p95/p99 no peores, empaquetar `SaturnTaisen-v0.3.8-ga36-mb12-rc2-lab.zip` con `package-rc.py` adaptado, sin tocar el ZIP de la RC1.
3. Conectar `ga36::Blit2xFrame` (`perf-vdp/port/ga36_blit2x.h`) en `frontend_sdl.cpp`, dentro de `SATRECOMP_GA36_HD_PILOT` y sólo para Original sin menú ni capas, con retorno a SDL en los demás casos. Después compilar `frontend-pilot.o`, reenlazar como RC3 y comparar las capturas fbdev píxel a píxel.
4. Mejoras grandes pendientes, por impacto esperado:
   - Colapsar las llamadas al DSP del SCSP pasado `m_programLength`.
   - Cachear la última página en `LoadPendingPage`.
   - Usar una época de 32 bits en `Matches`.
   - Probar `-marm` frente a Thumb‑2 en `runtime/` y `machine/sh2.cpp`.
   - Presentar cada cuadro en otro núcleo.
   Cada una se suma a la RC acumulativa siguiente solo con los hashes intactos.

Coste del enlace: unos 6,5 minutos por variante, así que conviene agrupar los cambios antes de reenlazar.

### RC3 de laboratorio (2026-11-25)

La RC2 de laboratorio quedó sustituida por la RC3, que acumula todas las mejoras sobre la RC1:
- `ga36-aot-fast-dispatch.patch`, tomado del overlay RC2 del 24/11 y ahora registrado en `patches/platform/`.
- `ga36-perf-sh2.patch`.
- `ga36-perf-sound.patch`.

El paquete lleva además un binario de diagnóstico compilado con `ga36-diagnostic-wide.patch`. La reconstrucción está en `local/build/ga36-a33/rc3/`: `build.py`, `link-diag.py`, `package-rc3.py` e `install-f.py`.

| Prueba | Estado |
| --- | --- |
| QEMU A/B/B/A RC1/RC3, 180 cuadros | Hashes de estado idénticos en primer ataque y mapa de Ogami. Tiempos no concluyentes: el equipo empaquetaba y copiaba a la vez. Las medianas de RC3 salieron 169–208 ms frente a 188–273 ms de RC1. |
| Hardware GA36 | Pendiente. |

El paquete es `local/entregas/SaturnTaisen-v0.3.8-ga36-mb12-rc3-lab.zip`, con SHA‑256 `2f8cbb44f275cde5bbbd1b48cddd7a75318991443b318d712351dcfc4db9fb7a`. El ZIP `…-rc2-lab.zip` es intermedio, no entregado, y lo reemplaza la RC3.

Instalación en la tarjeta (F:, HOME de ClonDiClon):
- Binarios en `ports/saturntaisen/` y `diag/`. Los documentos van en `docs-rc3/`.
- Entradas Puppy.
- Entradas de EmulationStation en `.local/clondiclon/ports`: «Sakura Taisen», «Sakura Taisen - Diagnostico» y «… Wide», con miniaturas de 640×480. La copia previa de la lista de juegos quedó en `gamelist.xml.antes-saturntaisen-rc3.bak`. No hay entrada inglesa en ES porque la tarjeta sólo tiene `game/es`.

Los diagnósticos quedan en `ports/saturntaisen/user/diagnostico.*/`:
- `frames.csv`, con el tiempo de cada presentación.
- `run.log`, con las estadísticas del emulador.
- `system.log`, con RSS, frecuencias y temperatura.

### NEON aprendido de ClonDiClon/ReKHCoM aplicado a SDL3 (2026-11-25)

En la GA36, ReKHCoM ganó más con NEON en la presentación. Duplica filas con `vld1q_u32`/`vzipq_u32` y escribe cada fila dos veces. También sustituye el blit genérico de SDL cuando el destino es un 2× exacto y sin efectos. En su prueba la presentación bajó de unos 8,4 ms a unos 2 ms.

En SaturnTaisen el cuadro Original va de una textura XBGR8888 de 320×224 a la superficie XRGB8888 de SDL a 2× con escalado nearest. SDL lo resuelve con `SDL_Blit_XBGR8888_XRGB8888_Scale`, que hace aritmética de 64 bits por cada píxel en ARMv7. `patches/platform/ga36-sdl3-neon-2x.patch` añade en `SDL_BlitSurfaceUncheckedScaled` una ruta para 2× exacto sin modulación, mezcla ni colorkey:
- Lee los canales con `vld4_u8` e intercambia R y B.
- Duplica cada píxel con `vzip_u8` y escribe 16 píxeles con `vst4q_u8`.
- Copia la fila duplicada con `memcpy` y deja el byte X en 0, igual que el blit genérico.
- Si falla cualquier condición se usa la ruta normal.

Se compila con `neon-blit/make.py` y las bibliotecas quedan en `sdl-neon/`. El control `sdl-neon-off/` es la misma configuración con `-DSDL_GA36_NO_NEON_2X`.

Medición en QEMU con el título y el framebuffer simulado: mismo binario RC3, 600 cuadros, pasadas control/NEON/control/NEON, dos ejecuciones por pasada. Durante la prueba corrían además dos `qemu-system-arm` ajenos.

| Variante | Ticks de CPU de qemu-arm | Media |
| --- | --- | ---: |
| Control | 8039, 5662, 10408, 10103 | 8553 |
| NEON | 5719, 6779, 7859, 8450 | 7202 |

Las 8 capturas tienen el mismo SHA‑256 (`4c79b772…`), así que la salida es idéntica píxel a píxel. El CPU baja en ambas parejas, un 9 % y un 20 %, unos 16 % de media. Es una medida ruidosa y en QEMU; falta confirmarla en la placa con el diagnóstico (`render_present_ms` de `frames.csv`). Para probarla basta sustituir `ports/saturntaisen/lib/libSDL3.so.0` por `sdl-neon/libSDL3.so.0.4.18`.

#### SDL3 NEON instalada en la tarjeta (2026-11-25)

- **Reconstrucción fiel.** Para reproducir la SDL3 original hacen falta `PKG_SYSROOT` y `CMAKE_PREFIX_PATH` apuntando a `device-deps`, las rutas `ASOUND_LIB`, `ALSA_*`, `DRM_LIB`, `GBM_LIB` y `OPENGL_*` de su caché, `SDL_UNIX_CONSOLE_BUILD=ON` y los enlaces `-rtlib=libgcc -unwindlib=libgcc`. Sin eso se pierden KMSDRM o ALSA.
- **Control.** Con esa receta, `sdl-neon-off` salió idéntico byte a byte a `sdl-focal` (SHA‑256 `2882892f…`).
- **Variante NEON.** `sdl-neon` (SHA‑256 `c012deb5…`) tiene el mismo `SDL_build_config.h` y repite el SHA‑256 `4c79b772…` del título en QEMU.
- **Tarjeta.** Instalada en `F:/ports/saturntaisen/lib/libSDL3.so.0`; la original queda en `libSDL3.so.0.rc3-original.bak`.
- **Arranque previo en placa.** Antes del cambio, una sesión de la RC3 con la SDL3 original llegó a 668 cuadros. Usó el fbdev 640×480 y detectó el mando GA36-MB. No dejó datos de tiempos.

### Primera medición en la GA36 real por USBdiag (2026-11-26)

Estado: medido en la placa con la RC3 instalada (`sakura` SHA‑256 `f13dc8fe…`, SDL3 NEON `c012deb5…`). No hay cambio de binario en este bloque.

**Cómo se mide.** La consola se usa por la cola compartida USBdiag (`D:\01Claude\GA36-USB\ga36usb.ps1`, nombre de proyecto `saturntaisen`, turnos de 5 min). Los scripts están en `tools/ga36/usbdiag/`. `medir.sh ETIQUETA BINARIO ESCENARIO CUADROS headless|fbdev` corre el binario sin instalar nada y lo hace desde un enlace duro en `ports/saturntaisen/usb/bin/`. Así no tiene `release.marker` al lado, porque con él al lado se rechazan los estados de prueba ("Load states are a development tool"). Usa `--unthrottled`, audio dummy y los estados `attack`/`map` de `local/work/sakura`. Cada segundo muestrea `/proc/PID/stat` (fallos de página, CPU de usuario/sistema) y escribe `sys.txt`.

| Escenario (600 cuadros, sin vídeo) | Cuadro medio | SH‑2 | Vídeo | Sonido | Fallos mayores | RSS |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Arranque/logos (sin estado) | ~100 ms | 54 ms | 4,7 ms | 15 ms | — | — |
| Primer ataque (estado) | ~128 ms (≈7,8 fps; 600 cuadros en 89 s) | 43 ms | 52 ms | 24 ms | 814 | 330 MB |

Con fbdev, la presentación NEON cuesta 8,0 ms por cuadro (`render present`). CPU a 1,2 GHz con `schedutil`; 491 MB de RAM, 256 MB de swap.

**Conclusiones.**
- El límite es la CPU, no la memoria. El binario de 1,06 GB de `.text` no cabe en la RAM, pero el juego solo toca ~330 MB y apenas hay 814 fallos mayores en 89 s. Reducir el binario para que quepa no acercaría la velocidad completa.
- Todo corre en un solo hilo (`/proc/PID/task` muestra uno) y los otros 3 núcleos quedan libres.
- El AOT genera unas 250 instrucciones ARM por bloque de ~10 instrucciones SH‑2. Cada acceso a memoria recarga por la GOT (PIE) `g_ramHigh`, el mapa de código escrito y su tamaño. Cada escritura incrementa además un contador de actividad de 64 bits, y cada lectura compara `here` con las 5 direcciones de `IsMap08BiosDataRead`.
- Perfil por muestreo (`tools/ga36/stprof.c` con LD_PRELOAD y el mapa del enlace; reenlazado con `-Map` da el mismo SHA‑256 que la RC3) en QEMU‑user de WSL, 200 cuadros de combate:
  - despachador `Dispatch`+`Run` ≈17 %, más que el código traducido (15 %);
  - composición VDP2 (`ComposeLine`, `NormalLine`, `SpriteLine`) ≈20 %, más la rasterización VDP1 ≈4 %;
  - SCSP (`Step`, `Effects`, envolventes) ≈14 %, más 68K ≈5 %;
  - fuera del binario (libc/memcpy) ≈10 %.
  QEMU reparte las muestras por bloques traducidos, así que sirve para el reparto por funciones, no para instrucciones concretas. El perfil en la placa (`prueba3.sh`, ya preparado) no se pudo correr porque la GA36 se desconectó del USB.
- Descartado: `SATRECOMP_EXPERIMENTAL_FUNCTIONS=1` (enlace entre bloques). Da el mismo hash (`7586b394…`, 300 cuadros), pero no ahorra tiempo y carga los 674.182 bloques de golpe (RSS 594 MB en QEMU).
- Descartado por ahora: el renderizador GPU del SDK. Usa SDL_GPU con shaders SPIR‑V `#version 450` y la Mali‑400 de la A33 solo tiene GLES2.

**Siguiente paso propuesto (por impacto).** Velocidad completa son 16,7 ms. Ni repartiendo perfectamente los 128 ms actuales entre 4 núcleos se baja de unos 32 ms, así que hacen falta a la vez paralelismo y recortes en cada subsistema.
1. Renderizador en otro núcleo. Un proxy implementa la interfaz de empuje que usa `machine/vdp.cpp` (`WriteVdp1/2Reg`, `RenderLine`, `BeginFrame`/`EndFrame`, `DrawCommand`, `SwapFramebuffer`, `EraseFramebuffer`…) y la pone en cola. Las escrituras a VRAM/CRAM/FB también se encolan hacia copias sombra. Hay que sincronizar en las lecturas de FB por la CPU (`machine.h:207/233` usa `DisplayFramebuffer()`). La salida debe coincidir cuadro a cuadro con la composición en línea. Se esperan ~50 ms menos por cuadro en el hilo principal.
2. Emisor AOT: fijar en locales del bloque los punteros de RAM y del mapa de código, usar un contador de actividad local con volcado a la salida y antes de `SN_CALL`, y filtrar `IsMap08BiosDataRead` por rango. Compilar con `-fno-pic` y enlazar sin PIE. Exige recompilar los 1.687 módulos (~38 min) y comprobar los hashes en QEMU.
3. Ruta rápida del despachador: evitar `GetRegisters` cuando no cambia nada y la lectura de `CCR` (`Read8(0xFFFFFE92)`) en cada vuelta, y añadir una caché directa PC→Entry por época.
4. SCSP: saltar las etapas de voces inactivas y el DSP vacío.

### RC4–RC6: hilos de vídeo y sonido y saltos exactos de espera (2026-11-26)

Estado: implementado, compilado y verificado en QEMU con hash idéntico. La medida en la placa está en curso. No hay paquete y no hay commit.

Tres parches nuevos en `patches/platform/`, que se aplican con `git apply --ignore-whitespace -p1` porque el SDK usa CRLF:

1. **`ga36-video-thread.patch`** (sobre `release-sdk`; toca `machine/{machine,vdp,state}.cpp` y añade `machine/video_thread.h`). Con `SATRECOMP_VIDEO_THREAD=1` el renderizador corre en otro núcleo.
   - Cada llamada de la máquina al renderizador (`WriteVdp1/2Reg`, `RenderLine`, `BeginFrame`, `DrawCommand`…) va a una cola SPSC de 64k comandos.
   - El renderizador lee copias sombra de VRAM1, VRAM2 y CRAM, que se actualizan por la misma cola y en el mismo orden.
   - El framebuffer VDP1 es compartido: las lecturas y escrituras de la CPU en él sincronizan antes.
   - `EndFrame` sincroniza y entrega el cuadro en el hilo de la máquina; `RunFrame`, `Reset` y `Serialize` terminan con la cola vacía.
   - El modo de CRAM se lee de la copia de RAMCTL de la máquina, sin preguntar al renderizador.
2. **`ga36-idle-skip.patch`** (sobre la `runtime/recomp.cpp` de la RC3). Dos saltos exactos que ahorran vueltas de espera:
   - *Espera contada* (`SkipCountedWait`, combate y otras escenas): el bucle del maestro en `060041BA`/`060338B8`/`060041C2` suma 1 a un contador en cada vuelta y da unas 18.600 vueltas por cuadro.
   - *Bucles de solo lectura* (`IdleFastForward`, mapa): la CPU vuelve al mismo PC con los mismos registros y sin actividad.
   - En los dos casos se cobran de golpe las vueltas que caben en el tramo, dejando la última como código, y solo tras medir dos veces seguidas el mismo coste por vuelta. No se salta si hay puntos de sincronización o bloques de un paso.
   - Desactivables con `SATRECOMP_NO_COUNTED_WAIT=1` y `SATRECOMP_NO_IDLE_SKIP=1`.
3. **`ga36-sound-thread.patch`** (sobre el 1; toca `machine/{machine,state}.cpp` y `runtime/music.cpp`, y añade `machine/sound_thread.h`). Con `SATRECOMP_SOUND_THREAD=1` el 68000 y el SCSP corren en otro núcleo.
   - La máquina encola "haz n muestras" y sus escrituras a la RAM y a los registros de sonido.
   - Sincroniza antes de leer del lado del sonido (unas 2 veces por cuadro), antes de los comandos SMPC de sonido, antes del estado guardado, al final de cada cuadro y antes de leer o cambiar la música de CD, mediante un gancho en `music.cpp`.
   - No se activa con los efectos HD de PC (sus callbacks leen la RAM principal).
   - En 300 cuadros de combate y de mapa la interrupción SCSP→SCU no se disparó ni una vez. Si un juego la usa, se aplica en la siguiente vuelta de `Run` y se cuenta como "late SCU interrupts".

Construcción: `local/build/ga36-a33/rc4/cc.py` compila una unidad con las mismas opciones que la RC3; con él, los objetos de la RC3 de `machine.cpp`, `vdp.cpp`, `state.cpp`, `recomp.cpp` y `music.cpp` salen idénticos byte a byte. `rc4/link.py`, `rc5/link.py` y `rc6/link.py` reenlazan sobre `rc3/link.rsp` cambiando solo esos objetos (unos 2,3 minutos).

| Binario | SHA‑256 | Contenido |
| --- | --- | --- |
| `rc4/sakura` | `d0819972…` | hilo de vídeo |
| `rc5/sakura` | `10f4a82e…` | + saltos de espera |
| `rc6/sakura` | `19700a30…` | + hilo de sonido; `rc6/sakura.xz` 130 MB (`96a17b3d…`) |

Verificación en QEMU‑user, 300 cuadros con `--hash-log`. El hash por cuadro incluye RAM, registros, la imagen y el sonido.

| Escenario | RC3 | RC5 | RC6 (todo encendido) | Hash |
| --- | ---: | ---: | ---: | --- |
| Primer ataque | 20,9 s | 11,7 s | 8,1 s | idéntico (`7586b394…`) |
| Mapa de Ogami | 20,4 s | 8,7 s | 6,2 s | idéntico (`82416007…`) |

Notas de USBdiag para este proyecto:
- Subir por MTP fue unas veces de 0,7 MB/s y otras de 2,5 MB/s. Comprimir con `xz -6` (la busybox trae `unxz`) y partir en trozos de 20 MB mantiene el turno vivo.
- La tarjeta no admite enlaces duros: no copiar binarios para esquivar `release.marker`; correr los de `usb/bin/<rc>/`, que no lo tienen al lado.
- Una copia silenciosa de 1,1 GB llenó la tarjeta (salud MALA, 13 MB libres) y se liberó con `limpiar.sh`.

### RC6 en la placa y RC7–RC9: compositor de fondos más ligero y salto opcional (2026-11-26)

Medición de la RC6 en la GA36 real por USBdiag (`medir.sh`, 600 cuadros sin pantalla, estados y entradas de `usb/`; media de los cuadros 20 en adelante):

| Escenario | RC6 todo apagado | RC6 todo encendido | RC7 todo encendido | Hash |
| --- | ---: | ---: | ---: | --- |
| Primer ataque | 7,3 fps (137 ms) | 16,1 fps (62 ms) | 19,7 fps (51 ms) | idéntico en los tres (`d6d78df6…`) |
| Mapa de Ogami | — | 18,0 fps (56 ms) | 21,8 fps (46 ms) | idéntico RC6/RC7 (`3bbd62ac…`) |

- En la placa el hash del ataque es otro que en QEMU porque el estado y la entrada de `usb/` no son los de `~/stp`; lo que se compara es apagado contra encendido en la misma placa.
- Perfil de la RC6 en la placa (`stprof.so`, muestras por hilo): el hilo de vídeo pasa un 83 % en componer los fondos (`ComposeLine` 38 %, `NormalLine` 25 %, `SpriteLine` 19 %) y un 10 % en dibujar sprites del VDP1. El 29 % del hilo principal está en libc llamado desde `VdpLineEnd`: es la espera al hilo de vídeo al final del cuadro. `StateHash` (9 %, solo con `--hash-log`) y `Finish` (5 %, al salir) no cuentan en el juego.

Tres parches nuevos en `patches/platform/` sobre `video/renderer.cpp` (se aplican en este orden con `git apply --ignore-whitespace -p1`; verificado que reproducen la fuente de laboratorio salvo los finales de línea):
1. **`ga36-lean-compose.patch`** (RC7). Sin captura de presentación HD en la línea (sin tarjetas, corchetes, glifos ni mezclas capturadas), `ComposeLine` toma un bucle que solo calcula el color: misma elección de capa, cálculo de color, desplazamiento y sombra. `SATRECOMP_NO_LEAN_COMPOSE=1` vuelve al de siempre. Las estadísticas dicen cuántas líneas lo usan.
2. **`ga36-sprite-line.patch`** (RC8). `SpriteLine` con punteros planos y las constantes de la línea leídas una vez; un punto vacío (palabra 0) toma valores calculados una vez por línea, los mismos que antes, incluido el color de CRAM que se guarda aunque no se vea.
3. **`ga36-frame-skip.patch`** (RC9). `SATRECOMP_FRAME_SKIP=N` compone 1 cuadro de cada N; la máquina corre todos y el estado de línea de las capas (banderas de rotación, tablas de desplazamiento) avanza igual, así que un cuadro compuesto es idéntico al de sin salto. Por defecto no salta.

Verificación en QEMU (300 cuadros, hilos encendidos):

| Escenario | Dibujo del hilo de vídeo RC6 | RC7 | RC8 | Hash |
| --- | ---: | ---: | ---: | --- |
| Primer ataque | 7,4 s | 5,2 s | 4,8 s | idéntico (`7586b394…`) |
| Mapa de Ogami | 5,7 s | 3,9 s | 3,5 s | idéntico (`82416007…`) |

Con la RC9 y `SATRECOMP_FRAME_SKIP=2`: sin la imagen en el hash (`SATRECOMP_HASH_NO_PICTURE=1`) el hash es el mismo que sin saltar (`b61f9d56…`). Con la imagen, los 150 cuadros compuestos son idénticos a los de sin saltar y solo cambian los 150 saltados. El dibujo baja de 5,0 s a 3,3 s.

| Binario | SHA‑256 | xz (partes de 20 MB) |
| --- | --- | --- |
| `rc7/sakura` | `88c7ca1e…` | `cc63ed5c…` |
| `rc8/sakura` | (solo QEMU) | — |
| `rc9/sakura` | `785a117c…` | `91960a31…` |

### RC11: composición en un cuarto núcleo (2026-11-27)

**`ga36-compose-thread.patch`** (sobre `ga36-frame-skip.patch`) y **`ga36-compose-thread-machine.patch`** (sobre el `machine.cpp` de la RC6). Con `SATRECOMP_COMPOSE_THREAD=1`, la composición ligera de cada línea pasa a otro hilo, unas líneas por detrás del de vídeo:
- La línea encolada se lleva los búferes de la línea (capas, sprites, ventana de cálculo de color) intercambiándolos con los del renderizador, sin copiar nada. Además se lleva los valores de registro que usa.
- El renderizador espera a la cola antes de todo lo que lee o cambia de tamaño la imagen: `EndFrame`, `SetResolution`, `SetMode`, `Serialize`, `Reset` y `Report`.
- Las líneas que se guardan para reutilizar se siguen componiendo en el mismo hilo.
- `Machine::~Machine` para el hilo, porque sus líneas apuntan al renderizador.

En QEMU el hash es idéntico con y sin el hilo. Medido en la placa:

| RC11, todo encendido | Sin 4.º núcleo | Con 4.º núcleo | Hash |
| --- | ---: | ---: | --- |
| Primer ataque, 300 cuadros con `--hash-log` | 18,5 fps | 23,7 fps | idéntico, y el mismo que en QEMU (`7586b394…`) |
| Primer ataque, 600 cuadros sin hash (como se juega) | 24,1 fps | 28,1 fps | — |
| Mapa de Ogami, 600 cuadros sin hash | 26,8 fps | 30,8 fps | — |
| Primer ataque en pantalla real (fbdev) | — | 37,1 ms de emulación + 8,5 ms de presentación | — |
| Ídem, componiendo 1 de cada 2 cuadros | — | 34,8 ms + 8,5 ms | — |

- `--hash-log` cuesta unos 5 ms por cuadro en la placa. `medir.sh` acepta `NOHASH=1` para medir tal como se juega.
- La pasada con pantalla real fallaba (`SDL_Init: dummy not available`) porque un binario en `usb/bin/<rc>/` no encuentra `$ORIGIN/lib` y carga el SDL del sistema (3.4.12, sin el parche fbdev). Ahora `medir.sh` le copia `lib/libSDL3.so.0` al lado.
- `tools/ga36/fbbench.c` mide la escritura en `/dev/fb0` reescribiendo los mismos píxeles que hay en pantalla. Un cuadro de 640×480 cuesta 1,67 ms con `memcpy` y 1,49 ms con NEON de 64 bytes y `pld`. De los 8,1 ms de "render present", unos 6,5 ms son, por tanto, el renderizador por software de SDL, no la copia al framebuffer.

Perfil en pantalla real (`stprof.c` con el mapa de bibliotecas): unos 22 puntos del hilo principal se van en SDL. `SDL_StretchSurfaceUncheckedNearest` (7,2) y `Blit_3or4_to_3or4__inversed_rgb` (3,2) son la subida de la textura XBGR a la superficie XRGB y el estirado 2× del mismo formato, que no pasaban por `ga36-sdl3-neon-2x`. `SDL_memset4` (4,3) son rellenos, la copia a fb0 (4,3) y `SDL_BlendLine_XRGB8888` (3,3) las líneas del marco decorativo. `ga36-sdl3-neon-present.patch` añade a la SDL dos rutas NEON exactas: la subida, que respeta el byte X del destino como el bucle genérico, y el 2× exacto del mismo formato. `sdlpresent_test.c` da el mismo hash con la SDL anterior y la nueva en QEMU (`005dc2b9…`). En la placa, "render present" bajó de 8,1 a 7,5 ms. El resto son rellenos y el marco que dibuja `frontend-pilot.cpp`; su objeto no se ha podido reproducir byte a byte y queda sin tocar.

Pendiente:
- Perfil en pantalla real con `stprof.c`, que ahora guarda el mapa de bibliotecas para atribuir muestras dentro de `libSDL3`, y recortar la presentación.
- Para 60 fps hace falta bajar a 16,7 ms tanto el hilo principal (unos 26 ms de SH‑2 en combate) como el de vídeo.
- Las variables `SATRECOMP_VIDEO_THREAD`, `SATRECOMP_SOUND_THREAD` y `SATRECOMP_COMPOSE_THREAD` siguen siendo opcionales. Ninguna está en el lanzador ni en un paquete.

## Integración en main y pre de seguimiento (2026-11-27)

Desde la v0.3.9, `tools/check_patch_stack.py --platform` aplica 15 parches de plataforma sobre la pila de 326 parches (hasta 0340). El orden está en `PLATFORM_ORDER`:
1. `r36s-original-only`, `ga36-armhf-state`, `ga36-hd-2x-pilot` y `ga36-diagnostic-wide`.
2. `ga36-perf-sh2`, `ga36-perf-sound` y `ga36-perf-vdp`.
3. `ga36-idle-skip`, `ga36-video-thread`, `ga36-sound-thread` y `ga36-compose-thread-machine`.
4. `ga36-lean-compose`, `ga36-sprite-line`, `ga36-frame-skip` y `ga36-compose-thread`.

`r36s-aot-pages` y `ga36-aot-fast-dispatch` ya no aplican: el parche 0340 de la pila registra los bloques por página y comprueba la página pendiente dentro de `LoadPendingPage`, que es lo que hacían. Se conservan para reconstruir las RC sobre 0.3.8.

Con la pila de `main` y esos 15 parches, las unidades tocadas compilan para `arm-linux-gnueabihf` con `-O3 -DSATRECOMP_OWN_MACHINE -DSATRECOMP_R36S -DSATRECOMP_GA36_HD_PILOT`: `machine/{machine,vdp,state,sh2}.cpp`, `runtime/{recomp,music}.cpp`, `video/{renderer,layers}.cpp` y `sound/chip.cpp`. Es solo compilación, sin enlace. El binario medido en la placa es la RC11 de laboratorio, sobre la base 0.3.8 (`rc11/sakura`, SHA‑256 `13c113e5…`); un binario enlazado desde la pila de `main` está pendiente.

`ga36-launch.sh` activa por defecto `SATRECOMP_VIDEO_THREAD`, `SATRECOMP_SOUND_THREAD` y `SATRECOMP_COMPOSE_THREAD`; cada uno se apaga con `0`. `SATRECOMP_FRAME_SKIP` sigue apagado. Las SDL3 `ga36-sdl3-neon-2x.patch` y `ga36-sdl3-neon-present.patch` van sobre el árbol de SDL3 3.4.18 después de `ga36-sdl3-fbdev.patch`.

Herramientas en `tools/ga36/`:
- `stprof.c`: muestreo por hilo con el mapa de bibliotecas; se simboliza con `stprof_symb.py`.
- `fbbench.c`: velocidad de escritura en `/dev/fb0`.
- `sdlpresent_test.c`: compara dos SDL píxel a píxel.
- `qemu_*.sh`: pruebas A/B en QEMU‑user.
- `usbdiag/`: `medir.sh` y los trabajos de la RC11 para la cola USBdiag.

## Mejoras compartidas en la pila numerada, PC incluido (2026-11-27)

Los diez parches de rendimiento que no dependen de la GA36 pasaron de `patches/platform/` a la pila como 0341–0350, en el mismo orden y sin cambios:
- `samecode-words`, `scsp-parked-envelope` y `exact-wait-skips`;
- `video-thread`, `sound-thread` y `compose-thread-machine`;
- `lean-vdp2-compose`, `sprite-line-constants`, `optional-compose-skip` y `compose-thread`.

**0351 (`sakura-tighter-wait-skips`).** En los dos saltos exactos se cobran `(fin − ahora − 1) / coste` pasadas, en vez de `(fin − ahora) / coste − 1`. Así la vuelta que cruza el final del tramo es la única que corre como código, y nunca se llega justo al final, donde correría el bloque siguiente. Un contador de despachos por dirección en QEMU mostró que el 82 % de los 8,0 millones de bloques despachados en 300 cuadros de combate eran las cuatro piezas del bucle de espera contada. Con el 0351 bajan a 6,55 millones, y los hashes de combate (`7586b394…`) y mapa (`82416007…`) son idénticos.

`PLATFORM_ORDER` queda en `r36s-original-only`, `ga36-armhf-state`, `ga36-hd-2x-pilot`, `ga36-diagnostic-wide` y `ga36-perf-vdp`. `check_patch_stack.py --platform` da 337 parches más 5 de plataforma.

PC (Windows x64, `build_runtime.py build` sobre la pila 0001–0351, en su propia worktree y con su propia worktree del SDK). Primer ataque, `chapter1-first-attack.state`, 1.200 cuadros sin pantalla y sin límite, `SATRECOMP_STRICT_NATIVE=1`, 0 bloques interpretados:

| PC | Reloj | CPU | Hash |
| --- | ---: | ---: | --- |
| Todo apagado (`SATRECOMP_NO_COUNTED_WAIT`, `NO_IDLE_SKIP`, `NO_LEAN_COMPOSE`) | 12,5 s | 12,2 s | `E46E5D14…` |
| Por defecto (saltos de espera) | 6,9 s | 6,8 s | idéntico |
| Con `SATRECOMP_VIDEO_THREAD`, `SOUND_THREAD` y `COMPOSE_THREAD` | 5,2 s | 14,9 s | idéntico |

En PC los hilos siguen apagados por defecto. En ventana el PC dibuja por GPU, la composición ligera no se usa porque hay captura de presentación, y el sonido en hilo se desactiva solo con las voces HD. Los hilos en ventana no se han probado.

**0352 (`sakura-counted-wait-landing`).** El bucle de espera contada son cuatro bloques fijos: `060041BA`, `060338B8`, `060338B4` y `060041C2`. El dispatcher apunta cuándo entra en cada uno y con qué registros. Cuando dos pasadas enteras seguidas coinciden en el coste de cada bloque y en los registros, la vuelta que cruza el final del tramo ya no corre como código: la CPU queda tras el bloque en que el tiempo llega al final, como la dejaría ese bloque, y el dispatcher devuelve el control.
- En esa vuelta solo cambian el contador en memoria y `r1`, que vale el contador anterior con extensión de signo más 1.
- `SATRECOMP_NO_COUNTED_WAIT_LANDING=1` vuelve al comportamiento del 0351.

Resultados:
- **QEMU, combate:** con 600 cuadros, el hash `d6d78df6…` es igual con y sin aterrizaje, y es el mismo que da la placa. Con 300 cuadros, los despachos bajan de 6,55 a 5,58 millones.
- **QEMU, mapa:** sin cambios (`82416007…`).
- **PC, mismos 1.200 cuadros:** por defecto 6,1 s y con hilos 4,0 s, con el mismo hash `E46E5D14…`.

