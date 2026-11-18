# Capítulo 2 — órdenes y primeras rondas de combate

Una partida propia del episodio 2, cargada por Continue desde el disco 1, llega al combate y permite ejecutar órdenes, cruzar la primera fase enemiga y volver al turno aliado. El candidato estricto ejecutó todos los tramos sin bloques interpretados. El capítulo queda en curso.

| Hito observado | Evidencia privada en `local/work/t30-chapter2-followup` |
|---|---|
| Continue muestra la introducción del episodio 2 | `cold-native/frame-009501.png` |
| María confirma un movimiento y queda en una posición nueva | `first-move/frame-000600.png` |
| Sakura ejecuta Defend y se ve el escudo | `sakura-defense/frame-000120.png` |
| Se completa la fase aliada y los enemigos se mueven y disparan | `fifth-end-order/frame-000180.png`, `fifth-end-order/frame-000540.png`, `enemy-turn/frame-000600.png` |
| María recupera el turno, selecciona a Musket #7 y confirma un ataque | `enemy-turn/frame-001800.png`, `maria-second-aim/frame-000180.png`, `maria-confirm-hit/frame-000180.png` |
| El ataque inflige 68 de daño y la barra de vida baja | `maria-confirm-hit/frame-000180.png`; SHA-256 `85c4846c77bdcb14082a58471b78c18e7adb1cf22e07b1c2f12d573ec2a889ef` |
| María vuelve a disparar después de la segunda fase enemiga. Musket #7 pierde la vida restante, explota y desaparece del campo | `maria-elimination/frame-000420.png`, `frame-000540.png` y `frame-000780.png` |
| Se abre un LIPS táctico con tres opciones. Se selecciona la segunda, aparece su respuesta y Kohran vuelve a recibir órdenes | `round-two-kohran-ranged/frame-000060.png` y `frame-000300.png`, `kohran-turn-ready/frame-000300.png` |

El tramo privado `first-defense` conserva su nombre original. La orden observada en ese tramo es Info → Advice. La defensa efectiva se probó en `sakura-defense`. La primera cuadrícula de ataque de María solo acredita selección de orden; el impacto se observó después de la fase enemiga.

## Comparación por tramos

Binario aislado de 674.182 bloques, patch 0050, SHA-256 `df68e9dbe2c7d9efe273e0e716c504774ba5c5f5f0826abc783a2e3d6bffcbd3`. Se comparó AOT estricto con el intérprete del mismo SDK, en presentación Original y con los mismos estados iniciales, SRAM y películas de mando. Las comparaciones cubren los hashes del huésped, las muestras RGB y los bytes de SRAM final.

| Tramo | Fotogramas comparados | Pares RGB |
|---|---:|---:|
| Continue desde arranque frío | 9.501 | 1 |
| Introducción del combate | 3.600 | 6 |
| Cancelación, cursor y primer movimiento | 960 | 16 |
| Advice, cuadrículas, relevo y Defend | 3.300 | 55 |
| Diálogo, órdenes de fin, fase enemiga y ataque de María | 8.580 | 143 |
| Segundo turno aliado, LIPS táctico y cuadrícula de Kohran | 2.580 | 43 |
| Segunda fase enemiga y eliminación de Musket #7 | 4.620 | 77 |
| Total por tramos | 33.141 | 341 |

Todos los pares coincidieron y la SRAM conservó SHA-256 `4c22bf1edd1437b082ccd05e12df5bbf46bdcc5c9058fa3cc869db281f043908`. Los informes se conservan en `cold-result.json`, `intro/cold-result.json`, `orders-result.json`, `tactical-interactions-result.json`, `enemy-turn-result.json`, `second-allied-turn-result.json` y `third-round-result.json`. Cada relevo conserva su película, estado final, SRAM y hashes.

El relevo más avanzado de esta comparación es `maria-elimination/finish.state` (SHA-256 `f1084a893b337712195d700b110855138e6f20b00104bd108742c7100302ca01`) con la SRAM del mismo directorio. Quedan pendientes la derrota de todas las unidades objetivo, la victoria y la salida del combate. Esta comparación evalúa la ruta en presentación Original y usa como referencia el intérprete del mismo SDK.
