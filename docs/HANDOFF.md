# Handoff técnico y artístico

Actualizado: 2026-11-18. Para otro bot o colaborador que se incorpora a SaturnTaisenFirst. Estado operativo en [PENDIENTES](PENDIENTES.md); los documentos de investigación conservan las evidencias detalladas.

## Objetivo y acuerdos del usuario

Recompilación estática AOT de Sakura Taisen Saturn, Windows x64, ambos SH-2. Saturn primero; PC jugable/traducción PC después. Los recursos PC ya se aprovechan para el mod HD Saturn. Traducción inglesa del equipo Saturn reutilizada/adaptada; el corpus no se publica en Git.

Original conserva presentación nativa. Mejorado recompone escenas a **16:9 máximo**, sin ultrawide y con enteros/nearest. No agrandar horizontalmente el raster para simular widescreen. Original de escena mantiene escala conjunta; Zoom usa enteros independientes para imagen y diálogo. El usuario aprobó el encuadre Zoom actual y canceló el último desplazamiento de +2 px: **no volver a moverlo por iniciativa propia**. Sombras de imagen y caja son independientes, se dibujan en orden correcto, sin sombra duplicada.

El launcher ofrece modos y ejemplos y se cierra cuando el juego confirma estar listo. Los ajustes ingame se abren con Start+Select/Back. HD/texto son opcionales; las sustituciones requieren identidad y evidencia, con fallback cuando falta un recurso válido. El producto final unifica ambos discos; el paquete personal de un solo disco es una excepción de pruebas ya autorizada.

## Al incorporarse

1. Leer `AGENTS.md`, esta guía y `docs/PENDIENTES.md`; comprobar fecha y cambios posteriores.
2. Ejecutar `git status --short`, `git branch --show-current` y consultar colaboradores activos. No limpiar un árbol sucio ajeno.
3. Base integrada de este bloque: `main` en `d54919e`, tras PR32/33. Consultar siempre HEAD, rama y estado presentes antes de trabajar. `VERSION`: 0.2.0-test.3, prerelease publicada desde `72affb2`. Su runtime es674.182/patch0049 (`377cb29b…`); no inferir el ejecutable local a partir de la versión. T11/patch0050 se integra por PR34 con candidato independiente (`df68e9db…`), sin empaquetar; test.3 conserva patch0049.
4. Acordar archivos propios y una tarea concreta. No editar a la vez `frontend_sdl.cpp`, renderer o patches; no compilar sobre una edición incompleta de otro bot.
5. Crear carpeta privada de resultados exclusiva por ensayo. Las imágenes se pueden sobrescribir sin querer: comprobar ruta absoluta, contenido visual y SHA antes de extraer conclusiones.

Al cerrar esta actualización, `wide_transitions` terminó el ajuste y liberó `video/renderer.h`, `renderer.cpp`, `layers.cpp` y `port/tactical_menu.h`. El coordinador integró el bloque y el patch 36 mediante PR #4, con revisión y pruebas. **Consultar con él antes de tocar esos archivos o recapturar el patch.** Los nombres de agentes y esta asignación son estado de sesión, no una reserva perpetua.

Trabajo útil para un segundo bot sin pisar esa integración: mejorar el inventario/matching de las 42 identidades pendientes del capítulo, preparar herramientas de catálogo/páginas de texto offline, o inventariar equivalencias de vídeos/HUD PC. Acordar una sola tarea y sus archivos; entregar manifest/propuesta y prueba, sin promover automáticamente candidatos dudosos ni reescribir el renderer. Si descubre un fallo en un archivo ajeno, enviar reproducción y propuesta al dueño.

## Mapa del workspace

