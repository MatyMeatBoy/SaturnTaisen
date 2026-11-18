# Pendientes — cola compartida

Actualizado 2026-11-18. Detalle verificable: [estado actual](ESTADO_ACTUAL.md). Método técnico/artístico: [handoff](HANDOFF.md).

Cola compartida para MatyMeatBoy y los agentes que ayudan (Claude, Codex). Cualquiera puede añadir filas; cada PR toma **una** fila. El detalle técnico sigue en [Prioridad Saturn](superpowers/plans/2026-11-17-saturn-priority.md) y [Capítulo 1](superpowers/plans/2026-11-17-chapter1-progression.md).

## Cómo se toma un pendiente

1. `git fetch` y leer esta lista en `origin/main`, más las PR abiertas (`gh pr list`). Una fila con rama o PR abierta ya está tomada.
2. Elegir la primera fila `libre` (las marcadas `tras Txx` esperan a esa fila) por prioridad (P0 antes que P1…) cuyo **Tipo** pueda resolverse con lo disponible:
   - `agente`: código, pruebas sintéticas o documentación, sin datos privados.
   - `local`: requiere `local/` del propietario (estados, discos preparados); solo en su PC y sin subir nada de `local/`.
   - `físico`: hardware (RX 6900 XT, mandos M30); lo prueba el propietario.
   - `decisión`: necesita respuesta del propietario antes de tocar código.
3. Si la fila no cabe en ~15 minutos, hacer la parte mínima verificable y dividir el resto en filas nuevas.
4. Trabajar en un worktree desde `origin/main`, rama `pendientes/<id>-<tema>`. Nunca mezclar el trabajo sin commitear de otra copia.
5. Abrir PR con: fila tomada, qué se verificó (comando y resultado) y qué no. Cambiar el estado de la fila en el mismo PR.
6. Prioridad ante todo: bloqueos o pérdida de progreso > validación de capítulo 1 > presentación > decoración.

Reglas de integración confirmadas por el usuario el 2026-11-18: Claude y los workers envían solo PR; Codex coordinador revisa, resuelve conflictos e integra las PR autorizadas. No pedir de nuevo autorización por cada integración rutinaria. Una PR abierta reclama la fila; consultar su rama antes de duplicar trabajo.

Reglas fijas: Autor siempre MatyMeatBoy; nunca subir discos, BIOS, partidas, recursos PC originales, `local/` ni el ZIP personal; v0.1.0, v0.1.5 y v0.1.2 son inmutables; Saturn tiene prioridad sobre PC; ninguna prueba parcial se presenta como capítulo o campaña completos.

## Lista

