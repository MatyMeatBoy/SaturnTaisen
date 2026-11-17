# SaturnTaisenFirst — diseño propuesto

Estado: borrador para revisión. La vía de recompilación estática Saturn fue elegida por el usuario; el runtime concreto aún no se ha elegido.

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
