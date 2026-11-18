# Puntos de validación posteriores al episodio 1

El episodio 2 ya tiene una entrada reproducible por Continue. Con el binario aislado de 614.024 bloques, AOT estricto y el intérprete del mismo SDK coinciden hasta el fotograma 6.688. El primero se detiene al entrar en `EVT02.BIN` en `00204000`. En el disco 2 inglés se completó la prueba de arranque y Continue del episodio 8 hasta el fotograma 9.501, con cero bloques interpretados y cero instrucciones individuales.

## Episodio 2 en disco 1

La copia SRAM `local/work/later-chapter-audit/episode2-test-copy.bin` se leyó del miembro `Battle Saves/Chapter 2 Battle.bkr` de `Battle_Saves.zip`. Contiene el contenedor SRAM compacto de 32 KiB del banco y un registro `SAKURA___01` de 5.708 bytes. Se preservaron todos los bytes del miembro original.

| Artefacto | SHA-256 |
| --- | --- |
| SRAM del episodio 2 | `4c22bf1edd1437b082ccd05e12df5bbf46bdcc5c9058fa3cc869db281f043908` |
| `Battle_Saves.zip` | `cd4f151db9ab0e0cc793060f6201c5233d3cafa35a2ecc02266a648a2b955677` |
| Binario aislado `local/build/sakura/sakura-test1.exe` | `67ef0bdc41321bd19231f637070d6dd39fe6bd17df63527dffde61aa4a79cbb7` |
| ISO inglés disco 1 | `5b19031460c87b4773ef2cbd70ef2170bef41c1117ec8cefe27b2af1309205ec` |
| `tests/cold-load.movie` | `0a54353b4d3a3338010a1d0f033306a1c6e8855d22b978d1f8f69424541419b3` |

Beetle Saturn v1.32.1 mostró tres casillas del episodio 2, todas marcadas CD‑1, en el fotograma 2.000 de `beetle-ep2`. File 1 cargó el diálogo de apertura sobre el campo táctico, visible en el fotograma 3.900. La continuación con A mostró unidades en el mapa en `beetle-ep2-tactical`. Esta muestra llega a la introducción del combate.

La prueba nativa usa `tests/cold-load.movie`, una copia individual de SRAM y el disco 1. Los registros `ep2-strict-anchor/frames.hash` y `ep2-reference-anchor/frames.hash` coinciden en sus primeros 6.688 fotogramas. El último hash común es `3408341dbb7917d3`. AOT estricto sale con código 4 al intentar ejecutar el bloque maestro `00204000`. El intérprete prosigue hasta el límite de 6.701, con `9a24e290a77f5d9d` en el fotograma 6.689.

En las dos rutas, el estado guardado en 6.688 contiene los 76.180 bytes contiguos de `/SAKURA2/EVT02.BIN` en Low WRAM a partir de `00204000`. La coincidencia es completa y ya consta en los estados de 6.686 y 6.687. SHA-256 del archivo `701d68ab48e67eabce1e1eb89bd4a8b790aa0f6a40ff68bbfa0600489b97c660`, LBA 221648. El disco 1 japonés preparado contiene los mismos bytes en LBA 251972. La ruta exacta de este módulo está ausente en ambos discos 2 preparados.

La evidencia completa permanece bajo `local/work/later-chapter-audit`, incluidos los comandos exactos, `episode2-overlay-attribution.json` y `ep2-strict-anchor/state-6688.bin` (SHA-256 `61b8cbb898f59c116509640a496ce8fb25e8b4d9d85c46d9ccef2d3533c05333`). La reproducción usa pulsaciones y carga normal de SRAM.

Al restaurar el estado de referencia de 6.700 y avanzar un fotograma sin pulsaciones, el hash vuelve a coincidir con el de 6.701 del arranque en frío, `673663ba1db8f5f8`. La captura `ep2-reference-6701-screenshot/shot-000001.png` muestra una pantalla negra en esa muestra. El inventario `evt-family-inventory.json` registra 14 archivos EVT por perfil y 27 variantes por SHA-256. Las bases observadas se consignan únicamente para EVT01 y EVT02.

```powershell
python local/work/later-chapter-audit/replay_ep2_anchor.py strict local/work/later-chapter-audit/replay-strict
python local/work/later-chapter-audit/replay_ep2_anchor.py reference local/work/later-chapter-audit/replay-reference
```

Cada invocación crea un destino nuevo con logs, hashes y estados de la frontera. El código 4 reproduce el fallo del binario de referencia en modo estricto.

## Otros puntos de entrada

