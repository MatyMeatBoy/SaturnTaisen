# SaturnTaisenFirst — diseño propuesto

Estado: diseño aprobado por el usuario el 17/11/2026, con ampliaciones posteriores incorporadas abajo. Se autoriza continuar hasta completar el recomp. El runtime concreto se decide con pruebas.

## Intención y alcance

Ejecutar Sakura Wars 1 de Saturn como programa nativo, manteniendo su traducción inglesa, ambos discos y la presentación original. Primera plataforma propuesta por el implementador: Windows x64, por ser el entorno disponible. No se presupone que el juego completo sea compatible con un toolkit actual.

El primer hito es una prueba reproducible de viabilidad: identificar ambos discos, preparar copias traducidas validadas y obtener la primera escena interactiva desde SH-2 recompilado. Si falta hardware o cobertura, registrar el bloqueo concreto. Un menú, una importación terminada o un arranque por intérprete no cuentan como recompilación jugable.

## Enfoques considerados

1. **AOT de la versión Saturn (elegido).** Evaluar saturnkit/saturn-recomp y satrecomp con los mismos programas y escenas. Conserva el material suministrado; requiere adaptar hardware y descubrir todo el código alcanzable.
2. **Emulación integrada.** Permitiría una referencia jugable más temprana, pero el usuario eligió recompilación estática. Se puede usar como instrumento de comparación.
3. **Decomp del port Windows.** Puede aportar comprensión del motor, pero requiere otros archivos y no aplica directamente el parche Saturn. Referencia de investigación.

La selección del toolkit comenzará con análisis de discos, licencia, instrucciones, overlays y compilación mínima. Se elegirá un candidato principal y se probarán escenas allí; solo se llevará otro hasta esas escenas si aparece un bloqueo o una diferencia que lo justifique. No fijar una dependencia por su nombre o por cifras de otros juegos.

## Preparación y ejecución

- Conservar dumps y parches originales. Calcular hashes y verificar CUE, sectores, producto y versión.
- Convertir copias a la entrada exacta esperada por xdelta; conservar CD-DA, pregaps y relación de pistas. Verificar comprobaciones del delta y registrar hashes de salida. Detener esa preparación si hay incompatibilidad; no forzarla.
- Analizar ambas versiones traducidas: arranque, ejecutables residentes, overlays y cambios de código. El código añadido por la traducción también debe recompilarse.
- Mantener el conocimiento de Sakura en una capa específica del juego y fijar el commit del toolkit. Registrar llamadas indirectas no descubiertas y nunca simular un retorno exitoso para ocultarlas.
- En el hito AOT y el ejecutable final, ambos SH-2 deben ejecutar código recompilado, sin recurrir a un intérprete para completar código faltante. La interpretación solo se admite para descubrimiento o referencia y se registra como tal. Los componentes de hardware que se interpreten, como la CPU de audio, se documentarán separadamente.

## Presentación

Conservar resolución interna y encuadre de cada modo observado. Proponer como predeterminado la proporción de presentación original, con el mayor escalado nítido compatible con ella, sin recorte ni filtrado borroso. Ofrecer además un modo de escala entera estricta de los píxeles fuente si la corrección de proporción impide cumplir ambas propiedades simultáneamente. Confirmar las dimensiones efectivas antes de fijar factores o prometer 4:3 en todos los modos.

El marco ocupa únicamente el área exterior al juego. Propuesta inicial: marco discreto temático, adaptable a ventana, 16:9 y ultrapanorámico, sin cubrir subtítulos ni interfaz. Su arte concreto queda pendiente; no es condición para probar AOT.

## Dos discos y persistencia

Un solo perfil de juego agrupa ambas imágenes traducidas y una memoria de respaldo persistente compartida. Los identificadores de recursos incluyen el disco para evitar colisiones entre archivos con el mismo nombre.

Primero observar en la referencia el cambio real. Después detectar la solicitud mediante estado o función conocida y realizar el montaje y, si el juego lo requiere, la continuación/reinicialización correspondiente. No fusionar ciegamente las ISO ni cambiar disco por tiempo transcurrido. Preservar guardados de forma atómica, mantener copia antes de una migración y restaurar al volver a abrir el programa el disco correcto.

## Ajustes, mandos y modificaciones — requisitos añadidos

Launcher y menú de pausa ingame comparten configuración persistente: imagen, escala, marco, audio, controles, mods y logros. Start + Select abre/cierra el menú; Select es una acción del port, no un botón inventado del Saturn. Reservar la combinación, dispararla una sola vez hasta liberar y evitar que botones mantenidos al cerrar alcancen al juego. Incluir atajo de teclado, navegación completa por mando y reconexión sin teclas retenidas.

