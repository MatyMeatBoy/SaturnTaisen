# Validación nativa del arranque y llegada al teatro

El recorrido reproducible `tests/theater.movie` llega desde el arranque a narración, diálogos ingleses y el mapa del teatro. Sus pulsaciones de A eligen una ruta inicial; no prueban todas las elecciones ni la campaña. El descubrimiento combinado contiene 8.488 variantes de bloques entre los dos discos y ambos idiomas. Los datos y el C++ generado permanecen en `local/`.

## Fallo de inicialización CD encontrado

El juego llamaba al servicio BIOS de salida, a través de `0x0600026C`, desde `0x06052C36`. El runtime imprimía un aviso y devolvía cero, permitiendo continuar después de una inicialización fallida. Que apareciera el título no probaba una inicialización correcta.

El dump BIOS japonés del propietario y su RAM en Beetle Saturn permitieron identificar el servicio real. Una traza del código original mostró el fallo: el comando CD `1100 0200 0000 0000` pide buscar la pista 2, pero el runtime solo actualizaba la posición al recibir una dirección FAD. Dejar la posición anterior provocaba el error de la biblioteca CD del juego.

El parche 0005 mueve el lector a la pista solicitada, conserva la posición con pausa y distingue una pista inválida. Después de corregirlo, el retorno original de esa inicialización es cero y desaparece la llamada BIOS de salida. Se prueba con comandos de bus sintéticos y con el arranque del disco real. La distinción pista/FAD está documentada en la [referencia de comandos de Yabause](https://wiki.yabause.org/index.php5?title=CDCommands) y en el [manual de comunicación CD de Sega](https://antime.kapsi.fi/sega/files/ST-162-062094.pdf).

El parche 0006 hace que AOT estricto rechace también servicios BIOS no implementados. El intérprete de investigación conserva su diagnóstico; una compilación de producción no puede aprobar este caso devolviendo éxito provisional.

## Composición VDP2

El parche 0004 implementa mezcla normal de dos pantallas, suma saturada, selección de proporción del primer o segundo plano, desplazamiento de color posterior a la mezcla y sombra posterior. También decodifica las proporciones de los sprites, sus cuatro condiciones de habilitación y la ventana de cálculo de color. Las pruebas usan VRAM, CRAM y framebuffer sintéticos con el renderizador real.

Las fórmulas y el orden de composición se contrastaron con el [compositor de Beetle Saturn](https://github.com/libretro/beetle-saturn-libretro/blob/master/mednafen/ss/vdp2_render.c). Las modalidades especiales por carácter/dot, extendidas y con pantalla de línea siguen pendientes; conservan su diagnóstico. La ruta larga probada no presenta avisos de composición pendiente.

## Evidencia y límites

- 30.000 hashes de estado por modo: intérprete, AOT conservador y repetición AOT iguales en todos los fotogramas. Evidencia local `local/work/sakura/parity-5ttcykm7/report.json`.
- El AOT recorrió esa ruta sin interpretación SH-2 ni servicios BIOS desconocidos. Agrupar funciones/enlazar llamadas sigue desactivado por una divergencia anterior en el fotograma 116.
- El perfil japonés conserva los bytes de datos y los tiempos del CUE original; solo cambia su representación a ISO/WAV. Sus hashes RA coinciden con los de los discos ingleses.
- La referencia de los hashes es el intérprete sobre el mismo runtime. No demuestra por sí sola fidelidad completa del hardware; hay que continuar la comparación con Beetle y validar lógica, sonido y gráficos de las escenas restantes.
- El rendimiento medido es headless en este recorrido. Las tareas concurrentes de desarrollo impiden tratarlo como una medición final del producto con ventana, audio y mandos.
- Faltan campaña, batallas, minijuegos, guardar/cargar y cambio real 1→2, además de las funciones finales de launcher, mandos, logros y mods. No se declara terminado el recomp.