| Ruta relativa a `D:\01Claude\Sakurawars` | Uso |
| --- | --- |
| `local/deps/satrecomp` | SDK fijado en `config/dependencies.json`; edición local, cambios exportados como patches. |
| `patches/0035-...patch`, `0036-...patch` | Coherencia HD/GUID y nuevas extensiones/presentación. El 36 ya contiene el ajuste de menús y la versión test.1; recapturar solo ante nuevos cambios de SDK. |
| `local/build/sakura/sakura.exe` | Runtime de desarrollo; puede ser posterior al ZIP público. |
| `local/work/sakura` | Estados y base de descubrimiento AOT privada (`blocks.txt`, `gen`, `block-order.json`). |
| `local/prepared/disc1`, `disc2` | Discos propios traducidos preparados; no publicar. |
| `local/art/tactics/stage01` | Referencias, generaciones, composición aprobada y `approved.json`; incluye contexto propietario. |
| `assets/generated` | Recursos generativos seleccionados, manifiestos y hashes; no copiar aquí referencias completas del juego. |
| `local/work/worker-wide-transitions` | Probes de capas, transiciones, comandos y arreglo de menús. |
| `local/work/worker-menu-oracle` | Referencia independiente Beetle Saturn; harness/estados/capturas privados. |
| `local/work/dialogue-catalog-worker` | Catálogo inglés JSONL/CSV extraído, solo local. |
| `local/work/portrait-coverage-worker` | Auditoría de cobertura y mezclas de retratos. |
| `local/releases` | Paquetes ya emitidos: inmutables. |

Nunca publicar discos, BIOS, SPR/FILM/MPG originales, guiones, estados ni imágenes extraídas. Un manifiesto no convierte una composición con píxeles originales en arte generativo publicable. El ZIP personal puede incluir los archivos propios expresamente autorizados; no se sube a GitHub.

## Método de depuración y validación

T02: el cierre del primer combate reveló dos rutinas copiadas a06002000. El estado anterior contiene238bytes de/SAKURA; al ejecutar,0SLG los reemplaza por206bytes. La prueba WATCH del instante de ejecución es la atribución correcta para el fallo06002042. El registro de ambas variantes produce674.182bloques; candidato aisladoe7dd1c0… pasó Save Complete/Resume con3.000hashes y15RGB iguales al intérprete y0interpretados. La cadena109.740frames sigue en prueba. Ver [seguimiento del combate](research/chapter1-victory-followup.md); no usar el candidato674.110 como corrección ni modificar test.2.

Reproducir antes de cambiar. Guardar estado inicial, copia de SRAM, pulsaciones/movie, settings, ejecutable/hash y registros. Aislar perfiles y eliminar variables `SATRECOMP_*` heredadas salvo las elegidas explícitamente. Usar `SATRECOMP_STRICT_NATIVE=1` y comprobar cero bloques interpretados para rutas AOT.

En pruebas de LIPS, un panel todavía visible puede estar ya confirmado y cerrándose. La igualdad entre dos ejecutables prueba paridad, pero no que el ensayo `select` haya cambiado la elección. Exigir postcondiciones: banco de resaltado en otra fila, panel cerrado antes que el control sin pulsaciones y destino de respuesta correspondiente; para timeout, dejar entrada neutra y observar el destino posterior. Si una semilla no permite seleccionar, buscar un estado anterior sin modificar el reloj ni el huésped. En T11 la semilla anterior de tres opciones ya permitió observar esas diferencias; la evidencia y los límites se mantienen en la PR34.

Separar tres preguntas: ¿falla la lógica nativa?, ¿falla la presentación del host?, ¿es un defecto del disco traducido? Comparar Original/Mejorado y, cuando importe, AOT/intérprete del mismo SDK. Esa última comparación **no es independiente**: pueden compartir un defecto de hardware emulado. Beetle Saturn se ha usado únicamente como oráculo de diagnóstico; no sustituye al runtime AOT del proyecto.