| ID | P | Tipo | Estado | Pendiente |
|---|---|---|---|---|
| T01 | P0 | agente | integrado · PR #4 | Patches 0035/0036, fondos, táctica, texto, catálogos, pruebas y handoff integrados. Nuevas tareas parten de origin/main; acordar archivos antes de tocar renderer compartido. |
| T02 | P0 | local | dividido · ver T02a–T02c | Victoria del primer combate y salida. El movie continuo de 23.443 frames se reproduce en el build actual con 0 interpretados y termina con el menú de órdenes abierto; estado de relevo local `local/work/t02/fin-multiple-turns.state` (SHA-256 4d67dd1a…). |
| T02a | P0 | local | libre | Desde el estado de relevo, grabar los turnos restantes hasta derrotar a todos los enemigos, con pulsaciones de varios frames (SMPC) y sin forzar HP ni variables. |
| T02b | P0 | local | tras T02a | Pantalla de victoria y salida del combate hasta el control normal, con hash guest y RGB iguales a la referencia. |
| T02c | P0 | local | tras T02b | Componer `battle-multiple-turns.movie` + T02a + T02b con `tools/stitch_battle_replay.py` y repetir de una sola carga; registrar en `chapter1-continuous-battle.json`. |
| T03 | P0 | local | tras T01 | Ruta continua New Game → fin del episodio 1, guardado nativo, reinicio y Continue, dos repeticiones. |
| T04 | P1 | local | implementado y probado · patch0045 | Texto HD LIPS de dos/tres opciones en Zoom/conjunto: diez perfiles,240hashes iguales por escena, cero interpretados; reloj/marco conservados. Vencimiento natural y otras elecciones pendientes; aún sin paquete nuevo (ver `chapter1-choice-hd.md`). |
| T05 | P1 | local | integrado · PR #4 | Solapamiento corregido en Mejorado; cinco pestañas y rutas verificadas. Conservar pruebas y fallback seguro para menús desconocidos. |
| T06 | P1 | agente | tras T01 | Pulir la junta de fase entre mosaicos LOADING y el centro protegido. |
| T07 | P1 | local | hecho desarrollo · T01 | Intro previa al título: área 288×144 en 16,24 a la mayor escala entera con subtítulos ingleses. |
| T08 | P1 | local | tras T01 | Fondos extendidos durante fundidos: medir los fotogramas exactos de fallback `native` (añadir número de fotograma a la traza de layout). |
| T09 | P2 | local | libre | Retratos pendientes del capítulo 1 (32 en el checkpoint 201), revisando `004f`, `0095`, `00a1`, `00ef`, `013b`, `013c` y `0169` por sus tres regiones. |
| T10 | P2 | local | integrado · PR #9 | Mezcla blanca HD con metadatos exactos, alfa y caché por peso; compositor sintético5/15/25 y testigo real25/32 a1440p pasan. Otras identidades/animaciones siguen T09/T19. |
| T11 | P2 | agente | tras T01 | Integrar el catálogo de diálogo precargado con el lector de tablas inglesas validado. |
| T12 | P2 | local | tras T01 | Cámara de combate con la extensión táctica STAGE01 anclada en 656,24 durante todo el combate. |
| T13 | P2 | agente | integrado · PR #2 | Normalizar finales de línea (avisos CRLF/LF) con `.gitattributes`, sin cambiar contenido. |
| T14 | P3 | agente | integrado · PR #3 | Índice de `docs/research` con una línea por documento. |
| T15 | P3 | decisión | libre | Revisar y fusionar `codex/catalog-listing` (ficha pública e icono). |
| T16 | P3 | físico | libre | Probar el ZIP portátil en RX 6900 XT y mandos M30 físicos. |
| T17 | P1 | local | libre | Cambio real de disco 1→2 e importador final unificado. |
| T18 | P2 | agente/local | libre | RetroAchievements 16546 softcore: catálogo/condiciones/badges 1:1, desbloqueo local offline, pestaña/popup, login y sync. Alcance ya aprobado, implementación pendiente. |
| T19 | P3 | local | libre | Cuerpos HD (NC): escala única por altura y eje cabeza/torso, con ojos/boca. |
| T20 | P3 | local | libre | Vídeos MPG del PC (MOVIE000..120): equivalencia, audio y subtítulos antes de sustituir. |

