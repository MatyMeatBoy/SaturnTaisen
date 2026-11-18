# Continuación del primer combate desde el relevo T02

La ruta parte de `local/work/t02/fin-multiple-turns.state` (SHA-256 `4d67dd1adc217d0a617baf1396b14ef29724663b68ee41f50552d88bef8d17b0`), con el disco 1 inglés y el ejecutable aislado `local/build/sakura/sakura-episode2.exe` de 643.320 bloques. Cada segmento usa una copia de SRAM y pulsaciones de ocho fotogramas. No se editaron los estados ni los datos del juego.

## Hitos observados

| Tramo | Resultado |
| --- | --- |
| `kill-six` | Sumire se acerca y acierta un ataque normal al soldado #6. El enemigo sigue presente. |
| `sakura-special` | Tras la fase enemiga, Sakura usa su especial contra #6. Se muestran 95 puntos de daño en el fotograma 1.200 y el soldado ya no figura en la escena del fotograma 1.600. |
| `maria-hit-eight` | María se recoloca en diagonal y ejecuta un ataque normal contra un soldado cuyo retrato muestra `8 #`. El soldado deja de verse en esa cámara antes del fotograma 750. |
| `inspect-map` | El minimapa muestra cinco marcadores magenta al oeste de las unidades aliadas. En esa captura sus identidades no están determinadas. |
| `next-west-round` | Tras mover a Sumire y a Ogami hacia el oeste, la fase enemiga muestra dos soldados adicionales junto a las ruinas. Al terminar esa fase empieza un diálogo entre Sakura y Ogami. |
| `west-dialogue` | Se abre una elección LIPS de tres respuestas durante el combate. El replay acepta la primera opción y termina con el menú de órdenes de Sakura abierto. |

En ese primer relevo quedan enemigos activos. Las etiquetas numéricas cambian durante la batalla, por lo que los sondeos de una misma posición y las animaciones de derrota son mejores referencias para seguir a cada enemigo.

## Relevo y reproducción

El material propietario queda en `local/work/chapter1-victory-followup`. El punto de partida para el próximo tramo es `west-dialogue/finish.state`, guardado antes de su fotograma 1.439, SHA-256 `c527fab10409aa06672d93c48d355840fc7de23a696f73c42f95c3e5ced08d2b`. Usar una copia de `west-dialogue/backup.bin`. Las capturas `maria-hit-eight/frame-000750.png`, `inspect-map/frame-000600.png`, `next-west-round/frame-000840.png` y `west-dialogue/frame-000540.png` documentan el progreso.

Los segmentos aceptados tienen traza estricta con cero bloques interpretados. `continuous/manifest.json` enumera su orden, hashes y desplazamientos de entrada. `continuous/input.movie` compone los 28 segmentos para una reproducción desde el relevo con una sola carga. El candidato tiene 24.993 fotogramas y SHA-256 `459c3477b0c42c7c5bde109aab18a4270f937940d89fdfd2447ceb7c4c2a6750`.

La reproducción continua terminó con salida 0 y cero bloques interpretados. Los 24.993 hashes coinciden fotograma a fotograma con el juego por segmentos. El hash guest final es `a8c36f754515e904` y el RGB de la captura final coincide. La comparación se hizo contra la ejecución segmentada en AOT estricto.

## Ronda adicional con test.2

La segunda ruta carga `west-dialogue/finish.state` con una copia de su SRAM y el ejecutable aislado `local/build/polish-test2-final/sakura.exe`, SHA-256 `a12b26d1990cabf9c54da562e4f05a9c842c7078d1b5c8ae3fe935a426c91418`. Sakura y Ogami avanzan y Sumire se coloca junto al soldado cuyo retrato muestra `7 #`. En `t2-seven-special-hit/frame-000600.png`, su especial le inflige 64 puntos de daño. El soldado sigue en el mapa. El cursor identifica al otro soldado occidental en `t2-maria-flank/frame-000150.png`. Tras terminar las órdenes de María, ambos soldados se acercan a su unidad. En `t2-next-enemy/frame-001600.png`, vuelve el turno de Sakura y se abre su menú de órdenes.

El relevo de test.2 es `t2-next-enemy/finish.state`, SHA-256 `3089f5020b5b45ad7d40f2fd4b54faa629e0b06a0f922e2dfcf9765fa157fd1a`, junto a una copia de `t2-next-enemy/backup.bin`, SHA-256 `4aa58364c1eaa4d0cee384894861caa4cde1e426aa2e43da7aa6b4e94379bc5b`. Los intentos posteriores de ataque de Sakura quedaron como ramas exploratorias y no forman parte del relevo.

