# Análisis offline de pendientes HD (2026-11-27)

Seis análisis de solo lectura, hechos en paralelo sobre `main` sin compilar ni ejecutar el juego. Nada de lo de abajo está verificado en juego salvo donde ya lo estaba. Lo único aplicado al código es la cuenta estricta de THD42 en `tools/hd_census.py`.

## THD42: donantes `hd` parciales
- Las cifras del pendiente estaban desfasadas. Hoy la escena total va 616/1088 y la principal (BG+BBG+ENDING+IC) 612/655, como en `docs/HD_PROGRESS.md`. El 586/1095 ya no aplica.
- Los 23 donantes `hd` con otra clave pendiente son 3 BG, 7 ENDING, 12 IC y 1 CG. En casi todos, una clave está integrada en un disco y la del otro disco pendiente. Ningún final de disco 1 está conectado. Los 12 IC tienen la clave de disco 2 sin conectar. BG2093 y BG2238 tienen un tamaño que el runtime no dibuja (T105c). BG2290 y BG_RYORI están en disco 2 sin testigo.
- Por registro y disco, ENDING va 24/60: 24 de 30 en disco 2 y 0 de 30 en disco 1.
- Los 22 `hd`+`excluded` son recortes BG3xxx/BG4xxx. La regla genérica `name[2] in '34'` de `tools/hd_chapter_coverage.py` excluye la clave del otro disco, aunque el runtime filtra estas filas por disco (parche 0215). Su estado honesto sería `paired-not-wired`. Reclasificarlos queda a decisión del dueño.
- **Aplicado:** `tools/hd_census.py` publica el «Integrado estricto» junto a la cifra actual: 593/1088 en escena y 590/655 en principal. Contando como pendientes los recortes del otro disco, queda en 571/1088 y 568/655. Los 10 tests de `tests/test_hd_census.py` pasan.

## THD47: los nueve iconos de objeto
- Los nueve son BUROICON #0, #1, #2, #9 y #13, e ITEMICON #19, #20, #28 y #84. El parche 0301 ya vincula siete, sin verificar en juego. Quedan abiertos #0 y #84.
- `NCOBJ.BIN` tiene 28 iconos de 32×32 a 8 bpp, con la paleta de CRAM 0xB00 (hash 3BBF6ACDF791D975). La correspondencia es ITEMICON #n ↔ slot n−1 ↔ ITEMnn, para n de 1 a 28. BUROICON repite piezas de ITEMICON.
- BUROICON #0 es una baldosa lisa sin pareja: propuesta excluirla. ITEMICON #84, la botella, no tiene icono compacto en NCOBJ: propuesta excluirlo.
- **Posible defecto en 0301**, deducido de los píxeles y no visto en pantalla: con `cropX=5` (BUROICON #2, #9 y #13, e ITEMICON #28) entra la columna del marco cian, con alfa 255. A 1440p se vería una franja de unos 3 px. La corrección probable es `cropX=4`, pendiente de captura a 1440p.
- Aparición natural de ITEM03, ITEM09 e ITEM27: un estado con el objeto en el inventario, Start y el cursor encima.

## THD32: denominadores tácticos y apariciones
- Los 542 SPR tienen estado explícito (el CSV se regenera con `python -I tools/thd32_audit.py <repo> <árbol PC> <salida>`):

  | Estado | Archivos | Detalle |
  | --- | ---: | --- |
  | verificado | 15 | suelos |
  | integrado sin verificar | 8 | suelos |
  | excluido | 78 | 57 ITEM con sección propia y 21 MAP que el PC no carga |
  | pendiente | 441 | 291 UNIT, 133 capas MAP, 17 SAKURA1/MAP y 3 suelos bloqueados |

- Sin duplicados, el denominador es 464, con integrado 23/464 y verificado 15/464. Los suelos van 23/26 integrados y 15/26 verificados.
- Apariciones (el CSV se regenera con `tools/thd32_apariciones.py` a partir del anterior):
  - Capítulo observado: MAP01–06, 08–10, 12–16, 19 y 21.
  - Capítulo inferido: MAP07, 11, 17, 18, 20 y 23.
  - Desconocido: MAP22 y MAP24–26.
  - Ninguna UNIT tiene capítulo observado.
- Decisiones abiertas:
  - Excluir o no los 21 MAP que el PC no carga.
  - Si TMAP/FUKA va a HUD.
  - Si las capas Priority, AllMapImage y Sky se excluyen por diseño.
  - Si UNIT se cuenta por archivo o por contenido.
- `hd-chapter-coverage.json` tiene MAP03 en `unassigned`, aunque la documentación lo da al capítulo 3.

## THD16: suelos directos del disco 2
- MAP17, 18, 24, 25 y 26 ya están registrados por el parche 0300, con `verified_in_game: false`. Solo tienen evidencia offline.
- MAP01 del disco 2 comparte BIN y clave con el disco 1 (1CAF3218B4B0F9F0). La fila de `hd-chapter-coverage.json` que lo da como `paired-not-wired` tiene el motivo desfasado.
- MAP10 y MAP19 se quedan con el suelo nativo: no hay evidencia nueva.
- Lo que falta es una ruta: ninguno de los 2.021 estados guardados contiene esas claves.
  - Para MAP17 y MAP18: la ruta Iris desde el final de MAP16.
  - Para MAP24–26: desde `bank-10-*`, tras cerrar MAP23 (THD17).
- La sonda documentada (`local/build/sakura-tgprobe`) es anterior a 0300: hay que pasarle un runtime v0.3.7 o posterior con `--exe`.

## THD21: marcos y menús del sistema
- FONT_CSL #0/#1, WINDOW #0–#3 y las cinco parejas SISTEM siguen cableadas.
- El resto de SYSTEM no tiene testigo Saturn con correlación ≥0,75. La más alta es 0,43.
- **Medida nueva:** el directorio de sprites de menú de los WKL del ISO inglés replica los bancos SLGSYS índice a índice, a la mitad de tamaño. Las 6 piezas ya cableadas dan IoU de máscara de 0,98 a 1,0.
- Quedan 20 candidatas firmes sin cablear: SLGSYS03 #1, #2 y #5–#20, SLGSYS00 #4 y SLGSYS02 #33. Antes de cablearlas hace falta la paleta y CMDCOLR de un estado táctico, porque el IoU solo mide la silueta.
- Necesitan un testigo de animación: SLGSYS02 #33–#45, SLGSYS01 y SLGSYS03 #4.
- No se sustituyen los rótulos que el Saturn lleva traducidos.
