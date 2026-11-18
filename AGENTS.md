# Entrada para colaboradores

Proyecto SaturnTaisenFirst. Antes de cambiar código, leer:

1. [Pendientes y estado actual](docs/PENDIENTES.md).
2. [Handoff y método de trabajo](docs/HANDOFF.md).
3. El documento de investigación del área que se vaya a tocar.

Saturn tiene prioridad; PC jugable/traducción PC quedan para después. Los recursos PC sí sirven al mod HD Saturn. Máximo 16:9, escalado entero, modo Original conservado. No mover otra vez el encuadre Zoom aprobado sin una petición nueva.

Los dumps, BIOS, guiones extraídos, estados, imágenes originales y composiciones de referencia permanecen en `local/`. No añadirlos a Git ni al release público. El ZIP personal autorizado es una entrega local distinta. Conservar los paquetes ya entregados.

La dependencia se modifica en `local/deps/satrecomp`, pero sus cambios se registran como patches en este repo. No ejecutar `build_runtime.py` mientras haya cambios de dependencia aún sin registrar: valida el árbol compuesto y debe rechazar diferencias. Coordinar propiedad de archivos y compilación con el colaborador activo antes de trabajar sobre ellos. No restaurar ni limpiar cambios ajenos para hacer pasar una prueba.

Al cerrar un bloque, actualizar pendientes y evidencia; distinguir implementado, probado e incluido en un paquete. Un estado guardado, una captura o una suite aprobada no acreditan capítulo/campaña completos.
