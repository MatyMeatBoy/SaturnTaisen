# Avance manual de diálogo con voz

Se comprobó la primera intervención hablada de Sumire tras entrar en el comedor del capítulo 1, con disco 1 inglés de Saturn y el ejecutable aislado de 643.320 bloques. La voz se identifica en la actividad real del juego. Los comandos PLAY con FAD `02AA3B` y `02AA53` leen los LBA 174.501 y 174.525 dentro de `/SAKURA1/VCEADV`. Se capturó el PCM estéreo de 44.100 Hz de la misma ejecución.

## Prueba de A, B y C

Desde `local/work/sakura/theater.state`, la pulsación A de ocho fotogramas en 100 entra en la escena. El estado privado `first-sumire/f0899.state` conserva la intervención anterior, ya escrita. Todas las comparaciones parten de ese estado con copia de SRAM y pulsan A en el fotograma relativo 20 durante ocho fotogramas para entrar en la línea hablada. Después se prueba por separado A, B o C, con pulsaciones de cuatro fotogramas en 120 y de ocho fotogramas en 155 y 300. Se suelta el botón entre pulsaciones.

| Botón probado | Texto incompleto en 120 | Texto completo en 155 | Pulsación tardía en 300 |
| --- | --- | --- | --- |
| A | Completa el texto, visible entero en 140. | Permanece la intervención de Sumire. | Avanza al interlocutor siguiente, visible en 360. |
| C | Mismo resultado visual y PCM que A. | Permanece la intervención de Sumire. | Avanza al interlocutor siguiente. |
| B | Completa el texto y altera el flujo de voz. | Avanza antes que A/C. La caja cambia entre las capturas 160 y 180. | Para entonces ya está en la siguiente intervención. |

El control sin pulsaciones tras iniciar la línea aún muestra escritura parcial en 180. El PCM de B empieza a diferir del de A y C hacia el fotograma 123, justo después de la primera pulsación B. La ejecución de B omite el segundo PLAY de la región de `VCEADV`. En A/C, el primer tramo tiene aún ocho sectores en buffer en el estado 119 y cuatro en 139. En 159 la unidad ya está en pausa, con cero sectores en buffer, aunque la CPU continúa copiando muestras a la RAM de sonido. El estado del lector de CD no mide por sí solo si sigue sonando una voz.

Cada película se repitió con AOT estricto y el intérprete SH-2 del mismo binario, con funciones recompiladas deshabilitadas en ambos modos para la comparación. Coinciden los 460 hashes por película, todas las capturas y todo el PCM. En AOT hay cero bloques interpretados. Esta equivalencia comprueba el modo de CPU para este caso. Falta compararlo con Saturn físico u otra implementación independiente.

## Entrada recibida por el juego

Los estados guardados antes del fotograma 159 contienen el reporte digital SMPC del puerto 1 activo bajo, con `FBFF` en A, `FEFF` en B y `FDFF` en C. Los valores coinciden entre AOT e intérprete. La falta de avance temprano con A/C ocurre aunque el juego recibe la entrada.

En esa muestra A/C tienen PC `0600AEEC`, PR `0600AE1C` y R7 `25A7D470`. El código escribe palabras de muestras hacia el espejo de la RAM de sonido. En B, la CPU está en `060041BA` con PR `060041BE`. Estas muestras acreditan rutas de ejecución distintas. La instrucción que decide permitir el avance sigue sin aislarse.

Se verificó que el menú nativo permite cambiar `Voice` de On a Off, con capturas del selector en ambos estados. Desde ese otro contexto, la muestra posterior de diálogo no hizo nuevas lecturas de `VCEADV`, por lo que no se usó para comparar On/Off en la intervención de Sumire.

Los movies, estados, PNG, hashes, trazas CD y volcados PCM permanecen en `local/work/dialogue-voice-advance`. La prueba documenta avance manual en una línea hablada. Su alcance excluye la función de salto automático y otros tipos de escena.