Los hashes por fotograma cubren el contrato de `StateHash`, no todos los campos serializados. Añadir comparación de píxeles, audio/entrada o guardados según el fallo. Una captura correcta no prueba la transición; un ataque no prueba victoria; una prueba desde estado no prueba arranque completo. Revisar imágenes individualmente con su etiqueta/ruta para evitar asociar una captura a otra.

Al analizar estados, leer el serializador real. En el formato actual: vector 0 HighRAM, 1 LowRAM, **2 sound RAM**, 3 VDP1 VRAM, 4/5 framebuffers, **6 VDP2 VRAM**, 7 CRAM. Se corrigió una interpretación anterior que confundía sound RAM con VDP2; no reutilizar aquel supuesto.

Cambios del host no deben modificar RAM/VRAM, framebuffer o entradas del huésped. Capturar comandos/paletas/texturas asociados al **framebuffer presentado**, no al último escrito. En sprites animados, distinguir retraso de fase, dato faltante, oclusión y mezcla VDP2. No ocultar un fallo de matching con una sustitución aproximada.

## PixelGen v1: cómo estamos haciendo los artes

1. Identificar la escena/recurso/capa/paleta reales. Separar fondo, personajes, imagen/vídeo, caja y HUD antes de generar. Las capturas anotadas del usuario orientan; no sirven como única geometría.
2. Guardar referencia limpia y original intacto en `local/`; definir una zona protegida y la franja que falta. Solicitar generación con contexto, mismo lenguaje visual, siluetas/materiales/paleta/dithering y densidad de píxel. No pedir un rediseño del centro.
3. Usar la herramienta ImageGen integrada para generación/edición. Leer las skills aplicables. No cambiar silenciosamente a una API de pago ni reemplazar la generación por edición programática. El exportador determinista sí recorta/normaliza **la franja ya aprobada** como procesamiento técnico de integración.
4. Revisar a tamaño nativo y a enteros reales: contornos, escala de flores/ladrillos/césped, luz, repetición, costura y ausencia de ruido/mezcla de densidades. Una buena miniatura no basta. Si cambia el centro, no aceptarla como sustitución completa: conservar solo la zona generada autorizada.
5. Normalizar a la rejilla y paleta nativas en el runtime. No afirmar pixel perfect solo porque el PNG es grande o se ve nítido. Guardar fuente generada, prompt/resumen, variante elegida, SHA, geometría y procedencia.
6. Para mapas, anclar en **coordenadas del mundo y scroll**, nunca al borde de la pantalla. Mantener unidades/efectos/HUD delante, sin nuevas casillas ni colisiones. Validar moviendo cámara y cambiando resolución.
7. Para fondos con centro original protegido, alinear el centro de la textura extendida con el mismo viewport entero; derivar el anclaje del centro nativo para evitar diferencias de redondeo en ventanas impares. Conservar fades y offsets de color.
8. Integrar solo assets generados seleccionados con allowlist y manifiesto. Rechazar hashes, dimensiones o identidad incorrectos al empaquetar. Documentar lo provisional: LOADING aún requiere pulir la fase del patrón en la unión.

Caso Stage01 aprobado: la referencia de salida es **940×448**, equivalente a **438×224** nativos con origen de mundo (277,24), no una ampliación uniforme ×2. La zona generada aprobada x814–895 se exporta a **39×224** y se coloca en **(656,24)**. El mapa termina en x655. No volver al antiguo cálculo provisional 41×224/origen (655,48). La franja exportada está en `assets/generated/tactical-extensions/STAGE01-right-v1.png`; contexto original solo en `local/`. Ver [PixelGen v1](research/pixelgen-v1.md).

Los motivos florales cambian según escena/paleta. Extender cada identidad y acompañar su transición real, sin mantener el fondo rosa donde toca azul, mapa o intermedio. El fondo floral con más flores fue la variante preferida por el usuario. Los fondos generados de pantalla y la franja táctica tienen allowlists separadas.

## Mod HD y texto

