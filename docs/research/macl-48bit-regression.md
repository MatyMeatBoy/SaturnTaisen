# MAC.L: acumulación saturada de 48 bits

La investigación del hilo de cheviman señaló un caso de aritmética SH-2 que se contrastó con el [manual oficial Renesas SH-1/SH-2/SH-DSP, sección6.1.31](https://www.renesas.com/en/document/mas/sh-1sh-2sh-dsp-software-manual). Con S activado participan los 48 bits bajos del acumulador. La lectura del código ajeno se utilizó como pista; la prueba y la corrección son propias y no incorporan código de htmlsaturn.

## Reproducción

Con acumulador 0xFFFF000000000000 y ambos operandos cero, los bits activos representan cero. Antes del cambio, el generador nativo devolvía el máximo de saturación y el intérprete propio el mínimo. Ambos incluían bits inactivos y el generador además elegía la dirección de saturación por el signo del producto. No es prueba de que este caso se haya producido durante una escena observada de Sakura.

Los registros completos se conservan localmente en v02-macl-red.log. La prueba falló en ambas rutas antes de corregirlas. Se revisa tanto el intérprete como el generador: corregir una sola ruta podría dejar una referencia errónea o C++ generado obsoleto.

## Corrección

El acumulador se enmascara y se interpreta con signo de 48 bits; el producto y la suma se calculan sin desbordamiento firmado y se limitan por comparación del resultado con los extremos permitidos. Con S desactivado se mantiene la suma modular de 64 bits. Se mantienen orden de lecturas, incremento de punteros, flags y ciclos nominales.

La prueba sintética compila las instrucciones emitidas por el sh2emit.py de producción, sin escribir un sustituto a mano. Cubre operandos extremos y cruces de signo, arrastre entre mitades, bits altos inactivos, registros de dirección coincidentes y distintos, S activado/desactivado y ambos SH-2. Son 11.616 casos por ruta (nativa e intérprete), incluyendo direcciones y conservación de flags. Los bits altos no activos de MACH no se tratan como un resultado definido de 48 bits. El modelo esperado usa aritmética de 128 bits, de forma independiente a la fórmula de producción.

Se regeneraron los 580.328 bloques AOT: el generador reescribió 708 archivos afectados y conservó el resto. No se eliminó cobertura para reducir la recompilación. Los archivos derivados del juego permanecen locales.

## Límites

Es una corrección de semántica, no una mejora de FPS medida. La comprobación sintética completa no prueba la campaña entera, todas las instrucciones SH-2 ni el backend GPU. La referencia y el código nativo pueden compartir defectos: se mantiene la comparación con documentación y expectativas independientes.

Validación final: build nativo completo aprobado y68 pruebas en103,707s. Incluye comprobaciones reales de arranque600 frames y recorrido inicial4.200 frames con cero instrucciones guest interpretadas. La v0.1.5 publicada no se modifica.