`t2-continuous/manifest.json` registra los 17 segmentos aceptados. El `input.movie` compuesto tiene SHA-256 `b740a60d4782c68a795e53c1d61da19dd084735c24f2a3784aa6b22ffe1a242b`. Los 12.454 hashes de la reproducción continua coinciden con la cadena segmentada, con cero bloques interpretados. El hash guest final es `4bb4b0576a5b297a` y el RGB final también coincide. Para la comparación RGB se repitió el último segmento con captura en su fotograma 1.700. Su SRAM y todos sus hashes de fotograma coincidieron. El archivo de estado de esta repetición difiere en cuatro bytes del estado de relevo fechado por su hash arriba.

## Fin del combate y cobertura postcombate

Sumire remata al soldado alcanzado por su especial. María elimina al otro soldado occidental y Sakura al primer soldado del puente, ambos tras dos ataques normales. Ogami alcanza al soldado del santuario y finalmente lo elimina. Tras su explosión se abre el diálogo de Satan. El retrato del soldado del santuario muestra `8 #` en `t4-sakura-bridge/frame-000650.png`, `7 #` en `t6-ogami-aim/frame-001050.png` y `6 #` después de acercarse al jefe en `t7-ogami-aim/frame-000500.png`.

El estado `t6-ogami-hit-plateau/finish.state` se guarda después del primer ataque al soldado del santuario, SHA-256 `fcf8823074ed494ff7844a691a94529fba91d20bcc8a89db21005a9a186e8d0f`. `t6-continuous/manifest.json` registra 38.757 hashes iguales a los de los segmentos desde el relevo `t2-next-enemy`. El hash guest final es `0195ee86c16a4f32`, el RGB final coincide y hubo cero bloques interpretados.

Los cuatro aliados atacan a Satan en rondas sucesivas. Al final de la primera ronda en que atacan los cuatro se observa una recuperación de 80 puntos del jefe. En la siguiente, el último ataque de María vacía su barra y lo retira del tablero. `t10-maria-hit-boss/frame-001100.png` muestra el daño final, `frame-001320.png` su ausencia y `frame-002200.png` su despedida. Ogami confirma que el grupo protegió la capital en `t10-after-boss/frame-000600.png`. Se observó la resolución del combate y el comienzo de la despedida del equipo. La secuencia aún no había llegado al menú de guardado en test.2.

`t10-continuous/manifest.json` registra la reproducción desde `t6-ogami-hit-plateau` hasta `t10-after-boss`. Los 55.038 hashes coinciden con los de la ruta segmentada, con cero bloques interpretados. El RGB final coincide y el último hash guest es `3d464a2e532559dc`.

La ruta `t10-curtain` reproduce el bloqueo al comienzo de la pose final. Carga `t10-after-boss/finish.state` SHA-256 `e43d120faf07392b36932ad42ca73df298a56d217e990c18b9d665a09dfd1c7a` y una copia de su SRAM con la misma huella que el relevo anterior. Su película de entrada tiene SHA-256 `518aab4a47f686646764515acb44e87ec6b46854aa371f59d91dc651786d8cd0`. Test.2 completa 495 hashes hasta `84d329001596f4de` y termina con salida 4 al alcanzar el bloque no recompilado `06002042` en el SH-2 principal. `t10-curtain-boundary/finish.state` se guarda justo antes del cuadro del fallo y tiene SHA-256 `b71e1c0c53ea4843c684e2c988b0f33b13467f8902787342d5835053cc90f364`.

En el estado anterior al fallo, High WRAM contiene un fragmento de `/SAKURA` en `06002000`. La rutina `06005C58` de ese programa copia 119 palabras desde `060535D8` al destino. Son 238 bytes desde el desplazamiento `0x4F5D8` del archivo, SHA-256 `2be6e6b0c337ca1e36dc67c4649ca04b67c3fa6ba72a6c6f1f0411672bbc182e`.

La traza al llegar a `06002042` demuestra otra copia entre el guardado y la ejecución. La rutina `06032B00` copia 103 palabras desde `0604BB14` al mismo destino. La llamada en `06032AC2` entra en `06002020` y la instrucción en `06002028` salta a `06002042`. Los 206 bytes ejecutados en `[06002000,060020CE)` coinciden con el archivo `/SAKURA2/0SLG.BIN` del disco 1 desde el desplazamiento `0x47B14`. SHA-256 del fragmento `c8f547b446ef793c22fad73f63a8d7c4632abce683cda4d794ab120fd87bee6e`. Los mismos bytes están en `/SAKURA2/SLG.BIN` en ese desplazamiento. La primera compilación que registraba solo el fragmento de `/SAKURA` reprodujo el mismo error porque la comparación de código descartó esa variante en el momento del salto. La RAM y la traza exactas de llegada permanecen en `local/work/postbattle-miss-diagnostic`.

