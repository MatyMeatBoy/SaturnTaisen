# Inventario de menús/HUD PC para el mod HD (T23)

Evidencia legible por máquina: [pc-menu-hud-inventory.json](pc-menu-hud-inventory.json).

Primer paso de T23: identificar qué recursos PC de menú/interfaz (`SAKURA1/SYSTEM/*.SPR`) tienen un archivo Saturn candidato equivalente, antes de intentar ninguna sustitución visual. `tools/audit_pc_menus.py` sigue el mismo patrón de solo-cabecera que `audit_hd_characters.py`: no copia píxeles ni arte al repositorio, solo cuenta imágenes y hashes.

## Resultado

```
python tools/audit_pc_menus.py --pc-root <extracción PC> --disc local/prepared/disc1/Track\ 01.iso --disc local/prepared/disc2/Track\ 01.iso --output <informe local>
```

29 archivos `.SPR` en `SAKURA1/SYSTEM`, 572 imágenes no vacías, 0 errores de cabecera. 20 de 29 tienen un archivo Saturn candidato por nombre.

De los 9 restantes, `KAO.SPR` (394 imágenes) no es un recurso de menú: ya lo cubre `audit_hd_characters.py` como retrato de personaje (T09/T19), fuera del alcance de T23. Los otros 8 (`BURO_W`, `FONT_CSL`, `JYOUKI`, `OP_WIN`, `R_HARI`, `SHADE_WA`, `SHADE_WB`, `TUIKA_W`) se buscaron por nombre completo y por fragmento en el listado ISO de ambos discos sin ningún resultado: no tienen archivo Saturn con un nombre reconocible. O el recurso Saturn equivalente usa un nombre distinto (requeriría comparación visual, no solo de nombre) o es exclusivo del PC (por ejemplo `SHADE_WA`/`SHADE_WB`, 576×320 y 608×128, parecen overlays de transición; `TUIKA_W`, 576×48/80 y 384×80, su nombre japonés sugiere «añadido», posible contenido extra solo-PC).

## Candidatos por nombre (sin verificar geometría ni paleta)

| PC (`SYSTEM/*.SPR`) | Saturn candidato | Nota |
| --- | --- | --- |
| `TITLE`, `SEGALOGO`, `REDLOGO`, `CAUTION`, `TL_BG0`, `TL_ROGO0` | `LOGO.SH2` | Pantalla de título; ya tiene texto propio traducido (ver `traduccion-espanol.md`). |
| `OPTION`, `WINDOW`, `EXIT_W` | `SAKURA` | Opciones/carga; coincide con las pantallas ya traducidas (`opciones()`, `carga()` en `tools/es/menus_es.py`). |
| `NOWLOAD` | `LOAD.BIN` | Descartado como atajo: `NOWLOAD.SPR` tiene una sola imagen de 640×480 (formato 0x15), igual de fundida que la pantalla LOADING de Saturn — el PC tampoco separa el texto del fondo aquí. `FONT_CSL.SPR` (16×32×2, nombre sugiere fuente) es la pista que queda por revisar si se busca una fuente propia para LOADING/episodio; no se ha verificado todavía. |
| `OMKMOV_W`, `OMKSND_W`, `KARAOKE`, `MINISAKU`, `MSTAFF` | `OMALL.DAT` | Candidatos para el menú extra (T25 lo dejó bloqueado por falta de tabla de punteros en Saturn). `KARAOKE.SPR` tiene 17 imágenes individuales de 32px de alto y ancho variable (192-352px) — compatible con una lista de etiquetas de texto separadas (títulos de canción), a diferencia de una imagen fundida única. Esto apoya que el menú extra de Saturn (271 pares DTE en `OMALL.DAT`) sea una lista real de etiquetas y no datos sin usar, aunque no resuelve su tabla de punteros. `OMKMOV_W`/`OMKSND_W` (500×376/480×376, varias por categoría) parecen paneles de fondo por pestaña, no texto suelto. |
| `SISTEM`, `SIS_BG`, `SIS_BG2`, `SIS_BG3`, `SIS_ICON` | `ICATALL.DAT` | Candidatos para estado/intermedio, ya traducidos en Saturn; sirven como referencia de diseño, no como bloqueo. |

## Siguiente paso

Para cada candidato con `found=true`: decodificar ambas imágenes (PC vía el exportador nativo `sakura.exe --export-pc-spr`, Saturn vía las herramientas ya existentes en `tools/es/`), comparar geometría y verificar si el PC separa el texto del fondo de un modo que Saturn no hace. Ninguna coincidencia de nombre aquí demuestra composición, paleta ni geometría compatibles — es una lista de candidatos a verificar, no una integración.
