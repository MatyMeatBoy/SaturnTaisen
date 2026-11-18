# Índice de recursos y escenas

El índice privado en `local/work/scene-index` reúne los recursos de los dos discos ingleses preparados y las observaciones documentadas de ejecución.

```powershell
python tools/build_scene_index.py
python -m unittest discover -s tests -p test_scene_index.py
```

- `resource-inventory.json` y `resource-inventory.csv` identifican las 3.570 entradas de archivo del sistema ISO, 1.785 por disco. Cada entrada conserva disco, ruta ISO, LBA, tamaño, SHA-256 y los flujos de vídeo identificados dentro del archivo.
- `scene-index.json` y `scene-index.csv` incluyen 166 candidatos procedentes de recursos y nueve observaciones de ejecución. Los candidatos comprenden 112 tablas de diálogo y 54 flujos de vídeo.
- `manifest.json` registra los hashes de los discos, el manifiesto y el JSONL de origen, los recuentos y el vocabulario de etiquetas.

Los seis rótulos visibles son **vídeo**, **diálogo**, **elección**, **mapa**, **combate** y **menú**. Sus IDs de intercambio son `video`, `dialogo`, `eleccion`, `mapa`, `combate` y `menu`. Una observación de transición puede tener etiqueta nula. `certainty` distingue observaciones e inferencias, con evidencia por fila. El índice inventaría los archivos de ambos discos. La cobertura de ejecución se limita a las nueve muestras anotadas.

## Vídeos y relación con el texto

El lector valida las estructuras FILM, FDSC y STAB para Cinepak, incluida la longitud de cada muestra dentro del archivo. Identificó cuatro flujos en archivos CPK independientes y 50 flujos dentro de `/SAKURA4`, 31 en el disco 1 y 19 en el disco 2. Cada flujo conserva el desplazamiento relativo, dimensiones, cantidad de muestras y SHA-256 de su extensión. El reconocimiento de archivo proporciona un candidato de vídeo. La presencia de texto y las condiciones de avance de estos clips siguen como desconocidas.

`dialogue_table` y `associated_record_keys` enlazan las 59.450 claves de registro con sus tablas exactas, identificadas por disco, ruta y hash. `record_association=table_inventory` explica el alcance de ese enlace. Determinar qué entradas aparecen durante un vídeo o una visita concreta requiere observar esa ruta. El índice evita asociar recursos por prefijo o numeración.

## Uso en Zoom y traducción

`runtime_layout` conserva el layout observado cuando figura en la evidencia. `zoom_eligibility=validated_for_observation` se ciñe al encuadre de esa muestra. Las filas desconocidas mantienen `fallback_layout=native`. Un `wait_for_text` nulo deja pendiente la decisión sobre el avance automático.

El traductor puede usar `associated_record_keys` para localizar las filas correspondientes en `local/work/spanish-translation`, que también contiene sus alias entre discos. El índice exporta metadatos y punteros a las evidencias locales. Los archivos de imagen, vídeo y guiones quedan en sus ubicaciones privadas.