| T21 | P0 | agente/local | integrado · PR #6 | Herramienta K001–K019 probada: reproduce exactamente 614.024 candidatos desde la semilla anterior. Código derivado solo local. |
| T22 | P0 | local | empaquetado y traslado verificados | v0.2.0-test.1: release público limpio y ZIP privado de 708.495.279 bytes, disco1 inglés + HD procesado. Escena HD y combate arrancan desde extracción nueva con PATH Windows, cero interpretados. RX 6900 XT física pendiente T16. |
| T23 | P1 | local | libre | Menús/HUD equivalentes PC: inventario y matches verificados para Saturn, sin deformar proporciones. |
| T24 | P2 | agente/local | libre | Medir y desactivar trabajo auxiliar táctico en Original sin cambiar píxeles/guest; declarar caché y condiciones. |
| T25 | P1 | agente/local | Claude · en curso | Parche al español (menús + capítulo 1). Herramientas en `tools/es/` y método en `docs/research/traduccion-espanol.md`; guion y datos solo en `local/work/guion-es`. Capítulo 1 traducido y revisado con japonés; título, intermedio, opciones y carga en español. Faltan estado, barra de combate, rótulos de carga/episodio/LOADING, extras, texto HD y opción de idioma en el launcher. |
| T26 | P0 | local | tras T02/T03 y huecos HD | Entrega posterior con el capítulo1 completo y su mod HD verificados. El test.1 solicitado para otro PC no cierra esta tarea. |
| T27 | P1 | local | libre | Ampliar observaciones del índice de escenas: actualmente inventario de ambos discos, 112 tablas, 54 vídeos y nueve observaciones. Confirmar por ruta los seis tags, texto/subtítulos y encuadre de cada clip; no convertir candidatos en cobertura probada. |
| T28 | P2 | agente/local | tras T27 por escena | Consumir etiquetas verificadas para la presentación/Zoom sin heurísticas ambiguas. El índice local de metadatos todavía no gobierna el runtime. |
| T29 | P0 | local | integrado · PR #8 | Capítulo2: EVT02 atribuido exactamente a 00204000. Candidato de 643.320 bloques pasa frontera1200 y arranque9501 con todos los hashes/RGB iguales al intérprete y cero interpretados. Base de la ampliación posterior de674.023; test.1 sigue inmutable. |
| T30 | P0 | local | libre | Continuar desde la introducción del combate del capítulo2, validar órdenes/ataques/victoria y presentación. Partida y estado9500 privados disponibles; no confundir carga corregida con capítulo completo. |
| T31 | P0 | local | integrado · PR #10 | Capítulo4: EVT06 registrado por coincidencia completa en RAM; candidato674.023 pasa frontera1200 y carga12000, con todos los hashes/RGB iguales al intérprete y cero interpretados. Integrar PR y continuar combate. |
| T32 | P0 | local | libre | Completar rutas intermedias, combates, guardados y finales de capítulos2–Finale. El barrido inicial valida entradas de ocho rutas (96.000 frames) y el arreglo de entrada de capítulo4, no capítulos completos. |
| T33 | P1 | local | coordinador · reproducción | Inicio y New Game: pétalos16:9, flashes sin borde4:3, caja vacía/sombras antes/después del primer vídeo y zoom de vídeo. Mantener posición aprobada de diálogo entre escenas. |
| T34 | P1 | local | integrado · PR #11 | Recorte exclusivo del vídeo de novela 288×144; cajas vacías antes/después siguen T33. |
| T35 | P1 | local | integrado · PR #11 | Continuidad floral y mezcla exacta del relleno del diálogo; fallback para mezclas no probadas. |
| T36 | P1 | local | integrado · PR #11 | El cursor en el borde izquierdo del mapa conserva el fondo ancho. |
| T37 | P1 | local | integrado parcial · PR #11 | Filas Sumire/María corregidas con placa VDP1; expansión a los44 glifos de9píxeles probada en la rama T39. Elecciones y cobertura completa pendientes. |
| T38 | P2 | local | auditoría · PR #11 | Avance con voz: B interrumpe antes que A/C en una línea real, entradas recibidas y paridad AOT/intérprete. Falta referencia Saturn independiente. |
| T39 | P1 | local | integrado · PR #13 | Fundido mapa↔floral y entrada directa aZoom;900hashes y9capturas nativas coinciden, muestreo exacto exterior/imagen/sombra. |
| T40 | P1 | agente/local | libre (coordinar SDK) | Opción «Idioma: English / Español» en el launcher según `docs/research/traduccion-espanol.md`: `language=es` en `launcher.ini`, `find_nearby` prioriza `disc1-es`, selector desactivado si falta. Mientras tanto funciona `tools/es/perfil_es.py`. |
| T41 | P1 | agente/local | coordinador · pendientes/T41-hd-progress | Panel HD generado y porcentajes por categoría/etapa, con fuentes, pendientes y puerta de100% verificado. Actualizar al aprobar nuevos assets. |


## División para colaboradores

- **Coordinador:** integración T01, revisión/merge y seguimiento de T02/T03/T22. Los otros bots no modifican los mismos archivos ni la base AOT compartida durante su compilación.
- **Claude:** escoger una fila libre, preferentemente inventario/matches T09/T19/T20/T23 o herramientas de texto T11. Una rama y una PR por bloque comprobable. No integrar directamente.
- **Otro worker:** elegir otra fila sin archivos compartidos con la anterior; si requiere renderer, reservar antes el archivo en la descripción de la PR y avisar al coordinador.

Al abrir PR indicar ID, archivos propios, prueba y limitaciones. No marcar «hecho» por una propuesta o por compilar. El coordinador actualiza a «integrado» después del merge. Las tareas `local` necesitan datos del propietario; las `físico` dependen de pruebas en su hardware. Ninguna tarea de PC jugable desplaza Saturn.

## Reproducciones visuales nuevas

- T34: viewport de vídeo de novela: corregido en desarrollo para usar 288x144,16,8; fixture pasa a1440p en x8. Falta comprobar runtime y empaquetar. No resuelve todavía cajas vacías antes/después del vídeo.
- Viñetas narrativas dentro del combate: auditoría de sombra original en curso; conservar composición por escena, sin imponer sombra de novela.
- Elecciones LIPS: texto HD pendiente T04; no considerar completo por el diálogo HD.

- T35: continuidad floral del relleno de diálogo en Zoom (reportada por el propietario). Diagnóstico: `Presentation.foreground` guarda RGB final opaco para source<5; al separar/escalar caja se transporta el NBG3 nativo mezclado a otra posición. Investigar captura de top/second/ratio y recomposición sobre el fondo extendido en coordenadas de destino, con aritmética Saturn exacta. No sustituir por opacidad estimada, no regenerar fondos aprobados, preservar Original, marco, retrato y glifos. Pendiente evidencia del estado y prueba de runtime; no incluido en test.1.