Las sustituciones PC conservan proporción uniforme, escala por altura y eje cabeza/torso del original. Nada de estirar ancho/alto independientemente. Distinguir cuerpo/pose, retrato y partes de ojos/boca; las animaciones requieren la familia completa o fallback coherente. Los matches ambiguos se rechazan. Revisar mezclas VDP2 antes de atribuir un parpadeo a una animación ausente.

La fuente HD debe respetar tamaño, avance y espaciado nativos con proporción natural, sin apariencia ancha. Cuatro líneas deben entrar con margen al marco. Los glifos se preparan antes del primer frame y el catálogo inglés se precarga una vez al activar HD. La narrativa verificada usa vistas del catálogo con máscara de celdas nativas; las elecciones conservan reconocimiento de comandos hasta identificar su conjunto completo. El catálogo exportado conserva IDs, bytes CP1252, controles, offsets y contexto de disco para la integración y futuras traducciones. No hacer OCR como única fuente si existe tabla nativa.

T11/patch0048 añade un catálogo sellado y un testigo de registro capturado junto al framebuffer por software. La tabla completa en Low WRAM0x00224000 debe coincidir; el punteroBE32 está en High WRAM0x0606851C. Conserva29.725 registros,29.723 preparables; los dos tabuladores quedan intactos. Patch0049 presta las líneas precargadas con una máscara probada por tiles/celdas: no muestra todo el registro solo porque el puntero coincide. Origen de comandosx64, recorte de tintax56; no confundirlos ni mover la UI.14casos comprobaron2.280hashes y104pares RGB idénticos, con0interpretados. LIPS necesita identificar el conjunto completo por separado y otras rutas requieren cobertura. Detalle en [precarga de diálogo](research/dialogue-preload-runtime.md); test.2 permanece inmutable.

LIPS requiere transformación del panel superior y una placa de píxeles que preserve el personaje bajo la transparencia. `underSprites` elimina toda la capa VDP1: no sirve para borrar solo los glifos de opciones. Ver [diagnóstico de transiciones](research/chapter1-wide-transitions.md).

## Comandos y precauciones de entorno

PowerShell; toolchain `C:\msys64\clang64`. Python del entorno normal tiene Pillow. Si se antepone MSYS al PATH antes de llamar `python`, puede elegirse otro Python sin Pillow. Usar un proceso separado o ruta absoluta al Python habitual.

```powershell
git status --short
python -m unittest discover -s tests -p test_frontend_safety.py -v
python -m unittest discover -s tests -p test_package_art.py -v
python -m unittest discover -s tests -p test_personal_bundle.py -v
python -m unittest discover -s tests -p test_chapter1_widescreen_runtime.py -v
python -m unittest discover -s tests -p test_widescreen_transitions.py -v
```

Pruebas runtime requieren fixtures privados y deben omitir rutas ausentes. Añadir pruebas dirigidas al fallo; no repetir suites caras sin cambios nuevos que lo justifiquen. Tests de cámara/menú deben conservar hashes y píxeles fuera de la zona que se cambió deliberadamente.

Para compilar una dependencia ya coherente y con propiedad acordada:

```powershell
$env:PATH='C:\msys64\clang64\bin;'+$env:PATH
cmake --build local/build/sakura -j 8
```

`python tools/build_runtime.py build` comprueba primero el árbol de patches. `recompile` necesita la base privada `blocks.txt`; no equivale a descubrir automáticamente todas las funciones del juego. No regenerar AOT por un ajuste de UI. El repro de menús independientes está documentado en [referencia táctica](research/tactical-menu-independent-reference.md).

Para cerrar el patch del SDK: crear índice Git temporal en la dependencia, partir del commit fijado, aplicar al índice los patches previos, calcular ese árbol base, añadir el árbol local al índice **temporal** y exportar el diff binario del último bloque. No usar/resetear el índice real de otro colaborador. El script privado actual es `local/work/capture-current-patch36.py`; revisar su alcance antes de ejecutarlo. Validar luego `build_runtime.dependency()`. No hacerlo mientras haya archivos de SDK a medio editar.

