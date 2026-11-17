# Preparación multinúcleo de fondos Saturn

Se separó la preparación CPU de los loaders de la creación/subida de texturas. Las superficies pertenecen a la tarea que las crea y se destruyen después de preparar la caché; las texturas permanecen en el hilo de la ventana. Los trabajadores poseen copias de sus entradas y no acceden al estado invitado, al renderer ni a las partidas.

## Comparación medida

Mismo ejecutable, recursos y calidad; 19 fondos Saturn y 19 alternativas HD para Saturn. Tres repeticiones por condición en orden alterno, con calentamiento previo. Se contrastan los 38 hashes RGBA con el binario secuencial conservado anterior a esta separación. Equipo: Ryzen 7 7435HS, 8 núcleos/16 hilos, RTX 4060 Laptop.

|Trabajadores|Caché derivada vacía|Preparada|Pico working set|Pico compromiso privado|
|---:|---:|---:|---:|---:|
|1|2.102s|0.262s|23.9 MiB|17.7 MiB|
|2|1.147s|0.158s|33.2 MiB|29.7 MiB|
|4|0.676s|0.110s|54.7 MiB|53.0 MiB|
|8|0.478s|0.104s|91.1 MiB|95.7 MiB|

Memoria: mediana de los picos del proceso en las tres preparaciones frías; no es VRAM ni memoria del juego completo. Medidas mediante GetProcessMemoryInfo. Caché fría se refiere únicamente a caché derivada, sin vaciar la caché del sistema operativo. Estos tiempos CPU excluyen subida GPU, frames y espera de CD invitado.

Durante el juego se usan hasta cuatro trabajadores, reducidos según el número de procesadores lógicos, para dejar margen a lógica/audio. La preparación previa usa hasta ocho. `SATRECOMP_BACKGROUND_WORKERS=0..8` permite diagnóstico y desactivación. La cola está limitada por el catálogo de temas reconocido y se libera al terminar. No retiene una copia CPU adicional de todos los fondos.

## Integración y validación

El modo mejorado prepara cachés de temas posteriores tras cargar la escena actual. Solo intenta las alternativas HD habilitadas. La carga síncrona conserva las decisiones y el fallback de escena; la tarea especulativa solo crea cachés. Al cerrar/recrear la ventana se cancela el trabajo pendiente y se unen las tareas en curso antes de cerrar SDL. La decodificación en curso termina normalmente; su duración está limitada por los tamaños de entrada aceptados.

`--prepare-saturn-backgrounds CUE CACHE_DIR` y `--prepare-pc-backgrounds ROOT CACHE_DIR` preparan los 19 temas únicos correspondientes sin ejecutar código invitado ni usar renderer. La segunda opción continúa comprobando todas las identidades del propietario.

La prueba real a 1280×720 compara la imagen completa con 0 y 4 trabajadores: igualdad exacta; 1 frente a 19 cachés válidas al finalizar. Se comprueban cancelación, unión, fallo aislado, reinicio y límites del pool.

Una prueba de ocho productores sobre la misma ruta reprodujo acceso denegado de Windows durante el reemplazo, porque un lector podía tener abierto el destino. La publicación acepta el resultado existente únicamente si pasa la lectura íntegra y coincide píxel a píxel con la superficie que se intentaba publicar. Si no coincide sigue devolviendo fallo. Los temporales se limpian y la carga original continúa disponible.

La composición final ya usa Direct3D 11. Esto no convierte el rasterizador Saturn en GPU ni demuestra frame pacing: la primera carga activa todavía puede requerir preparación síncrona. La campaña completa y el cambio real de disco siguen pendientes.