- T36: transiciones widescreen: retirar marco rosa host durante fallback de Mejorado (patch39 en desarrollo, falta runtime). Extender también fondos y efectos de transición manteniendo fase/paleta; ocultar el borde no equivale a resolver el fallback nativo ni las flores/pétalos horneados. Revisar entrada muñeco, título/New Game, mapa↔novela y cambios de escena.

- T37: cobertura HD de texto y calidad de los guiones base de traducción. Caso Sumire: registro50039, índice473 de /SAKURA1/0100TBL.BIN, tres filas de27/30/5 caracteres, sin controles desconocidos; la fila intermedia está íntegra en catálogo pero sigue SD en la captura. No corregir prosa ni reescribir la traducción de Claude para ocultar un rechazo de render. Auditoría estructural actual:112 tablas físicas/59450 registros, SHA del JSONL90c3c35f2661f1c8ac7d5bac512655b02d64ea9844a3ca2c17d93230b0ac3684; dos tabuladores no resueltos en el disco1. Falta cobertura visual/elecciones/menús y validación de guiones editados sin sobrescribir target_es.

  T37, segundo testigo: María, registro50064/índice498 de0100TBL, fila3 terminaCP1252 0x85 (puntos suspensivos), texto íntegro y sin controles desconocidos. Sumire reproducida: w enX296,Y172 tiene dos píxeles visibles enX304,Y176–177; `NarrativeInkFits` rechaza la fila completa porX<304. Allí también hay bisel VDP1: no ensanchar ni borrar con underSprites a ciegas. Preparar placa exacta y encaje HD, comprobar María antes de atribuir causa compartida.

- T38: avance de diálogo con voz: comparar A/B/C con pulsos sostenidos y releases, texto revelándose/completo y voz activa/terminada; contrastar AOT/intérprete y referencia Saturn independiente antes de declarar comportamiento original. Medir sondeoSMPC y esperaCD/audio, no asumir cargaSSD. El MessageSkip porR descrito por Kayama15048 es exclusivoDreamcast y posterior a completar, no evidencia de avance manualSaturn. No cambiar temporizadores ni forzar fin de voz para ocultar fallo. Auditoría asignada a wide_transitions tras cerrar filasHD.

### Bloque visual en revisión

- Patches38–41: crop de película288x144; sin bordehostOriginal enMejorado; panel exacto y continuidad floral; mapa con cursorizquierdo verificado200frames; helper deZoom en fundidos con test sintético, aún falta replay integrado.
- T35 panel: implementado y verificado en office-return-3000 (12hashes iguales, región superior intacta); no incluido en ZIPtest.1.
- T36 mapa cursorizquierdo: reproducción before/after confirmada; transición mapa↔novela completa sigue en validación.
- Limpieza: retirados dos candidatos exe sustituidos (1.604.792.320bytes), hashes y sustitutos en local/work/retired-test-binaries.json. Conservar estados y releases.

### Texto de borde: corrección validada

- T37: patch42 convierte las filas reportadas de Sumire/María. PlacaVDP1 con primer píxel anterior y hasta dos glifos escritores; invalidación por tercer escritor, sobreescritura no glifo o escritura guest. Las filas con tinta compartida requieren borrado atómico. Se conserva el clipHD original.
- Pruebas:12hashes por caso iguales entreOriginal,MejoradoHD,MejoradoSD ytest.1Original; RGBOriginalidéntico; AOTestricto0interpretados. Ver hd-text-row-rejections.md. Cobertura de eleccionesLIPS y todoslosguiones sigue pendiente, no declarar todoeltextoHD completo.
- T38: auditoría voz cerrada para primera línea deSumire: Binterrumpe/avanzaantesqueA/C; inputsSMPC recibidos,460hashes+PCM porbotón igualesAOT/intérprete. FaltaSaturnindependiente.
- Patch43 contiene primitivas de mezcla exterior mapa/floral; patch44 las consume en la entrada al comedor, con pruebas de continuidad. Otras transiciones siguen pendientes.

### Integración futura de idiomas

El idioma será una selección del launcher con una variante coherente de guiones, menús, fuentes y recursos. Compartir mapeos de fuente solo cuando el atlas y su codificación coincidan; las cachés de guion/recurso deben incluir idioma/revisión o hash de contenido. No regenerar hojas españolas ni copiar configuración de mandos encima de un perfil ya editado. PR12 integra herramientas privadas de preparación, no declara terminado el selector ni todo el juego traducido. Saturn y las correcciones visuales mantienen prioridad.



| T42 | P2 | local | Sakura y Sumire integradas en PR #15 y #17 · tercer lote revisado | Checkpoint reproducible de 201/304 y 91/123 del capítulo 1. Del tercer lote, María `0064` en base verificada en juego y cuatro identidades comprobadas en atlas. El ZIP entregado conserva su catálogo. |