## Entregas y comunicación

Al cerrar una tarea: explicar qué cambió, qué se probó, qué sigue pendiente y si está solo en desarrollo o en un paquete. Actualizar `docs/PENDIENTES.md` y el informe del área. Conservar nombres y hashes de ZIP anteriores; nueva entrega, nueva identidad. Nunca afirmar que la campaña o el capítulo están completos por pasar tests parciales.

Release normal: código, DLL y assets generativos permitidos; recursos del juego aportados por el usuario. ZIP personal: nueva build + disco 1 inglés propio + HD ya procesado, todo junto para traslado, sin juego PC completo. Debe arrancar tras extracción en otro directorio sin Python/MSYS/toolkits. El producto final exigirá los dos discos. RX 6900 XT y variantes físicas M30 requieren pruebas del usuario en el equipo correspondiente.

## Integración por PR

El usuario autorizó expresamente al coordinador Codex a integrar las PR el 2026-11-18. Claude y los demás workers entregan PR; el coordinador revisa diff, head SHA, pruebas y conflictos, integra y actualiza la cola. Cada rama toma un ID de `docs/PENDIENTES.md`; revisar main y las PR abiertas antes de reclamarlo. Evitar commits directos a main y PR que mezclen tareas ajenas. Una integración no publica automáticamente un release.

Las PR #1 (cola), #2 (finales de línea) y #3 (índice de investigación) fueron revisadas e integradas. El conflicto de #2 se resolvió conservando la cola más nueva; nunca restaurar una lista vieja para hacer entrar una PR. Al añadir informes, actualizar también `docs/research/README.md`, comprobado por `test_research_index.py`.

## Entrega y material actual para Claude

v0.2.0-test.1 publicada; ZIP personal privado de 708.495.279 bytes, con disco1 inglés y HD procesado. Probado tras extracción en carpeta nueva y PATH de Windows: escena HD y combate, 38/38 fondos, 382 variantes, cero bloques interpretados. PC vídeos no integrados: los vídeos Saturn están en el disco1 incluido. No se afirma capítulo completo ni prueba física RX6900XT.

Guiones editables: `local/work/spanish-translation`, 56 tablas, 29.725 entradas EN canónicas con campo ES vacío y alias al disco2. Índice: `local/work/scene-index`, seis tags sencillos (vídeo, diálogo, elección, mapa, combate, menú). Inventaría ambos discos y 54 vídeos, pero solo nueve observaciones runtime están anotadas; no asumir vídeo sin texto ni autorizar Zoom por un candidato de archivo. El índice todavía no controla la presentación del runtime.

## Pruebas automáticas sin interrumpir al propietario

Para probar el runtime, ejecutar directamente el binario aislado `sakura.exe`, con `--disc`, `--settings`, `--backup` absolutos y `SATRECOMP_WINDOW_HIDDEN=1`. No usar el launcher `--play` para un replay que no esté probando el launcher. Si se prueba el launcher, preparar un perfil privado válido y `SATURN_TAISEN_FIRST_HOME` absoluto antes de iniciarlo: un perfil ausente puede abrir el mensaje de configuración encima del juego del propietario. No matar procesos por nombre ni sobrescribir un ejecutable en uso. El 18 de noviembre se observó este aviso mientras una prueba de la preview española usaba `timeout … SaturnTaisenFirst.exe --play`; el launcher.ini español conservaba su disco configurado. Registro local: `local/work/coordination-current.json`.

## Relevo del checkpoint de patches0046 y retratos201

Las PR hasta19 están integradas en main `d7e94cd`; consultar siempre el HEAD actual. El SDK compartido coincide con el árbol compuesto0001..0046 del checkout del coordinador. Los cambios ya están exportados: no restaurar el SDK para acomodarlo a un config/dependencies.json antiguo de otro worktree. Traer los commits nuevos o usar el checkout actualizado, preservando cualquier cambio ajeno.

