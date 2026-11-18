# Identificación de grupos LIPS por el cursor de script

Dos estados propios del disco 1 inglés v2.1 permiten asociar el panel LIPS visible con un registro único de `/SAKURA1/0102TBL.BIN`. Cada registro contiene todas las opciones en orden, separadas por CR. Las coincidencias de frases individuales con otros registros de la misma tabla no identifican el panel.

| Estado privado | Cursor BE32 en `0x060685B4` | Offset de comando en `0102.BIN` | ID decimal e índice de registro en TBL | Offset en TBL y prefijo | Filas nativas Y y celdas |
|---|---|---|---|---|---|
| `prebattle-3000.state` | `0x002068CE` | `0x28C5` | 20008, índice 285 | `0x53CC`, `00000000` | 62: 17, 94: 30 |
| `resume-chapter-6000.state` | `0x002051F2` | `0x11E9` | 20002, índice 64 | `0x2BB0`, `00000000` | 54: 20, 78: 25, 102: 23 |

La comparación verificó ambos archivos completos en Low WRAM de cada estado. `/SAKURA1/0102.BIN` ocupa 26.646 bytes desde `0x00204000` (SHA-256 `0d7fe995a3c488ef4989791068b8b1e97259087ad26cea8150638caaf3e77f4e`). `/SAKURA1/0102TBL.BIN` reside desde `0x00224000` (SHA-256 `7b08f9cd054200f17153db7a6690624b364bff31125a583ae1b689a23a2b2ae2`).

En las dos muestras, el comando empieza nueve bytes antes del cursor. Los bytes iniciales son `2E 80 00` seguidos del ID BE16. El [clasificador FindDialogOrder del equipo traductor](https://github.com/NoahSteam/RomHackingTools/blob/10aefa40c555c2b1135b5836434c2315135b5306/SakuraTaisen/SakuraTaisen.cpp#L2287-L2305) reconoce `2E 80 00` y `17 80 00` como LIPS. La segunda forma queda sin validar en ejecución. El puntero narrativo `0x0606851C` apunta a otro registro en ambos estados.

La inspección de los comandos VDP1 verificó un reloj por panel, filas centradas, espaciado de ocho píxeles y 115 tiles de glifo que coinciden byte por byte con las ranuras del atlas inglés para esas opciones. Ambos estados muestran la primera opción seleccionada. El verificador local `local/work/dialogue-preload-worker/lips-group-verify.py` genera `lips-group-witnesses.json` con los hashes y la geometría; los estados y el texto del juego quedan en local.

## Uso previsto en el runtime

Preparar un índice acotado por identidad del script, offset de comando e ID de registro. En el fotograma presentado, resolver el grupo con el cursor y el script y la tabla residentes verificados. Confirmar las filas del registro contra el panel completo y los tiles antes de prestar su texto. Los controles actuales de reloj, posición, color y propiedad de tinta siguen siendo necesarios. Si falla alguna comprobación, conservar la reconstrucción actual por glifos.

Quedan por comprobar el significado de los cuatro bytes finales del comando, la distancia al cursor para otras ramas u opcodes, las coordenadas de otros paneles, LIPS de combate y el disco 2. Este estudio no modifica el SDK ni integra texto precargado para elecciones.
