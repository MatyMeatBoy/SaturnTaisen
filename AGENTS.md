# Entrada para colaboradores

Proyecto SaturnTaisenFirst. Antes de cambiar código, leer:

1. [Pendientes y estado actual](docs/PENDIENTES.md).
2. [Handoff y método de trabajo](docs/HANDOFF.md).
3. El documento de investigación del área que se vaya a tocar.

Saturn tiene prioridad; PC jugable/traducción PC quedan para después. Los recursos PC sí sirven al mod HD Saturn. Máximo 16:9, escalado entero, modo Original conservado. No mover otra vez el encuadre Zoom aprobado sin una petición nueva.

Los dumps, BIOS, guiones extraídos, estados, imágenes originales y composiciones de referencia permanecen en `local/`. No añadirlos a Git ni al release público. El ZIP personal autorizado es una entrega local distinta. Conservar los paquetes ya entregados.

La dependencia se modifica en `local/deps/satrecomp`, pero sus cambios se registran como patches en este repo. No ejecutar `build_runtime.py` mientras haya cambios de dependencia aún sin registrar: valida el árbol compuesto y debe rechazar diferencias. Coordinar propiedad de archivos y compilación con el colaborador activo antes de trabajar sobre ellos. No restaurar ni limpiar cambios ajenos para hacer pasar una prueba.

Al cerrar un bloque, actualizar pendientes y evidencia; distinguir implementado, probado e incluido en un paquete. Un estado guardado, una captura o una suite aprobada no acreditan capítulo/campaña completos.

## Higiene obligatoria del workspace

- Máximo dos worktrees existentes: repositorio principal y una copia auxiliar. Reutilizar la auxiliar disponible; no crear otra mientras esté ocupada. Consultar `git worktree list --porcelain` antes de comenzar.
- Al integrar una PR, retirar su worktree cuando esté limpio, no contenga datos locales únicos y su HEAD esté conservado en Git. Usar `git worktree remove` sin `--force`, seguido de `git worktree prune`. Nunca borrar cambios ajenos para liberar una copia.
- Mantener el proyecto por debajo de 20.000.000.000 bytes y el ZIP de desarrollo por debajo de 10.000.000.000 bytes. Medir y registrar el tamaño al cerrar cada bloque; retirar intermediarios regenerables antes de duplicarlos.
- Conservar un runtime actual y una referencia anterior conocida, que puede archivarse comprimida verificando CRC y SHA del ejecutable restaurado. Conservar las bases AOT y sus órdenes para regenerar fuentes/objetos; retirar árboles generados y cachés de ensayos cerrados.
- Compartir los recursos gráficos entre pruebas; cada ensayo usa perfiles y salidas absolutos independientes. Conservar estados inicial/final, entradas, informes y capturas de límites relevantes; no acumular copias completas de recursos ni centenares de estados por defecto.
- Dumps, BIOS, guiones, fuentes de arte, partidas útiles y paquetes ya entregados se conservan. Una extracción duplicada solo se retira tras verificar su manifiesto y el archivo que permite recuperarla. Los ZIP entregados son inmutables.
- La limpieza es selectiva y documentada: no usar `git clean -xfd`, borrados recursivos indiscriminados ni restauraciones de cambios ajenos. El ZIP personal en subida no se modifica para incorporar cambios posteriores.
