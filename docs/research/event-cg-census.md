# Censo EVENT/CG sin equivalente (THD09) - PARCIAL

Estado: herramienta `tools/hd_event_cg_census.py` (borrador, sin tests ni JSON final). No se generó `config/hd-event-cg-census.json` ni se tocó el registro.

Hallazgos offline (sin píxeles):
- EVENT (235 SPR) son sprites de actores tácticos que usa `EVENTANM.TAB`; en Saturn son bancos de imágenes VDP1 (`EVS*.BIN`, conjuntos de imágenes por índices de paleta), no placas. Único par con evidencia: EV00S24 imagen 0 con tiras de EVS02100 (IoU 0,96885, tactical-pairing.md).
- CG (223 SPR) es arte de minijuegos; los 8 fondos ya están emparejados en `config/hd-minigame-bg-pairs.json` (corr. 0,9999). El resto (UI, cartas, cursores) no tiene banco Saturn decodificado.
- Pool Saturn construido: 853 placas distintas (BG, BBG, EVE, IC, KABE, TITLE, OMAKE, LOAD, minijuegos, registros de bancos `*_CG`) y 4.476 siluetas de conjuntos de imágenes.
- Muestra de 6 archivos (ejecución parcial): ninguna placa/componente/silueta firme; mejores placas 0,68 y mejores siluetas 0,72-0,88 (ambiguas o sin pareja). Coherente con el primer pase de SHARDS.md (sin placa EVENT/CG adicional).

No verificado: ejecución completa sobre los 459 archivos, umbrales calibrados con controles (ENDING/ICATCH), tests, filas de registro.
Falta (agente): ejecutar `--build` completo, añadir `--check`, tests sintéticos, clasificar con motivo, enlazar a hd_census. Propietario: ensamblado de tiras VDP1 de EVS requiere traza de runtime.
