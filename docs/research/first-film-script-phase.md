# Identificación de la transición de la primera película

La reproducción parte de `title-final.state` con `tests/chapter1-title-new-game.movie`, disco 1 inglés y `sakura-test1.exe` de 614.024 bloques. La repetición continua en AOT estricto produjo los mismos 6.201 hashes de fotograma que la ruta con ventana, con cero bloques interpretados. Los sondeos, los estados y los registros permanecen en `local/work/intro-petals-audit/t33-analysis`. El registro del candidato con cada cambio de cursor está en `local/work/first-film-phase-boundary/enhanced/run.log`.

## Identidad del script y fases observadas

| Archivo | Dirección en Low WRAM | Tamaño | SHA-256 |
| --- | --- | ---: | --- |
| `0100.BIN` | `00204000` | 15.404 bytes | `fd6e18df40fe670341c178588c2f27e10e3599827d31622d66ec8625d952d1e3` |
| `0100TBL.BIN` | `00224000` | 54.018 bytes | `1924569ae54147c461a2bef077ff2ef7bf9c8e668a649e49b609b7421538c7c4` |

Las regiones cargadas coincidieron byte por byte con los archivos del disco en las muestras. `0100.BIN` contiene bytecode y sus cursores son direcciones dentro de la región. Su FNV-1a de 64 bits es `5DA24532C9356735`. El cursor es la palabra BE32 en High WRAM `060685B4`. La palabra BE32 adyacente `060685B8` valía 0 en las muestras 804 y 5992 y 1 en 812, 820 y 5956. El significado de la segunda palabra queda sin atribuir.

| Primer fotograma del cursor en la traza continua | Cursor | Evidencia |
| ---: | --- | --- |
| 705 | `00204006` | Entrada a la transición. El cursor anterior `00204000` se observó en 650, 703 y 704. |
| 806 | `00204462` | Cursor durante un solo callback consecutivo entre `4006` y `4ED8`. |
| 807 | `00204ED8` | El sondeo 807 muestra ornamentación sin imagen. Los estados 812 y 820 corroboran ese cursor y el distintivo en fundido. |
| 824 | `00204EDE` | Aparece en los intervalos previos a la imagen, durante el vídeo y durante la salida. Sigue presente en el estado 5956. |
| 5968 | `00204EE4` | Palabra inmediatamente anterior a `00204EE6`. |
| 5987 | `00204EE6` | Persiste al desaparecer el pie y durante el rótulo de episodio posterior. |

La traza establece el orden de los estados visibles por el host. Queda pendiente identificar la instrucción SH-2 que escribe el cursor y la semántica de cada opcode. El PC muestreado alterna entre rutinas de espera y del decodificador. La cabecera FILM sigue residente en `06080000` cuando vuelve el fondo floral y tampoco delimita por sí sola la reproducción.

## Límites de la supresión del pie

El pie observado es un sprite normal VDP1 sin giro ni inversión, modo `00A0`, color `C500`, origen (8, 152), tamaño 304 × 64 y huella de textura `924C9C726F152DB2`. El distintivo usa modo `00A0`, origen (16, 160), tamaño 40 × 48 y huella `7CA30C1792ED4682`. Su color cambia de `C400` a `4400` durante el fundido. Las muestras del tramo previo y posterior carecen de glifos de diálogo. También hay muestras después del vídeo con la sombra residual de VDP2 y cero sprites dibujables.

La intersección de módulo exacto, cursor conocido, ausencia de capas de imagen y lista cerrada de sprites delimita la supresión. En la muestra 807, la capa 0 ocupa 1.214 píxeles, la capa 3 ocupa 16.922 y la capa 5 ocupa 53.544. Durante el vídeo, la capa 1 ocupa la región de 288 × 144. Al llegar al rótulo de episodio, `00204EE6` sigue presente y la capa 4 ocupa los 71.680 píxeles nativos. Estos casos requieren el veto por capa de imagen incluso con un cursor admitido.

De 160 estados archivados, 29 coincidieron con el módulo completo. Se encontró un único estado fuera de los muestreos de introducción con uno de los cursores iniciales comprobados. `cold-load-discovery.state` muestra esta misma película, con 41.472 píxeles de capa 1. Los controles de teatro, diálogo posterior y conversación con María usan `0020582C`, `00205990` y `00205FA8`, respectivamente. El muestreo cubre esta ruta inglesa y sus controles locales. En el host, la identidad del script y el cursor deben capturarse con el mismo fotograma presentado para conservar esa relación con runahead.
