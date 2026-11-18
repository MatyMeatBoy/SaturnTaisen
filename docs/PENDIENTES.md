# Pendientes

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

Reglas fijas: los agentes solo abren PR; fusionar o integrar lo hace únicamente MatyMeatBoy. Autor siempre MatyMeatBoy; nunca subir discos, BIOS, partidas, recursos PC originales, `local/` ni el ZIP personal; v0.1.0, v0.1.5 y v0.1.2 son inmutables; Saturn tiene prioridad sobre PC; ninguna prueba parcial se presenta como capítulo o campaña completos.

## Lista

| ID | P | Tipo | Estado | Pendiente |
|---|---|---|---|---|
| T01 | P0 | decisión | propietario | Integrar en una rama el trabajo sin commitear de `implementation/enhanced-v011` (patches 0035/0036, fondos de pantalla, franja táctica, catálogo de diálogo, auditorías y movies). Solo lo hace el propietario; los agentes no integran. |
| T02 | P0 | local | tras T01 | Victoria del primer combate y salida, continuando `tests/battle-multiple-turns.movie` sin cargas intermedias; cero bloques interpretados. |
| T03 | P0 | local | tras T01 | Ruta continua New Game → fin del episodio 1, guardado nativo, reinicio y Continue, dos repeticiones. |
| T04 | P1 | local | tras T01 | Placa de glifos LIPS: reconocer `C510`/`C570`, filas Y=54/78/102 y 62/94, transformación y recorte por grupo (ver `chapter1-wide-transitions.md`). |
| T05 | P1 | local | libre | Solapamiento del submenú táctico con la barra horizontal en Mejorado (referencia Beetle Saturn ya documentada). |
| T06 | P1 | agente | tras T01 | Pulir la junta de fase entre mosaicos LOADING y el centro protegido. |
| T07 | P1 | local | libre | Intro previa al título: área 288×144 en 16,24 a la mayor escala entera con subtítulos ingleses. |
| T08 | P1 | local | tras T01 | Fondos extendidos durante fundidos: medir los fotogramas exactos de fallback `native` (añadir número de fotograma a la traza de layout). |
| T09 | P2 | local | libre | Retratos pendientes del capítulo 1 (42), revisando `004f`, `00ef`, `013b`, `013c` por sus tres regiones. |
| T10 | P2 | local | libre | Mezcla hacia blanco de retratos: aceptar en `PortraitPixelsVisible` las mezclas exactas 5/15/25 sobre 32. |
| T11 | P2 | agente | tras T01 | Integrar el catálogo de diálogo precargado con el lector de tablas inglesas validado. |
| T12 | P2 | local | tras T01 | Cámara de combate con la extensión táctica STAGE01 anclada en 656,24 durante todo el combate. |
| T13 | P2 | agente | libre | Normalizar finales de línea (avisos CRLF/LF) con `.gitattributes`, sin cambiar contenido. |
| T14 | P3 | agente | hecho (PR) | Índice de `docs/research` con una línea por documento. |
| T15 | P3 | decisión | libre | Revisar y fusionar `codex/catalog-listing` (ficha pública e icono). |
| T16 | P3 | físico | libre | Probar el ZIP portátil en RX 6900 XT y mandos M30 físicos. |
| T17 | P3 | decisión | libre | Cambio real de disco 1→2 e importador final unificado. |
| T18 | P3 | decisión | libre | RetroAchievements: alcance confirmado. |
| T19 | P3 | local | libre | Cuerpos HD (NC): escala única por altura y eje cabeza/torso, con ojos/boca. |
| T20 | P3 | local | libre | Vídeos MPG del PC (MOVIE000..120): equivalencia, audio y subtítulos antes de sustituir. |