Soporte general mediante SDL para Xbox, PlayStation, Nintendo, mandos genéricos y todos los modelos M30 que expongan entradas accesibles en PC. Perfiles automáticos Saturn para dispositivos/modos reconocidos; remapeo y asistente para desconocidos. Los ajustes del usuario prevalecen. No identificar un M30 únicamente por un nombre Xbox genérico. Tuplas GUID/VID/PID/transporte/modo con procedencia y confianza; perfiles elegibles manualmente cuando el modo oculta el modelo. Mantener etiquetas Saturn A/B/C y X/Y/Z, L/R, Start, y Select del port. Contemplar cruceta como hat o ejes y C/Z o L/R como botones o ejes con histéresis. El propietario tiene M30 Bluetooth pero no disponible para validación física.

Traducción inglesa y packs compatibles instalados estarán activados por defecto y se podrán desactivar. Mantener preparaciones japonesa e inglesa separadas, con identidad y código generado de cada variante. No aplicar un código recompilado de otra variante sobre una imagen distinta. Cambios que alteran código/recursos requieren reinicio seguro. Buscar mods HD y mejoras existentes en fuentes de autores; evaluar cobertura, versión, licencia e impacto en memoria/RA. No presentar un shader, un port de PC o un pack de otro juego como mod HD verificado de Sakura Saturn. El marco original sigue disponible.

## RetroAchievements y logros locales — requisitos añadidos

Set oficial https://retroachievements.org/game/16546 (68 logros al consultar el 17/11/2026). Usar exactamente sus identificadores, condiciones, títulos, descripciones y badges: ningún reto propio. Pestaña Logros en launcher e ingame, filtro/progreso y avisos con badge, título y descripción al desbloquear, similares en función a ReKHCoM.

Login opcional, softcore forzado por rc_client; nunca solicitar contraseñas en el chat ni guardarlas. Windows protege el token con DPAPI. Separar cuenta y progreso local. Descargar/cachear el catálogo oficial y badges con versión/procedencia y usar rcheevos para evaluar offline la misma definición. El primer uso totalmente offline necesita un catálogo legítimamente disponible localmente; no prometer descarga sin conexión. Sin catálogo, informar indisponibilidad sin inventar logros.

Los logros offline se guardan localmente de forma atómica por juego/variante/usuario local. Separar evaluación real de previews, run-ahead y regresiones; estos últimos no conceden logros. No reenviar automáticamente premios históricos al conectar otra cuenta ni simular una sesión online offline. La cola/reintento de una sesión online usa solo el flujo admitido por rc_client. Guardar/restaurar estado de evaluación junto al estado del juego, reiniciar del modo adecuado ante reset y notificar cambio de disco mediante rc_client_begin_change_media.

El mapa oficial Saturn de rcheevos aplana WRAM-L en 0x000000–0x0FFFFF y WRAM-H en 0x100000–0x1FFFFF. Leer de las memorias reales del runtime con límites y orden de bytes correctos, no de direcciones del host. do_frame se ejecuta una vez por frame lógico real, nunca por frame de presentación. Los dos hashes de los dumps originales coinciden con los registrados en RA; repetir identificación y comprobar las referencias de memoria después del parche. No forzar el game ID ni sustituir hashes para ocultar incompatibilidad.

## Validación

- Comparar con una referencia madura y los mismos discos traducidos: arranque, vídeo, escena de diálogo con voz, elección, batalla, minijuego y guardar/cargar.
- Capturas en momentos reproducibles para encuadre, proporción, prioridades, transparencias, fuentes y subtítulos; comprobar además audio y sincronización.
- Cubrir contenidos exclusivos de ambos discos y probar el paso real 1→2, la primera partida del disco 2 y cerrar/reabrir después de la transición.
- Registrar qué se probó y qué queda pendiente. Una ruta de prueba no certifica todas las ramas ni una campaña completa.

## Material disponible y necesidades

Ya hay discos y xdelta para comenzar la investigación. El usuario aportó también la carpeta local `Sega Saturn BIOS`, que contiene once archivos de 512 KiB. Una BIOS propia ayuda a la referencia (por ejemplo Beetle Saturn/Mednafen) y al diagnóstico; la necesidad final depende del runtime seleccionado. Mantenerla local y registrar su hash, sin subirla al repositorio. No asumir que cualquier región o revisión sirve para el emulador elegido.

Una partida cercana al final del disco 1 será muy útil para probar la transición. No es requisito para analizar el arranque. Si no existe, habrá que obtener ese punto jugando la referencia. No confundir savestate de un emulador con memoria de respaldo portable.

## Límites y decisiones pendientes

No hay todavía código de producto ni una compilación de Sakura. No se prometen mejoras de FPS, widescreen del área del juego ni compatibilidad completa. Quedan pendientes la selección del runtime, la comprobación del parche, los modos gráficos observados y el mecanismo del cambio de disco. El repositorio remoto será privado; solo contendrá documentación, código propio y dependencias que puedan redistribuirse según sus licencias. Se excluyen BIOS, dumps, xdelta, partidas, ejecutables extraídos, recursos y C++ generados desde el juego.
