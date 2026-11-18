# Inventario de menús/HUD PC para el mod HD (T23)

Evidencia legible por máquina: [pc-menu-hud-inventory.json](pc-menu-hud-inventory.json).

Primer paso de T23: identificar qué recursos PC de menú/interfaz (`SAKURA1/SYSTEM/*.SPR`) tienen un archivo Saturn candidato equivalente, antes de intentar ninguna sustitución visual. `tools/audit_pc_menus.py` sigue el mismo patrón de solo-cabecera que `audit_hd_characters.py`: no copia píxeles ni arte al repositorio, solo cuenta imágenes y hashes.

## Resultado

```
python tools/audit_pc_menus.py --pc-root <extracción PC> --disc local/prepared/disc1/Track\ 01.iso --disc local/prepared/disc2/Track\ 01.iso --output <informe local>
```

29 archivos `.SPR` en `SAKURA1/SYSTEM`, 572 imágenes no vacías, 0 errores de cabecera. 20 de 29 tienen un archivo Saturn candidato por nombre; los otros 9 (`BURO_W`, `FONT_CSL`, `JYOUKI`, `KAO`, `OP_WIN`, `R_HARI`, `SHADE_WA`, `SHADE_WB`, `TUIKA_W`) no tienen todavía una correspondencia propuesta.

## Candidatos por nombre (sin verificar geometría ni paleta)

| PC (`SYSTEM/*.SPR`) | Saturn candidato | Nota |
| --- | --- | --- |
| `TITLE`, `SEGALOGO`, `REDLOGO`, `CAUTION`, `TL_BG0`, `TL_ROGO0` | `LOGO.SH2` | Pantalla de título; ya tiene texto propio traducido (ver `traduccion-espanol.md`). |
| `OPTION`, `WINDOW`, `EXIT_W` | `SAKURA` | Opciones/carga; coincide con las pantallas ya traducidas (`opciones()`, `carga()` en `tools/es/menus_es.py`). |
| `NOWLOAD` | `LOAD.BIN` | **Candidato directo para la pantalla LOADING** marcada como bloqueada en T25 (arte pintado a mano en Saturn, sin texto en tiles). Si el PC guarda «Now Loading» como sprite independiente en vez de fundido con el fondo, podría dar una vía de traducción que Saturn no ofrece sola. Pendiente inspeccionar su geometría y paleta antes de asumir nada. |
| `OMKMOV_W`, `OMKSND_W`, `KARAOKE`, `MINISAKU`, `MSTAFF` | `OMALL.DAT` | Candidatos para el menú extra (T25 lo dejó bloqueado por falta de tabla de punteros en Saturn). El PC podría tener el equivalente en una tabla de texto más simple. |
| `SISTEM`, `SIS_BG`, `SIS_BG2`, `SIS_BG3`, `SIS_ICON` | `ICATALL.DAT` | Candidatos para estado/intermedio, ya traducidos en Saturn; sirven como referencia de diseño, no como bloqueo. |

## Siguiente paso

Para cada candidato con `found=true`: decodificar ambas imágenes (PC vía el exportador nativo `sakura.exe --export-pc-spr`, Saturn vía las herramientas ya existentes en `tools/es/`), comparar geometría y verificar si el PC separa el texto del fondo de un modo que Saturn no hace. Ninguna coincidencia de nombre aquí demuestra composición, paleta ni geometría compatibles — es una lista de candidatos a verificar, no una integración.
