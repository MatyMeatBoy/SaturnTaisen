# Barrido AOT de partidas de episodios posteriores

Se usó el ejecutable aislado `local/build/sakura/sakura-episode2.exe` de 643.320 bloques. Su SHA-256 es `a5fabd38b0b2fd80d877482903d9d5537c2c7920f9ad36042d4ca1075fcb0e2e`. Cada prueba comienza con SRAM copiada, arranque del disco inglés indicado y Continue mediante pulsaciones. Para identificar el episodio y el disco de la partida se revisó el menú del juego. El banco y sus fuentes se describen en [Puntos de validación posteriores al episodio 1](later-chapter-validation.md).

Los archivos de ejecución están bajo `local/work/later-chapter-audit/chapter-sweep`. Cada carpeta contiene la entrada derivada de `tests/cold-load.movie`, parámetros de ejecución, captura de selección de casilla, hashes y registro del runtime. `seeds.json` identifica el hash de cada copia de SRAM y el miembro del banco cuando corresponde. `provenance.json` conserva los hashes de los dos discos, el banco y el ejecutable.

## Puntos verificados

| Selección observada | Tramo strict AOT | Evidencia posterior a Continue |
| --- | --- | --- |
| Episodio 3, File 1, CD‑1 | 12.000 fotogramas, cero bloques interpretados | Diálogo de apertura y rótulo del episodio 3 al final. Carpeta `bank-3-battle-1-strict`. |
| Episodio 4, File 1, CD‑1 | 6.678 fotogramas completos. Sale con código 4 al entrar en `00204000`. | Menú de carga confirmado. Carpeta `bank-4-battle-strict`. |
| Episodio 5, File 1, CD‑1 | 12.000 fotogramas, cero bloques interpretados | Diálogo de apertura posterior a Continue. Carpeta `bank-5-battle-strict`. |
| Episodio 6, File 1, CD‑1 | 12.000 fotogramas, cero bloques interpretados | Diálogo de apertura posterior a Continue. Carpeta `bank-6-battle-strict`. |
| Episodio 7, File 1, CD‑1 | 12.000 fotogramas, cero bloques interpretados | Rótulo del episodio en 10.500 y diálogo en 12.000. Carpeta `bank-7-battle-strict`. |
| Episodio 8, File 1, CD‑2 | 12.000 fotogramas, cero bloques interpretados | Narración de Año Nuevo y diálogo posterior. Carpeta `bank-8-battle-1-strict`. |
| Episodio 9, File 2, CD‑2 | 12.000 fotogramas, cero bloques interpretados | Diálogo posterior a la carga en las capturas de 7.500 y 12.000. Carpeta `public-9-strict`. |
| Finale, File 1, CD‑2 | 12.000 fotogramas, cero bloques interpretados | Diálogo inicial. El nombre del miembro del banco declara capítulo 10. Carpeta `bank-10-battle-1-strict`. |
| Finale, File 3, CD‑2 | 12.000 fotogramas, cero bloques interpretados | Otro diálogo de Finale. Carpeta `public-finale-strict`. |

Ocho rutas completaron 12.000 fotogramas cada una, 96.000 en total, con cero interpretados y cero instrucciones individuales. `final-state-matches.json` conserva los hashes y los archivos que coinciden en RAM. `observed-scene-resources.json` vincula las etiquetas `menu` y `dialogo` con el disco, el episodio mostrado en Continue, la captura observada y el estado de ejecución. La aptitud para Zoom sigue desconocida y el fallback indicado es nativo.

Los scripts narrativos de la tabla siguiente coinciden byte por byte desde `00204000` en los estados guardados. Para cada familia también coinciden la tabla de diálogo desde `00224000` y el atlas de retratos desde `00251000`. Los tres archivos están en `/SAKURA1` y su correspondencia se documenta por residencia en RAM.

| Episodio observado | Disco | Familia BIN / TBL / FCE |
| --- | --- | --- |
| 3 | CD‑1 | `0301` |
| 5 | CD‑1 | `0501` |
| 6 | CD‑1 | `0601` |
| 7 | CD‑1 | `0700` |
| 8 | CD‑2 | `0801` |
| 9 | CD‑2 | `0900` |
| Finale, File 1 | CD‑2 | `1001` |
| Finale, File 3 | CD‑2 | `1004` |

## Primer bloqueo del episodio 4

El intérprete del mismo binario completa 6.692 fotogramas. Sus primeros 6.678 hashes coinciden con AOT, incluido `3879c325e99c165a` en el último fotograma común. Los estados del intérprete de 6.677 a 6.680 contienen los **77.716 bytes** de `/SAKURA2/EVT06.BIN` en `00204000`. Este archivo de LBA 221800 en el disco 1 inglés tiene SHA-256 `3214506d26f1b9fbec18190e993acf4ef5502532522790d7a327efe7125c89e5`. La comparación de RAM es exacta en los cuatro estados.

`bank-4-battle-reference/state-6678.bin` conserva la frontera, SHA-256 `42ab8d52f4b844bd45ae80ca799b98a7732e84f8e0814164a4b89a1f718cba14`. Restaurar este estado en AOT estricto con una copia de SRAM y sin pulsaciones vuelve a producir la misma salida 4 en el primer fotograma. El comando está en `bank-4-strict-from-boundary/boundary-replay.json`. Las rutas y los registros coincidentes figuran en `checkpoint-state-matches.json`.

## Inventario EVT

`evt-pointer-metadata.json` reúne 27 archivos por contenido de los cuatro perfiles preparados. Cada candidato registra SHA-256, ubicaciones ISO y palabras alineadas de 32 bits que apuntarían dentro de su propio rango si se cargara en `00204000`. Esta señal ofrece candidatos de inspección. La base comprobada en RAM se distingue con `base_observed`.

La coincidencia de EVT06 en el estado de frontera añade una base observada a las de EVT01 y EVT02. El barrido inicial de punteros se guardó antes de la prueba de EVT06 y su informe de coincidencias conserva la evidencia posterior.

Una ruta de 12.000 fotogramas acredita el hito que aparece en la captura. Las etiquetas de las partidas nombran el destino propuesto por el banco y el juego puede empezar con el prólogo del episodio. Quedan por ejecutar los segmentos intermedios y finales de cada capítulo.

## Corrección posterior de EVT06

La entrada registrada de `discover_registered_overlays.py` añade EVT06 únicamente tras la atribución completa de sus bytes a 00204000. Desde la base de 643.320 candidatos, se añaden 30.703 y se obtiene **674.023**. La base y el binario aislados quedan privados; la semilla y el ejecutable compartidos no se sustituyen.

El binario anterior falla en la regresión desde el estado 6678 con código 4. El candidato pasa 1.200 fotogramas desde ese estado, con todos los hashes y el RGB final iguales al intérprete. También conserva la regresión del episodio 2. La ruta desde SRAM original y `tests/chapter4-load.movie` completa **12.000 fotogramas** con cero bloques interpretados, todos los hashes iguales al intérprete y RGB final idéntico. Los primeros 6.678 hashes coinciden además con la ejecución anterior al arreglo. El último hash es `c8f0bd57666eb8e9` y la captura muestra el campo táctico con las unidades.

El [informe del arreglo](episode4-aot-fix.json) conserva hashes y límites. El verificador privado tenía un error de formato en el nombre del PNG después de comparar los hashes; se corrigió y se verificó la imagen existente con su nombre real, sin alterar ni repetir los datos del juego. Ambos procesos del juego terminaron con código 0. Este resultado cierra el bloqueo observado de carga, no la victoria ni todo el capítulo. La versión test.1 publicada no se modifica.