La referencia con `--cpu free` y `SATRECOMP_NO_BLOCKS=1` desde el estado anterior al fallo completa 1.200 cuadros. Su película de entrada traslada los eventos restantes al fotograma 0 del relevo y tiene SHA-256 `abd1094cd2320aa5767c138f73c9cf27f390b4e36f31c701d208220b36ef0e3d`. El registro confirma que el SH-2 principal ejecuta `06002042` y continúa por la rutina copiada. En `t10-curtain-free-reference/frame-000360.png` aparece el menú de intermedio, `frame-000720.png` confirma la selección de guardado y `frame-001200.png` muestra `Save Complete!`. El último hash guest es `c99aea4e279c6dbb` y el SHA-256 de la copia de SRAM resultante es `6d96f3daa07711500e1b8d2d7cbe1e69ac8bc285e83124271597347a9e4e03df`. Esta ruta acredita el guardado en la referencia interpretada. La cobertura en AOT se verifica con el candidato posterior.

La comparación estática encuentra los 238 bytes de `/SAKURA` en los discos 1 inglés, español y japonés en `0x4F5D8`, y en los discos 2 inglés y japonés en `0x4F5E8`. Los cinco programas tienen la rutina de copia de 119 palabras al destino `06002000`. Los mismos 206 bytes de `/SAKURA2/0SLG.BIN` y `/SAKURA2/SLG.BIN` aparecen en `0x47B14` en las cinco imágenes. El recorrido interactivo anterior se probó con el disco 1 inglés.

Una continuación interpretada desde el guardado selecciona `Resume` en `t10-resume-free-reference/frame-000840.png` y muestra el epílogo de hanami en `frame-001800.png`. Completa 1.800 hashes y conserva la huella de la SRAM guardada. La película tiene SHA-256 `0e900c1c0a2add2dbe819be90f624d98fa9cc694d3a50b367cd7b66c012c698c` y su hash guest final es `3cbd8ffb97c0500b`.

## Corrección AOT comprobada

`tools/discover_registered_overlays.py` registra `MAIN_RELOCATED` y `SLG_RELOCATED`. Cada registro valida el tamaño y SHA256 del archivo completo antes de extraer el fragmento copiado. El analizador solo admite PCs y bytes dentro de ese fragmento; conserva variantes distintas en una misma dirección. Una prueba sintética cubre límites, alineación, alteración fuera del fragmento y procedencia. Los datos derivados siguen en `local/`.

Desde la base de674.023bloques, ambos registros producen674.182:159candidatos adicionales. La reproducción directa coincide byte a byte con la expansión en dos pasos; SHA256 de la base final `eeb6cf3a498d2ca5434b036f5dc5aca3d3379b19406230ce2df7c3a484c668ae`. Esto acredita generación reproducible; la ejecución se prueba por separado.

Reproducción local, con un destino que todavía no exista:

```powershell
python tools/discover_registered_overlays.py --image "D:/01Claude/Sakurawars/local/prepared/disc1/Track 01.iso" --module MAIN_RELOCATED --module SLG_RELOCATED --seed-blocks local/work/episode4-aot/blocks.txt --sdk-root D:/01Claude/Sakurawars/local/deps/satrecomp --output local/work/postbattle-aot-reproduction
```

El candidato aislado `local/build/postbattle-slg-candidate/sakura.exe`, SHA256 `e7dd1c007e0b7610485f4fe98dd0bb2de4f47411e0cbc3cec835e8758fd120ec`, conserva el host de patch0048. Los objetos anteriores se verificaron por hash durante el enlace incremental y no se sustituyó el ejecutable del propietario. La primera variante por sí sola, candidato674.110, se conserva como reproducción fallida; el diagnóstico se compiló fuera del SDK y no forma parte del candidato aprobado.

El candidato674.182 pasó los1.200fotogramas desde la frontera hasta `Save Complete!`, y después1.800desde su propio estado guardado hasta hanami. Los3.000hashes coincidieron con las referencias interpretadas. Coincidieron diez pares RGB en guardado y cinco en Resume, y la SRAM resultante fue idéntica a la referencia en ambas fases. Todas las ejecuciones del candidato registraron cero interpretados. Evidencia privada: `local/work/postbattle-fixed-validation/result.json` y sus subcarpetas `save`/`resume`.

## Reproducción continua tras LIPS

