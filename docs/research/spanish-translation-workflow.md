# Guiones del disco traducido para la edición en español

El directorio privado `local/work/spanish-translation` contiene 56 tablas UTF‑8 en JSONL y CSV. `translation-manifest.json` indica la ruta y cantidad de registros de cada tabla. El primer guion tiene 605 registros en `tables/disc1/SAKURA1/0100TBL.jsonl`.

```powershell
python tools/prepare_translation_workspace.py
python -m unittest discover -s tests -p test_translation_workspace.py
```

El generador lee `local/work/dialogue-catalog-worker`. También admite `--catalog` para otro catálogo validado y `--output` para crear un nuevo directorio bajo `local/work`. El generador exige un destino nuevo para proteger el trabajo ya editado.

## Edición

- Elegir JSONL o CSV como copia de trabajo. Ambas versiones arrancan con el mismo contenido y se editan por separado.
- Escribir el español en `target_es` y actualizar `status` según el avance. El estado inicial es `untranslated`. Conservar `record_key` como identificador de la fila.
- Leer `source_en` para conservar los CR y los caracteres originales decodificados desde Windows‑1252. `source_en_display` muestra el mismo texto con saltos LF para lectura. En JSONL, CR y tabuladores aparecen como escapes. En CSV, los saltos van dentro de celdas entrecomilladas. Abrir con un lector CSV e importar las columnas como texto si se usa una hoja de cálculo.
- Revisar `prefix0`, `prefix1`, offsets, `text_bytes_hex` y `unsupported_controls` cuando una línea requiera contexto. Los dos prefijos preservan los valores nativos y sus semánticas siguen sin verificar. El flujo prepara guiones y deja la reinserción en Saturn para la herramienta de parche.

## Identidad entre discos

El catálogo contiene 59.450 registros físicos, 29.725 por disco. Para compartir la traducción se exige la misma ruta ISO, el mismo SHA‑256 de tabla y la misma secuencia de registros. El primer disco identifica las 29.725 filas canónicas de esta edición. Cada campo `alias_record_keys` identifica explícitamente la fila física equivalente del disco 2. Las tablas con rutas o hashes distintos conservan traducciones separadas, incluso si reutilizan IDs.

`source-manifest.json` conserva el manifiesto original con los hashes de los discos y las tablas. `translation-manifest.json` registra también los SHA‑256 del manifiesto y del JSONL de origen. Los guiones permanecen en el árbol privado excluido de Git. La cobertura corresponde a los recursos nativos `*TBL.BIN` del catálogo de inglés.
