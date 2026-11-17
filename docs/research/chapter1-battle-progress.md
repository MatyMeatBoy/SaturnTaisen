# Capítulo1: validación de combate en curso

No se ha verificado todavía el capítulo entero. La ruta continua anterior llega a un pasillo; los tramos siguientes parten de estados locales para investigar y no completan esa ruta.

Se completó el tutorial de órdenes y se verificó un ataque normal de Sakura: efecto de ataque, desaparición del enemigo y retorno a las acciones restantes. tests/battle-first-attack.movie reproduce ese ataque desde la escena local fijada. tests/test_battle_progression.py compara1200 hashes de frame y la imagen final entre AOT estricto y el intérprete del mismo SDK: coinciden. AOT ejecuta cero bloques interpretados. Es comparación de rutasCPU, no una referencia independiente de todo el hardware.

También se observaron defensa, cambio de turno, cámara de fase enemiga y movimiento de María con confirmación/cancelación. Se preservan backups originales y los movies/logs/estados bajo local/work/chapter1-progression. Ningún tramo fuerzaHP, victoria o variables de misión. Las pulsaciones cubren varios campos para que el sondeoSMPC pueda observarlas; una transición de un solo frame puede no ser muestreada por el juego.

Faltan victoria del combate, final del episodio, composición continua sin cargas de estado y guardado/carga nativa del final. No se convierten estos hitos parciales en afirmación de capítulo completo.