Con el candidato de 674.182 bloques se cargó `west-dialogue/finish.state` una vez y se reprodujo la película compuesta sin cargar estados intermedios. La ruta completa el combate, guarda en el intermedio y selecciona `Resume` hasta el epílogo de hanami. Los 109.740 hashes guest coincidieron con la referencia segmentada y se registraron cero bloques interpretados. El último hash guest fue `3cbd8ffb97c0500b`. El RGB final y la SRAM resultante coincidieron con la referencia.

La película tiene SHA-256 `3e7db4e78a2c498d892864fa850bc363bc5faa769bbfe8c525ab842249732693` y la SRAM resultante tiene SHA-256 `6d96f3daa07711500e1b8d2d7cbe1e69ac8bc285e83124271597347a9e4e03df`. El registro de verificación se conserva en `local/work/chapter1-victory-followup/t10-save-resume-native-full/verification.json`.

Quedan por unir los relevos anteriores y probar New Game hasta el final del capítulo. El ZIP test.2 ya entregado precede a este candidato.

## Continue desde un arranque en frío

Se reinició el candidato de 674.182 bloques con una copia de la SRAM que produjo el guardado del combate. `tests/cold-load.movie` abre Continue, selecciona la ranura 1 y confirma la carga. La pantalla del epílogo de hanami aparece en el fotograma 7.000. La reproducción de 9.500 fotogramas arranca sin cargar estados del emulador. Coinciden todos los hashes guest y 19 capturas RGB entre AOT estricto y la referencia interpretada del mismo ejecutable. La copia de SRAM conserva su SHA-256 inicial y el candidato registra cero bloques interpretados. El último hash guest es `d74aa82a82d17894`.

El informe privado está en `local/work/chapter1-victory-followup/t10-cold-continue/comparison.json`. Quedan pendientes dos repeticiones del recorrido completo desde New Game, con guardado, reinicio y Continue.

## Del pasillo al guardado nocturno

Desde `stairs-scan.state` se avanza por la elección LIPS del pasillo, el regreso al despacho de Yoneda y el diálogo de Sakura antes del intermedio. Se guardó la partida en la ranura 1 con entradas normales y se observó `Save Complete!`. El tramo usa una copia propia de SRAM y el candidato de 674.182 bloques.

Una sola carga inicial reproduce los 29.597 hashes de los cuatro segmentos. Para los mismos 29.597 cuadros, la referencia interpretada coincide en hashes, RGB final y SRAM guardada. El candidato AOT registró cero bloques interpretados. El último hash guest es `f5282806f43e9908`. La película tiene SHA-256 `34df861ba09b6ba1899d4708ce44e3cb31abe4acd7ee5404f247683bc0288596` y la SRAM guardada tiene SHA-256 `2e96cc84378141ecc42d37c1ba1d71976974f6984ce85c791b68d9b95390801c`. La evidencia privada está en `local/work/chapter1-victory-followup/corridor-bridge/verification.json`.

El ancla del pasillo corresponde al fotograma 119.780 de la repetición anterior desde New Game, según la comparación histórica de estados salvo el puntero de RAM de sonido que restaura el lector. Queda por probar el empalme desde New Game.

## Del guardado nocturno al tutorial de combate

Desde el guardado nocturno, el comando `Resume` devuelve el control al teatro. La ronda pasa por la biblioteca, la planta baja y el vestidor. Tras devolver a Jean-Paul a Iris, Ogami termina la ronda. La salida de la mañana lleva a un segundo intermedio y a un guardado en la ranura 1 antes del combate. Al reanudar, la ruta llega a la selección de objetivo tras las instrucciones de María.

Con una sola carga inicial del estado del guardado nocturno, el candidato de 674.182 bloques reproduce los 147.730 hashes guest de los 21 segmentos. El RGB final y la SRAM guardada coinciden, con cero bloques interpretados. El último hash guest es `f26cfda21efe6e60`. La película tiene SHA-256 `0e8cd95c6802a3ad702794cf25299366fd468a82cb5b8088da73ea8640aa5fef` y la SRAM resultante, `5c71f7178690356219a0c800e1206412ad059de11dd9981873472c15e83868d0`. En el tramo de entrada al combate también coinciden 5.400 hashes, nueve capturas RGB y la SRAM entre AOT estricto y la referencia interpretada.

La evidencia privada está en `local/work/chapter1-victory-followup/corridor-bridge/continuous-night-to-tutorial/verification.json`. El relevo del nuevo tutorial llega a una interfaz similar a la del estado histórico, con diferencias de RGB y RAM guest. Quedan por enlazar la nueva ruta con los turnos de combate ya comprobados y por probar dos recorridos completos desde New Game con guardado, reinicio y Continue.
