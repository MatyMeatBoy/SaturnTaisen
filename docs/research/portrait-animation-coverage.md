# Cobertura de retratos HD y animaciones

La auditoría compara los atlas de Saturn y PC con el paquete HD preparado. También puede reconstruir el retrato descrito por los comandos VDP1 de estados locales y compararlo con capturas nativas de 320 × 224. Lee los insumos en el lugar y escribe los informes en un directorio nuevo bajo `local/work`.

```powershell
python tools/audit_portrait_coverage.py --states local/work/sakura
python -m unittest discover -s tests -p test_portrait_coverage.py
```

Usar `--output` con otro directorio para repetir la ejecución. Se pueden indicar otros insumos con `--project`, `--pack` y `--disc` repetido por disco. `portrait-coverage.csv` sirve para filtrar las identidades por capítulo, estado o región. `portrait-coverage.json` añade los FCE de origen, las puntuaciones, las medidas alfa y las comparaciones con estados y capturas.

## Cobertura del catálogo

El auditor comparó los 304 atlas Saturn de 40 × 80 del proyecto con los FCE de ambos discos y verificó por SHA-256 los 394 atlas PC de 80 × 160, con índices continuos del 0 al 393. Verificó también el archivo KAO original. En el paquete, validó el catálogo binario y los hashes FNV de las 382 variantes PNG. Al comparar sus píxeles RGBA con los regenerados a densidad 1× y 2×, las 382 variantes coincidieron. Ninguna tiene un píxel con alfa parcial o cero donde Saturn requiere opacidad.

El capítulo 1 abarca la unión de identidades encontradas en los seis FCE `0100`, `0101`, `0102`, `0103`, `0108` y `0109` en ambos discos.

| Ámbito | Saturn | Base HD | Ojos HD | Boca HD | Ambas tiras HD disponibles | PNG verificados | Pendientes |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Catálogo | 304 | 191 | 191 | 191 | 191 | 382 | 113 |
| Capítulo 1 | 123 | 81 | 81 | 81 | 81 | 162 | 42 |

Cada atlas válido tiene 48 filas de base y dos tiras de 16 filas. La columna de ambas tiras confirma su disponibilidad en los PNG. Su dibujo simultáneo depende de los comandos del juego y del fotograma mostrado. El campo `nearest_strip_rows` mide la distancia entre índices de color por fila de colocación y sirve como hipótesis sobre el destino de cada tira.

Los 191 emparejamientos automáticos respetan `índice PC = ID Saturn - 1`. Entre los pendientes, el candidato visual primero del ranking respeta esa regla en 102 de 113 filas, incluidas 38 de las 42 del capítulo 1. En el primer capítulo, los cuatro pendientes con un candidato distinto son `004f`, `00ef`, `013b` y `013c`. Ningún pendiente obtuvo distancia cero. El índice aporta una señal adicional para revisar cada retrato con sus tres regiones.

Rangos pendientes del capítulo 1 en hexadecimal

```text
0013-0014 001d 0040-0041 0044-0045 0049-004a 004f 005b 0064
006b 006d-006e 007f 0088 0091-0096 0098 009b-009c 009e 00a1
00c0 00c2-00c3 00c5 00ee-00f0 00f2 00f4 013a-013c 013f 0169
```

## Estados guardados y retrato de Yoneda

En los 160 estados disponibles, 79 tenían un comando de retrato en la posición esperada y usaban la paleta esperada. Se obtuvieron 63 coincidencias únicas con el catálogo HD y 16 sin coincidencia. Los 16 casos sin coincidencia tenían una identidad Saturn exacta entre las pendientes. Se capturaron seis estados con una tira activa y ninguno con dos. Los estados `maria-face-discovery.state` y `maria-exit.state` muestran, respectivamente, ojos y boca de `0176` en la misma fila relativa 16 en momentos distintos.

Las expresiones civiles de Yoneda `00e2–00e7` tienen ambos PNG HD completos. Las dos tiras de cada atlas Saturn tienen su mínimo de distancia en la fila relativa 8. El comando de ojos de `00e2` confirma esa fila en `office-return-6000.state`.

| Muestra | Comando guardado | Comparación con la captura |
| --- | --- | --- |
| `office-return-3000.state` | Base `00e3` | Los 1.920 píxeles coinciden con los colores de la paleta Saturn. |
| `office-return-6000.state` | Base `00e2` y ojos en fila 8, una coincidencia HD | Difieren 1.901 píxeles de la base sin mezcla y 1.904 de la composición de los comandos guardados. Los 1.920 píxeles coinciden al mezclar la base sin la tira de ojos hacia blanco. |

La muestra de 6000 cumple exactamente `(canal_base * 27 + 248 * 5) >> 5` por canal, con blanco de RGB555 expandido a 248. El estado describe los comandos pendientes de VDP1. La captura muestra el retrato base bajo mezcla, coherente con un desfase entre los comandos guardados y la imagen presentada. El guardián `PortraitPixelsVisible` exige igualdad con el color Saturn sin mezcla y por ello rechazaría ese retrato. El atlas, la paleta y el reconocedor por bytes sí pasaron las comprobaciones de los comandos guardados.

El informe incluye 42 pares de captura y estado. En 36 pares, la base coincide con la captura sin mezcla. Tres muestran mezcla exacta hacia blanco con pesos 5, 15 y 25 sobre 32. Los tres restantes requieren más evidencia para explicar sus diferencias. La auditoría valida estos fotogramas guardados y la disponibilidad de los atlas. La frecuencia de las caídas en una ejecución continua queda fuera de esta muestra.
