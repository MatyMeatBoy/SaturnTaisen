# Elecciones LIPS desde datos precargados

Continúa T11 dentro del alcance aprobado de texto HD precargado. Evidencia: [cursor LIPS](../../research/lips-script-cursor.md). No modifica el guion, los tiempos, las entradas, las posiciones ni los ZIP entregados.

## Diseño y límites

Preparar un índice inmutable de comandos completos `2E8000` y su registro de opciones. Cada grupo ocupa un registro con saltos CR. Capturar su testigo junto al framebuffer, con coincidencia completa de script y TBL residentes y cursor BE32 en060685B4. El puntero narrativo no identifica las opciones.

El helper admite límites explícitos y rechaza referencias ambiguas. La primera activación del host queda fijada a0102.BIN/26646bytes/FNV0CE1CF29E7390A98, la fuente observada. No generalizar178000, batalla u otros scripts sin evidencia. La ausencia de un testigo conserva la ruta previa.

La sustitución es atómica por panel: reloj, filas, centrado, bancos, tinta y placas actuales siguen siendo obligatorios. Solo si todas las opciones coinciden con sus tiles/bytes y el registro completo se toman vistas prestadas del catálogo sellado. No reconstruir cadenas para el grupo preparado; mantener la reconstrucción existente en fallback.

## Trabajo

- [x] Helper ChoicePreload e índice acotado; tests RED/GREEN de cursor, revisiones, ambiguos y límites.
- [x] Helper puro de filas/tiles de opciones y tests de dos/tres filas, centrado, CP1252 y bounds.
- [x] Fixture de panel completo: préstamo de todas las filas, fallback atómico por registro equivocado y propiedad de tinta intacta.
- [x] Conectar preparación, captura bajo fbMutex y copia junto a píxeles; mantener Original/headless/GPU fuera del trabajo nuevo.
- [x] Capturar patch0050 y validar árbol SDK antes de compilar en una salida aislada.
- [x] Comparar paneles de dos/tres opciones, selección, confirmación y vencimiento; hashes/RGB idénticos y traza efectiva de catálogo. Conservar las referencias y la falta de prueba de otras ramas.
- [x] Revisión, pendientes y evidencia; integración por PR34. Test.3 queda inmutable.

## Verificación en curso

Tres fixtures pasan contra el SDK compuesto0001..0050, validado de nuevo sin diferencias. El candidato674.182 tiene SHA256 `df68e9dbe2c7d9efe273e0e716c504774ba5c5f5f0826abc783a2e3d6bffcbd3`. Doce pares de ejecuciones coinciden en3.240 hashes y102 pares RGB, incluidos Original, texto nativo, Zoom, conjunto y run-ahead2. Las trazas verifican11 comandos precargados y consumo real de los grupos20008/20002. Evidencia privada: `local/work/choice-preload-runtime/result.json`.

El primer ensayo partía de paneles ya confirmados y cerrándose. Se obtuvieron semillas anteriores mediante entradas normales, sin cambiar huésped ni reloj. El verificador privado `choice-input-probe/verify.py` pasa para dos/tres filas: Abajo mueve el resaltado a la segunda fila en30; A elimina el panel antes de150 y abre la respuesta correspondiente en170; el control neutro conserva el panel en150 y vence con otra respuesta en450. La inspección del frontend confirmó que el guard `moviePlay.empty()` sí engloba la escritura del mando; no hubo que corregir entradas SDL.

La comparación adicional desde esas semillas ya pasa para tres opciones: seis perfiles,2.100 hashes y59 pares RGB idénticos,0 interpretados. La suite equivalente de dos opciones también pasa: otros 2.100 hashes y 59 pares RGB. Las tres suites suman 24 pares de ejecuciones, 7.440 hashes y 220 pares RGB iguales, con cero interpretados. Revisión independiente de helpers/panel y tres fixtures sin bloqueos.
