# Tercer lote de retratos HD del capítulo 1

La revisión comparó la base y ambas tiras por identidad y vestuario. Sakura `001d` lleva bufanda, María `0064` lleva cuello oscuro y `006d/006e` comparten el cuello claro con expresiones distintas. Iris `0096` conserva los ojos abiertos, la boca redonda y el mismo vestuario que su atlas Saturn.

| ID Saturn | Candidato PC | Evidencia |
| --- | ---: | --- |
| `001d` | 28 | Base y ambas tiras verificadas en atlas |
| `0064` | 99 | Base y ambas tiras verificadas en atlas. Base observada antes del primer combate |
| `006d` | 108 | Base y ambas tiras verificadas en atlas |
| `006e` | 109 | Base y ambas tiras verificadas en atlas |
| `0096` | 149 | Base y ambas tiras verificadas en atlas |

Las tres regiones de cada atlas obtuvieron su mejor alineación con desplazamiento cero frente a desplazamientos de un píxel nativo. La concordancia de las tiras disminuyó al intercambiarlas. Ambas densidades conservaron la máscara Saturn completa, con 3.200 píxeles opacos a 1× y 12.800 a 2×, sin huecos. Las diferencias de color de Iris se conservan como parte del arte PC. `0093`, `0095`, `00a1`, `00c2` y `0169` quedan fuera de este lote.

El [registro de revisiones](../../config/hd-portrait-reviewed.json) fija el KAO y los hashes de los atlas nativos, los píxeles PC y ambas variantes preparadas. La reproducción desde el proyecto inicial de 191 retratos aplica los diez emparejamientos aprobados y exporta un proyecto nuevo. La reproducción obtuvo los mismos 404 archivos del candidato, con un manifiesto SHA-256 `b3ee89d7bea42ed2d50df70389059c9f8d4c2adba5a94dedf8d0d4c718ea0a25`.

```powershell
python tools/apply_reviewed_hd_portraits.py --output-project local/work/chapter1-hd-201/project.json --export
```

El checkpoint alcanza 201/304 identidades globales y 91/123 del capítulo 1. La auditoría verificó 402 variantes, con cero errores, y deja 103 pendientes en el catálogo, 32 en el capítulo 1. Los 19 fondos del checkpoint de 196 coinciden byte por byte con los preparados junto a los 201 retratos. El recibo del paquete privado tiene SHA-256 `e1fb09fed81cfd4450ee2b3f4058178f48086a7fb2f5904b1da1e64b70b5be7b`.

La build v0.2.0-test.1 mostró la base de María `0064` a 2560×1440 y densidad 2. Al comparar los paquetes de 196 y 201 coincidieron los 180 hashes del juego y tres capturas RGB nativas. La diferencia de la GUI en el fotograma 8 quedó dentro del retrato `[404,644) × [996,1284)`. Ambas ejecuciones registraron cero bloques interpretados. Las tiras de María y los otros cuatro retratos esperan verificación en juego.
