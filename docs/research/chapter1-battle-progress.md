# Capítulo1: validación de combate en curso

No se ha verificado todavía el capítulo entero. La ruta continua anterior llega a un pasillo; los tramos siguientes parten de estados locales para investigar y no completan esa ruta.

Se completó el tutorial de órdenes y se verificó un ataque normal de Sakura: efecto de ataque, desaparición del enemigo y retorno a las acciones restantes. tests/battle-first-attack.movie reproduce ese ataque desde la escena local fijada. tests/test_battle_progression.py compara1200 hashes de frame y la imagen final entre AOT estricto y el intérprete del mismo SDK: coinciden. AOT ejecuta cero bloques interpretados. Es comparación de rutasCPU, no una referencia independiente de todo el hardware.

También se observaron defensa, cambio de turno, cámara de fase enemiga y movimiento de María con confirmación/cancelación. Se preservan backups originales y los movies/logs/estados bajo local/work/chapter1-progression. Ningún tramo fuerzaHP, victoria o variables de misión. Las pulsaciones cubren varios campos para que el sondeoSMPC pueda observarlas; una transición de un solo frame puede no ser muestreada por el juego.

Faltan victoria del combate, final del episodio, composición continua sin cargas de estado y guardado/carga nativa del final. No se convierten estos hitos parciales en afirmación de capítulo completo.


## Turnos continuos y bloqueo de Sumire

`tests/battle-multiple-turns.movie` recorre 23.443 frames desde un fixture local posterior al primer ataque de Sakura, con una sola carga inicial y ninguna carga intermedia. El hash guest y los píxeles RGB finales coinciden con el último probe de la cadena. El binario cd4407e ejecutó cero bloques interpretados. Esto valida composición y progresión de esos turnos; todavía no incluye victoria ni ruta desde New Game. El fixture SHA y alcance están en chapter1-continuous-battle.json.

A continuación, el ataque normal de Sumire reproduce una salida AOT estricta código 4 en 060783FC. La ejecución instrumentada de referencia atribuye los bytes a `/SAKURA2/K002.BIN`, offset03FC, base06078000, SHA256 8ce336483ca256b87e0d96eb1575afca07959a42e7ce48eccbde67684253cbcb. La referencia completa el ataque y elimina uno de los enemigos. Este fallo afecta al binario de v0.1.2; su ZIP y etiqueta se conservan inmutables. La ampliación de candidatos estáticos se verifica antes de declarar corregido el bloqueo.

En desarrollo se añadieron33.696 candidatos AOT para las18 variantes únicas de la familiaK001–K019, hasta614.024 bloques estáticos. Las regresiones de ataques de Sakura1200frames y Sumire1800frames coincidieron en cada hash guest y RGB final con la referencia, con cero instrucciones interpretadas en AOT. Evidencia previa al trabajo de presentación: `local/logs/sumire-fixed-parity.log`. La corrección no modifica los ZIPs ya entregados y todavía no acredita victoria ni capítulo completo.

## Relevo hacia la victoria

Repetición del 2026-11-18 sobre el build local actual: `tests/battle-multiple-turns.movie` desde el fixture `chapter1-multiple-turns.state` (SHA-256 87f69986…) completa los 23.443 frames con 0 bloques interpretados. El último frame muestra el menú de órdenes de una unidad (Move/Atk/Def/Info/End). Se guardó en el frame 23.400 un estado local de relevo, `local/work/t02/fin-multiple-turns.state` (SHA-256 4d67dd1adc217d0a617baf1396b14ef29724663b68ee41f50552d88bef8d17b0), para grabar los turnos restantes (T02a). No se comparó con la referencia en esta repetición ni se contó el número de enemigos restantes.