Candidatos distintos, todos privados: `local/build/visual-fixes-candidate/sakura.exe` prueba presentación con614.024 bloques; `local/build/polish-test2-final/sakura.exe` combina el mismo host con674.023 y pasa las cargas9501/12000 de capítulos2/4. El CMake compartido recuperó su directorio de salida habitual, sin recompilar encima del exe del propietario. Antes de otro build, volver a comprobar procesos y elegir un destino aislado.

El preparado más reciente contiene201 retratos y19 fondos, en `local/work/portrait-chapter1-third-review/prepared-hd`; el coordinador reprodujo sus404 archivos de retratos byte por byte desde el proyecto original191 y las diez aprobaciones hash-locked. Sigue pendiente probar las animaciones no observadas y las32 identidades restantes del capítulo1. T45 propone reordenado offline para00a1; todavía no aprobado ni implementado.

Primer vídeo: usar el testigo capturado con el framebuffer; nunca inferir reproducción por una cabecera FILM residual o por ausencia de letras. Las fases y sus límites están en first-film-script-phase.md y first-film-transition-fix.md. El rótulo del episodio comparte cursor con la salida y se conserva por su capa de imagen. Las correcciones de este checkpoint se incorporaron posteriormente a test.2; test.1 permanece intacto.

## Empaquetado desde un worktree actualizado

package_release.py acepta --owner-root para leer dependencias/licencias privadas del propietario y --build-dir para seleccionar launcher/importador aislados; el código, VERSION, arte permitido y commit del manifest siguen siendo los del checkout ejecutado. --runtime selecciona el candidato AOT. package_personal_bundle.py acepta --owner-root para localizar exclusivamente disco, previews y fixtures privados. Ambos rechazan destinos de entrega existentes.

Para test.2 se prepara el launcher en local/build/launcher-test2 con salida local/build/test2-package-binaries y GAME_VERSION0.2.0-test.2; no sobrescribe el launcher del propietario. El perfil personal mantiene HD activado (valores0 de fondos/retratos) y precarga1. El manifest personal enumera también hashes de BAT/defaults/texto generados, aparte de sus recursos fuente; se excluye a sí mismo del inventario recursivo.

## Entrega test.2 verificada

Publicada v0.2.0-test.2 con fuente limpia92edea7; ZIP público317.215.196bytes. Bundle personal725.331.460bytes solo local, disco1 inglés y HD201/19fondos. Extracción limpia con PATH Windows: launcher, escenaHD, combate y película6201frames funcionan;402variantes sin fallos y cero interpretados. El recibo público de metadatos está en docs/releases/v0.2.0-test.2-validation.json; el detalle privado en local/work/test2-relocation-report.json. No se cambian los bytes ni la etiqueta de los paquetes anteriores.

Trabajo posterior: wide_transitions continúaT02a sin modificar RAM ni SDK. T48 quedó registrado en patch0047 y el árbol compuesto se validó. Su candidato aislado674.023 pasó cuatro perfiles/8ejecuciones de90frames con402variantes. El header ya no tiene ediciones sin registrar; consultar el commit integrado antes del próximo build. El binario de test.2 y sus ZIP permanecen inmutables durante ese trabajo.

## Candidato posterior a test.2: fallback del catálogo de retratos

local/build/portrait-fallback-candidate/sakura-674.exe contiene el patch0047; no sustituye los binarios de test.2. El runtime prueba el paquete incluido cuando el catálogo del perfil falla autenticación, conservando la prioridad de un mod personal que sí pasa la validación. Los PNG siguen verificándose al cargar; su fallback diferido es un caso aparte. Prueba integrada en research/portrait-pack-profile-fallback.md. No cambiar el ZIP ni el release para incluir un arreglo posterior.
