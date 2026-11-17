# Generación incremental durante el descubrimiento

La ruta Continue añadió entradas con direcciones anteriores a bloques ya generados. El orden global actual cambia entonces cientos de archivos C++, aunque solo se añadan unas pocas variantes. Mantener sus posiciones permite ampliar la recompilación sin repetir esas compilaciones.

- Añadir al generador fijado una opción de manifiesto privado de orden: primera generación idéntica al orden anterior; siguientes generaciones conservan las entradas y añaden las nuevas al final.
- Identificar cada variante por dirección y SHA-256 de sus bytes. Rechazar manifiestos duplicados, cambios de tamaño de archivo y retirada de entradas; regenerar en otra carpeta si se requiere una base diferente.
- Probar con programas SH-2 sintéticos que añadir una dirección inferior y otra variante de la misma dirección conserva exactamente los archivos anteriores, y que un manifiesto inválido no modifica la salida.
- Activar el manifiesto en la herramienta local; conservar el control de bytes del runtime, AOT estricto y funciones agrupadas desactivadas.
- Inicializarlo con los 253.163 bloques ya compilados, incorporar el menú Continue y comprobar la carga real antes de afirmar que funciona.

Es una adaptación del flujo de construcción aprobado, sin cambios en las instrucciones guest ni en el comportamiento del juego. El manifiesto y los C++ derivados permanecen en `local/`.
