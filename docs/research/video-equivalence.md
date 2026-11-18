# Equivalencia de vídeos Saturn ↔ PC

Alcance T20, solo inventario: sin sustituir ninguna reproducción. Las medidas salieron de ffprobe sobre los flujos FILM de ambos discos (extraídos por LBA/desplazamiento del inventario de escenas) y sobre los MPEG de PC extraídos del cabinet; ningún archivo original se versiona.

| Dato | Valor |
| --- | --- |
| Flujos FILM Saturn únicos | 51 (50 clips + stub de logo de 0,15 s) |
| MPEG PC | 52 (MOVIE000–MOVIE120 sueltos + REDLOGO) |
| Pares con orden consecutivo y duración ≤ 0,5 s | 44 |
| Pares con duración distinta (revisar montaje) | 6: 743bce↔009 (0,65 s), d33904↔105 (0,98), b39c1e↔004 (1,06), ab833c↔011 (1,08), 7b1472↔102 (1,51), def7a6↔020 (3,73) |
| PC sin pareja Saturn asignada | MOVIE118 (9,43 s, similar a MOVIE015), REDLOGO (5,32 s) |

Método: duración relativa, miniaturas grises de 24×12 en cinco puntos relativos y orden de flujo en `/SAKURA4` (flujo k ↔ `MOVIE00k`). Las miniaturas por sí solas son débiles (la paleta Saturn difiere), por lo que la asignación manda por duración y orden; no se declara montaje, audio ni subtítulos equivalentes.

Pendiente: revisar los seis pares, comparar audio/subtítulos/saltos y diseñar la decodificación MPEG-1/MP2 y la sincronía en el runtime. No integrado en test.4.