| Fuente | Capítulo declarado u observado | Ruta de prueba |
| --- | --- | --- |
| `Battle_Saves.zip` | Los 16 nombres declaran combates en capítulos 1 a 10. Los nombres son pistas de selección. Se observó el episodio 2 en el juego. | Comprobar la casilla y el disco indicados por Continue antes de fijar cada ruta. |
| `disc2Start.bkr` | Menú observado en Beetle. File 1, episodio 7 CD‑1. File 2, episodio 6 CD‑1. File 3, episodio 8 CD‑2. | File 3 cargó la introducción del episodio 8 en el disco 2 inglés. File 1 activó el aviso de cambio a CD‑1. |
| Importación pública de privateye | Menú observado. File 1, episodio 8 CD‑2. File 2, episodio 9 CD‑2. File 3, Finale CD‑2. | El episodio 8 cargó con AOT estricto durante 9.501 fotogramas en el binario de 614.024 bloques. SRAM SHA-256 `1b3457dc6b2f0f5d3aefd1e69873ca7126720be75253554551219d77acb8c5f2`. |
| Importación pública de Pimpeaux | Menú observado. File 1, episodio 8 CD‑2. File 2, episodio 7 CD‑1. File 3, Finale CD‑2. | La ruta histórica de File 3 cargó Finale con cero bloques interpretados según `public-save-fixtures.json`. El estado y el replay se conservan en `local/work/sakura`. |

El banco está en `local/research/noahsteam-repo/SakuraTaisen/Data/SaveData` del checkout `10aefa40c555c2b1135b5836434c2315135b5306`. `disc2Start.bkr` y `bkramDisc2Start.bin` tienen contenedores distintos con el mismo SHA-256 del registro de juego. La pista de datos inglesa del disco 2 tiene SHA-256 `fb813e8fe15caf03887321a5ceacb32d5d8822801fba460af726a59a6753770b`.

El inventario privado `inventory.json` registra el banco y la revisión de los candidatos de nombre y formato en `local/work` y `local/profiles`. De 639 archivos candidatos, 579 decodificaron un registro de Sakura, agrupados en diez hashes de contenedor. Las copias con el mismo hash se enumeran juntas. Los estados históricos de episodio 8 y Finale se verificaron por firma de estado v9 y por comparación de cada par nativo/intérprete. En esos pares, las únicas diferencias caen dentro del puntero de host documentado.

## Ensayo de seguimiento

1. Verificar hashes y copiar la SRAM a un perfil de prueba nuevo por ejecución. Usar el disco indicado por la casilla y Continue del juego. Conservar el `movie` y el estado inmediatamente anterior a cada hito.
2. Comparar AOT estricto e intérprete del mismo binario con el mismo `movie`. Registrar el primer bloque ausente, su PC y el contenido de Low/High WRAM en estados de ambos lados del fallo. Identificar el módulo en el disco por la coincidencia de bytes.
3. Tras ampliar una ruta, repetir desde la SRAM y el replay originales. Registrar el tramo nuevo hasta el siguiente hito y conservar la comparación de hashes.

Las rutas arrancan desde partidas avanzadas. La verificación cubre entrada al episodio 2, reproducibilidad del primer bloque que falta y carga del episodio 8. Quedan por recorrer los combates, los finales y la transición continua entre discos.

## Corrección EVT02 verificada en candidato local

El registro de `tools/discover_registered_overlays.py` fija EVT02 a la versión y base atribuidas por la coincidencia completa en RAM. Rechaza versiones con tamaño/hash diferentes; no supone que todos los EVT estén colocados en esa dirección. Los candidatos nuevos se generan en un directorio privado y conservan las variantes anteriores de una misma dirección de CPU.

Se añadieron 29.296 candidatos a los 614.024 existentes, hasta 643.320. La build aislada recompiló 75 objetos generados y reutilizó los 1.535 restantes cuyos fuentes eran idénticos. No sustituyó el ejecutable compartido de las pruebas de español ni modificó su base activa. Los objetos/pasos y hashes están en el manifiesto privado de `local/work/episode2-candidate`; el [informe público](episode2-aot-fix.json) contiene solo metadatos y resultados.

Antes del cambio, la regresión desde el estado 6688 falla con salida 4 en 00204000. Después, el candidato pasa 1.200 fotogramas desde el mismo estado: todos los hashes y el RGB final coinciden con el intérprete, con cero bloques interpretados en AOT. La prueba desde arranque y SRAM originales también completa **9.501 fotogramas**, todos coincidentes con el intérprete, RGB final idéntico y cero bloques interpretados. El último hash es `332fc7fa22f639e9`; la captura muestra el diálogo de apertura del combate. Esto cierra el bloqueo observado de carga, no el combate entero.

La v0.2.0-test.1 permanece inmutable y todavía contiene ese bloqueo del capítulo 2. La corrección está verificada en un candidato local, no en un nuevo release. La build usada para este resultado conserva la presentación anterior al prototipo T10, aislando la ampliación de código de los cambios visuales que se prueban por separado.

```powershell
python tools/discover_registered_overlays.py `
  --image "local/prepared/disc1/Track 01.iso" --module EVT02 `
  --seed-blocks local/work/sakura/blocks.txt `
  --output local/work/episode2-aot
```

El resultado es una base candidata: coordinar su regeneración AOT en un directorio propio antes de promoverla. Para la regresión, `tests/test_later_chapter_runtime.py` usa los fixtures privados; `SAKURA_OWNER_ROOT` y `SAKURA_LATER_TEST_EXE` permiten señalar el workspace del propietario y el binario aislado desde un worktree. `SAKURA_LATER_COLD=1` habilita la comparación larga desde SRAM; sin esa variable se prueba la frontera de 1.200 fotogramas.
