# Mapeador de mandos por entradas físicas

Herramienta independiente del juego, con esquemas propios Saturn, Genesis 3 y Genesis 6. Compilación: `python tools/build_controller_mapper.py`; ejecutable local en `local/build/controller-mapper/Mapear M30.exe`, con sus DLL al lado. No necesita discos, BIOS, recursos PC, Python ni compiladores en el equipo de uso.

El usuario selecciona el dispositivo y la disposición, deja todo en reposo y pulsa Comenzar. La figura resalta cada posición física. Se registran botones, mitades de eje con su valor de reposo y crucetas hat, sin presuponer la normalización SDL. Se exige soltar antes de otro paso; entradas duplicadas y diagonales de hat se rechazan. Repetir/Omitir permiten corregir o declarar botones ausentes. Back/Select es extra PC y no se presenta como botón original Saturn.

Guardar informe crea un JSON en informes junto al EXE, con fallback en AppData si no puede escribirse allí. Contiene esquema, nombre/GUID/VID/PID observados, modo declarado, mapping SDL existente y acciones→entradas físicas. No envía datos, no toma números de serie y no aplica bindings al juego. La identidad se conserva si el dispositivo se desconecta después de completar el recorrido, para no perder el informe.

Pruebas: núcleo sintético de layouts, liberación, duplicados, ejes opuestos y JSON; arranque/interfaz sin toolchain en PATH; recorrido completo con joystick SDL virtual, cuatro hats y diez botones, guardado y parseo del JSON. La prueba virtual no acredita el mapping físico del M30: ese informe lo completará el propietario.

Para reutilizar mappings, distinguir identidad observada de nombre comercial: un dispositivo XInput genérico puede ocultar el modelo. Contrastar el informe con el backend/modo exacto antes de cambiar Auto, y respetar overrides del usuario.
