# Traslado a otro PC — v0.2.0-test.4

## Para jugar

1. Extrae **todo** el ZIP en una carpeta con permiso de escritura. No ejecutes el programa dentro del ZIP.
2. Abre `Jugar.bat`. En el paquete personal se detectan el disco 1 inglés y el HD procesado incluidos.
3. Elige Original o Mejorado y la visualización Original o Zoom. F11 cambia pantalla completa; Esc/F1 o Start+Select/Back abre ajustes.
4. Para una prueba rápida usa `Probar escena HD.bat` o `Probar combate.bat`. Son accesos del paquete personal y usan partidas de prueba separadas.

El paquete público requiere tus discos propios. El personal es una excepción local de pruebas con disco 1; no se publica. El juego final unificado necesitará ambos discos. Los vídeos que contiene esta entrega son los de Saturn: la sustitución por vídeos PC sigue pendiente.

## Qué viene incluido

- Launcher, runtime Windows x64 y sus DLL: SDL3, libc++, iconv y zlib.
- `import-saves.exe` y el importador integrado en el launcher.
- `Mapear M30.exe`, herramienta independiente para registrar botones y guardar un informe JSON. Su fuente y la guía están en `tools/` y `docs/research/controller-mapper.md`.
- Scripts, configuración, fuentes propias y patches reproducibles del proyecto. El HD procesado y el disco están únicamente en el ZIP personal.

**Para jugar no necesitas instalar Python, MSYS2, compiladores, SDK ni una BIOS externa.** Los scripts `.py` son herramientas de desarrollo y mantenimiento, no pasos del arranque. Si un diagnóstico informa que falta una DLL, conserva el mensaje y comprueba que extrajiste la carpeta completa; no descargues DLL sueltas.

## Partidas, mandos y diagnósticos

`Jugar.bat` guarda el perfil portátil en `user/`. Conserva esa carpeta al actualizar; las partidas normales están en `user/saves/`. Haz una copia antes de importar o sustituir archivos. Los accesos de prueba mantienen sus backups separados de la partida normal.

El M30 XInput documentado usa A→A/South, B→B/East, C→RT, X→X/West, Y→Y/North, Z→RB, L→LB y R→LT. Un dispositivo que se presenta como Xbox genérico puede requerir seleccionar el perfil M30 manualmente. DInput y el hardware del PC destino no quedan certificados por estas pruebas. `Mapear M30.exe` guarda informes; no aplica el mapeo al juego automáticamente ni envía información por Internet.

Si falla, abre `Ver logs.bat` y conserva `user/logs/`, `user/settings.ini`, versión, pasos para reproducir, resolución, GPU y modo/conexión del mando. Para un problema de botones añade el JSON creado por el mapper. No publiques discos, BIOS, recursos PC ni partidas privadas en una incidencia pública.

## Para quien retome el desarrollo

Leer `docs/PENDIENTES.md`, `docs/HANDOFF.md`, las notas de esta versión y la investigación del área. El runtime entregado tiene674.182bloques AOT y patches0001–0050; su SHA256 es `df68e9dbe2c7d9efe273e0e716c504774ba5c5f5f0826abc783a2e3d6bffcbd3`.

La dependencia está fijada en `config/dependencies.json`; las modificaciones se registran como patches. Para reconstruir se requiere un entorno de desarrollo separado con Python, CMake/Ninja y LLVM/Clang de MSYS2 clang64, más los dumps propios y el procedimiento de descubrimiento AOT. El ZIP de juego no instala ese entorno ni contiene el código derivado de los discos.

El experimento de destello0051 quedó fuera de esta entrega, preservado en la rama `pendientes/T33-petal-transitions` (`7888d08`). Solo cubre un subconjunto del destello; aún hay fases parciales y pétalos por resolver. El SDK compartido se devolvió a la pila0050. No aplicar ese experimento como si estuviera validado o incluido.

Se detiene el trabajo por petición del usuario después de cerrar esta entrega. Los relevos privados de capítulos1/2 y sus límites están documentados; no equivalen a una campaña completa.
